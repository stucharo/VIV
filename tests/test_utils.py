import math

import pytest

import tests.conftest as ct
import src.utils as u


def test_get_A():
    assert u.get_A(1, 0.5) == pytest.approx(0.5890486)
    assert u.get_A(1) == pytest.approx(math.pi / 4)


def test_Seabed():
    s = u.Seabed(**ct.inputs["Seabed"])
    assert s.K_vert_sta == ct.inputs["Seabed"]["K_vert_sta"]
    assert s.K_ax_dyn == ct.inputs["Seabed"]["K_ax_dyn"]
    assert s.mu_ax == ct.inputs["Seabed"]["mu_ax"]
    assert s.C_V == ct.inputs["Seabed"]["C_V"]
    assert s.C_L == ct.inputs["Seabed"]["C_L"]
    assert s.nu == ct.inputs["Seabed"]["nu"]


def test_Pipe():
    p = u.Pipe(**ct.inputs["Pipe"])

    assert p.od == ct.inputs["Pipe"]["od"]
    assert p.wt == ct.inputs["Pipe"]["wt"]
    assert p.E == ct.inputs["Pipe"]["E"]
    assert p.nu == ct.inputs["Pipe"]["nu"]
    assert p.alpha == ct.inputs["Pipe"]["alpha"]
    assert p.rho_steel == ct.inputs["Pipe"]["rho_steel"]
    assert p.rho_contents == ct.inputs["Pipe"]["rho_contents"]
    assert p.Pi == ct.inputs["Pipe"]["Pi"]
    assert p.T == ct.inputs["Pipe"]["T"]


def test_Pipe_rho_eff(pipe):
    actual = pipe.get_rho_eff()
    expected = 9.1416985e3

    assert actual == pytest.approx(expected)


def test_Pipe_get_sigma_ax(pipe):
    actual = pipe.get_sigma_ax()
    expected = 3.455259e7

    assert actual == pytest.approx(expected)


def test_Model():
    mod = u.Model(**ct.inputs["Model"])

    assert mod.element_length == ct.inputs["Model"]["element_length"]
    assert mod.g == ct.inputs["Model"]["g"]
    assert mod.water_depth == ct.inputs["Model"]["water_depth"]
    assert mod.rho_sw == ct.inputs["Model"]["rho_sw"]
    assert mod.bathymetry == ct.inputs["Model"]["bathymetry"]
