import re
from . import chart as _chart

_Re_timing_group = re.compile(r'^\s*timinggroup\(([^)]*)\){')
_Re_timing_group_end = re.compile(r'^\s*}')
_Re_action = re.compile(r'^\s*([A-Za-z0-9#]*)\(([^)]*)\)((?:\[[^\]]*\])?);\s*$')

_Arg_note = (int, int)
_Arg_hold = (int, int, int)
_Arg_arc = (int, int, float, float, str, float, float, int, str, str)
_Arg_timing = (int, float, float)
_Arg_scenecontrol = (int, str, str, str)

def _analyze_args(args, pattern):
    args = args.split(',')
    if len(pattern) < len(args):
        pattern = (*pattern, *(str for i in range(len(args) - len(pattern))))
    res = []
    for arg, func in zip(args, pattern):
        res.append(func(arg))
    return res

def _read_meta(seq):
    meta = {}
    while seq:
        line = seq.pop()
        if line.startswith('-'):
            return meta
        pos = line.find(':')
        if pos >= 0:
            meta_name = line[:pos]
            meta_info = line[pos + 1:]
            meta[meta_name] = meta_info
    return meta

def _read_extra_args(extra_args : str):
    if len(extra_args) < 2:
        return []
    extra_args = extra_args[1:-1].split(',')
    res = []
    for extra_arg in extra_args:
        extra_arg = extra_arg.strip()
        if extra_arg.startswith('arctap('):
            res.append(int(extra_arg[7:-1]))
    return res

def _read_scene_control(args, chart : _chart.Chart, timing_group : _chart.TimingGroup):
    time, name, *params = _analyze_args(args, _Arg_scenecontrol)
    name = name.strip()
    if name == 'enwidenlanes':
        enwiden = _chart.EnwidenLanes(time, float(params[0]), params[1] != '0')
        chart.enwidenlaneses.append(enwiden)
    else:
        # others
        pass

def _read_action(line, chart : _chart.Chart, timing_group : _chart.TimingGroup):
    m = re.search(_Re_action, line)
    if m is None:
        print(f'Warning: unidentified line "{line}"')
    action_name, args, extra_args = m.groups()
    try:
        if action_name == '':
            # note
            action = _chart.GroundNote(*_analyze_args(args, _Arg_note))
            timing_group.notes.append(action)
        elif action_name == 'hold':
            action = _chart.Hold(*_analyze_args(args, _Arg_hold))
            timing_group.holds.append(action)
        elif action_name == 'arc':
            taps = _read_extra_args(extra_args)
            arc = _chart.Arc(*_analyze_args(args, _Arg_arc), taps=taps)
            timing_group.arcs.append(arc)
        elif action_name == 'timing':
            action = _chart.Timing(*_analyze_args(args, _Arg_timing))
            timing_group.timings.append(action)
        elif action_name == 'scenecontrol':
            _read_scene_control(args, chart, timing_group)
        else:
            # others
            pass
    except Exception as e:
        print(f'Warning: unidentified line "{line}" with exception: {e}')
        raise

def _read_timing_group_args(timing_group, args):
    args = args.split('_')
    res = {}
    for arg in args:
        if arg == 'noinput':
            res['noinput'] = True
        elif arg == 'fadingholds':
            res['fadingholds'] = True
        elif arg.startswith('anglex'):
            res['anglex'] = arg[6:]
        elif arg.startswith('angley'):
            res['angley'] = arg[6:]
        else:
            # others
            res[arg] = res.setdefault(arg, 0) + 1
    return res

def _read_timing_group(chart, lines, args=None, depth=0, read_noinput=True):
    timing_group = _chart.TimingGroup()
    res = _read_timing_group_args(timing_group, args)
    if not read_noinput and res.get('noinput', False):
        return None
    chart.timing_groups.append(timing_group)
    while lines:
        line = lines.pop()
        if (m := re.search(_Re_timing_group, line)):
            tg_args = m.group(1)
            tg = _read_timing_group(chart, lines, tg_args, depth + 1, read_noinput=read_noinput)
        elif re.search(_Re_timing_group_end, line):
            break
        else:
            _read_action(line, chart, timing_group)
    return timing_group

def read(chart : str, read_noinput=True):
    lines = list(reversed(chart.splitlines(False)))
    meta = _read_meta(lines)
    chart = _chart.Chart(meta=meta)
    _read_timing_group(chart, lines, read_noinput=read_noinput)
    return chart
