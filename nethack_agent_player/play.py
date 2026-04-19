import sys
import os
import time

sys.path.insert(0, "/mnt/c/Users/ASUS/Desktop/ai_play_nethack/nethack_agent_player")
from scripts import create_env
from scripts.memory import Memory

character = sys.argv[1] if len(sys.argv) > 1 else None
env = create_env(character=character)
memory = Memory(os.path.join(os.path.dirname(__file__), "run_history.json"))

# bypass input() in reset
obs, _ = env.env.reset()
env._obs = obs
env.turn = 0
env.history = []
state = env.render(obs)

with open("/tmp/nethack_state", "w", encoding="utf-8") as f:
    f.write(state)

while True:
    if os.path.exists("/tmp/nethack_action"):
        with open("/tmp/nethack_action", "r", encoding="utf-8") as f:
            action = f.read().strip()
        os.remove("/tmp/nethack_action")
        state = env.step(action)
        with open("/tmp/nethack_state", "w", encoding="utf-8") as f:
            f.write(state)
        if "[GAME OVER]" in state:
            # save placeholder record — agent must update with real lessons after analysis
            memory.save({
                "turns": env.turn,
                "depth": 1,
                "cause": "unknown — agent should update after analysis",
                "lessons": [],
            })
            # signal agent to do post-game analysis
            with open("/tmp/nethack_gameover", "w", encoding="utf-8") as f:
                f.write(state)
            break
    time.sleep(0.1)
env.close()
