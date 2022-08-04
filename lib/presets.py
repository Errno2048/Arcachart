from .chart import TrackMetaInfo as _TrackMetaInfo

_default = _TrackMetaInfo(
    track_file='assets/default_track.png',
    enwiden_file='assets/default_extralane.png',
    note_file='assets/default_note.png',
    hold_file='assets/default_hold.png',
    arc_file='assets/default_arc.png',
)

_light = _TrackMetaInfo(
    track_file='assets/track.png',
    enwiden_file='assets/track_extralane_light.png',
    note_file='assets/note.png',
    hold_file='assets/note_hold.png',
    arc_file='assets/arc_body.png',
)
_light.bar_line_color = (127, 127, 127, 255)
_light.track_line_color = (127, 127, 127, 255)
_light.black_color = (175, 95, 223, 95)
_light.font_color = (0, 0, 0, 191)
_light.extra_color = (0, 0, 0, 0)

_dark = _TrackMetaInfo(
    track_file='assets/track_dark.png',
    enwiden_file='assets/track_extralane_dark.png',
    note_file='assets/note_dark.png',
    hold_file='assets/note_hold_dark.png',
    arc_file='assets/arc_body.png',
)
_dark.bar_line_color = (191, 191, 191, 255)
_dark.track_line_color = (191, 191, 191, 255)
_dark.black_color = (223, 127, 255, 95)
_dark.font_color = (255, 255, 255, 191)
_dark.extra_color = (0, 0, 0, 0)

_light_tomato = _light.clone()
_light_tomato.note_file = 'assets/note_tomato.png'
_light_tomato.hold_file = 'assets/note_hold_tomato.png'

_dark_tomato = _dark.clone()
_dark_tomato.note_file = 'assets/note_tomato.png'
_dark_tomato.hold_file = 'assets/note_hold_tomato.png'

_arcana = _dark.clone()
_arcana.track_file = 'assets/track_arcana.png'

_black = _dark.clone()
_black.track_file = 'assets/track_black.png'

_colorless = _light.clone()
_colorless.track_file = 'assets/track_colorless.png'

_dark_nijuusei = _dark.clone()
_dark_nijuusei.track_file = 'assets/track_dark_nijuusei.png'

_dark_vs = _dark.clone()
_dark_vs.track_file = 'assets/track_dark_vs.png'

_finale = _dark.clone()
_finale.track_file = 'assets/track_finale.png'

_pentiment = _dark.clone()
_pentiment.track_file = 'assets/track_pentiment.png'

_rei = _light.clone()
_rei.track_file = 'assets/track_rei.png'

_tempestissimo = _dark.clone()
_tempestissimo.track_file = 'assets/track_tempestissimo.png'

_presets = {
    'default': _default,
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

def get(name):
    track_meta_template = _presets.get(name, None)
    if track_meta_template:
        return track_meta_template.clone()
    return None
