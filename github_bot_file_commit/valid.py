import ast
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll


def is_python_file_valid(f):
    source = f.read()
    f.seek(0)
    try:
        ast.parse(source)
    except Exception:
        return False
    return True


def is_file_damaged(f, original_file):
    source = f.read().decode('cp1251')
    f.seek(0)
    with open(original_file, 'r') as orig:
        for i in orig.readlines():
            if ('class' in i or 'def' in i) and '#' not in i:
                if i.strip() not in source:
                    return True
    return False


def is_correct_vk_id_and_token(group_id, token):
    try:
        vk_session = VkApi(token=token)
        longpoll = VkBotLongPoll(vk_session, group_id)
    except Exception:
        return False
    return True
