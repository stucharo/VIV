import glob
import math
import os
import pytest
import src.modes as m
import filecmp
from pathlib import Path
import shutil
from unittest.mock import call
import tests.conftest as ct

import numpy as np


def test_Seabed():
    s = m.Seabed(ct.K_vert_sta, ct.K_ax_dyn, ct.K_vert_dyn, ct.K_lat_dyn, ct.mu_ax)
    assert s.K_vert_sta == ct.K_vert_sta
    assert s.K_ax_dyn == ct.K_ax_dyn
    assert s.K_vert_dyn == ct.K_vert_dyn
    assert s.K_lat_dyn == ct.K_lat_dyn
    assert s.mu_ax == ct.mu_ax


def test_Pipe():
    p = m.Pipe(
        ct.od, ct.wt, ct.E, ct.nu, ct.alpha, ct.rho_steel, ct.rho_contents, ct.Pi, ct.T
    )

    assert p.od == ct.od
    assert p.wt == ct.wt
    assert p.E == ct.E
    assert p.nu == ct.nu
    assert p.alpha == ct.alpha
    assert p.rho_steel == ct.rho_steel
    assert p.rho_contents == ct.rho_contents
    assert p.Pi == ct.Pi
    assert p.T == ct.T


def test_get_A():
    assert m.get_A(1, 0.5) == pytest.approx(0.5890486)
    assert m.get_A(1) == pytest.approx(math.pi / 4)


def test_Pipe_rho_eff(pipe):
    actual = pipe.get_rho_eff()
    expected = 9.1416985e3

    assert actual == pytest.approx(expected)


def test_Pipe_get_sigma_ax(pipe):
    actual = pipe.get_sigma_ax()
    expected = 3.455259e7

    assert actual == pytest.approx(expected)


def test_Model():
    mod = m.Model(
        ct.span_length,
        ct.span_height,
        ct.total_length,
        ct.element_length,
        ct.g,
        ct.water_depth,
        ct.rho_sw,
    )

    assert mod.span_length == ct.span_length
    assert mod.span_height == ct.span_height
    assert mod.total_length == ct.total_length
    assert mod.element_length == ct.element_length
    assert mod.g == ct.g
    assert mod.water_depth == ct.water_depth
    assert mod.rho_sw == ct.rho_sw


def test_write_in_place_pp_file(tmp_path):
    m.write_in_place_pp_file(tmp_path)

    assert filecmp.cmp(
        Path(tmp_path, "in_place_pp.py"), Path("tests/refs/in_place_pp.py")
    )


def test_write_in_place_input_file(tmp_path, pipe, model, seabed):
    m.write_in_place_input_file(tmp_path, model, pipe, seabed)

    assert filecmp.cmp(Path(tmp_path, "in_place.inp"), Path("tests/refs/in_place.inp"))


def test_run_in_place(tmp_path, mocker, pipe, model, seabed):
    mocked_subprocess_run = mocker.patch("src.modes.subprocess.run")

    m.run_in_place(tmp_path, model, pipe, seabed)

    assert filecmp.cmp(Path(tmp_path, "in_place.inp"), Path("tests/refs/in_place.inp"))
    mocked_subprocess_run.assert_called_once_with(
        [
            "C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat",
            "j=in_place",
            "ask_delete=no",
            "cpus=2",
            "-int",
        ],
        cwd=tmp_path,
    )


def test_pp_in_place(tmp_path, mocker):
    mocked_subprocess_run = mocker.patch("src.modes.subprocess.run")

    m.pp_in_place(tmp_path)

    assert filecmp.cmp(
        Path(tmp_path, "in_place_pp.py"), Path("tests/refs/in_place_pp.py")
    )
    mocked_subprocess_run.assert_called_once_with(
        ["C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat", "python", "in_place_pp.py"],
        cwd=tmp_path,
    )


def test_get_gaps():
    gaps = m.get_gaps(Path("tests/refs"))

    assert gaps == REF_GAPS


def test_get_added_mass_1():
    e = 0.9
    d = 0.2

    actual = m.get_added_mass(e, d)
    expected = 1

    assert actual == expected


def test_get_added_mass():
    e = 0.01609
    d = 0.1683

    actual = m.get_added_mass(e, d)
    expected = 1.762532663

    assert actual == pytest.approx(expected)


def test_write_modal_inp(tmp_path, seabed, pipe, model):
    shutil.copyfile(Path("tests/refs/gaps.dat"), Path(tmp_path, "gaps.dat"))

    m.write_modal_inp(tmp_path, pipe, seabed, model)

    assert filecmp.cmp(Path(tmp_path, "modal.inp"), Path("tests/refs/modal.inp"))


def test_run_modal(tmp_path, mocker, seabed, pipe, model):
    shutil.copyfile(Path("tests/refs/gaps.dat"), Path(tmp_path, "gaps.dat"))

    mocked_subprocess_run = mocker.patch("src.modes.subprocess.run")

    m.run_modal(tmp_path, pipe, seabed, model)

    assert filecmp.cmp(Path(tmp_path, "modal.inp"), Path("tests/refs/modal.inp"))
    mocked_subprocess_run.assert_called_once_with(
        [
            "C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat",
            "j=modal",
            "ask_delete=no",
            "cpus=2",
            "-int",
        ],
        cwd=tmp_path,
    )


def test_write_modal_pp_file(tmp_path):
    m.write_modal_pp_file(tmp_path)

    assert filecmp.cmp(Path(tmp_path, "modal_pp.py"), Path("tests/refs/modal_pp.py"))


def test_pp_modal(tmp_path, mocker):
    mocked_subprocess_run = mocker.patch("src.modes.subprocess.run")

    m.pp_modal(tmp_path)

    assert filecmp.cmp(Path(tmp_path, "modal_pp.py"), Path("tests/refs/modal_pp.py"))
    mocked_subprocess_run.assert_called_once_with(
        ["C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat", "python", "modal_pp.py"],
        cwd=tmp_path,
    )


def test_get_mode_shapes(tmp_path, mocker, seabed, pipe, model):
    shutil.copyfile(Path("tests/refs/gaps.dat"), Path(tmp_path, "gaps.dat"))
    ref_mode_shape_files = glob.glob("mode_*.dat", root_dir=Path("tests/refs"))
    for f in ref_mode_shape_files:
        shutil.copyfile(Path("tests/refs", f), Path(tmp_path, f))
    shutil.copyfile(Path("tests/refs/freqs.dat"), Path(tmp_path, "freqs.dat"))

    mocked_subprocess_run = mocker.patch("src.modes.subprocess.run")

    m.get_mode_shapes(
        tmp_path,
        model,
        pipe,
        seabed,
    )

    calls = [
        call(
            [
                "C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat",
                "j=in_place",
                "ask_delete=no",
                "cpus=2",
                "-int",
            ],
            cwd=tmp_path,
        ),
        call(
            ["C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat", "python", "in_place_pp.py"],
            cwd=tmp_path,
        ),
        call(
            [
                "C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat",
                "j=modal",
                "ask_delete=no",
                "cpus=2",
                "-int",
            ],
            cwd=tmp_path,
        ),
        call(
            ["C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat", "python", "modal_pp.py"],
            cwd=tmp_path,
        ),
    ]

    mocked_subprocess_run.assert_has_calls(calls)

    assert filecmp.cmp(
        Path(tmp_path, "in_place_pp.py"), Path("tests/refs/in_place_pp.py")
    )
    assert filecmp.cmp(Path(tmp_path, "in_place.inp"), Path("tests/refs/in_place.inp"))
    assert filecmp.cmp(Path(tmp_path, "modal.inp"), Path("tests/refs/modal.inp"))
    assert filecmp.cmp(Path(tmp_path, "modal_pp.py"), Path("tests/refs/modal_pp.py"))


def test_cli(mocker, model, pipe, seabed):
    mocked_get_mode_shapes = mocker.patch("src.modes.get_mode_shapes")

    m.cli("tests\\refs\\viv.toml")

    mocked_get_mode_shapes.assert_called_once_with(os.getcwd(), model, pipe, seabed)


def test_read_natural_freqs(tmp_path):
    shutil.copyfile(Path("tests/refs/freqs.dat"), Path(tmp_path, "freqs.dat"))

    actual = m.read_natural_freqs(tmp_path)
    expected = REF_FREQS

    assert actual == pytest.approx(expected)


def test_read_mode_shape_files(tmp_path):
    ref_mode_shape_files = glob.glob("mode_*.dat", root_dir=Path("tests/refs"))
    for f in ref_mode_shape_files:
        shutil.copyfile(Path("tests/refs", f), Path(tmp_path, f))

    modes = m.read_mode_shapes(tmp_path)

    assert len(modes.keys()) == len(ref_mode_shape_files)
    for k, v in modes.items():
        assert type(v["mode_shape"]) is np.ndarray
        assert v["mode_shape"].shape[1] == 2
        print(k)
        assert v["direction"] == REF_DIRS[k]


def test_get_modes(tmp_path):
    ref_mode_shape_files = glob.glob("mode_*.dat", root_dir=Path("tests/refs"))
    for f in ref_mode_shape_files:
        shutil.copyfile(Path("tests/refs", f), Path(tmp_path, f))
    shutil.copyfile(Path("tests/refs/freqs.dat"), Path(tmp_path, "freqs.dat"))

    actual = m.get_modes(tmp_path)

    assert type(actual) is dict
    assert len(actual.keys()) == len(ref_mode_shape_files)
    freqs = np.array([(k, actual[k]["frequency"]) for k in actual.keys()])
    for i in [0, 1]:
        assert np.all(np.diff(freqs[:, i]) > 0)


def test_plot_modes(tmp_path, model, mocker):
    ref_mode_shape_files = glob.glob("mode_*.dat", root_dir=Path("tests/refs"))
    for f in ref_mode_shape_files:
        shutil.copyfile(Path("tests/refs", f), Path(tmp_path, f))
    shutil.copyfile(Path("tests/refs/freqs.dat"), Path(tmp_path, "freqs.dat"))

    mocked_savefig = mocker.patch("src.modes.plt.savefig")

    m.plot_modes(tmp_path, model.element_length)

    mocked_savefig.assert_called_once_with("mode_shapes.png")


def test_get_direction(mode_shape):
    d = m.get_direction(mode_shape)
    assert d == "inline"

    ms_1 = np.copy(mode_shape[:, 1])
    mode_shape[:, 1] = mode_shape[:, 2]
    mode_shape[:, 2] = ms_1
    d = m.get_direction(mode_shape)
    assert d == "cross-flow"

    ms_1 = np.copy(mode_shape[:, 1])
    mode_shape[:, 1] = mode_shape[:, 0]
    mode_shape[:, 0] = ms_1
    d = m.get_direction(mode_shape)
    assert d == "axial"

    # assert False


REF_GAPS = [
    (1, -5.792e-03),
    (2, -5.792e-03),
    (3, -5.792e-03),
    (4, -5.792e-03),
    (5, -5.792e-03),
    (6, -5.792e-03),
    (7, -5.792e-03),
    (8, -5.792e-03),
    (9, -5.792e-03),
    (10, -5.792e-03),
    (11, -5.793e-03),
    (12, -5.793e-03),
    (13, -5.793e-03),
    (14, -5.793e-03),
    (15, -5.793e-03),
    (16, -5.793e-03),
    (17, -5.793e-03),
    (18, -5.794e-03),
    (19, -5.794e-03),
    (20, -5.794e-03),
    (21, -5.794e-03),
    (22, -5.794e-03),
    (23, -5.794e-03),
    (24, -5.793e-03),
    (25, -5.792e-03),
    (26, -5.791e-03),
    (27, -5.790e-03),
    (28, -5.788e-03),
    (29, -5.786e-03),
    (30, -5.783e-03),
    (31, -5.780e-03),
    (32, -5.776e-03),
    (33, -5.772e-03),
    (34, -5.768e-03),
    (35, -5.764e-03),
    (36, -5.761e-03),
    (37, -5.760e-03),
    (38, -5.761e-03),
    (39, -5.765e-03),
    (40, -5.774e-03),
    (41, -5.789e-03),
    (42, -5.811e-03),
    (43, -5.842e-03),
    (44, -5.883e-03),
    (45, -5.936e-03),
    (46, -5.999e-03),
    (47, -6.074e-03),
    (48, -6.159e-03),
    (49, -6.250e-03),
    (50, -6.342e-03),
    (51, -6.428e-03),
    (52, -6.496e-03),
    (53, -6.533e-03),
    (54, -6.518e-03),
    (55, -6.430e-03),
    (56, -6.242e-03),
    (57, -5.924e-03),
    (58, -5.443e-03),
    (59, -4.766e-03),
    (60, -3.862e-03),
    (61, -2.705e-03),
    (62, -1.284e-03),
    (63, 3.992e-04),
    (64, 2.313e-03),
    (65, 4.396e-03),
    (66, 6.551e-03),
    (67, 8.650e-03),
    (68, 1.053e-02),
    (69, 1.200e-02),
    (70, 1.283e-02),
    (71, 1.276e-02),
    (72, 1.150e-02),
    (73, 8.724e-03),
    (74, 4.075e-03),
    (75, -2.832e-03),
    (76, -1.242e-02),
    (77, -2.511e-02),
    (78, -4.130e-02),
    (79, -6.126e-02),
    (80, -8.506e-02),
    (81, 8.875e-01),
    (82, 8.572e-01),
    (83, 8.245e-01),
    (84, 7.901e-01),
    (85, 7.546e-01),
    (86, 7.185e-01),
    (87, 6.823e-01),
    (88, 6.465e-01),
    (89, 6.116e-01),
    (90, 5.780e-01),
    (91, 5.460e-01),
    (92, 5.160e-01),
    (93, 4.883e-01),
    (94, 4.632e-01),
    (95, 4.409e-01),
    (96, 4.217e-01),
    (97, 4.058e-01),
    (98, 3.932e-01),
    (99, 3.842e-01),
    (100, 3.787e-01),
    (101, 3.769e-01),
    (102, 3.787e-01),
    (103, 3.842e-01),
    (104, 3.932e-01),
    (105, 4.058e-01),
    (106, 4.217e-01),
    (107, 4.409e-01),
    (108, 4.632e-01),
    (109, 4.883e-01),
    (110, 5.160e-01),
    (111, 5.460e-01),
    (112, 5.780e-01),
    (113, 6.116e-01),
    (114, 6.465e-01),
    (115, 6.823e-01),
    (116, 7.185e-01),
    (117, 7.546e-01),
    (118, 7.901e-01),
    (119, 8.245e-01),
    (120, 8.572e-01),
    (121, 8.875e-01),
    (122, -8.506e-02),
    (123, -6.126e-02),
    (124, -4.130e-02),
    (125, -2.511e-02),
    (126, -1.242e-02),
    (127, -2.832e-03),
    (128, 4.075e-03),
    (129, 8.724e-03),
    (130, 1.150e-02),
    (131, 1.276e-02),
    (132, 1.283e-02),
    (133, 1.200e-02),
    (134, 1.053e-02),
    (135, 8.650e-03),
    (136, 6.551e-03),
    (137, 4.396e-03),
    (138, 2.313e-03),
    (139, 3.992e-04),
    (140, -1.284e-03),
    (141, -2.705e-03),
    (142, -3.862e-03),
    (143, -4.766e-03),
    (144, -5.443e-03),
    (145, -5.924e-03),
    (146, -6.242e-03),
    (147, -6.430e-03),
    (148, -6.518e-03),
    (149, -6.533e-03),
    (150, -6.496e-03),
    (151, -6.428e-03),
    (152, -6.342e-03),
    (153, -6.250e-03),
    (154, -6.159e-03),
    (155, -6.074e-03),
    (156, -5.999e-03),
    (157, -5.936e-03),
    (158, -5.883e-03),
    (159, -5.842e-03),
    (160, -5.811e-03),
    (161, -5.789e-03),
    (162, -5.774e-03),
    (163, -5.765e-03),
    (164, -5.761e-03),
    (165, -5.760e-03),
    (166, -5.761e-03),
    (167, -5.764e-03),
    (168, -5.768e-03),
    (169, -5.772e-03),
    (170, -5.776e-03),
    (171, -5.780e-03),
    (172, -5.783e-03),
    (173, -5.786e-03),
    (174, -5.788e-03),
    (175, -5.790e-03),
    (176, -5.791e-03),
    (177, -5.792e-03),
    (178, -5.793e-03),
    (179, -5.794e-03),
    (180, -5.794e-03),
    (181, -5.794e-03),
    (182, -5.794e-03),
    (183, -5.794e-03),
    (184, -5.794e-03),
    (185, -5.793e-03),
    (186, -5.793e-03),
    (187, -5.793e-03),
    (188, -5.793e-03),
    (189, -5.793e-03),
    (190, -5.793e-03),
    (191, -5.793e-03),
    (192, -5.792e-03),
    (193, -5.792e-03),
    (194, -5.792e-03),
    (195, -5.792e-03),
    (196, -5.792e-03),
    (197, -5.792e-03),
    (198, -5.792e-03),
    (199, -5.792e-03),
    (200, -5.792e-03),
    (201, -5.792e-03),
]

REF_FREQS = [
    1.101099999999999968e00,
    1.314799999999999969e00,
    2.632699999999999818e00,
    2.704299999999999926e00,
    4.775800000000000267e00,
    4.950199999999999712e00,
    5.438399999999999679e00,
    5.556899999999999729e00,
    5.840200000000000280e00,
    5.920899999999999608e00,
    7.688200000000000145e00,
    7.925500000000000433e00,
    1.095199999999999996e01,
    1.135299999999999976e01,
    1.286100000000000065e01,
    1.289799999999999969e01,
    1.320500000000000007e01,
    1.416600000000000037e01,
    1.454400000000000048e01,
    1.471799999999999997e01,
]

REF_DIRS = {
    1: "inline",
    2: "cross-flow",
    3: "cross-flow",
    4: "inline",
    5: "cross-flow",
    6: "inline",
    7: "cross-flow",
    8: "cross-flow",
    9: "inline",
    10: "inline",
    11: "cross-flow",
    12: "inline",
    13: "cross-flow",
    14: "inline",
    15: "axial",
    16: "cross-flow",
    17: "cross-flow",
    18: "inline",
    19: "inline",
    20: "cross-flow",
}
