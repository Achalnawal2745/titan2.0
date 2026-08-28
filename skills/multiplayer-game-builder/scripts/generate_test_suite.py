import os
import sys

def generate_test_suite(game_name):
    test_dir = "test"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    files_to_create = [
        "deck.test.js",
        "bidding.test.js",
        "trick.test.js",
        "scoring.test.js",
        "game.test.js",
        "socket.test.js"
    ]
    
    for file_name in files_to_create:
        file_path = os.path.join(test_dir, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"// Test suite for {file_name.replace(".test.js", "")}\n")
            print(f"✅ Created {file_path}")
        else:
            print(f"⚠️ {file_path} already exists, skipping.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        game_name = "my-game"
    else:
        game_name = sys.argv[1]
        
    print(f"🚀 Generating test suite for [1m{game_name}[0m...")
    generate_test_suite(game_name)
    print("✅ Test suite generated successfully!")
