import math
import pytest
from app import monte_carlo_simulation

def test_pocket_aces_equity():
    """
    Test that pocket aces (AA) win approximately 85% of the time heads-up preflop.
    """
    player_hand = ["Ac", "Ad"]  # Ace of clubs and Ace of diamonds
    community_cards = []       # Preflop scenario
    num_opponents = 1
    simulations = 20000        # Higher iterations for improved accuracy

    probability = monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations) * 100
    # Allow a tolerance of ±5 percentage points.
    assert math.isclose(probability, 85, abs_tol=5), f"Expected equity near 85%, got {probability}%"

def test_7_2_offsuit_equity():
    """
    Test that 7-2 offsuit wins approximately 37% of the time heads-up preflop,
    given that our simulation counts ties as wins.
    """
    player_hand = ["7c", "2d"]  # 7 of clubs and 2 of diamonds
    community_cards = []       # Preflop scenario
    num_opponents = 1
    simulations = 20000        # Higher iterations for improved accuracy

    probability = monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations) * 100
    # Allow a tolerance of ±5 percentage points.
    assert math.isclose(probability, 37, abs_tol=5), f"Expected equity near 37%, got {probability}%"