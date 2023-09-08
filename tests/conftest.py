from pathlib import Path
import tomllib
import pytest

import numpy as np

import src.modes as m


f = Path("tests/refs/viv.toml")
with open(f, "rb") as i:
    inputs = tomllib.load(i)


@pytest.fixture
def seabed():
    return m.Seabed(**inputs["Seabed"])


@pytest.fixture
def pipe():
    return m.Pipe(**inputs["Pipe"])


@pytest.fixture
def model():
    return m.Model(**inputs["Model"])


@pytest.fixture
def system():
    return m.System(**inputs["System"])


@pytest.fixture
def mode_shape():
    return np.array(
        [
            [0, 0, 0],
            [0, 0, np.sin(np.pi / 4)],
            [0, 0, 1],
            [0, 0, np.sin(3 * np.pi / 4)],
            [0, 0, 0],
        ]
    )
