import math
import os
import pytest
import src.modes as m
import filecmp
from pathlib import Path
import shutil
from unittest.mock import call
import tests.conftest as ct


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


def test_get_added_mass_1():
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



REF_GAPS = [
    (1, -0.005793),
    (2, -0.005793),
    (3, -0.005793),
    (4, -0.005793),
    (5, -0.005793),
    (6, -0.005793),
    (7, -0.005793),
    (8, -0.005793),
    (9, -0.005793),
    (10, -0.005793),
    (11, -0.005793),
    (12, -0.005793),
    (13, -0.005793),
    (14, -0.005793),
    (15, -0.005793),
    (16, -0.005793),
    (17, -0.005793),
    (18, -0.005793),
    (19, -0.005793),
    (20, -0.005793),
    (21, -0.005793),
    (22, -0.005793),
    (23, -0.005793),
    (24, -0.005793),
    (25, -0.005793),
    (26, -0.005793),
    (27, -0.005793),
    (28, -0.005793),
    (29, -0.005793),
    (30, -0.005793),
    (31, -0.005793),
    (32, -0.005793),
    (33, -0.005793),
    (34, -0.005793),
    (35, -0.005793),
    (36, -0.005793),
    (37, -0.005793),
    (38, -0.005793),
    (39, -0.005793),
    (40, -0.005793),
    (41, -0.005793),
    (42, -0.005793),
    (43, -0.005793),
    (44, -0.005793),
    (45, -0.005793),
    (46, -0.005793),
    (47, -0.005793),
    (48, -0.005793),
    (49, -0.005793),
    (50, -0.005793),
    (51, -0.005793),
    (52, -0.005793),
    (53, -0.005793),
    (54, -0.005793),
    (55, -0.005793),
    (56, -0.005793),
    (57, -0.005793),
    (58, -0.005793),
    (59, -0.005793),
    (60, -0.005793),
    (61, -0.005793),
    (62, -0.005793),
    (63, -0.005793),
    (64, -0.005793),
    (65, -0.005793),
    (66, -0.005793),
    (67, -0.005793),
    (68, -0.005793),
    (69, -0.005793),
    (70, -0.005793),
    (71, -0.005793),
    (72, -0.005793),
    (73, -0.005793),
    (74, -0.005793),
    (75, -0.005793),
    (76, -0.005793),
    (77, -0.005793),
    (78, -0.005793),
    (79, -0.005793),
    (80, -0.005793),
    (81, -0.005793),
    (82, -0.005793),
    (83, -0.005793),
    (84, -0.005793),
    (85, -0.005793),
    (86, -0.005793),
    (87, -0.005793),
    (88, -0.005793),
    (89, -0.005793),
    (90, -0.005793),
    (91, -0.005793),
    (92, -0.005793),
    (93, -0.005793),
    (94, -0.005793),
    (95, -0.005793),
    (96, -0.005793),
    (97, -0.005793),
    (98, -0.005793),
    (99, -0.005793),
    (100, -0.005793),
    (101, -0.005793),
    (102, -0.005793),
    (103, -0.005792),
    (104, -0.005792),
    (105, -0.005792),
    (106, -0.005792),
    (107, -0.005793),
    (108, -0.005793),
    (109, -0.005793),
    (110, -0.005793),
    (111, -0.005793),
    (112, -0.005793),
    (113, -0.005793),
    (114, -0.005793),
    (115, -0.005794),
    (116, -0.005794),
    (117, -0.005794),
    (118, -0.005794),
    (119, -0.005794),
    (120, -0.005795),
    (121, -0.005795),
    (122, -0.005794),
    (123, -0.005794),
    (124, -0.005793),
    (125, -0.005792),
    (126, -0.00579),
    (127, -0.005788),
    (128, -0.005785),
    (129, -0.005781),
    (130, -0.005777),
    (131, -0.005772),
    (132, -0.005767),
    (133, -0.005761),
    (134, -0.005756),
    (135, -0.005751),
    (136, -0.005748),
    (137, -0.005748),
    (138, -0.005752),
    (139, -0.005762),
    (140, -0.005778),
    (141, -0.005804),
    (142, -0.005841),
    (143, -0.005891),
    (144, -0.005955),
    (145, -0.006035),
    (146, -0.006129),
    (147, -0.006238),
    (148, -0.006357),
    (149, -0.006481),
    (150, -0.0066),
    (151, -0.006701),
    (152, -0.006766),
    (153, -0.006773),
    (154, -0.006694),
    (155, -0.006495),
    (156, -0.006138),
    (157, -0.00558),
    (158, -0.00478),
    (159, -0.003696),
    (160, -0.002292),
    (161, -0.0005477),
    (162, 0.001539),
    (163, 0.003939),
    (164, 0.006589),
    (165, 0.009393),
    (166, 0.01222),
    (167, 0.01492),
    (168, 0.01728),
    (169, 0.01908),
    (170, 0.02006),
    (171, 0.01993),
    (172, 0.01838),
    (173, 0.01504),
    (174, 0.009551),
    (175, 0.001494),
    (176, -0.009561),
    (177, -0.02407),
    (178, -0.04246),
    (179, -0.06503),
    (180, -0.09189),
    (181, 0.8772),
    (182, 0.843),
    (183, 0.8061),
    (184, 0.7673),
    (185, 0.7271),
    (186, 0.6862),
    (187, 0.6451),
    (188, 0.6044),
    (189, 0.5647),
    (190, 0.5263),
    (191, 0.4897),
    (192, 0.4554),
    (193, 0.4237),
    (194, 0.395),
    (195, 0.3694),
    (196, 0.3474),
    (197, 0.3291),
    (198, 0.3146),
    (199, 0.3042),
    (200, 0.2979),
    (201, 0.2958),
    (202, 0.2979),
    (203, 0.3042),
    (204, 0.3146),
    (205, 0.3291),
    (206, 0.3474),
    (207, 0.3694),
    (208, 0.395),
    (209, 0.4237),
    (210, 0.4554),
    (211, 0.4897),
    (212, 0.5263),
    (213, 0.5647),
    (214, 0.6044),
    (215, 0.6451),
    (216, 0.6862),
    (217, 0.7271),
    (218, 0.7673),
    (219, 0.8061),
    (220, 0.843),
    (221, 0.8772),
    (222, -0.09189),
    (223, -0.06503),
    (224, -0.04246),
    (225, -0.02407),
    (226, -0.009561),
    (227, 0.001494),
    (228, 0.009551),
    (229, 0.01504),
    (230, 0.01838),
    (231, 0.01993),
    (232, 0.02006),
    (233, 0.01908),
    (234, 0.01728),
    (235, 0.01492),
    (236, 0.01222),
    (237, 0.009393),
    (238, 0.006589),
    (239, 0.003939),
    (240, 0.001539),
    (241, -0.0005477),
    (242, -0.002292),
    (243, -0.003696),
    (244, -0.00478),
    (245, -0.00558),
    (246, -0.006138),
    (247, -0.006495),
    (248, -0.006694),
    (249, -0.006773),
    (250, -0.006766),
    (251, -0.006701),
    (252, -0.0066),
    (253, -0.006481),
    (254, -0.006357),
    (255, -0.006238),
    (256, -0.006129),
    (257, -0.006035),
    (258, -0.005955),
    (259, -0.005891),
    (260, -0.005841),
    (261, -0.005804),
    (262, -0.005778),
    (263, -0.005762),
    (264, -0.005752),
    (265, -0.005748),
    (266, -0.005748),
    (267, -0.005751),
    (268, -0.005756),
    (269, -0.005761),
    (270, -0.005767),
    (271, -0.005772),
    (272, -0.005777),
    (273, -0.005781),
    (274, -0.005785),
    (275, -0.005788),
    (276, -0.00579),
    (277, -0.005792),
    (278, -0.005793),
    (279, -0.005794),
    (280, -0.005794),
    (281, -0.005795),
    (282, -0.005795),
    (283, -0.005794),
    (284, -0.005794),
    (285, -0.005794),
    (286, -0.005794),
    (287, -0.005794),
    (288, -0.005793),
    (289, -0.005793),
    (290, -0.005793),
    (291, -0.005793),
    (292, -0.005793),
    (293, -0.005793),
    (294, -0.005793),
    (295, -0.005793),
    (296, -0.005792),
    (297, -0.005792),
    (298, -0.005792),
    (299, -0.005792),
    (300, -0.005793),
    (301, -0.005793),
    (302, -0.005793),
    (303, -0.005793),
    (304, -0.005793),
    (305, -0.005793),
    (306, -0.005793),
    (307, -0.005793),
    (308, -0.005793),
    (309, -0.005793),
    (310, -0.005793),
    (311, -0.005793),
    (312, -0.005793),
    (313, -0.005793),
    (314, -0.005793),
    (315, -0.005793),
    (316, -0.005793),
    (317, -0.005793),
    (318, -0.005793),
    (319, -0.005793),
    (320, -0.005793),
    (321, -0.005793),
    (322, -0.005793),
    (323, -0.005793),
    (324, -0.005793),
    (325, -0.005793),
    (326, -0.005793),
    (327, -0.005793),
    (328, -0.005793),
    (329, -0.005793),
    (330, -0.005793),
    (331, -0.005793),
    (332, -0.005793),
    (333, -0.005793),
    (334, -0.005793),
    (335, -0.005793),
    (336, -0.005793),
    (337, -0.005793),
    (338, -0.005793),
    (339, -0.005793),
    (340, -0.005793),
    (341, -0.005793),
    (342, -0.005793),
    (343, -0.005793),
    (344, -0.005793),
    (345, -0.005793),
    (346, -0.005793),
    (347, -0.005793),
    (348, -0.005793),
    (349, -0.005793),
    (350, -0.005793),
    (351, -0.005793),
    (352, -0.005793),
    (353, -0.005793),
    (354, -0.005793),
    (355, -0.005793),
    (356, -0.005793),
    (357, -0.005793),
    (358, -0.005793),
    (359, -0.005793),
    (360, -0.005793),
    (361, -0.005793),
    (362, -0.005793),
    (363, -0.005793),
    (364, -0.005793),
    (365, -0.005793),
    (366, -0.005793),
    (367, -0.005793),
    (368, -0.005793),
    (369, -0.005793),
    (370, -0.005793),
    (371, -0.005793),
    (372, -0.005793),
    (373, -0.005793),
    (374, -0.005793),
    (375, -0.005793),
    (376, -0.005793),
    (377, -0.005793),
    (378, -0.005793),
    (379, -0.005793),
    (380, -0.005793),
    (381, -0.005793),
    (382, -0.005793),
    (383, -0.005793),
    (384, -0.005793),
    (385, -0.005793),
    (386, -0.005793),
    (387, -0.005793),
    (388, -0.005793),
    (389, -0.005793),
    (390, -0.005793),
    (391, -0.005793),
    (392, -0.005793),
    (393, -0.005793),
    (394, -0.005793),
    (395, -0.005793),
    (396, -0.005793),
    (397, -0.005793),
    (398, -0.005793),
    (399, -0.005793),
    (400, -0.005793),
    (401, -0.005793),
]
