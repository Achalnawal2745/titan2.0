import json
import sys

def validate_game_state(state):
    errors = []
    
    # Basic structure
    if "players" not in state or not isinstance(state["players"], list) or len(state["players"]) != 4:
        errors.append("State must have a 'players' array with 4 elements")
    if "scores" not in state or not isinstance(state["scores"], dict):
        errors.append("State must have a 'scores' object")
    if "bidding" not in state or not isinstance(state["bidding"], dict):
        errors.append("State must have a 'bidding' object")
    if "tricks" not in state or not isinstance(state["tricks"], list):
        errors.append("State must have a 'tricks' array")
    if "currentTrick" not in state or not isinstance(state["currentTrick"], list):
        errors.append("State must have a 'currentTrick' array")
    
    # Player structure
    for i, player in enumerate(state.get("players", [])):
        if "hand" not in player or not isinstance(player["hand"], list):
            errors.append(f"Player {i} must have a 'hand' array")
        if "userId" not in player:
            errors.append(f"Player {i} must have a 'userId'")
            
    # Card counts
    total_cards = sum(len(p.get("hand", [])) for p in state.get("players", [])) + len(state.get("nest", [])) + len(state.get("currentTrick", []))
    if total_cards != 55:
        errors.append(f"Total cards in play should be 55, but found {total_cards}")
        
    return errors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_game_state.py <game_state.json>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        with open(file_path, "r") as f:
            game_state = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        sys.exit(1)
        
    print(f"🚀 Validating game state from 	{file_path}	...")
    validation_errors = validate_game_state(game_state)
    
    if validation_errors:
        print("❌ Validation failed with the following errors:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("✅ Game state is valid!")
