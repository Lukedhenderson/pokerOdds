import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_api_valid_request(client):
    payload = {
        "player_hand": ["Ac", "Kd"],
        "community_cards": ["Qs", "Jh", "Td"],
        "num_opponents": 1,
        "pot_size": 200,
        "call_amount": 50,
        "simulations": 1000
    }
    response = client.post("/api/poker_decision", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "win_probability" in data
    probability = data["win_probability"]
    assert isinstance(probability, float)
    assert 0.0 <= probability <= 100.0

def test_api_invalid_player_hand(client):
    payload = {
        "player_hand": ["Ac"],  # Only one card provided.
        "community_cards": ["Qs", "Jh", "Td"],
        "num_opponents": 1,
        "pot_size": 200,
        "call_amount": 50,
        "simulations": 1000
    }
    response = client.post("/api/poker_decision", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_api_invalid_card_format(client):
    payload = {
        "player_hand": ["Ac", "ZZ"],  # "ZZ" is invalid.
        "community_cards": ["Qs", "Jh", "Td"],
        "num_opponents": 1,
        "pot_size": 200,
        "call_amount": 50,
        "simulations": 1000
    }
    response = client.post("/api/poker_decision", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data