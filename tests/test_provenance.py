"""Checks that a run record is complete, honest about the code state and never overwritten."""
import hashlib
import json
import subprocess
from datetime import UTC, datetime

import numpy as np
import pytest

from vfdebye import provenance


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        check=True, capture_output=True,
    )


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "repo"
    path.mkdir()
    git(path, "init", "-q")
    (path / "tracked.py").write_text("x = 1\n", encoding="utf-8")
    (path / "uv.lock").write_bytes(b"lock\n")  # bytes: no CRLF translation on Windows
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "init")
    return path


def read(record):
    return json.loads((record.dir / provenance.RECORD).read_text(encoding="utf-8"))


def test_completed_run_records_settings_inputs_code_and_environment(tmp_path, repo):
    data = tmp_path / "table.csv"
    data.write_bytes(b"a,b\n1,2\n")
    settings = {"band_hz": (1e7, 1e10), "order": 6, "poles0": np.array([-1 + 2j, -1 - 2j])}
    with provenance.run("demo", settings=settings, inputs=[data], runs_dir=tmp_path / "runs",
                        repo=repo, command=["demo"]) as record:
        assert read(record)["status"] == "running"
        record.update(stop_reason="tolerance", iterations=np.int64(7))
    saved = read(record)
    assert saved["status"] == "completed" and saved["error"] is None
    assert saved["finished"] is not None and saved["duration_seconds"] >= 0
    assert saved["command"] == ["demo"]
    assert saved["settings"] == {
        "band_hz": [1e7, 1e10], "order": 6,
        "poles0": [{"re": -1.0, "im": 2.0}, {"re": -1.0, "im": -2.0}],
    }
    assert saved["inputs"] == [{"path": str(data.resolve()),
                                "sha256": hashlib.sha256(b"a,b\n1,2\n").hexdigest()}]
    assert saved["outcome"] == {"stop_reason": "tolerance", "iterations": 7}
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    assert saved["code"]["commit"] == head and saved["code"]["dirty"] is False
    assert saved["environment"]["uv_lock_sha256"] == hashlib.sha256(b"lock\n").hexdigest()
    assert saved["environment"]["packages"]["numpy"] == np.__version__
    blas = np.show_config(mode="dicts")["Build Dependencies"]["blas"]["name"]
    assert saved["environment"]["linear_algebra"]["blas"]["name"] == blas


def test_uncommitted_changes_are_saved_with_the_run(tmp_path, repo):
    (repo / "tracked.py").write_text("x = 2\n", encoding="utf-8")
    (repo / "new.py").write_text("y = 3\n", encoding="utf-8")
    with provenance.run("dirty", settings={}, runs_dir=tmp_path / "runs", repo=repo) as record:
        pass
    code = read(record)["code"]
    assert code["dirty"] is True
    diff = (record.dir / "uncommitted.diff").read_bytes()
    assert b"+x = 2" in diff
    assert code["uncommitted_diff"]["sha256"] == hashlib.sha256(diff).hexdigest()
    assert [entry["path"] for entry in code["untracked"]] == ["new.py"]
    assert (record.dir / "untracked" / "new.py").read_text(encoding="utf-8") == "y = 3\n"


def test_missing_git_repository_is_reported_not_invented(tmp_path):
    folder = tmp_path / "not-a-repo"
    folder.mkdir()
    with provenance.run("nogit", settings={}, runs_dir=tmp_path / "runs", repo=folder) as record:
        pass
    code = read(record)["code"]
    assert code["available"] is False and code["reason"]
    assert "commit" not in code


def test_failed_run_is_recorded_and_the_error_propagates(tmp_path, repo):
    with pytest.raises(RuntimeError, match="diverged"):
        with provenance.run("fail", settings={}, runs_dir=tmp_path / "runs", repo=repo) as record:
            raise RuntimeError("diverged")
    saved = read(record)
    assert saved["status"] == "failed"
    assert saved["error"] == "RuntimeError: diverged"
    assert saved["finished"] is not None


def test_run_directory_is_never_overwritten(tmp_path, repo, monkeypatch):
    fixed = datetime(2026, 11, 9, 12, 0, 0, tzinfo=UTC)

    class FixedClock:
        @staticmethod
        def now(tz):
            return fixed

    monkeypatch.setattr(provenance, "datetime", FixedClock)
    with provenance.run("same", settings={}, runs_dir=tmp_path / "runs", repo=repo):
        pass
    with pytest.raises(FileExistsError):
        with provenance.run("same", settings={}, runs_dir=tmp_path / "runs", repo=repo):
            pass


def test_missing_input_file_is_an_error_and_leaves_no_run(tmp_path, repo):
    runs = tmp_path / "runs"
    with pytest.raises(ValueError, match="do not exist"):
        with provenance.run("x", settings={}, inputs=[tmp_path / "nope.csv"],
                            runs_dir=runs, repo=repo):
            pass
    assert list(runs.iterdir()) == []


def test_reserved_fields_and_bad_names_are_rejected(tmp_path, repo):
    with pytest.raises(ValueError, match="experiment name"):
        provenance.new_run_id("bad name", datetime.now(UTC))
    with provenance.run("ok", settings={}, runs_dir=tmp_path / "runs", repo=repo) as record:
        with pytest.raises(ValueError, match="status"):
            record.update(status="completed")


def test_to_jsonable_keeps_non_finite_values_and_rejects_unknown_types():
    assert provenance.to_jsonable([np.nan, np.inf, -np.inf, 1.5, "nan"]) == [
        {"float": "nan"}, {"float": "inf"}, {"float": "-inf"}, 1.5, "nan"]
    assert provenance.to_jsonable(np.float32(0.5)) == 0.5
    assert provenance.to_jsonable({"z": 1j}) == {"z": {"re": 0.0, "im": 1.0}}
    with pytest.raises(TypeError, match="set"):
        provenance.to_jsonable({1, 2})


def test_input_inside_the_repository_is_recorded_relative_to_it(tmp_path, repo):
    (repo / "data").mkdir()
    inside = repo / "data" / "table.csv"
    inside.write_bytes(b"x\n")
    with provenance.run("rel", settings={}, inputs=[inside], runs_dir=tmp_path / "runs",
                        repo=repo) as record:
        pass
    assert read(record)["inputs"][0]["path"] == "data/table.csv"
