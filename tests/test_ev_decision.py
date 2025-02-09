import pytest
from app import make_ev_decision

def test_ev_positive_decision():
    # With break-even equity of 30% and win probability 50,
    # 50 > 30+6 (i.e. 36), so positive EV.
    assert make_ev_decision(50, 30) == "Call or Raise (Positive EV)"

def test_ev_marginal_decision():
    # With break-even equity 35 and win probability 40,
    # 40 is not greater than 35+6 (i.e. 41) but is >= 35, so marginal.
    assert make_ev_decision(40, 35) == "Marginal Call (Borderline EV)"

def test_ev_negative_decision():
    # With break-even equity 50 and win probability 20, decision is to fold.
    assert make_ev_decision(20, 50) == "Fold (Negative EV)"