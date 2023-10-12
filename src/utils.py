from collections import namedtuple
from dataclasses import dataclass
import math

Seabed = namedtuple("Seabed", "K_vert_sta K_ax_dyn mu_ax C_V C_L nu")

Model = namedtuple("Model", "element_length g water_depth rho_sw bathymetry")

System = namedtuple("System", "abaqus_bat_path cpus")


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


def get_A(od: float, id: float = 0):
    return math.pi * (od**2 - id**2) / 4
