import pytest
from app import calculate_break_even_equity

def test_break_even_equity_normal():
    # For a $200 pot and $50 call, expected break-even equity = (50/200)*100 = 25%
    assert calculate_break_even_equity(200, 50) == 25.0

def test_break_even_equity_free_call():
    # If call is free, break-even equity should be 0.
    assert calculate_break_even_equity(200, 0) == 0