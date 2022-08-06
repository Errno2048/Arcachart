from .chart import TrackMetaInfo as _TrackMetaInfo
import os as _os
import json as _json

_default = _TrackMetaInfo(
    track_file='default/default_track.png',
    enwiden_file='default/default_extralane.png',
    note_file='default/default_note.png',
    hold_file='default/default_hold.png',
    arc_file='default/default_arc.png',
    side=0,
)

_default_dark = _TrackMetaInfo(
    track_file='default/default_track_dark.png',
    enwiden_file='default/default_extralane_dark.png',
    note_file='default/default_note_dark.png',
    hold_file='default/default_hold_dark.png',
    arc_file='default/default_arc_dark.png',
    side=1,
)
_default_dark.bar_line_color = (191, 191, 191, 255)
_default_dark.track_line_color = (191, 191, 191, 255)
_default_dark.black_color = (223, 127, 255, 95)
_default_dark.font_color = (255, 255, 255, 191)
_default_dark.extra_color = (102, 101, 114, 255)

_light = _TrackMetaInfo(
    track_file='assets/img/track.png',
    enwiden_file='assets/img/track_extralane_light.png',
    note_file='assets/img/note.png',
    hold_file='assets/img/note_hold.png',
    arc_file='assets/models/tap_l.png',
    side=0,
)
_light.bar_line_color = (127, 127, 127, 255)
_light.track_line_color = (127, 127, 127, 255)
_light.black_color = (175, 95, 223, 95)
_light.font_color = (0, 0, 0, 191)
_light.extra_color = (252, 248, 248, 255)

_dark = _TrackMetaInfo(
    track_file='assets/img/track_dark.png',
    enwiden_file='assets/img/track_extralane_dark.png',
    note_file='assets/img/note_dark.png',
    hold_file='assets/img/note_hold_dark.png',
    arc_file='assets/models/tap_d.png',
    side=1,
)
_dark.bar_line_color = (191, 191, 191, 255)
_dark.track_line_color = (191, 191, 191, 255)
_dark.black_color = (223, 127, 255, 95)
_dark.font_color = (255, 255, 255, 191)
_default_dark.extra_color = (102, 101, 114, 255)

_light_tomato = _light.clone()
_light_tomato.note_file = 'assets/img/note_tomato.png'
_light_tomato.hold_file = 'assets/img/note_hold_tomato.png'
_light_tomato.arc_file = 'assets/models/tap_tomato.png'

_dark_tomato = _dark.clone()
_dark_tomato.note_file = 'assets/img/note_tomato.png'
_dark_tomato.hold_file = 'assets/img/note_hold_tomato.png'
_dark_tomato.arc_file = 'assets/models/tap_tomato.png'

_arcana = _dark.clone()
_arcana.track_file = 'assets/img/track_arcana.png'

_black = _dark.clone()
_black.track_file = 'assets/img/track_black.png'

_colorless = _light.clone()
_colorless.track_file = 'assets/img/track_colorless.png'

_dark_nijuusei = _dark.clone()
_dark_nijuusei.track_file = 'assets/img/track_dark_nijuusei.png'

_dark_vs = _dark.clone()
_dark_vs.track_file = 'assets/img/track_dark_vs.png'

_finale = _dark.clone()
_finale.track_file = 'assets/img/track_finale.png'

_pentiment = _dark.clone()
_pentiment.track_file = 'assets/img/track_pentiment.png'

_rei = _light.clone()
_rei.track_file = 'assets/img/track_rei.png'

_tempestissimo = _dark.clone()
_tempestissimo.track_file = 'assets/img/track_tempestissimo.png'

_presets = {
    'default': _default,
    'default_dark': _default_dark,
    'light': _light,
    'dark': _dark,
    'light_tomato': _light_tomato,
    'dark_tomato': _dark_tomato,
    'arcana': _arcana,
    'black': _black,
    'colorless': _colorless,
    'dark_nijuusei': _dark_nijuusei,
    'dark_vs': _dark_vs,
    'finale': _finale,
    'pentiment': _pentiment,
    'rei': _rei,
    'tempestissimo': _tempestissimo,
}

def register(name, track_meta : _TrackMetaInfo, overwrite=False):
    if overwrite:
        _presets[name] = track_meta
    else:
        _presets.setdefault(name, track_meta)

def get(name, default=None):
    track_meta_template = _presets.get(name, None)
    if track_meta_template:
        return track_meta_template.clone()
    if default is not None:
        track_meta_template = _presets.get(default, None)
        if track_meta_template:
            return track_meta_template.clone()
    return None

_bg_light = ['aegleseeker', 'arcahv', 'auxesia', 'chuni-worldvanquisher', 'felis', 'fractureray', 'gou', 'modelista', 'nirvluce', 'omegafour', 'pragmatism', 'pragmatism3', 'quon', 'ringedgenesis', 'shiawase', 'shiawase2', 'solitarydream', 'tanoc_red', ]
_bg_conflict = ['aterlbus', 'axiumcrisis', 'chuni-garakuta', 'chuni-ikazuchi', 'cyaegha', 'grievouslady', 'maimai-boss', 'saikyostronger', 'sheriruth', 'tiferet', 'wacca_boss', ]

_bg_no_inverse = {
    'alexandrite': 'black',
    'arcanaeden': 'arcana',
    'epilogue': 'colorless',
    'etherstrike': 'rei',
    'lethaeus': 'black',
    'mirai_awakened': 'black',
    'pentiment': 'pentiment',
    'saikyostronger': 'black',
    'tempestissimo': 'tempestissimo',
    'testify': 'colorless',
}
for _item in _bg_light:
    _bg_no_inverse[_item] = 'light'
for _item in _bg_conflict:
    _bg_no_inverse[_item] = 'dark'

_bg_to_preset = {
    'finale_conflict': 'finale',
    'mirai_conflict': 'black',
    'nijuusei-conflict-b': 'dark_nijuusei',
    'nijuusei2_conflict': 'dark_nijuusei',
    'vs_conflict': 'dark_nijuusei',
}

_inverse_bg_to_preset = {
    'finale_light': 'finale',
    'mirai_light': 'black',
    'nijuusei-light-b': 'dark_nijuusei',
    'nijuusei2_light': 'dark_nijuusei',
    'vs_light': 'dark_nijuusei',
}

_songlist_file = 'assets/songs/songlist'
_songdict = {}
_songdict_inverse = {}
_sides = {}
if _os.path.isfile(_songlist_file):
    _extra_ids = [
        {"id": "ignotusafterburn", "side": 1, "bg": "base_conflict"},
        {"id": "redandblueandgreen", "side": 1, "bg": "base_conflict"},
        {"id": "singularityvvvip", "side": 1, "bg": "nijuusei-conflict-b"},
        {"id": "overdead", "side": 1, "bg": "nijuusei-conflict-b"},
        {"id": "mismal", "side": 1, "bg": "vs_conflict"},
    ]
    with open(_songlist_file, 'r', encoding='utf8') as _f:
        _songlist = _json.load(_f)['songs']
    for _dic in _songlist + _extra_ids:
        _id = _dic['id']
        _side = _dic['side']
        _bg = _dic['bg']
        _no_inverse = _bg_no_inverse.get(_bg, None)
        _sides[_id] = _side
        if _no_inverse:
            _songdict[_id] = _no_inverse
            _songdict_inverse[_id] = _no_inverse
        else:
            _original = _bg_to_preset.get(_bg, None)
            if _original:
                _songdict[_id] = _original
            else:
                if _side == 1:
                    _songdict[_id] = 'dark'
                else:
                    _songdict[_id] = 'light'
            _inverse = _inverse_bg_to_preset.get(_bg, None)
            if _inverse:
                _songdict_inverse[_id] = _inverse
            else:
                if _side == 1:
                    _songdict_inverse[_id] = 'light'
                else:
                    _songdict_inverse[_id] = 'dark'

def from_id(id):
    preset = _songdict.get(id, 'default')
    side = _sides.get(id, 0)
    default = 'default_dark' if side == 1 else 'default'
    return get(preset, default=default)

def from_id_inverse(id):
    preset = _songdict_inverse.get(id, 'default')
    side = _sides.get(id, 0)
    default = 'default' if side == 1 else 'default_dark'
    return get(preset, default=default)

__all__ = list(filter(lambda x: x[0] != '_', globals()))
