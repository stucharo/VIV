from collections import namedtuple
from dataclasses import dataclass
import glob
import math
from textwrap import dedent
import subprocess
from pathlib import Path

import numpy as np

Seabed = namedtuple("Seabed", "K_vert_sta K_ax_dyn mu_ax C_V C_L nu")

Model = namedtuple("Model", "element_length g water_depth rho_sw bathymetry")

System = namedtuple("System", "abaqus_bat_path cpus")


def get_A(od: float, id: float = 0):
    return math.pi * (od**2 - id**2) / 4


@dataclass
class Pipe:
    od: float
    wt: float
    E: float
    nu: float
    alpha: float
    rho_steel: float
    rho_contents: float
    Pi: float
    T: float

    def _get_total_mass(self):
        A_steel = get_A(self.od, self.od - 2 * self.wt)
        m_steel = A_steel * self.rho_steel
        m_contents = get_A(self.od - 2 * self.wt) * self.rho_contents
        return m_steel + m_contents

    def get_rho_eff(self):
        A_steel = get_A(self.od, self.od - 2 * self.wt)
        return self._get_total_mass() / A_steel

    def get_sigma_ax(self):
        A_steel = get_A(self.od, self.od - 2 * self.wt)
        A_cont = get_A(self.od - 2 * self.wt)
        eaf = (
            self.Pi * A_cont * (1 - 2 * self.nu)
            + self.E * A_steel * self.alpha * self.T
        )
        return eaf / A_steel

    def get_rho_s_rho(self, rho_seawater):
        A_OA = get_A(self.od)
        m_total = self._get_total_mass()
        rho_pipe = m_total / A_OA
        return rho_pipe / rho_seawater


def get_mode_shapes(
    model_path,
    model: Model,
    pipe: Pipe,
    seabed: Seabed,
    system: System,
):
    run_in_place(model_path, model, pipe, seabed, system)
    pp_in_place(model_path, system)
    run_modal(model_path, pipe, seabed, model, system)
    modes = pp_modal(model_path, system)
    return modes


def run_in_place(model_path, model: Model, pipe: Pipe, seabed: Seabed, system: System):
    write_in_place_input_file(model_path, model, pipe, seabed)
    run_abaqus(model_path, "in_place", system)


def write_in_place_input_file(
    model_path,
    model: Model,
    pipe: Pipe,
    seabed: Seabed,
):
    number_of_elements = int(
        (model.bathymetry[-1][0] - model.bathymetry[0][0]) / model.element_length
    )
    last_node = number_of_elements + 1
    with open(Path(model_path, "in_place.inp"), "w") as i:
        i.write(
            dedent(
                f"""\
                *NODE, NSET=PIPELINE
                1, {model.bathymetry[0][0]}, 0
                {last_node}, {model.bathymetry[-1][0]}, 0
                *NGEN, NSET=PIPELINE
                1, {last_node}, 1
                *ELEMENT, TYPE=PIPE21H, ELSET=PIPELINE
                1, 1, 2
                *ELGEN, ELSET=PIPELINE
                1, {number_of_elements}
                *BEAM SECTION, ELSET=PIPELINE, SECTION=THICK PIPE, MATERIAL=STEEL
                {pipe.od}, {pipe.wt}
                *MATERIAL, NAME=STEEL
                *ELASTIC, TYPE=ISOTROPIC
                {pipe.E:.3e}, {pipe.nu}
                *EXPANSION, TYPE=ISO
                {pipe.alpha:.3e}
                *DENSITY
                {pipe.get_rho_eff():.3e}
                *BOUNDARY, TYPE=DISPLACEMENT
                1, 1, 1, 0
                1, 6, 6, 0
                {last_node}, 1, 1, 0
                {last_node}, 6, 6, 0
                *SURFACE, NAME=PIPELINE, TYPE=ELEMENT
                PIPELINE
                *NODE, NSET=SEABED_REF
                {last_node+1}, -10, 0
                *SURFACE, TYPE=SEGMENTS, NAME=SEABED
                START, {model.bathymetry[0][0]-10}, {model.bathymetry[0][1]}
                """
            )
        )
        for p in model.bathymetry:
            i.write(f"LINE, {p[0]}, {p[1]}\n")
        i.write(
            dedent(
                f"""\
                LINE, {model.bathymetry[-1][0]+10}, {model.bathymetry[-1][1]}
                *SURFACE INTERACTION, NAME=SEABED
                *SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=LINEAR
                {seabed.K_vert_sta:.3e}
                *FRICTION
                {seabed.mu_ax:.3e}
                *RIGID BODY, ANALYTICAL SURFACE=SEABED, REF NODE=SEABED_REF
                *CONTACT PAIR, INTERACTION=SEABED, TYPE=NODE TO SURFACE
                PIPELINE, SEABED
                *STEP, NLGEOM=YES
                *STATIC
                0.1,1,1E-10,1
                *BOUNDARY, OP=NEW, FIXED
                1, 1, 1, 0
                1, 6, 6, 0
                {last_node}, 1, 1, 0
                {last_node}, 6, 6, 0
                SEABED_REF, 1, 2, 0
                SEABED_REF, 6, 6, 0
                *DLOAD, OP=NEW
                PIPELINE, GRAV, {model.g}, 0, -1
                *OUTPUT, FIELD, VARIABLE=PRESELECT
                *ELEMENT OUTPUT, ELSET=PIPELINE, VARIABLE=PRESELECT
                ESF1, SF, SE, S
                *NODE OUTPUT, NSET=PIPELINE, VARIABLE=PRESELECT
                *END STEP
                *STEP, NLGEOM=YES
                *STATIC
                0.1, 1, 1E-10, 1
                *DLOAD, OP=MOD
                PIPELINE, PI, {pipe.Pi:.3e}, {pipe.od-2*pipe.wt:.3e}
                *TEMPERATURE
                PIPELINE, {pipe.T:.3e}
                *OUTPUT, FIELD, VARIABLE=PRESELECT
                *ELEMENT OUTPUT, ELSET=PIPELINE, VARIABLE=PRESELECT
                ESF1, SF, SE, S
                *NODE OUTPUT, NSET=PIPELINE, VARIABLE=PRESELECT
                *END STEP
                """
            )
        )


def pp_in_place(model_path, system: System):
    write_in_place_pp_file(model_path)
    pp_abaqus(model_path, "in_place_pp.py", system)


def write_in_place_pp_file(model_path):
    with open(Path(model_path, "in_place_pp.py"), "w") as p:
        p.write(
            dedent(
                """\
                import numpy as np

                import odbAccess

                odb = odbAccess.openOdb("in_place.odb")
                u = odb.steps["Step-2"].frames[-1].fieldOutputs["U"]
                n = odb.rootAssembly.instances["PART-1-1"].nodes
                seabed_segments = odb.rootAssembly.instances["SEABED"].analyticSurface.segments

                seabed_surface = np.zeros((len(seabed_segments), 2))
                for i in range(len(seabed_segments)):
                    coords = seabed_segments[i].data[0]
                    seabed_surface[i, 0] = coords[0]
                    seabed_surface[i, 1] = coords[1]

                with open("in_place_nodes.dat", "w") as f:
                    f.write("*NODE, NSET=PIPE\\n")

                    with open("gaps.dat", "w") as c:
                        for i in range(len(n) - 1):
                            # get displaced coordinates
                            x = n[i].coordinates[0] + u.values[i].data[0]
                            y = n[i].coordinates[1] + u.values[i].data[1]

                            node = i + 1
                            # interpolate seabed elevation below node and calculate vertical gap
                            # this is required because COPEN also considers the wall of the span
                            sb_elevation = np.interp(x, seabed_surface[:, 0], seabed_surface[:, 1])
                            gap = y - sb_elevation
                            # write modal node file
                            f.write("{0:4d}, {1:9.3e}, {2:9.3e}, 0\\n".format(node, x, y))
                            # write gap file
                            c.write("{0:4d}, {1:9.3e}\\n".format(node, y - sb_elevation))
                """
            )
        )


def run_modal(model_path, pipe: Pipe, seabed: Seabed, model: Model, system: System):
    write_modal_inp(model_path, pipe, seabed, model)
    run_abaqus(model_path, "modal", system)


def write_modal_inp(model_path, pipe: Pipe, seabed: Seabed, model: Model):
    gaps = get_gaps(model_path)
    nodes = len(gaps)

    contacts = [n for n in gaps if n[1] <= 0]
    num_contacts = len(contacts)

    with open(Path(model_path, "modal.inp"), "w") as s:
        s.write(
            dedent(
                f"""\
                *INCLUDE, INPUT=in_place_nodes.dat
                *ELEMENT, ELSET=PIPE, TYPE=PIPE31H
                1, 1, 2
                *ELGEN, ELSET=PIPE
                1, {nodes-1}, 1, 1
                *BEAM SECTION,SECT=PIPE,ELSET=PIPE,MATERIAL=STEEL
                {pipe.od}, {pipe.wt}
                *MATERIAL, NAME=STEEL
                *ELASTIC
                {pipe.E:.3e}, {pipe.nu}
                *DENSITY
                {pipe.get_rho_eff():.3e}
                """
            )
        )
        for n, contact in enumerate(contacts):
            s.write(
                dedent(
                    f"""\
                    *ELEMENT, TYPE=SPRING1, ELSET=SPR_AX
                    {nodes+n}, {contact[0]}
                    *ELEMENT, TYPE=SPRING1, ELSET=SPR_VERT
                    {nodes+num_contacts+n}, {contact[0]}
                    *ELEMENT, TYPE=SPRING1, ELSET=SPR_LAT
                    {nodes+2*num_contacts+n}, {contact[0]}
                    """
                )
            )
        s.write(
            dedent(
                f"""\
                *SPRING, ELSET=SPR_AX
                1
                {seabed.K_ax_dyn*model.element_length:9.3e}
                *SPRING, ELSET=SPR_VERT
                2
                {get_K_V_d(pipe, seabed, model)*model.element_length:9.3e}
                *SPRING, ELSET=SPR_LAT
                3
                {get_K_L_d(pipe, seabed, model)*model.element_length:9.3e}
                *AQUA
                -{model.water_depth}, 0., {model.g}, {model.rho_sw}
                *INITIAL CONDITIONS, TYPE=STRESS
                PIPE, {pipe.get_sigma_ax():.3e}
                *STEP, INC=100, NLGEOM 
                INITIAL SET UP
                *STATIC
                0.0001, 1.0, 1.0E-9   
                *CONTROLS, ANALYSIS=DISCONTINUOUS
                *BOUNDARY, OP=NEW 
                1, 1, 6 
                {nodes}, 2, 3
                PIPE, 1, 3
                *OUTPUT, FIELD, FREQ=10, VARIABLE=PRESELECT 
                **   
                *ELEMENT OUTPUT, ELSET=PIPE     
                SF, SE, ESF1, TEMP
                *NODE OUTPUT, NSET=PIPE
                U, COORD
                ** 
                *OUTPUT, HISTORY, FREQ=0, VARIABLE=PRESELECT
                **
                *END STEP 
                *STEP, NLGEOM, UNSYMM=YES, INC=2000
                FREQUENCY EXTRACTION
                *FREQUENCY, EIGENSOLVER=LANCZOS
                20
                **
                *BOUNDARY, OP=NEW
                1, 1, 6
                {nodes}, 2, 3
                PIPE, 4, 4
                *D ADDED MASS
                """
            )
        )
        for i in range(nodes - 1):
            avg_gap = max((gaps[i + 1][1] + gaps[i][1]) / 2, 0)
            s.write(f"{i+1}, FI, {pipe.od}, {get_added_mass(avg_gap, pipe.od)}\n")
        s.write(
            dedent(
                f"""\
                *NODE PRINT, GLOBAL=YES, NSET=PIPE, FREQ=999
                U,
                *OUTPUT, FIELD, VARIABLE=ALL, FREQUENCY=999
                *MODAL FILE
                *END STEP
                """
            )
        )


def get_gaps(model_path):
    gaps = []
    lines = 0
    with open(Path(model_path, "gaps.dat"), "r") as c:
        for line in c.readlines():
            lines += 1
            node, gap = line.split(",")
            gaps.append((int(node), float(gap)))
    return gaps


def get_added_mass(e, D):
    if e <= 0:
        return 2.28
    if e / D < 0.8:
        return 0.68 + 1.6 / (1 + 5 * e / D)
    return 1


def pp_modal(model_path, system: System):
    write_modal_pp_file(model_path)
    pp_abaqus(model_path, "modal_pp.py", system)
    modes = get_modes(model_path)
    return modes


def write_modal_pp_file(model_path):
    with open(Path(model_path, "modal_pp.py"), "w") as p:
        p.write(
            dedent(
                """\
                import numpy as np

                import odbAccess

                odb = odbAccess.openOdb("modal.odb")

                s = odb.steps["Step-2"]
                nodes = odb.rootAssembly.instances["PART-1-1"].nodes

                modes = len(s.frames)

                freqs = []

                for m in range(1, modes):
                    f = s.frames[m]
                    freqs.append(f.frequency)
                    ms = np.zeros((len(nodes), 3))
                    for n in range(len(nodes)):
                        ms[n, :] = f.fieldOutputs["U"].values[n].data
                    fname = "mode_{0}.dat".format(m)
                    np.savetxt(fname, ms, delimiter=",")

                np.savetxt("freqs.dat", freqs, delimiter=",")
                """
            )
        )


def get_modes(model_path):
    nf = read_natural_freqs(model_path)
    modes = read_mode_shapes(model_path)

    for k in modes.keys():
        modes[k]["frequency"] = nf[k - 1]

    return modes


def read_natural_freqs(model_path):
    with open(model_path / "freqs.dat", "r") as f:
        freqs = [float(n.strip()) for n in f.readlines()]

    return freqs


def read_mode_shapes(model_path):
    modes = {}
    mode_shape_files = glob.glob("mode_*.dat", root_dir=model_path)

    for msf in mode_shape_files:
        ms = np.loadtxt(model_path / msf, delimiter=",")
        mode_number = int(msf[msf.find("_") + 1 : msf.find(".")])
        modes[mode_number] = {
            "mode_shape": rotate_mode(ms),
            "direction": get_direction(ms),
        }

    return dict(sorted(modes.items()))


def rotate_mode(ms):
    max_amplitude = np.argmax(np.sqrt(ms[:, 1] ** 2 + ms[:, 2] ** 2))
    angle = -np.arctan2(ms[max_amplitude, 1], ms[max_amplitude, 2])

    _x = np.cos(angle) * ms[:, 2] - np.sin(angle) * ms[:, 1]
    _y = np.sin(angle) * ms[:, 2] + np.cos(angle) * ms[:, 1]

    return np.vstack((_x, _y)).T


def get_direction(ms):
    d = np.unravel_index(np.argmax(ms), ms.shape)[1]
    if d == 0:
        return "axial"
    if d == 1:
        return "cross-flow"
    return "inline"


def get_K_V_d(pipe: Pipe, seabed: Seabed, model: Model):
    return (
        seabed.C_V
        / (1 - seabed.nu)
        * (2 / 3 * pipe.get_rho_s_rho(model.rho_sw) + (1 / 3))
        * math.sqrt(pipe.od)
    )


def get_K_L_d(pipe: Pipe, seabed: Seabed, model: Model):
    return (
        seabed.C_L
        * (1 + seabed.nu)
        * (2 / 3 * pipe.get_rho_s_rho(model.rho_sw) + (1 / 3))
        * math.sqrt(pipe.od)
    )


def run_abaqus(model_path, jobname, system: System):
    subprocess.run(
        [
            system.abaqus_bat_path,
            f"j={jobname}",
            "ask_delete=no",
            f"cpus={system.cpus}",
            "-int",
        ],
        cwd=model_path,
    )


def pp_abaqus(model_path, script, system: System):
    subprocess.run(
        [system.abaqus_bat_path, "python", script],
        cwd=model_path,
    )
