# nethack_agent_player

让 Agent 通过 NLE 接口玩 NetHack。

## 安装依赖

```bash
pip install gymnasium nle
```

## 用法

```python
import sys
sys.path.insert(0, '/path/to/nethack_agent_player')
from scripts import create_env

env = create_env(character='wizard')  # 或 None 随机角色
state = env.reset()

while True:
    action = your_llm_decide(state)  # LLM 读 state 决策
    state = env.step(action)
    if '[GAME OVER]' in state:
        break

env.close()
```

## state 格式

```
Turn 3 | Dlvl:1 | HP:14/14 | AC:10 | XP:1 | Gold:0
Message: You see a jackal.
[24行 ASCII 游戏画面]
Inventory (1): a) +1 quarterstaff
```

## 可用动作

```
north south east west
northeast southeast southwest northwest
wait search pickup eat drink open descend ascend
```

## 角色选项

`character` 格式：`role-race-gender-align`，如 `wizard-human-male-neutral`
或直接用职业名：`wizard` `knight` `valkyrie` `barbarian` 等

## 参考

- [NetHack Wiki](https://nethackwiki.com/wiki/Main_Page)
- [NLE GitHub](https://github.com/facebookresearch/nle)
- 符号参考：`references/nethack_wiki_mapping.md`
