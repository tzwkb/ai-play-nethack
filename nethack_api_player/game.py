import os
import sys
import re
import json


def load_cfg():
    search = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '.nethack_cfg'),
        '/tmp/.nethack_cfg',
    ]
    for path in search:
        if os.path.exists(path):
            cfg = {}
            with open(path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        cfg[k.strip()] = v.strip()
            return cfg
    return {}


cfg = load_cfg()
script_dir = cfg.get('NETHACK_SCRIPT_DIR') or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from scripts.env import create_env
from scripts.memory import Memory
from scripts.logger import GameLogger
from scripts.i18n import t, set_lang

set_lang(cfg.get('NETHACK_LANG', 'zh'))


def _load_knowledge(filename):
    """Load monsters.json or items.json and return compact text summary."""
    path = os.path.join(script_dir, filename)
    if not os.path.exists(path):
        return ''
    with open(path, encoding='utf-8') as f:
        db = json.load(f)
    lines = []
    for record in db.values():
        if filename == 'monsters.json':
            lines.append(f"- {record['name']} ({record['symbol']}): threat={record['threat']}. {record['notes']}")
        else:
            lines.append(f"- {record['name']} [{record['category']}]: {record['effect']} | {record['notes']}")
    return '\n'.join(lines)

SYSTEM_PROMPT = """You are playing NetHack. Each turn you receive: stats, message, map, inventory.
Reply with ONLY one action word: north south east west northeast southeast southwest northwest wait search eat descend ascend

## Map symbols
@ = you
> = DOWN stairs — stand on it and use "descend" to go deeper. THIS IS YOUR GOAL.
< = UP stairs — do NOT use ascend. < is NOT the exit, it goes the wrong way.
. = floor  # = corridor  + = closed door (walk into it to open)
| - = walls  $ = gold  % = food  f/d = pet
^ = trap (avoid)  _ = altar  { = fountain

## Decision priority each turn

STEP 1: Is > visible on the map? → Move toward it. When standing on it, use "descend".
STEP 2: Is # or + visible? → Move toward it. Corridors and doors lead to new rooms.
STEP 3: None of the above visible? → You are stuck in a room. Use "search" up to 3 times to find hidden doors. Then try moving in a direction you have NOT tried yet.

## Anti-loop rules (CRITICAL)

- If the [LOOP WARNING] tag appears in your input, you are going in circles. IMMEDIATELY pick a completely different direction or use "search".
- Never walk the same rectangular path twice. If you have visited all visible floor tiles, there MUST be a hidden door — use "search".
- Do NOT walk east then west then east then west. That wastes turns.
- If the last 3 actions were the same direction and the map did not change, STOP and try a perpendicular direction.

## Other rules

- READ THE MESSAGE every turn. "can't go" or "It's a wall" = blocked, pick another direction immediately.
- "You swap places with your little dog" = your pet is in the way, move a different direction.
- Never repeat a blocked action.

Reply with just the action word, nothing else."""

VALID_ACTIONS = {
    'north', 'south', 'east', 'west', 'northeast', 'southeast',
    'southwest', 'northwest', 'wait', 'search', 'eat', 'descend', 'ascend'
}

GOAL_INTERVAL = 20


def parse_action(text):
    for word in re.split(r'\W+', text.strip().lower()):
        if word in VALID_ACTIONS:
            return word
    return 'wait'


def analyze_death(client, model, final_state):
    # extract real cause from scoreboard line first
    raw_cause = 'unknown'
    m = re.search(r'(quit|killed by|died|starved|choked|poisoned|burned|drowned|crushed)[^\n]*', final_state, re.IGNORECASE)
    if m:
        raw_cause = m.group(0).strip()

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content':
                f"NetHack game over. Actual cause from scoreboard: \"{raw_cause}\"\n"
                f"Final state:\n{final_state}\n\n"
                "Reply in JSON only, no markdown:\n"
                '{"cause": "one sentence based on the actual cause above", "lessons": ["lesson1", "lesson2", "lesson3"]}'}],
            max_tokens=200,
            temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
        m2 = re.search(r'\{.*\}', text, re.DOTALL)
        if m2:
            return json.loads(m2.group())
    except Exception:
        pass
    return {'cause': raw_cause, 'lessons': []}


def update_goal(client, model, messages, current_goal):
    try:
        recent = messages[-10:] if len(messages) > 10 else messages
        resp = client.chat.completions.create(
            model=model,
            messages=recent + [{'role': 'user', 'content':
                'In one short sentence, what should be the immediate goal right now? '
                'Reply with just the goal sentence.'}],
            max_tokens=50,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return current_goal


def main():
    from openai import OpenAI

    api_key   = cfg.get('NETHACK_API_KEY') or os.environ.get('NETHACK_API_KEY', '')
    api_url   = cfg.get('NETHACK_API_URL') or os.environ.get('NETHACK_API_URL', '')
    model     = cfg.get('NETHACK_MODEL')   or os.environ.get('NETHACK_MODEL', '')
    character = cfg.get('NETHACK_CHARACTER') or None
    verbose   = cfg.get('NETHACK_VERBOSE', '1') == '1'

    if not api_key or not api_url or not model:
        print(t('cfg_missing'))
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=api_url)
    memory = Memory(path=os.path.join(script_dir, 'run_history.json'))
    past = memory.load()

    log_dir = os.path.join(script_dir, 'logs')
    logger = GameLogger(log_dir=log_dir, model=model, character=character)

    monsters_kb = _load_knowledge('monsters.json')
    items_kb = _load_knowledge('items.json')
    kb_section = ''
    if monsters_kb:
        kb_section += '\n\n## Known monsters\n' + monsters_kb
    if items_kb:
        kb_section += '\n\n## Known items\n' + items_kb

    system = SYSTEM_PROMPT + kb_section + ('\n\nPast lessons:\n' + past if past else '')
    messages = [{'role': 'system', 'content': system}]
    current_goal = None
    last_action = None
    last_message = None
    recent_positions = []  # track (x, y) to detect loops
    loop_counter = 0

    env = create_env(character=character or None, verbose=verbose)
    state = env.reset()

    print(t('game_start', model=model) + '\n')

    while True:
        # extract player position from state for loop detection
        pos_m = re.search(r'T:(\d+)', state)
        map_lines = state.split('\n')[1:23]
        player_pos = None
        for row_i, line in enumerate(map_lines):
            col_i = line.find('@')
            if col_i != -1:
                player_pos = (row_i, col_i)
                break
        if player_pos:
            recent_positions.append(player_pos)
            if len(recent_positions) > 20:
                recent_positions.pop(0)
            unique_pos = len(set(recent_positions))
            if len(recent_positions) >= 20 and unique_pos <= 6:
                loop_counter += 1
            else:
                loop_counter = max(0, loop_counter - 1)

        loop_warning = '[LOOP WARNING: you are going in circles. Use search or pick a completely new direction.]\n' if loop_counter >= 2 else ''

        # inject feedback and loop warning
        if last_action:
            feedback = f"[Last action: {last_action} | Result: {last_message or 'ok'}]\n"
            user_content = loop_warning + feedback + state
        else:
            user_content = state
        messages.append({'role': 'user', 'content': user_content})

        if env.turn > 0 and env.turn % GOAL_INTERVAL == 0:
            current_goal = update_goal(client, model, messages, current_goal)
            if current_goal:
                messages[0] = {'role': 'system', 'content':
                    system + f'\n\nCurrent goal: {current_goal}'}
                print(t('goal_update', goal=current_goal))

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=16,
            temperature=0.3,
        )
        api_raw = resp.choices[0].message.content
        action = parse_action(api_raw)
        messages.append({'role': 'assistant', 'content': action})
        logger.log_turn(env.turn, state, messages[:-1], api_raw, action)
        print(t('turn', turn=env.turn, action=action))

        last_action = action
        state = env.step(action)

        # extract message line from new state for next turn's feedback
        msg_m = re.search(r'消息[:：]\s*(.+)', state)
        if not msg_m:
            msg_m = re.search(r'Message[:：]\s*(.+)', state)
        last_message = msg_m.group(1).strip() if msg_m else None

        if '[GAME OVER]' in state:
            print(state)
            analysis = analyze_death(client, model, state)
            print(t('death_cause', cause=analysis['cause']))
            for lesson in analysis['lessons']:
                print(t('death_lesson', lesson=lesson))

            depth_m = re.search(r'Dlvl:(\d+)', state)
            final_depth = int(depth_m.group(1)) if depth_m else 1
            memory.save({
                'turns': env.turn,
                'depth': final_depth,
                'cause': analysis['cause'],
                'lessons': analysis['lessons'],
            })
            logger.log_result(
                cause=analysis['cause'],
                lessons=analysis['lessons'],
                total_turns=env.turn,
                final_depth=final_depth,
            )
            break

        if len(messages) > 60:
            messages = messages[:1] + messages[-40:]

    env.close()


if __name__ == '__main__':
    main()
