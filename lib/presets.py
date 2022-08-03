from .chart import TrackMetaInfo as _TrackMetaInfo

_default = _TrackMetaInfo(
    track_file='assets/default_track.png',
    enwiden_file='assets/default_extralane.png',
    note_file='assets/default_note.png',
    hold_file='assets/default_hold.png',
    arc_file='assets/default_arc.png',
)
_default.bar_line_color = (127, 127, 127, 255)
_default.track_line_color = (127, 127, 127, 255)

_light = _TrackMetaInfo(
    track_file='assets/track.png',
    enwiden_file='assets/track_extralane_light.png',
    note_file='assets/note.png',
    hold_file='assets/note_hold.png',
    arc_file='assets/arc_body.png',
)
_light.bar_line_color = (127, 127, 127, 255)
_light.track_line_color = (127, 127, 127, 255)

_dark = _TrackMetaInfo(
    track_file='assets/track_dark.png',
    enwiden_file='assets/track_extralane_dark.png',
    note_file='assets/note_dark.png',
    hold_file='assets/note_hold_dark.png',
    arc_file='assets/arc_body_hi.png',
)
_dark.bar_line_color = (191, 191, 191, 255)
_light.track_line_color = (191, 191, 191, 255)

_presets = {
    'default': _default,
    'light': _light,
    'dark': _dark,
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
