import pytest

import src.modes as m


K_vert_sta = 2e5
K_ax_dyn = 1e6
K_vert_dyn = 2e6
K_lat_dyn = 3e6
mu_ax = 0.5
od = 0.1683
wt = 0.0127
E = 207e9
nu = 0.3
alpha = 1.17e-5
rho_steel = 7850
rho_contents = 500
Pi = 10e6
T = 10
span_length = 40
span_height = 1
total_length = 200
element_length = 1
g = 9.80665
water_depth = 150
rho_sw = 1025


@pytest.fixture
def seabed():
    return m.Seabed(K_vert_sta, K_ax_dyn, K_vert_dyn, K_lat_dyn, mu_ax)


@pytest.fixture
def pipe():
    return m.Pipe(od, wt, E, nu, alpha, rho_steel, rho_contents, Pi, T)


@pytest.fixture
def model():
    return m.Model(
        span_length, span_height, total_length, element_length, g, water_depth, rho_sw
    )
