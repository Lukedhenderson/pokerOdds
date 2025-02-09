import pytest
from app import analyze_draws

def test_flush_draw_detection():
    # With two hearts in hand and Qh, Jh on board plus one other heart,
    # we expect a flush draw.
    result = analyze_draws(["Ah", "Kh"], ["Qh", "Jh", "2c"])
    assert result["flush_draw"] is True
    # In this case, we don't expect a straight draw.
    
def test_straight_draw_detection():
    # Player hand: 8c, 9d; Board: 7h, 6s, 2c.
    # The cards 6,7,8,9 are present (missing 5 or 10) so there is an open-ended straight draw.
    result = analyze_draws(["8c", "9d"], ["7h", "6s", "2c"])
    assert result["straight_draw"] is True

def test_no_draw_scenario():
    # With no near-straight and no flush draw.
    result = analyze_draws(["Ac", "Kd"], ["Qs", "Jh", "5d"])
    assert result["flush_draw"] is False
    assert result["straight_draw"] is False