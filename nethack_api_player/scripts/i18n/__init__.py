from scripts.i18n import zh, en

_LANGS = {'en': en.STRINGS, 'zh': zh.STRINGS}
_lang = 'en'

SUPPORTED_LANGS = list(_LANGS.keys())


def set_lang(lang):
    global _lang
    if lang in _LANGS:
        _lang = lang


def get_lang():
    return _lang


def lang_ask():
    """动态生成语言选择提示，自动包含所有已注册语言"""
    codes = '/'.join(SUPPORTED_LANGS)
    label = _LANGS[_lang].get('lang_ask', 'Language')
    return f"{label} ({codes}) [{_lang}]: "


def t(key, **kwargs):
    s = _LANGS.get(_lang, _LANGS['en']).get(key, key)
    return s.format(**kwargs) if kwargs else s


def add_lang(code, strings_module):
    """扩展新语言用"""
    _LANGS[code] = strings_module.STRINGS
    SUPPORTED_LANGS.append(code)
