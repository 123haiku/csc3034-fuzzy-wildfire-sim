"""Cross-checks the hand-written Mamdani engine against scikit-fuzzy."""

import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fuzzy_system.reference_engine import SCENARIOS, SKFUZZY_AVAILABLE, cross_check

pytestmark = pytest.mark.skipif(
    not SKFUZZY_AVAILABLE, reason="scikit-fuzzy is not installed; pip install -r requirements.txt"
)

TOLERANCE = 0.5


@pytest.mark.parametrize("scenario", [name for name, _ in SCENARIOS])
def test_engine_matches_scikit_fuzzy(scenario):
    """Every output of both engines agrees within TOLERANCE on every scenario."""
    row = next(r for r in cross_check() if r["scenario"] == scenario)
    assert row["fri_delta"] <= TOLERANCE, f"FRI {row['fri_ours']} vs ref {row['fri_ref']}"
    assert row["speed_delta"] <= TOLERANCE, f"speed {row['speed_ours']} vs ref {row['speed_ref']}"
    assert row["alert_delta"] <= TOLERANCE, f"alert {row['alert_ours']} vs ref {row['alert_ref']}"


def test_alert_consequent_matches_scikit_fuzzy_on_every_tier():
    """The third output must reproduce the reference across the whole 0-3 band."""
    rows = cross_check()
    bands = {round(r["alert_ref"]) for r in rows}
    assert len(bands) >= 3, f"scenarios never exercise enough alert tiers: {sorted(bands)}"
