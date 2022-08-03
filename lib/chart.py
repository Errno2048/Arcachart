import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from tqdm import tqdm

VISION_HEIGHT = 6
VISION_CAP = 5
# -0.2?
GROUND_HEIGHT = 0

LIGHT_HEIGHT = 10

def _zoomed(tup, zoom):
    return tuple(map(lambda x: round(x * zoom), tup))

class TrackMetaInfo:
    def __init__(self, track_file='assets/track.png', enwiden_file='assets/track_extralane_light.png', note_file='assets/note.png', hold_file='assets/note_hold.png', arc_file='assets/arc_body_hi.png'):
        self.track_file = track_file
        self.enwiden_file = enwiden_file
        self.bar_line_width = 2
        self.bar_line_color = (127, 127, 127, 255)
        self.track_line_color = (127, 127, 127, 255)
        self.__track_line_width = 2
        self.__zoom = 1.0
        self.note_file = note_file
        self.hold_file = hold_file
        self.arc_file = arc_file
        self.height_limit = 24000
        self.speed = 2000
        self.group_tolerance = 0
        self.draw_black_line = False

    def clone(self):
        res = self.__class__()
        res.track_file = self.track_file
        res.enwiden_file = self.enwiden_file
        res.note_file = self.note_file
        res.hold_file = self.hold_file
        res.arc_file = self.arc_file
        res.bar_line_width = self.bar_line_width
        res.bar_line_color = self.bar_line_color
        res.track_line_width = self.track_line_width
        res.track_line_color = self.track_line_color
        res.zoom = self.zoom
        res.height_limit = self.height_limit
        res.speed = self.speed
        res.group_tolerance = self.group_tolerance
        res.draw_black_line = self.draw_black_line
        return res

    @property
    def zoom(self):
        return self.__zoom

    @zoom.setter
    def zoom(self, value):
        self.__zoom = value
        self.__refresh_note()
        self.__refresh_hold()
        self.__refresh_arc()

    @property
    def track_line_width(self):
        return self.__track_line_width

    @track_line_width.setter
    def track_line_width(self, value):
        self.__track_line_width = value
        self.__refresh_note()
        self.__refresh_hold()
        self.__refresh_arc()

    @property
    def track_file(self):
        return self.__track_file

    @track_file.setter
    def track_file(self, value):
        self.__track_file = value
        self.__track_image: Image.Image = Image.open(value).transpose(Image.FLIP_TOP_BOTTOM)

    @property
    def enwiden_file(self):
        return self.__enwiden_file

    @enwiden_file.setter
    def enwiden_file(self, value):
        self.__enwiden_file = value
        self.__enwiden_image: Image.Image = Image.open(value).transpose(Image.FLIP_TOP_BOTTOM)

    @property
    def note_file(self):
        return self.__note_file

    @note_file.setter
    def note_file(self, value):
        self.__note_file = value
        self.__note_image: Image.Image = Image.open(value).transpose(Image.FLIP_TOP_BOTTOM)
        self.__refresh_note()

    def __refresh_note(self):
        w, h = self.__note_image.size
        target_w = 238 - self.__track_line_width
        ratio = target_w / w
        target_w = round(target_w * self.zoom)
        target_h = round(h * ratio * self.zoom)
        self.__stretched_note_image = self.__stretch(target_w, target_h, self.__note_image)

    @property
    def hold_file(self):
        return self.__hold_file

    @hold_file.setter
    def hold_file(self, value):
        self.__hold_file = value
        self.__hold_image: Image.Image = Image.open(value).transpose(Image.FLIP_TOP_BOTTOM)
        self.__refresh_hold()

    def __refresh_hold(self):
        w, h = self.__hold_image.size
        target_w = round((238 - self.__track_line_width) * self.zoom)
        h = round(h * self.zoom)
        self.__stretched_hold_image = self.__stretch(target_w, h, self.__hold_image)

    @property
    def arc_file(self):
        return self.__arc_file

    @arc_file.setter
    def arc_file(self, value):
        self.__arc_file = value
        self.__arc_image: Image.Image = Image.open(value).transpose(Image.FLIP_TOP_BOTTOM)
        self.__refresh_arc()

    def __refresh_arc(self):
        w, h = self.__arc_image.size
        target_w = 238 - self.__track_line_width
        ratio = target_w / w
        target_w = round(target_w * self.zoom)
        target_h = round(32 * ratio * self.zoom)
        self.__stretched_arc_image = self.__stretch(target_w, target_h, self.__arc_image)

    @property
    def track_image(self):
        return self.__track_image

    @property
    def enwiden_image(self):
        return self.__enwiden_image

    @property
    def note_image(self):
        return self.__note_image

    @property
    def hold_image(self):
        return self.__hold_image

    def __duplicate_height(self, height, image):
        height = max(height, 1)
        ori_width, ori_height = image.size
        clips = math.ceil(height / ori_height)
        new_image = Image.new('RGBA', (ori_width, height), color=(0, 0, 0, 0))
        for index in range(clips - 1):
            new_image.paste(image, (0, ori_height * index), mask=image)
        index = clips - 1
        rest_height = height - ori_height * index
        cropped = image.crop((0, 0, ori_width, rest_height))
        new_image.paste(cropped, (0, ori_height * index), mask=cropped)
        return new_image

    def __stretch_width(self, width, image : Image.Image):
        width = max(width, 1)
        if width == image.size[0]:
            return image
        return image.resize((width, image.size[1]), Image.LANCZOS)

    def __stretch_height(self, height, image : Image.Image):
        height = max(height, 1)
        if height == image.size[1]:
            return image
        return image.resize((image.size[0], height), Image.LANCZOS)

    def __stretch(self, width, height, image : Image.Image):
        width = max(width, 1)
        height = max(height, 1)
        if width == image.size[0] and height == image.size[1]:
            return image
        return image.resize((width, height), Image.LANCZOS)

    def track_to_image(self, height):
        res = self.__duplicate_height(height, self.__track_image)
        return self.__stretch(round(1024 * self.zoom), round(height * self.zoom), res)

    def enwiden_to_image(self, height):
        res = self.__stretch_height(height, self.__enwiden_image)
        return self.__stretch(round(238 * self.zoom), round(height * self.zoom), res)

    def note_to_image(self):
        return self.__stretched_note_image

    def hold_to_image(self, height):
        return self.__stretch_height(round(height * self.zoom), self.__stretched_hold_image)

    def arc_to_image(self, ratio):
        base = self.__stretched_arc_image
        w, h = base.size
        new_w, new_h = round(w * ratio ), round(h * ratio)
        return self.__stretch(new_w, new_h, base)

class Easing:
    STRAIGHT = 0
    SINE_IN = 1
    SINE_OUT = 2
    BOTH = 3
    def __init__(self, easing : str):
        self.__x = self.STRAIGHT
        self.__y = self.STRAIGHT
        if easing == 'b':
            self.__x = self.BOTH
        elif easing == 's':
            self.__x = self.STRAIGHT
        elif len(easing) >= 2:
            if easing[:2] == 'si':
                self.__x = self.SINE_IN
            elif easing[:2] == 'so':
                self.__x = self.SINE_OUT
            if len(easing) >= 4:
                if easing[2:4] == 'si':
                    self.__y = self.SINE_IN
                elif easing[2:4] == 'so':
                    self.__y = self.SINE_OUT

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @classmethod
    def position(cls, easing, x1, x2, time_ratio):
        if easing == cls.BOTH:
            x = (x1 - x2) / 2 * math.cos(math.pi * time_ratio) + (x1 + x2) / 2
        elif easing == cls.SINE_IN:
            x = (x2 - x1) * math.sin(math.pi * time_ratio / 2) + x1
        elif easing == cls.SINE_OUT:
            x = (x1 - x2) * math.cos(math.pi * time_ratio / 2) + x2
        else:
            x = (x2 - x1) * time_ratio + x1
        return x

    def __hash__(self):
        return (self.__y << 2) + self.__x

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__x == other.__x and self.__y == other.__y

def _pos_to_x(x : float):
    # The x span is from -1 to 2
    return 36 + (x + 1) * 1428 / 3

def _arc_pos_to_height_ratio(y : float):
    # The y span is from -0.2? to 1.61?
    vision_height = VISION_HEIGHT
    same_size_height = GROUND_HEIGHT
    if y > VISION_CAP:
        y = VISION_CAP

    y_distance = vision_height - y
    g_distance = vision_height - same_size_height
    return g_distance / y_distance

def _tap_pos_to_height_ratio(y : float):
    vision_height = VISION_HEIGHT
    same_size_height = GROUND_HEIGHT
    if y > VISION_CAP:
        y = VISION_CAP

    y_distance = vision_height - y
    g_distance = vision_height - same_size_height
    return g_distance / y_distance

def _pos_shadow(x, y):
    light = LIGHT_HEIGHT
    ground = GROUND_HEIGHT
    y_distance = light - y
    g_distance = light - ground
    ratio = g_distance / y_distance
    new_x = ratio * x
    return new_x

def _time_to_height(time, speed : float):
    return speed * time / 1000

def _height_to_time(height, speed : float):
    return height * 1000 / speed

class _Drawable:
    def draw(self, image : Image.Image, draw : ImageDraw.ImageDraw, track_meta : TrackMetaInfo, speed : float):
        return image

class GroundNote(_Drawable):
    def __init__(self, start, lane):
        self.start = start
        self.lane = lane

    def __lt__(self, other):
        return self.start < other.start

    def draw(self, image : Image.Image, draw : ImageDraw.ImageDraw, track_meta : TrackMetaInfo, speed : float):
        note_image = track_meta.note_to_image()
        dest_x = 36 + track_meta.track_line_width // 2 + 238 * self.lane
        # TODO: is - note_image.size[1] / 2 correct?
        dest_x = round(dest_x * track_meta.zoom)
        dest_y = round(_time_to_height(self.start, speed) * track_meta.zoom)# - note_image.size[1] / 2
        image.alpha_composite(note_image, dest=(dest_x, dest_y))
        return image

class Hold(_Drawable):
    def __init__(self, start, end, lane):
        self.start = start
        self.end = end
        self.lane = lane

    def __lt__(self, other):
        return self.start < other.start

    def draw(self, image : Image.Image, draw : ImageDraw.ImageDraw, track_meta : TrackMetaInfo, speed : float):
        hold_image = track_meta.hold_to_image(round(_time_to_height(self.end - self.start, speed)))
        dest_x = 36 + track_meta.track_line_width // 2 + 238 * self.lane
        dest_x = round(dest_x * track_meta.zoom)
        dest_y = round(_time_to_height(self.start, speed) * track_meta.zoom)
        image.alpha_composite(hold_image, dest=(dest_x, dest_y))
        return image

class Arc(_Drawable):
    def __init__(self, start, end, x_start, x_end, easing, y_start, y_end, color, hitsound, skyline, taps=None):
        self.start = start
        self.end = end
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        self.easing = Easing(easing)
        self.color = color
        self.hitsound = hitsound
        self.skyline = not (isinstance(skyline, str) and skyline.lower() == 'false' or not skyline)
        self.taps = []
        if taps is not None:
            for time in taps:
                self.taps.append(time)

    def arc_notes(self):
        res = []
        for time in self.taps:
            x, y = self.position(time)
            res.append((y, time, x))
        return res

    def position(self, time):
        t, t1, t2 = time, self.start, self.end
        x1, x2, y1, y2 = self.x_start, self.x_end, self.y_start, self.y_end
        time_ratio = (t - t1) / (t2 - t1)
        x, y = Easing.position(self.easing.x, x1, x2, time_ratio), Easing.position(self.easing.y, y1, y2, time_ratio)
        return x, y

    def __slope(self, time, x_start, x_end, easing):
        """
        d_x / d_time
        """
        time_span = self.end - self.start
        if time_span <= 0:
            if x_end > x_start:
                return float('inf')
            elif x_end < x_start:
                return -float('inf')
            else:
                return 0
        slope_base = (x_end - x_start) / time_span
        time_position = (time - self.start) / time_span
        if easing == Easing.BOTH:
            slope = slope_base * math.sin(math.pi * time_position)
        elif easing == Easing.SINE_IN:
            slope = slope_base * math.cos(math.pi / 2 * time_position)
        elif easing == Easing.SINE_OUT:
            slope = slope_base * math.sin(math.pi / 2 * time_position)
        else:
            slope = slope_base
        return slope

    def x_slope(self, time):
        return self.__slope(time, self.x_start, self.x_end, self.easing.x)

    @classmethod
    def x_real_slope(cls, speed, x_slope):
        return x_slope * 1428 / (3 * _time_to_height(1, speed))

    def height_slope(self, time):
        return self.__slope(time, self.y_start, self.y_end, self.easing.y)

    @classmethod
    def draw_arc_note(cls, x, y, time, image : Image.Image, draw : ImageDraw.ImageDraw, track_meta: TrackMetaInfo, speed):
        ratio = _tap_pos_to_height_ratio(y)
        arc_note = track_meta.arc_to_image(ratio)
        real_x = round(_pos_to_x(x) * track_meta.zoom - arc_note.size[0] / 2)
        # TODO: -1/2?
        real_y = round(_time_to_height(time, speed) * track_meta.zoom)
        image.alpha_composite(arc_note, dest=(real_x, real_y))
        return image

    def __lt__(self, other):
        if self.start < other.start:
            return True
        if other.start < self.start:
            return False
        return self.end < other.end

def group_arcs(arcs, tolerance=0):
    # To join arcs together.
    color_dict = {}
    for arc in arcs:
        arc : Arc
        if arc.skyline:
            color = -1
        else:
            color = arc.color
        start_dict, end_dict = color_dict.setdefault(color, ({}, {}))
        if tolerance > 0:
            time_start = round(arc.start / tolerance) * tolerance
            time_end = round(arc.end / tolerance) * tolerance
        else:
            time_start = arc.start
            time_end = arc.end
        start_point = (time_start, arc.x_start, arc.y_start)
        end_point = (time_end, arc.x_end, arc.y_end)

        prev_arcs : list = end_dict.setdefault(start_point, [])
        if prev_arcs:
            # Simply use the last previous arc
            prev_arc = prev_arcs.pop()
            prev_arc.append(arc)
            new_end = end_dict.setdefault(end_point, [])
            new_end.append(prev_arc)
            continue

        next_arcs : list = start_dict.setdefault(end_point, [])
        if next_arcs:
            next_arc = next_arcs.pop()
            next_arc.append(arc)
            new_start = start_dict.setdefault(start_point, [])
            new_start.append(next_arc)
            continue

        # New arc
        arcs = [arc]
        new_start = start_dict.setdefault(start_point, [])
        new_end = end_dict.setdefault(end_point, [])
        new_start.append(arcs)
        new_end.append(arcs)
    arc_groups = []
    for color, (start_dict, end_dict) in color_dict.items():
        for start_point, arc_lists in start_dict.items():
            for arc_list in arc_lists:
                new_group = ArcGroups(arc_list, color)
                arc_groups.append(new_group)
    return arc_groups

class ArcGroups(_Drawable):
    # Pixels of small lines
    DRAW_DIFFERENTIAL_LENGTH = 20
    BASE_ARC_WIDTH = 80
    BASE_LINE_WIDTH = 20

    def __init__(self, arcs=None, color=None):
        if arcs is None:
            arcs = []
        if color is None:
            color = -1
        self.arcs = sorted(arcs)
        self.color = color

    @classmethod
    def pos_from_angle(cls, x_angle, width=1.0, base=(0, 0), postprocess=None):
        # angle: dx / dt
        base_x, base_y = base
        delta_x = width * math.sin(x_angle)
        delta_y = width * math.cos(x_angle)
        x = base_x + delta_x
        y = base_y + delta_y
        if postprocess:
            x, y = postprocess(x), postprocess(y)
        return x, y

    @classmethod
    def arc_sequence(cls, arc : Arc, speed):
        assert arc.start < arc.end
        delta_dis = cls.DRAW_DIFFERENTIAL_LENGTH

        points = []
        if arc.easing.x == Easing.BOTH:
            time_start, time_end, time_half = arc.start, arc.end, (arc.start + arc.end) / 2
            y_start, y_end, y_half = _time_to_height(time_start, speed), _time_to_height(time_end, speed), _time_to_height(time_half, speed)

            y_current = y_start
            while y_current < y_half:
                time_current = _height_to_time(y_current, speed)
                points.append(time_current)
                current_slope = arc.x_real_slope(speed, arc.x_slope(time_current))
                assert not np.isinf(current_slope), 'The slope is inf or -inf'
                delta_y = delta_dis / math.sqrt(1 + current_slope * current_slope)
                y_current += delta_y
            rev_points = [time_end - (time_current - time_start) for time_current in points]
            points.append(time_half)
            points.extend(reversed(rev_points))
        else:
            time_start, time_end = arc.start, arc.end
            y_start, y_end = _time_to_height(time_start, speed), _time_to_height(time_end, speed)

            y_current = y_start
            while y_current < y_end:
                time_current = _height_to_time(y_current, speed)
                points.append(time_current)
                current_slope = arc.x_real_slope(speed, arc.x_slope(time_current))
                assert not np.isinf(current_slope), 'The slope is inf or -inf'
                delta_y = delta_dis / math.sqrt(1 + current_slope * current_slope)
                y_current += delta_y
            points.append(time_end)

        return points

    def arc_notes(self):
        res = []
        for arc in self.arcs:
            res.extend(arc.arc_notes())
        return res

    def draw(self, image : Image.Image, draw : ImageDraw.ImageDraw, track_meta : TrackMetaInfo, speed : float):
        # self.arcs has to be sorted
        diff_len = self.DRAW_DIFFERENTIAL_LENGTH
        if self.color >= 0:
            base_width = self.BASE_ARC_WIDTH
        else:
            base_width = self.BASE_LINE_WIDTH

        left_pos = []
        right_pos = []
        slopes = [self.arcs[i].x_slope(self.arcs[i].start) for i in range(1, len(self.arcs))]
        slopes.append(self.arcs[-1].x_slope(self.arcs[-1].end))
        prev_left = None
        prev_right = None
        for arc, next_slope in zip(self.arcs, slopes):
            arc : Arc
            next_angle = math.atan(Arc.x_real_slope(speed, next_slope))
            if arc.end <= arc.start:
                # vertical arc
                y_base = _time_to_height(arc.start, speed)
                sign_factor = 1 if arc.x_start < arc.x_end else -1
                current_angle = sign_factor * math.pi / 2

                x_start = _pos_to_x(arc.x_start)
                x_end = _pos_to_x(arc.x_end)
                if x_start < x_end:
                    x_pos = list(np.arange(x_start, x_end, diff_len))
                elif x_start > x_end:
                    x_pos = list(np.arange(x_start, x_end, -diff_len))
                else:
                    x_pos = None
                if not left_pos or not right_pos:
                    # left_pos and right_pos is empty
                    # TODO: to check if the sign_factor is correct or inversed
                    w_initial = base_width * _arc_pos_to_height_ratio(arc.y_start)
                    left_pos.append((x_start, y_base - sign_factor * w_initial // 2))
                    right_pos.append((x_start, y_base + sign_factor * w_initial // 2))
                if x_pos is not None:
                    # The last position pair
                    # left: (angle1 + angle2 + pi) / 2
                    # right: (angle1 + angle2 - pi) / 2
                    w_end = base_width * _arc_pos_to_height_ratio(arc.y_end)
                    a_left = (current_angle + next_angle + math.pi) / 2
                    a_right = (current_angle + next_angle - math.pi) / 2
                    left_end = self.pos_from_angle(a_left, w_end // 2, base=(x_end, y_base))
                    right_end = self.pos_from_angle(a_right, w_end // 2, base=(x_end, y_base))

                    y_for_x = (arc.y_end - arc.y_start) / (x_end - x_start)
                    for index in range(len(x_pos) - 1):
                        dx_start, dx_end = x_pos[index], x_pos[index + 1]
                        #dy_start = y_for_x * (dx_start - x_start)
                        dy_end = y_for_x * (dx_end - x_start)
                        #w_start = base_width * _arc_pos_to_height_ratio(dy_start)
                        w_end = base_width * _arc_pos_to_height_ratio(dy_end)

                        if sign_factor > 0:
                            # x_start < x_end, discard right pos at the end, discard left pos at the beginning
                            if prev_left is None or dx_end > prev_left[0]:
                                left_pos.append((dx_end, y_base - sign_factor * w_end // 2))
                            if dx_end < right_end[0]:
                                right_pos.append((dx_end, y_base + sign_factor * w_end // 2))
                        else:
                            # x_start > x_end, discard left pos at the end, discard right pos at the beginning
                            if prev_right is None or dx_end < prev_right[0]:
                                right_pos.append((dx_end, y_base + sign_factor * w_end // 2))
                            if dx_end > left_end[0]:
                                left_pos.append((dx_end, y_base - sign_factor * w_end // 2))

                        left_pos.append((dx_end, y_base - sign_factor * w_end // 2))
                        right_pos.append((dx_end, y_base + sign_factor * w_end // 2))
                    left_pos.append(left_end)
                    right_pos.append(right_end)
                    prev_left, prev_right = left_end, right_end
                else:
                    # x_start == x_end
                    current_angle = 0
                    w_end = base_width * _arc_pos_to_height_ratio(arc.y_end)
                    a_left = (current_angle + next_angle + math.pi) / 2
                    a_right = (current_angle + next_angle - math.pi) / 2
                    left_end = self.pos_from_angle(a_left, w_end // 2, base=(x_end, y_base))
                    right_end = self.pos_from_angle(a_right, w_end // 2, base=(x_end, y_base))
                    left_pos.append(left_end)
                    right_pos.append(right_end)
                    prev_left, prev_right = left_end, right_end
            else:
                # ordinary arc
                time_points = self.arc_sequence(arc, speed)
                if not left_pos or not right_pos:
                    _start_index = 0
                else:
                    _start_index = 1

                # The last point
                current_time = time_points[-1]
                real_slope = arc.x_real_slope(speed, arc.x_slope(current_time))
                current_x, current_y = arc.position(current_time)
                real_x = _pos_to_x(current_x)
                real_w = base_width * _arc_pos_to_height_ratio(current_y)
                real_y = _time_to_height(current_time, speed)
                current_angle = math.atan(real_slope)
                a_left = (current_angle + next_angle + math.pi) / 2
                a_right = (current_angle + next_angle - math.pi) / 2

                left_pos_end = self.pos_from_angle(a_left, real_w // 2, base=(real_x, real_y))
                right_pos_end = self.pos_from_angle(a_right, real_w // 2, base=(real_x, real_y))

                for current_time in time_points[_start_index:-1]:
                    real_slope = arc.x_real_slope(speed, arc.x_slope(current_time))
                    current_x, current_y = arc.position(current_time)
                    real_x = _pos_to_x(current_x)
                    real_w = base_width * _arc_pos_to_height_ratio(current_y)
                    real_y = _time_to_height(current_time, speed)
                    current_angle = math.atan(real_slope)

                    _left_pos = self.pos_from_angle(current_angle + math.pi / 2, real_w // 2, base=(real_x, real_y))
                    _right_pos = self.pos_from_angle(current_angle - math.pi / 2, real_w // 2, base=(real_x, real_y))
                    # ordinary arcs can simply compare time
                    if (prev_left is None or prev_left[1] < _left_pos[1]) and  _left_pos[1] < left_pos_end[1]:
                        left_pos.append(_left_pos)
                    if (prev_right is None or prev_right[1] < _right_pos[1]) and  _right_pos[1] < right_pos_end[1]:
                        right_pos.append(_right_pos)
                left_pos.append(left_pos_end)
                right_pos.append(right_pos_end)
                prev_left, prev_right = left_pos_end, right_pos_end
        pos = []
        pos.extend(left_pos)
        pos.extend(reversed(right_pos))

        if self.color == 0:
            # Blue
            fill_color = (63, 223, 255, 127)
        elif self.color == 1:
            # Red
            fill_color = (255, 63, 191, 127)
        elif self.color == 2:
            # Green
            fill_color = (63, 255, 63, 127)
        elif self.color >= 3:
            # Yellow
            fill_color = (223, 223, 63, 127)
        else:
            # line
            fill_color = (223, 31, 255, 95)
        real_pos = []
        for x, y in pos:
            real_pos.append((round(x * track_meta.zoom), round(y * track_meta.zoom)))
        draw.polygon(real_pos, fill=fill_color)
        return image

class Camera:
    def __init__(self, time, transverse, bottomzoom, linezoom, steadyangle, topzoom, angle, easing, lastingtime):
        self.start = time
        self.end = time + lastingtime
        self.transverse = transverse
        self.bottomzoom = bottomzoom
        self.linezoom = linezoom
        self.steadyangle = steadyangle
        self.topzoom = topzoom
        self.angle = angle
        self.easing = easing

class SceneControl:
    def __init__(self, time, type, *params):
        self.time = time
        self.type = type
        self.params = params

class Timing:
    def __init__(self, time, bpm, beats=4.00):
        self.time = time
        self.bpm = bpm
        self.beats = beats

    @property
    def bar_span(self):
        if self.bpm <= 0:
            return None
        return 60000 * self.beats / self.bpm

    def __lt__(self, other):
        return self.time < other.time

class TimingGroup(_Drawable):
    def __init__(self):
        self.notes = []
        self.holds = []
        self.arcs = []
        self.arc_groups = []
        self.timings = []
        self.total_time = 0

    def clone(self):
        res = self.__class__()
        res.notes = self.notes
        res.holds = self.holds
        res.arcs = self.arcs
        res.arc_groups = self.arc_groups
        res.timings = self.timings
        res.total_time = self.total_time
        return res

    def merge(self, other):
        other : TimingGroup
        self.notes.extend(other.notes)
        self.holds.extend(other.holds)
        self.arcs.extend(other.arcs)
        self.arc_groups.extend(other.arc_groups)
        self.timings.extend(other.timings)
        self.total_time = max(self.total_time, other.total_time)
        return self

    def refine(self, track_meta : TrackMetaInfo=None):
        self.notes.sort()
        self.holds.sort()
        self.arcs.sort()
        self.timings.sort()

        self.total_time = 0
        for note in self.notes:
            self.total_time = max(self.total_time, note.start)
        for hold in self.holds:
            self.total_time = max(self.total_time, hold.end)
        for arc in self.arcs:
            self.total_time = max(self.total_time, arc.end)
        for timing in self.timings:
            self.total_time = max(self.total_time, timing.time)

        if track_meta is not None:
            tolerance = track_meta.group_tolerance
        else:
            tolerance = 0
        self.arc_groups = group_arcs(self.arcs, tolerance)

    @classmethod
    def _bsearch_arcnotes(cls, arc_notes, time, left_bound=False):
        left, right = 0, len(arc_notes)
        if left_bound:
            while left < right:
                mid = (left + right) >> 1
                if arc_notes[mid][1] < time:
                    left = mid + 1
                else:
                    right = mid
            return left
        else:
            while left < right:
                mid = (left + right) >> 1
                if arc_notes[mid][1] <= time:
                    left = mid + 1
                else:
                    right = mid
            return left - 1

    def draw(self, image : Image.Image, draw : ImageDraw.ImageDraw, track_meta : TrackMetaInfo, speed : float):
        for hold in self.holds:
            hold.draw(image, draw, track_meta, speed)
        for note in self.notes:
            note.draw(image, draw, track_meta, speed)
        arc_notes = []
        for arc in self.arcs:
            arc_notes.extend(arc.arc_notes())
        arc_notes.sort(reverse=True)
        arc_note_label = [False for i in range(len(arc_notes))]

        for arc in self.arcs:
            if arc.color < 0:
                # Black lines are not taken into consideration
                continue
            start, end = arc.start, arc.end
            left_index = self._bsearch_arcnotes(arc_notes, start, left_bound=True)
            right_index = self._bsearch_arcnotes(arc_notes, end, left_bound=False)
            if left_index >= len(arc_notes) or right_index < 0:
                continue
            for index in range(left_index, right_index + 1):
                y, time, x = arc_notes[index]
                x_arc, y_arc = arc.position(time)
                if y_arc > y:
                    arc_note_label[index] = True

        for arc_note, is_overlapped in zip(arc_notes, arc_note_label):
            if is_overlapped:
                y, time, x = arc_note
                Arc.draw_arc_note(x, y, time, image, draw, track_meta, speed)

        line_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_image)
        color_images = {}
        for arc_group in self.arc_groups:
            arc_group : ArcGroups
            color = arc_group.color
            if color < 0:
                if track_meta.draw_black_line:
                    arc_group.draw(line_image, line_draw, track_meta, speed)
            else:
                color_image = color_images.get(color, None)
                if color_image is None:
                    color_image = Image.new('RGBA', image.size, (255, 255, 255, 0))
                    color_draw = ImageDraw.Draw(color_image)
                    color_images[color] = (color_image, color_draw)
                else:
                    color_image, color_draw = color_image
                arc_group.draw(color_image, color_draw, track_meta, speed)
        new_image = np.array(Image.new('RGBA', image.size, (255, 255, 255, 0)))
        for color_image, color_draw in color_images.values():
            np_image = np.array(color_image)
            color_channels = np_image[:, :, :3]
            alpha_channel = np_image[:, :, 3]
            new_image[:, :, :3] = np.min(np.stack([new_image[:, :, :3], color_channels], axis=0), axis=0)
            new_image[:, :, 3] = np.max(np.stack([new_image[:, :, 3], alpha_channel], axis=0), axis=0)
        new_image = Image.fromarray(new_image, mode='RGBA')
        if track_meta.draw_black_line:
            image.alpha_composite(line_image)
        image.alpha_composite(new_image)

        for arc_note, is_overlapped in zip(arc_notes, arc_note_label):
            if not is_overlapped:
                y, time, x = arc_note
                Arc.draw_arc_note(x, y, time, image, draw, track_meta, speed)

        return image

class EnwidenLanes:
    def __init__(self, time, duration, on=True):
        self.time = time
        self.duration = duration
        self.on = on

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.time == other.time and self.duration == other.duration and self.on == other.on

    def __hash__(self):
        return hash((self.time, self.duration, self.on))

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError()
        return self.time < other.time

class Chart:
    def __init__(self, meta=None):
        self.enwidenlaneses = []
        self.timing_groups = []
        self.total_time = 0
        self.total_draw_time = 0
        if meta is None:
            meta = {}
        self.meta = meta

    def refine(self):
        self.enwidenlaneses.sort()
        self.total_time = 0
        for timing_group in self.timing_groups:
            timing_group.refine()
            self.total_time = max(self.total_time, timing_group.total_time)
        self.total_draw_time = self.total_time
        if self.timing_groups:
            bar_span = None
            index = -1
            while bar_span is None:
                last_timing : Timing = self.timing_groups[0].timings[index]
                last_time = last_timing.time
                bar_span = last_timing.bar_span
                index -= 1
            assert bar_span is not None, 'BPM is zero'
            self.total_draw_time = last_time + math.ceil((self.total_draw_time - last_time) / bar_span) * bar_span

    def background(self, speed, track_meta : TrackMetaInfo):
        """
        speed: pixel height per second

        The slope of track line is 1.25.
        The size of track image is 1024 x 256.
        The size of inner tracks is 952. (238 per track)
        The width of border is 36.
        The size of extra lane image is 1 x 1000.
        Thus, the total width has to be 238 * 6 + 36 * 2 = 1500.
        """

        enwiden_spans = []
        enwiden_times = [0]
        prev_enwiden = None
        for enwiden in self.enwidenlaneses:
            enwiden : EnwidenLanes
            if enwiden.on:
                if prev_enwiden is not None:
                    continue
                prev_enwiden = enwiden.time
            else:
                if prev_enwiden is None:
                    continue
                # TODO: + enwiden.duration ?
                end_enwiden = enwiden.time + enwiden.duration
                enwiden_spans.append((prev_enwiden, end_enwiden))
                enwiden_times.append(prev_enwiden)
                enwiden_times.append(end_enwiden)
                prev_enwiden = None
        if prev_enwiden is not None:
            enwiden_spans.append((prev_enwiden, self.total_draw_time))
            enwiden_times.append(prev_enwiden)
        enwiden_times.append(self.total_draw_time)

        height_limit = track_meta.height_limit
        total_height = _time_to_height(self.total_draw_time, speed)
        total_height = math.ceil(total_height / height_limit) * height_limit

        track_base_image = track_meta.track_to_image(height=total_height)
        track_enwiden_image = track_meta.enwiden_to_image(height=total_height)

        bg_image = Image.new('RGBA', _zoomed((1500, total_height), track_meta.zoom), (0, 0, 0, 255))
        bg_image.paste(track_base_image, _zoomed((238, 0), track_meta.zoom), track_base_image)
        bg_image.paste(track_enwiden_image, _zoomed((0, 0), track_meta.zoom), track_enwiden_image)
        bg_image.paste(track_enwiden_image, _zoomed((1262, 0), track_meta.zoom), track_enwiden_image)

        bg_draw = ImageDraw.Draw(bg_image)
        bg_draw.line((_zoomed((512, 0), track_meta.zoom), _zoomed((512, total_height), track_meta.zoom)), track_meta.track_line_color, round(track_meta.track_line_width * track_meta.zoom))
        bg_draw.line((_zoomed((750, 0), track_meta.zoom), _zoomed((750, total_height), track_meta.zoom)), track_meta.track_line_color, round(track_meta.track_line_width * track_meta.zoom))
        bg_draw.line((_zoomed((988, 0), track_meta.zoom), _zoomed((988, total_height), track_meta.zoom)), track_meta.track_line_color, round(track_meta.track_line_width * track_meta.zoom))

        for enwiden_span in enwiden_spans:
            start, end = _time_to_height(enwiden_span[0], speed), _time_to_height(enwiden_span[1], speed)
            start, end = round(start), round(end)
            lane = track_enwiden_image.crop(_zoomed((0, start, 238, end), track_meta.zoom))
            # draw left lane
            left_border = track_base_image.crop(_zoomed((0, start, 36, end), track_meta.zoom))
            bg_image.paste(left_border, _zoomed((0, start), track_meta.zoom), left_border)
            bg_image.paste(lane, _zoomed((36, start), track_meta.zoom), lane)
            # draw right lane
            right_border = track_base_image.crop(_zoomed((988, start, 1024, end), track_meta.zoom))
            bg_image.paste(right_border, _zoomed((1464, start), track_meta.zoom), right_border)
            bg_image.paste(lane, _zoomed((1226, start), track_meta.zoom), lane)
            bg_draw.line((_zoomed((274, start), track_meta.zoom), _zoomed((274, end), track_meta.zoom)), track_meta.track_line_color, round(track_meta.track_line_width * track_meta.zoom))
            bg_draw.line((_zoomed((1226, start), track_meta.zoom), _zoomed((1226, end), track_meta.zoom)), track_meta.track_line_color, round(track_meta.track_line_width * track_meta.zoom))

        bars = []
        main_timing_group : TimingGroup = self.timing_groups[0]
        for index, timing in enumerate(main_timing_group.timings):
            start = timing.time
            if index < len(main_timing_group.timings) - 1:
                end = main_timing_group.timings[index + 1].time
            else:
                end = self.total_draw_time
            bar_span = timing.bar_span
            if bar_span is None:
                continue
            if index == 0:
                start = start + bar_span
            bars.extend(np.arange(start, end, bar_span))

        bar_index = 0
        bar_total = len(bars)
        for index in range(len(enwiden_times) - 1):
            start_time, end_time, is_enwiden = enwiden_times[index], enwiden_times[index + 1], index & 1
            while bar_index < bar_total:
                bar_time = bars[bar_index]
                #if start_time < bar_time and bar_time < end_time \
                #    or (bar_time == start_time or bar_time == end_time) and not is_enwiden:
                if bar_time < end_time or bar_time == end_time and not is_enwiden:
                    if is_enwiden:
                        x_start, x_end = 36, 1464
                    else:
                        x_start, x_end = 274, 1226
                    y = round(_time_to_height(bar_time, speed))
                    bg_draw.line((_zoomed((x_start, y), track_meta.zoom), _zoomed((x_end, y), track_meta.zoom)), track_meta.bar_line_color, round(track_meta.bar_line_width * track_meta.zoom))
                    bar_index += 1
                else:
                    break

        return bg_image

    def image(self, track_meta : TrackMetaInfo):
        self.refine()
        speed = track_meta.speed
        image = self.background(speed, track_meta)
        draw = ImageDraw.Draw(image)
        merged_timing_group = TimingGroup()
        for tg in self.timing_groups:
            merged_timing_group.merge(tg)
        merged_timing_group.refine(track_meta)
        merged_timing_group.draw(image, draw, track_meta, speed)

        height_limit = round(track_meta.height_limit * track_meta.zoom)
        w, h = image.size
        # Apply `round` instead of `ceil` to prevent float precision problem
        crops = round(h / height_limit)
        new_w = w * crops
        new_image = Image.new('RGBA', (new_w, height_limit), (0, 0, 0, 0))
        for index in range(crops):
            y_start = index * height_limit
            y_end = min(h, (index + 1) * height_limit)
            new_x_start = index * w
            new_image.paste(image.crop((0, y_start, w, y_end)), (new_x_start, 0))
        new_image = new_image.transpose(Image.FLIP_TOP_BOTTOM)
        return new_image
