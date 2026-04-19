import os
import sys
import json
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREFS_PATH = os.path.join(SCRIPT_DIR, '.nethack_prefs')

sys.path.insert(0, SCRIPT_DIR)
from scripts.i18n import t, set_lang, get_lang, SUPPORTED_LANGS, lang_ask

ROLES = [
    ('random', 'role_random'), ('archeologist', 'role_archeologist'),
    ('barbarian', 'role_barbarian'), ('caveman', 'role_caveman'),
    ('healer', 'role_healer'), ('knight', 'role_knight'),
    ('monk', 'role_monk'), ('priest', 'role_priest'),
    ('ranger', 'role_ranger'), ('rogue', 'role_rogue'),
    ('samurai', 'role_samurai'), ('tourist', 'role_tourist'),
    ('valkyrie', 'role_valkyrie'), ('wizard', 'role_wizard'),
]

RACES = [
    ('random', 'race_random'), ('human', 'race_human'),
    ('elf', 'race_elf'), ('dwarf', 'race_dwarf'),
    ('gnome', 'race_gnome'), ('orc', 'race_orc'),
]


def load_prefs():
    if os.path.exists(PREFS_PATH):
        with open(PREFS_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_prefs(prefs):
    with open(PREFS_PATH, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def ask_with_memory(prompt_key, pref_key, prefs):
    saved = prefs.get(pref_key, '')
    if saved:
        val = input(f"{t(prompt_key)} [{saved}]: ").strip()
        return val if val else saved
    return input(f"{t(prompt_key)}: ").strip()


def choose_from_menu(title_key, options):
    print(f"\n{t(title_key)}")
    for i, (val, label_key) in enumerate(options):
        suffix = f" ({val})" if val != 'random' else ''
        print(f"  {i:2d}) {t(label_key)}{suffix}")
    while True:
        raw = input(t('choose_number')).strip()
        if raw == '':
            return options[0][0]
        if raw.isdigit() and 0 <= int(raw) < len(options):
            return options[int(raw)][0]
        print(t('invalid_input'))


def check_wsl():
    try:
        result = subprocess.run(['wsl', '-l', '-v'], capture_output=True, timeout=10)
        output = result.stdout.decode('utf-16-le', errors='ignore')
        return 'Ubuntu' in output or 'ubuntu' in output.lower()
    except Exception:
        return False


def check_nle():
    try:
        result = subprocess.run(
            ['wsl', '-d', 'Ubuntu', '--', 'python3', '-c', 'import nle; print("ok")'],
            capture_output=True, text=True, timeout=15
        )
        return 'ok' in result.stdout
    except Exception:
        return False


def install_nle():
    print(t('nle_installing'))
    r = subprocess.run([
        'wsl', '-d', 'Ubuntu', '--', 'bash', '-c',
        'apt-get update -qq && apt-get install -y -qq python3 python3-pip cmake build-essential libncurses-dev bison flex && pip3 install nle gymnasium'
    ])
    return r.returncode == 0


def main():
    prefs = load_prefs()

    # 语言选择（最先，影响后续所有输出）
    saved_lang = prefs.get('lang', 'en')
    set_lang(saved_lang)
    raw = input(lang_ask()).strip().lower()
    lang = raw if raw in SUPPORTED_LANGS else saved_lang
    set_lang(lang)
    prefs['lang'] = lang
    save_prefs(prefs)

    print(f"\n{t('title')}\n")
    print(t('checking_env'))

    if not check_wsl():
        print(f"\n{t('wsl_missing')}")
        print(t('wsl_install_hint'))
        input(f"\n{t('press_enter_exit')}")
        sys.exit(1)
    print(t('wsl_ok'))

    if not check_nle():
        print(t('nle_missing'))
        ans = input(t('nle_install_ask')).strip().lower()
        if ans != 'y':
            input(t('press_enter_exit'))
            sys.exit(1)
        if not install_nle():
            print(t('nle_install_fail'))
            input(t('press_enter_exit'))
            sys.exit(1)
        print(t('nle_install_ok'))
    print(f"{t('nle_ok')}\n")

    print(t('api_config'))
    api_key = ask_with_memory('api_key', 'api_key', prefs)
    api_url = ask_with_memory('api_url', 'api_url', prefs)
    model   = ask_with_memory('model',   'model',   prefs)

    prefs.update({'api_key': api_key, 'api_url': api_url, 'model': model})
    save_prefs(prefs)

    role = choose_from_menu('choose_role', ROLES)
    race = choose_from_menu('choose_race', RACES)

    if role == 'random' and race == 'random':
        character = ''
    elif role == 'random':
        character = f'-{race}'
    elif race == 'random':
        character = role
    else:
        character = f'{role}-{race}'

    verbose = input(f"\n{t('verbose_ask')}").strip().lower() != 'n'

    print(f"\n{t('launching')}\n")

    win_path = (SCRIPT_DIR.replace('\\', '/')
                .replace('C:', '/mnt/c').replace('D:', '/mnt/d')
                .replace('E:', '/mnt/e').replace('F:', '/mnt/f'))

    cfg_path = os.path.join(SCRIPT_DIR, '.nethack_cfg')
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.write(f"NETHACK_API_KEY={api_key}\n")
        f.write(f"NETHACK_API_URL={api_url}\n")
        f.write(f"NETHACK_MODEL={model}\n")
        f.write(f"NETHACK_CHARACTER={character}\n")
        f.write(f"NETHACK_VERBOSE={'1' if verbose else '0'}\n")
        f.write(f"NETHACK_SCRIPT_DIR={win_path}\n")
        f.write(f"NETHACK_LANG={lang}\n")

    bash_cmd = f'pip3 install -q openai 2>/dev/null; cd {win_path} && python3 game.py'
    subprocess.run(['wsl', '-d', 'Ubuntu', '--', 'bash', '-c', bash_cmd])

    input(f"\n{t('game_over_exit')}")


if __name__ == '__main__':
    main()
