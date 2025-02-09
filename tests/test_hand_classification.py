import pytest
from app import classify_hand_strength

def test_strong_hand():
    # Win probability > 75 should be classified as a strong hand.
    assert classify_hand_strength(80) == "Strong Hand"

def test_medium_hand():
    # Win probability between 50 and 75 is medium.
    assert classify_hand_strength(60) == "Medium Hand"

def test_weak_hand():
    # Win probability between 30 and 50 is weak.
    assert classify_hand_strength(40) == "Weak Hand"

def test_drawing_hand():
    # Win probability 30 or lower is considered drawing.
    assert classify_hand_strength(20) == "Drawing Hand"