import src.modes as m
import filecmp
from pathlib import Path


def test_get_mode_shapes(tmp_path, seabed, model, pipe):
    m.get_mode_shapes(
        tmp_path,
        model,
        pipe,
        seabed,
    )
    
    assert filecmp.cmp(
        Path(tmp_path, "in_place_pp.py"), Path("tests/refs/in_place_pp.py")
    )
    assert filecmp.cmp(Path(tmp_path, "in_place.inp"), Path("tests/refs/in_place.inp"))
    assert filecmp.cmp(Path(tmp_path, "modal.inp"), Path("tests/refs/modal.inp"))
    assert filecmp.cmp(Path(tmp_path, "modal_pp.py"), Path("tests/refs/modal_pp.py"))
    for n in range(20):
        assert Path(tmp_path, f"mode_{n+1}.dat").is_file()
    assert filecmp.cmp(Path(tmp_path, "freqs.dat"), Path("tests/refs/freqs.dat"))
    assert filecmp.cmp(
        Path(tmp_path, "in_place_nodes.dat"), Path("tests/refs/in_place_nodes.dat")
    )


def test_cli(tmp_path):
    m.cli("tests\\refs\\viv.toml", tmp_path)
    
    assert filecmp.cmp(
        Path(tmp_path, "in_place_pp.py"), Path("tests/refs/in_place_pp.py")
    )
    assert filecmp.cmp(Path(tmp_path, "in_place.inp"), Path("tests/refs/in_place.inp"))
    assert filecmp.cmp(Path(tmp_path, "modal.inp"), Path("tests/refs/modal.inp"))
    assert filecmp.cmp(Path(tmp_path, "modal_pp.py"), Path("tests/refs/modal_pp.py"))
    for n in range(20):
        assert Path(tmp_path, f"mode_{n+1}.dat").is_file()
    assert filecmp.cmp(Path(tmp_path, "freqs.dat"), Path("tests/refs/freqs.dat"))
    assert filecmp.cmp(
        Path(tmp_path, "in_place_nodes.dat"), Path("tests/refs/in_place_nodes.dat")
    )
