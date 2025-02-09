# tests/test_monte_carlo.py
import pytest
from app import monte_carlo_simulation

def test_valid_simulation():
    """
    Run a simulation with valid input.
    The returned win probability should be a float between 0 and 1.
    """
    player_hand = ["Ac", "Kd"]
    community_cards = []  # Preflop scenario
    num_opponents = 1
    simulations = 500  # Use a reduced number for fast tests

    probability = monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations)
    assert isinstance(probability, float)
    assert 0.0 <= probability <= 1.0

def test_invalid_card_input():
    """
    Passing an invalid card should raise a ValueError.
    """
    player_hand = ["Ac", "ZZ"]  # "ZZ" is not valid
    community_cards = []
    num_opponents = 1
    simulations = 100

    with pytest.raises(ValueError):
        monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations)

def test_duplicate_cards_error():
    """
    Passing duplicate cards in the input should raise a ValueError.
    """
    # Both player cards are the same.
    player_hand = ["Ac", "Ac"]
    # Also use valid notation for the community cards.
    community_cards = ["Qs", "Jh", "Td"]
    num_opponents = 1
    simulations = 100

    with pytest.raises(ValueError):
        monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations)