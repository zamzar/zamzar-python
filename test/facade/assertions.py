from pathlib import Path


def assert_empty_file(path: Path):
    assert path.exists(), f"File {path} should exist"
    assert path.stat().st_size == 0, f"File {path} should be empty"


def assert_non_empty_file(path: Path):
    assert path.exists(), f"File {path} should exist"
    assert path.stat().st_size > 0, f"File {path} should not be empty"
