import os
import argparse
from lib.reader import read
from lib import presets

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('id', type=str, help='Official file ID. If official file with this ID is not found, Arcachart will consider the value as a path instead.')
    parser.add_argument('difficulty', type=int, default=None, nargs='?', help='Difficulty from 0 to 3. The default is the highest difficulty.')
    parser.add_argument('--preset', '-p', type=str, default=None, help='The preset of track style. The default value depends on song ID. Input "inverse" to get inversed preset depends on ID.')
    parser.add_argument('--speed', '-s', type=float, default=2000, help='Pixel per second (before zooming). The default value is 2000.')
    parser.add_argument('--height', '-H', type=float, default=24000, help='The height of output image (before zooming). The default value is 24000.')
    parser.add_argument('--extra-width', '-e', type=int, default=None,
                        help='Extra border width of output image (before zooming). '
                             'When not specified, the extra width is automatically calculated. '
                             'Input a value less than zero (e.g. -1) to consider black lines in the automatic calculation.')
    parser.add_argument('--arc-group-tolerance', '-t', type=int, default=20,
                        help='Tolerance of span between arcs. '
                             'Arcs with a distance less than this value will be considered as in the same group. '
                             'The default value is 10.')
    parser.add_argument('--zoom', '-z', type=float, default=0.2, help='Zoom scale of the output image. The default value is 0.2.')
    parser.add_argument('--ignore-black-line', '-B', action='store_true', help='To ignore draw black lines.')
    parser.add_argument('--read-noinput', '-n', action='store_true', help='To draw noinputs.')
    parser.add_argument('--format', type=str, default='png', help='The format of output image file.')

    args = parser.parse_args()

    read_noinput = args.read_noinput

    format_ = args.format

    file_id = args.id
    file_diff = args.difficulty
    if file_diff is None:
        diffs = (3, 2, 1, 0)
    else:
        diffs = (file_diff, )

    file = None
    final_diff = None
    preset_name = args.preset
    preset = None

    if not os.path.isabs(file_id):
        songs_dir = f'assets/songs/{file_id}'
        if os.path.isdir(songs_dir):
            for diff in diffs:
                _file = f'{songs_dir}/{diff}.aff'
                if os.path.isfile(_file):
                    file = _file
                    final_diff = diff
                    break
        if file is None:
            for diff in diffs:
                _file = f'dl/{file_id}_{diff}'
                if os.path.isfile(_file):
                    file = _file
                    final_diff = diff
                    break
        if file is not None:
            if preset_name is None:
                preset = presets.from_id(file_id)
            elif preset_name == 'inverse':
                preset = presets.from_id_inverse(file_id)
    if file is None:
        for diff in diffs:
            _file = f'{file_id}_{diff}'
            if os.path.isfile(_file):
                file = _file
                final_diff = diff
                break
    if file is None:
        if os.path.isfile(file_id):
            file = file_id
            final_diff = None
    assert file is not None, f'ID {file_id} with {"unspecified difficulty" if file_diff is None else "difficulty %d" % file_diff} is not found.'
    if final_diff is not None:
        output_file = f'{file_id}_{final_diff}.{format_}'
    else:
        output_file = f'{file_id}.{format_}'

    if preset is None:
        preset = presets.get(preset_name)
    if preset is None:
        preset = presets.get('default')

    preset.speed = args.speed
    preset.group_tolerance = args.arc_group_tolerance
    preset.zoom = args.zoom
    preset.draw_black_line = not args.ignore_black_line
    preset.height_limit = args.height

    with open(file, 'r', encoding='utf8') as f:
        chart_data = f.read()
    chart = read(chart_data, read_noinput=read_noinput)

    extra_width = args.extra_width
    if extra_width is None:
        extra_width = chart.max_extra_width(ignore_black=True)
    elif extra_width < 0:
        extra_width = chart.max_extra_width(ignore_black=False)
    preset.extra_width = extra_width

    image = chart.image(preset)
    image.save(output_file, format=format_)
