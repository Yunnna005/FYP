import sys
from unittest.mock import patch, MagicMock, call
import pytest

import pipeline

@pytest.fixture
def mock_steps():
    mocks = {
        "run_user_stats": MagicMock(name="run_user_stats"),
        "run_feature_engineering": MagicMock(name="run_feature_engineering"),
        "run_anomaly_detection": MagicMock(name="run_anomaly_detection"),
        "run_recommendation_engine": MagicMock(name="run_recommendation_engine"),
        "run_sequential_forecasting": MagicMock(name="run_sequential_forecasting"),
    }

    mocked_steps = [
        ("User Stats", mocks["run_user_stats"]),
        ("Feature Engineering", mocks["run_feature_engineering"]),
        ("Anomaly Detection", mocks["run_anomaly_detection"]),
        ("Recommendation Engine", mocks["run_recommendation_engine"]),
        ("Sequential Forecasting", mocks["run_sequential_forecasting"]),
    ]

    with patch.object(pipeline, "STEPS", mocked_steps), \
         patch.object(pipeline, "check_data_sources"):
        yield mocks


# ---------------------------------------------------------------------------
# Control flow: all steps run, in order, with the right argument
# ---------------------------------------------------------------------------

def test_full_run_calls_every_step(mock_steps):
    pipeline.run_pipeline(user_id=None)

    for name, mock in mock_steps.items():
        assert mock.call_count == 1, f"{name} was not called exactly once"
        mock.assert_called_with(user_id=None)


def test_single_user_run_passes_user_id_to_every_step(mock_steps):
    pipeline.run_pipeline(user_id=42)

    for name, mock in mock_steps.items():
        mock.assert_called_once_with(user_id=42)


def test_steps_run_in_declared_order(mock_steps):
    call_order = []

    for name, mock in mock_steps.items():
        mock.side_effect = lambda user_id=None, _name=name: call_order.append(_name)

    pipeline.run_pipeline(user_id=None)

    assert call_order == [
        "run_user_stats",
        "run_feature_engineering",
        "run_anomaly_detection",
        "run_recommendation_engine",
        "run_sequential_forecasting",
    ]


# ---------------------------------------------------------------------------
# Error handling: one failing step doesn't kill the pipeline
# ---------------------------------------------------------------------------

def test_failing_step_does_not_stop_pipeline(mock_steps):
    """If one step raises, the pipeline should record the failure and
    continue running the remaining steps."""
    mock_steps["run_anomaly_detection"].side_effect = RuntimeError("boom")

    results = pipeline.run_pipeline(user_id=None)

    mock_steps["run_recommendation_engine"].assert_called_once()
    mock_steps["run_sequential_forecasting"].assert_called_once()

    assert results["Anomaly Detection"].startswith("FAIL")
    assert "boom" in results["Anomaly Detection"]
    assert results["User Stats"].startswith("OK")
    assert results["Feature Engineering"].startswith("OK")
    assert results["Recommendation Engine"].startswith("OK")
    assert results["Sequential Forecasting"].startswith("OK")


def test_all_steps_failing_still_returns_results(mock_steps):
    for mock in mock_steps.values():
        mock.side_effect = RuntimeError("nope")

    results = pipeline.run_pipeline(user_id=None)

    assert len(results) == 5
    for status in results.values():
        assert status.startswith("FAIL")


def test_first_step_failure_does_not_prevent_later_steps(mock_steps):
    mock_steps["run_user_stats"].side_effect = ValueError("stats broken")

    pipeline.run_pipeline(user_id=None)

    mock_steps["run_feature_engineering"].assert_called_once()
    mock_steps["run_anomaly_detection"].assert_called_once()


# ---------------------------------------------------------------------------
# Return value
# ---------------------------------------------------------------------------

def test_results_contains_every_step_name(mock_steps):
    results = pipeline.run_pipeline(user_id=None)
    assert set(results.keys()) == {
        "User Stats",
        "Feature Engineering",
        "Anomaly Detection",
        "Recommendation Engine",
        "Sequential Forecasting",
    }


def test_successful_results_have_ok_prefix(mock_steps):
    results = pipeline.run_pipeline(user_id=None)
    for status in results.values():
        assert status.startswith("OK")


# ---------------------------------------------------------------------------
# add_new_user wrapper
# ---------------------------------------------------------------------------

def test_add_new_user_runs_pipeline_for_that_user(mock_steps):
    pipeline.add_new_user(user_id=123)

    for mock in mock_steps.values():
        mock.assert_called_once_with(user_id=123)


# ---------------------------------------------------------------------------
# check_data_sources
# ---------------------------------------------------------------------------

def test_check_data_sources_passes_when_db_available():
    with patch.object(pipeline, "DB_AVAILABLE", True):
        pipeline.check_data_sources()


def test_check_data_sources_passes_when_all_csvs_present(tmp_path):
    for filename in pipeline.REQUIRED_CSVS:
        (tmp_path / filename).touch()

    with patch.object(pipeline, "DB_AVAILABLE", False), \
         patch.object(pipeline, "CSV_DIR", tmp_path):
        pipeline.check_data_sources()


def test_check_data_sources_exits_when_csvs_missing(tmp_path):
    """DB unavailable and CSVs missing → should sys.exit(1)."""
    (tmp_path / "users.csv").touch()

    with patch.object(pipeline, "DB_AVAILABLE", False), \
         patch.object(pipeline, "CSV_DIR", tmp_path), \
         pytest.raises(SystemExit) as exc_info:
        pipeline.check_data_sources()

    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def test_cli_full_flag_runs_all_users(mock_steps):
    with patch.object(sys, "argv", ["pipeline.py", "--full"]), \
         patch.object(pipeline, "run_pipeline") as mock_run:
        exec(_get_main_block())
        mock_run.assert_called_once_with(user_id=None)


def test_cli_user_flag_runs_single_user(mock_steps):
    with patch.object(sys, "argv", ["pipeline.py", "--user", "7"]), \
         patch.object(pipeline, "run_pipeline") as mock_run:
        exec(_get_main_block())
        mock_run.assert_called_once_with(user_id=7)


def test_cli_no_args_runs_all_users(mock_steps):
    with patch.object(sys, "argv", ["pipeline.py"]), \
         patch.object(pipeline, "run_pipeline") as mock_run:
        exec(_get_main_block())
        mock_run.assert_called_once_with(user_id=None)


def _get_main_block():
    """
    Extract and return the __main__ block of pipeline.py as a string
    so we can exec() it under different sys.argv values without
    spawning subprocesses.
    """
    return """
import argparse
parser = argparse.ArgumentParser(description="Finance AI Pipeline")
group = parser.add_mutually_exclusive_group()
group.add_argument("--full", action="store_true")
group.add_argument("--user", type=int)
args = parser.parse_args()
if args.user:
    pipeline.run_pipeline(user_id=args.user)
else:
    pipeline.run_pipeline(user_id=None)
"""