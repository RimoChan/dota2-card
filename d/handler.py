import time
import base64
import functools
from pathlib import Path

import hrml
import jinja2
import requests


此处 = Path(__file__).absolute().parent

with open(此处/'模板.hrml', encoding='utf8') as f:
    模板 = jinja2.Template(hrml.masturbate(f.read()))


@functools.lru_cache(maxsize=128)
def get(u):
    resp = requests.get(f'https://api.opendota.com/api/{u}')
    resp.raise_for_status()
    return resp.json()


英雄 = {x['id']: x for x in get('heroes')}


@functools.lru_cache(maxsize=0)
def sget(s):
    resp = requests.get(s)
    resp.raise_for_status()
    return 'data:image/png;base64,'+base64.b64encode(resp.content).decode()

    
class 人:
    def __init__(self, player):
        self._player = player
        self._b = {}
        j = self._get('')
        self._基本信息 = {
            'personaname': j['profile']['personaname'],
            'avatar': j['profile']['avatarmedium'],
            'rank_tier': j['rank_tier']
        }

    def _get(self, x):
        u = f'players/{self._player}/{x}'
        if u not in self._b:
            self._b[u] = get(u)
        return self._b[u]

    def 比赛(self):
        q = self._get('wl')
        return f'{q["win"]+q["lose"]:,d}'

    def 胜负场次(self):
        q = self._get('wl')
        return f'{q["win"]:,d}/{q["lose"]:,d}'

    def 胜率(self):
        q = self._get('wl')
        return f'{q["win"]/(q["win"]+q["lose"]):.1%}'

    def 近期胜负场次(self):
        q = self._get('wl?limit=20')
        return f'{q["win"]} - {q["lose"]}'

    def 近期胜率(self):
        q = self._get('wl')
        return f'{q["win"]/(q["win"]+q["lose"]):.1%}'

    def 常用英雄(self):
        q = max(self._get('heroes'), key=lambda x: x['games'])
        return 英雄[int(q['hero_id'])]['localized_name']

    def 首场比赛(self):
        q = self._get('matches')
        print(q[0])
        t = min([x['start_time'] for x in q])
        return time.strftime("%Y-%m-%d", time.localtime(t))

    def 比赛时长(self):
        q = self._get('matches')
        h = sum([x['duration'] for x in q]) // 3600
        return f'{h}小时'


def 黄泉颤抖(id, 要):
    我 = 人(id)
    s = []
    for x in 要:
        assert x[0] != '_', '太怪了，不行！'
        s.append(getattr(我, x)())
    return 我._基本信息, s


def 召唤(id, 要):
    要组 = 要.split(',')
    信息, 组 = 黄泉颤抖(id, 要组)
    t = 信息['rank_tier']
    if t:
        a, b = t//10, t%10
        图 = sget(f'https://www.opendota.com/assets/images/dota2/rank_icons/rank_icon_{a}.png'), sget(f'https://www.opendota.com/assets/images/dota2/rank_icons/rank_star_{b}.png'), sget(信息['avatar'])
    else:
        图 = sget(f'https://www.opendota.com/assets/images/dota2/rank_icons/rank_icon_0.png'), '', sget(信息['avatar'])
    return 模板.render(
        personaname=信息['personaname'],
        组=zip(要组, 组),
        图=图,
    )


# print(黄泉颤抖(335153592, ['游戏时长']))
