import json
import os

SAVE_PATH = "saves/game0.json"

def setup_evolution_test():
    if not os.path.exists(SAVE_PATH):
        print(f"Error: Save file {SAVE_PATH} not found!")
        return

    with open(SAVE_PATH, "r") as f:
        data = json.load(f)

    monsters = data.get("bag", {}).get("monsters", [])
    
    # 1. Look for Capybara
    capy_idx = -1
    for i, m in enumerate(monsters):
        if m["name"] == "Capybara":
            capy_idx = i
            break
            
    if capy_idx != -1:
        print("Found existing Capybara. Modifying for evolution test...")
        # Set to low level but high XP
        # My implementation: Req Level 3. Threshold Lvl*100.
        # Set to Lvl 2 with 190 XP (Need 200). Win 1 battle (50xp) -> Level 3 -> Evolve.
        monsters[capy_idx]["level"] = 2
        monsters[capy_idx]["xp"] = 190
        monsters[capy_idx]["hp"] = monsters[capy_idx]["max_hp"] # Heal it
        print("Capybara is now Level 2 with 190/200 XP.")
    else:
        print("Capybara not found. Adding new test Capybara...")
        new_capy = {
            "name": "Capybara",
            "hp": 100,
            "max_hp": 100,
            "level": 2,
            "xp": 190
        }
        monsters.append(new_capy)
        print("Added new Capybara (Level 2, 190 XP).")

    # 2. Look for Charizard
    char_idx = -1
    for i, m in enumerate(monsters):
        if m["name"] == "Charizard":
            char_idx = i
            break
            
    if char_idx != -1:
        print("Found existing Charizard. Modifying for evolution test...")
        # Req Level 5.
        # Set to Lvl 4 with 390 XP (Need 400).
        monsters[char_idx]["level"] = 4
        monsters[char_idx]["xp"] = 390
        monsters[char_idx]["hp"] = monsters[char_idx]["max_hp"]
        print("Charizard is now Level 4 with 390/400 XP.")
    
    # Cleaning: Remove 'sprite_path' from all monsters if present
    print("Cleaning up sprite_path from save data...")
    for m in monsters:
        if "sprite_path" in m:
            del m["sprite_path"]

    # Save back
    data["bag"]["monsters"] = monsters
    
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"\nSuccess! Save file {SAVE_PATH} updated.")
    print("INSTRUCTIONS:")
    print("1. Start the game.")
    print("2. Enter a battle with Capybara or Charizard.")
    print("3. Win the battle.")
    print("4. Watch them level up and evolve!")

if __name__ == "__main__":
    setup_evolution_test()
