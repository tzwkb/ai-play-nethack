import subprocess, time, os

subprocess.run(['tmux', 'kill-session', '-t', 'nethack'], capture_output=True)
time.sleep(1)
subprocess.run(['tmux', 'new-session', '-d', '-s', 'nethack'])
time.sleep(1)
cmd = 'cd /mnt/c/Users/ASUS/.kimi/skills/nethack_agent_player ; PYTHONDONTWRITEBYTECODE=1 python3 play.py val-hum-fem-neu'
subprocess.run(['tmux', 'send-keys', '-l', '-t', 'nethack', cmd])
subprocess.run(['tmux', 'send-keys', '-t', 'nethack', 'Enter'])
time.sleep(4)
print('done')
