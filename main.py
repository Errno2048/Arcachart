import os
import argparse
from lib.reader import read
from lib import presets

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, nargs='+', help='Input aff files.')
    parser.add_argument('--preset', type=str, default='default', help='The preset of track style. The default value is "default".')
    parser.add_argument('--speed', '-s', type=float, default=2000, help='Pixel per second. The default value is 2000.')
    parser.add_argument('--arc-group-tolerance', '-t', type=int, default=20,
                        help='Tolerance of span between arcs. '
                             'Arcs with a distance less than this value will be considered as in the same group. '
                             'The default value is 10.')
    parser.add_argument('--zoom', '-z', type=float, default=0.2, help='Zoom scale of the output image. The default value is 0.2.')
    parser.add_argument('--ignore-black-line', '-B', action='store_true', help='To ignore draw black lines.')
    parser.add_argument('--read-noinput', '-n', action='store_true', help='To draw noinputs.')
    parser.add_argument('--format', type=str, default='png', help='The format of output image file.')

    args = parser.parse_args()

    preset = presets.get(args.preset)
    if preset is None:
        preset = presets.get('default')

    preset.speed = args.speed
    preset.group_tolerance = args.arc_group_tolerance
    preset.zoom = args.zoom
    preset.draw_black_line = not args.ignore_black_line

    read_noinput = args.read_noinput

    format_ = args.format

    for file in args.file:
        with open(file, 'r') as f:
            chart_data = f.read()
        output_file = os.path.basename(file) + '.' + format_
        chart = read(chart_data, read_noinput=read_noinput)
        image = chart.image(preset)
        image.save(output_file, format=format_)
