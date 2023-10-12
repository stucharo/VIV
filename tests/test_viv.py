import glob
import os
from pathlib import Path
import shutil

import src.viv as viv
import src.modes as m


def test_cli(mocker, model, pipe, seabed, system):
    mocked_get_mode_shapes = mocker.patch("src.viv.get_mode_shapes")

    viv.cli("tests\\refs\\viv.toml")

    mocked_get_mode_shapes.assert_called_once_with(
        os.getcwd(), model, pipe, seabed, system
    )


def test_plot_modes(tmp_path, model, pipe, seabed, system, mocker):
    ref_mode_shape_files = glob.glob("mode_*.dat", root_dir=Path("tests/refs"))
    for f in ref_mode_shape_files:
        shutil.copyfile(Path("tests/refs", f), Path(tmp_path, f))
    shutil.copyfile(Path("tests/refs/freqs.dat"), Path(tmp_path, "freqs.dat"))

    modes = m.get_modes(tmp_path)

    mocked_get_mode_shapes = mocker.patch("src.viv.get_mode_shapes", return_value=modes)
    mocked_savefig = mocker.patch("src.viv.plt.savefig")

    viv.plot_modes(tmp_path, pipe, model, seabed, system)

    mocked_savefig.assert_called_once_with(Path(tmp_path / "mode_shapes.png"))
    mocked_get_mode_shapes.assert_called_once_with(tmp_path, model, pipe, seabed, system)
