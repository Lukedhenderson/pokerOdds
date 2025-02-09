import sys
import os

# Ensure the project root is in the path so that we can import app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import analyze_draws, has_straight_draw, eval7

# Mapping from eval7 raw rank to conventional rank
RANK_MAPPING = {
    0: "2",
    1: "3",
    2: "4",
    3: "5",
    4: "6",
    5: "7",
    6: "8",
    7: "9",
    8: "T",
    9: "J",
    10: "Q",
    11: "K",
    12: "A"
}

def debug_analyze_draws(player_hand, community_cards):
    """
    A debug version of the analyze_draws function that prints intermediate values.
    This version converts eval7 raw ranks into conventional rank strings.
    """
    # Create card objects using eval7
    all_cards = [eval7.Card(card) for card in player_hand + community_cards]
    
    # Extract suits and raw ranks from each card.
    suits = [card.suit for card in all_cards]
    raw_ranks = [card.rank for card in all_cards]
    
    # Convert raw ranks to conventional rank strings.
    converted_ranks = [RANK_MAPPING.get(r, str(r)) for r in raw_ranks]
    
    print("----- Debug Info for Draw Analysis -----")
    print("Player Hand:", player_hand)
    print("Community Cards:", community_cards)
    print("Combined Cards:", [f"{converted_ranks[i]}{suits[i]}" for i in range(len(all_cards))])
    print("Raw Ranks:", raw_ranks)
    print("Converted Ranks:", converted_ranks)
    print("Suits:", suits)
    
    # Compute flush draw: check if exactly 4 cards of any suit exist.
    suit_counts = {suit: suits.count(suit) for suit in set(suits)}
    flush_draw = any(count == 4 for count in suit_counts.values())
    print("Suit Counts:", suit_counts)
    print("Flush Draw Detected:", flush_draw)
    
    # Compute straight draw using has_straight_draw on the conventional rank strings.
    straight_draw = has_straight_draw(converted_ranks)
    print("Straight Draw Detected:", straight_draw)
    
    # Calculate outs.
    outs = 0
    if flush_draw:
        outs += 9  # Typical flush draw outs.
    if straight_draw:
        outs += 8  # Typical open-ended straight draw outs.
    print("Calculated Outs:", outs)
    
    # Calculate draw probability based on the number of community cards.
    if len(community_cards) == 3:
        draw_probability = outs * 4
    elif len(community_cards) == 4:
        draw_probability = outs * 2
    else:
        draw_probability = 0
    draw_probability = min(draw_probability, 100)
    print("Calculated Draw Probability:", draw_probability)
    print("----- End Debug Info -----\n")
    
    return {
        "flush_draw": flush_draw,
        "straight_draw": straight_draw,
        "outs": outs,
        "draw_probability": draw_probability
    }

def test_debug_straight_draw():
    """
    Test input for a straight draw.
    Expected: For player hand ["8c", "9d"] and community cards ["7h", "6s", "2c"],
    after converting raw ranks, we expect the ranks to be ["8", "9", "7", "6", "2"].
    This should detect a straight draw (with 7,8,9,? - though note the gap for a 5 or 10).
    For our example, with these cards, we expect:
      - Straight draw: True (if the logic considers 6,7,8,9 as consecutive)
      - Outs: 8
      - Draw Probability: 32 (if 8 * 4)
    """
    player_hand = ["8c", "9d"]
    community_cards = ["7h", "6s", "2c"]
    result = debug_analyze_draws(player_hand, community_cards)
    # Assert that the straight draw flag is True.
    assert result["straight_draw"] is True, "Expected straight draw not detected!"

if __name__ == '__main__':
    test_debug_straight_draw()