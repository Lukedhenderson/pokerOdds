import random
import multiprocessing
import eval7
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def calculate_break_even_equity(pot_size, call_amount):
    """Calculate break-even equity as a percentage.
       (Call amount divided by pot size, times 100)"""
    if call_amount == 0:
        return 0  # Free call requires no equity.
    return (call_amount / pot_size) * 100

def make_ev_decision(win_probability, break_even_equity, threshold=6):
    """
    Provide a decision based on EV analysis.
    If win_probability is strictly greater than (break_even_equity + threshold), return positive EV.
    If win_probability is at least break_even_equity (but not higher than the threshold above),
    return marginal; otherwise, fold.
    """
    if win_probability > break_even_equity + threshold:
        return "Call or Raise (Positive EV)"
    elif win_probability >= break_even_equity:
        return "Marginal Call (Borderline EV)"
    else:
        return "Fold (Negative EV)"

def has_straight_draw(ranks):
    """
    Check if the provided ranks (from cards) contain an open-ended straight draw.
    This function works if the ranks are given as strings (e.g. "8", "T", "A")
    or as integers. It converts to numbers if needed.
    """
    # If all ranks are integers, use them directly.
    if all(isinstance(r, int) for r in ranks):
        numbers = sorted(set(ranks))
    else:
        # Normalize: convert all rank strings to uppercase.
        rank_map = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        numbers = sorted({rank_map[r.upper()] for r in ranks if r.upper() in rank_map})
    for start in range(2, 11):  # possible straights: 2-6, 3-7, ..., 10-A
        straight_set = set(range(start, start+5))
        count = sum(1 for n in numbers if n in straight_set)
        if count == 4:
            return True
    return False

# Add this mapping near the top of app.py (or inside the function)
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

def analyze_draws(player_hand, community_cards):
    """
    Analyze the hand for flush and straight draw possibilities.
    Converts eval7 raw ranks to conventional rank strings.
    Returns a dictionary with flags, outs, and draw probability.
    """
    all_cards = [eval7.Card(card) for card in player_hand + community_cards]
    suits = [card.suit for card in all_cards]
    raw_ranks = [card.rank for card in all_cards]
    
    # Convert raw ranks to conventional rank strings using the mapping.
    converted_ranks = [RANK_MAPPING.get(r, str(r)) for r in raw_ranks]
    
    # Determine if there is a flush draw (exactly 4 cards of one suit)
    flush_draw = any(suits.count(suit) == 4 for suit in set(suits))
    
    # Use the conventional ranks for straight draw detection.
    straight_draw = has_straight_draw(converted_ranks)
    
    outs = 0
    if flush_draw:
        outs += 9  # Typical flush draw outs.
    if straight_draw:
        outs += 8  # Typical open-ended straight draw outs.
    
    # Calculate draw probability based on community card stage.
    if len(community_cards) == 3:
        draw_probability = outs * 4
    elif len(community_cards) == 4:
        draw_probability = outs * 2
    else:
        draw_probability = 0
    draw_probability = min(draw_probability, 100)
    
    return {
        "flush_draw": flush_draw,
        "straight_draw": straight_draw,
        "outs": outs,
        "draw_probability": draw_probability
    }

def classify_hand_strength(win_probability):
    """Classify hand strength based on win probability."""
    if win_probability > 75:
        return "Strong Hand"
    elif win_probability > 50:
        return "Medium Hand"
    elif win_probability > 30:
        return "Weak Hand"
    else:
        return "Drawing Hand"

def simulate_single_run(args):
    """A single Monte Carlo simulation run."""
    player_hand, community_cards, num_opponents, remaining_deck = args

    num_missing_community = 5 - len(community_cards)
    sampled_cards = random.sample(remaining_deck, num_opponents * 2 + num_missing_community)
    opponent_hands = [sampled_cards[i:i+2] for i in range(0, num_opponents * 2, 2)]
    completed_community = community_cards + sampled_cards[num_opponents * 2:]

    player_score = eval7.evaluate([eval7.Card(card) for card in (player_hand + completed_community)])
    opponent_scores = [
        eval7.evaluate([eval7.Card(card) for card in (opp + completed_community)])
        for opp in opponent_hands
    ]

    return all(player_score >= opp_score for opp_score in opponent_scores)

def monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations=10000):
    """Estimate win probability using Monte Carlo simulation."""
    deck = [r + s for r in '23456789TJQKA' for s in 'cdhs']
    input_cards = player_hand + community_cards
    if len(set(input_cards)) != len(input_cards):
        raise ValueError("Duplicate cards detected in input.")
    known_cards = set(input_cards)
    remaining_deck = [card for card in deck if card not in known_cards]

    args = [
        (player_hand, community_cards, num_opponents, remaining_deck[:])
        for _ in range(simulations)
    ]
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        wins = sum(pool.map(simulate_single_run, args))
    return wins / simulations

@app.route('/api/poker_decision', methods=['POST'])
def poker_decision_api():
    """
    API endpoint that returns:
      - Win probability (from simulation)
      - Break-even equity (from pot odds)
      - EV-based decision suggestion
      - Draw analysis (outs and probability)
      - Hand strength classification
    """
    data = request.json
    player_hand = data.get("player_hand", [])
    community_cards = data.get("community_cards", [])
    num_opponents = data.get("num_opponents", 1)
    pot_size = data.get("pot_size", 100)
    call_amount = data.get("call_amount", 20)
    simulations = data.get("simulations", 10000)

    valid_deck = {r+s for r in '23456789TJQKA' for s in 'cdhs'}
    for card in player_hand + community_cards:
        if card not in valid_deck:
            return jsonify({"error": "Invalid card detected: " + card}), 400

    if len(player_hand) != 2:
        return jsonify({"error": "Player hand must have exactly 2 cards."}), 400
    if not (0 <= len(community_cards) <= 5):
        return jsonify({"error": "Community cards must be between 0 and 5."}), 400

    win_probability = monte_carlo_simulation(player_hand, community_cards, num_opponents, simulations) * 100
    break_even_equity = calculate_break_even_equity(pot_size, call_amount)
    ev_decision = make_ev_decision(win_probability, break_even_equity)
    draw_analysis = analyze_draws(player_hand, community_cards)
    hand_strength = classify_hand_strength(win_probability)

    return jsonify({
        "win_probability": win_probability,
        "break_even_equity": break_even_equity,
        "ev_decision": ev_decision,
        "draw_analysis": draw_analysis,
        "hand_strength": hand_strength
    })

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)