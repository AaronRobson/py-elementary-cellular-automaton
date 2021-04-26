import argparse
from functools import lru_cache

# http://en.wikipedia.org/wiki/Elementary_cellular_automaton

_DEFAULT_GENERATIONS = 6


def bool_sequence_to_base2_str(bool_collection):
    return ''.join((str(int(bool(item))) for item in bool_collection))


def bool_sequence_to_int(bool_collection):
    return int(bool_sequence_to_base2_str(bool_collection), 2)


def width_at_given_generation(generation):
    '''Holds only for pyramid based rules like rule 30.'''
    generation = int(generation)

    if generation < 0:
        raise ValueError('A negative generation is not allowed.')

    return generation*2 + 1


_CHOICES = [False, True]
_NUMBER_OF_CHOICES = len(_CHOICES)

_NEIGHBOURHOOD_SCOPE = 1
_NEIGHBOURHOOD_SIZE = _NEIGHBOURHOOD_SCOPE*2 + 1
_NUM_NEIGHBOURHOOD_CONFIGURATIONS = _NUMBER_OF_CHOICES**_NEIGHBOURHOOD_SIZE
_NEIGHBOURHOOD_CONFIGURATION_INDEXES = tuple(
    range(_NUM_NEIGHBOURHOOD_CONFIGURATIONS-1, 0-1, -1))


def index_to_num(index):
    return _NUMBER_OF_CHOICES**index


def int_to_neighbours(int_neighbours):
    assert int_neighbours in _NEIGHBOURHOOD_CONFIGURATION_INDEXES
    # bin assumes two choices
    return (bool(int(b)) for b in bin(int_neighbours)[2:])


def neighbours_to_int(neighbours):
    neighbours = tuple(neighbours)
    assert len(neighbours) <= _NEIGHBOURHOOD_SIZE
    return bool_sequence_to_int(neighbours)


NEIGHBOURHOOD_CONFIGURATIONS = tuple(
    map(index_to_num, _NEIGHBOURHOOD_CONFIGURATION_INDEXES))

NEIGHBOURHOODS = tuple(
    map(int_to_neighbours, _NEIGHBOURHOOD_CONFIGURATION_INDEXES))

NUM_OF_WOLFRAM_CODES = _NUMBER_OF_CHOICES**_NUM_NEIGHBOURHOOD_CONFIGURATIONS
LOW_WOLFRAM_CODE = 0
HIGH_WOLFRAM_CODE = NUM_OF_WOLFRAM_CODES - 1

WOLFRAM_CODES = tuple(
    range(LOW_WOLFRAM_CODE, NUM_OF_WOLFRAM_CODES))


def is_wolfram_code_valid(num_rule):
    '''http://en.wikipedia.org/wiki/Wolfram_code
    '''
    return num_rule in WOLFRAM_CODES


def ensure_wolfram_code_is_valid(wolfram_code):
    if not is_wolfram_code_valid(wolfram_code):
        raise ValueError(f'Wolfram code {wolfram_code} is invalid, '
                         'use values between '
                         f'{LOW_WOLFRAM_CODE} and {HIGH_WOLFRAM_CODE}')


_DEFAULT_RULE = 30

_symbolchar = {
    True: '#',
    False: ' ',
}

for value in _symbolchar.values():
    assert len(value) == 1


def symbol_to_char(symbol):
    try:
        return _symbolchar[symbol]
    except KeyError:
        raise ValueError('%r is not a valid symbol value.' % symbol)


def symbols_to_chars(symbols):
    return map(symbol_to_char, symbols)


def symbols_to_string(symbols):
    return ''.join(symbols_to_chars(symbols))


def to_svg(data, side=10, foreground='#000000', background='#ffffff'):
    side = int(side)
    if side <= 0:
        raise ValueError('Only strictly positive whole numbers shall '
                         'be accepted as side lengths.')

    data = list(map(list, data))
    item_count = len(data[0])
    line_count = len(data)
    width = item_count * side
    height = line_count * side

    yield '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
    yield '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" ' \
        '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
    yield '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" ' \
        f'width="{width}px" height="{height}px">'
    yield f'\t<rect width="{width}" height="{height}" fill="{background}" />'
    yield ''
    yield f'\t<g fill="{foreground}">'

    def rect(width, height):
        def shape(x, y):
            x_scaled = x*width
            y_scaled = y*height
            return f'\t\t<rect x="{x_scaled}" y="{y_scaled}" ' + \
                f'width="{width}" height="{height}" />'
        return shape

    def square(dimension):
        return rect(dimension, dimension)

    draw = square(side)

    for y, y_item in enumerate(data):
        yield f'\t\t<!-- Line: {y} -->'

        for x, x_item in enumerate(y_item):
            if x_item:
                yield draw(x, y)

        yield ''

    yield '\t</g>'

    yield '</svg>'
    yield ''


def _validate_rule_code(rule):
    # TODO: rewrite with ensureWolframCodeIsValid
    value = int(rule)
    min = 0
    max = 0xff
    if not (min <= value <= max):
        raise argparse.ArgumentTypeError(
            f'Rule {value} must be between {min} and {max} inclusive.')
    return value


def a_single_cell(x):
    return x == 0


@lru_cache(maxsize=None)
def find_cell_value(x, y, rule, starting_line=None):
    ensure_wolfram_code_is_valid(rule)

    if starting_line is None:
        starting_line = a_single_cell

    if y < 0:
        return False

    if y == 0:
        return starting_line(x)

    neighbour_values = (
        find_cell_value(
            x=x-1, y=y-1,
            rule=rule, starting_line=starting_line),
        find_cell_value(
            x=x+0, y=y-1,
            rule=rule, starting_line=starting_line),
        find_cell_value(
            x=x+1, y=y-1,
            rule=rule, starting_line=starting_line),
    )

    neighbour_index = neighbours_to_int(neighbour_values)
    assert neighbour_index in _NEIGHBOURHOOD_CONFIGURATION_INDEXES

    return bool(index_to_num(neighbour_index) & rule)


def find_x_coordinates(width):
    if width < 0:
        raise ValueError('width must be positive')

    offset = width // 2
    remainder = width % 2
    lower_inclusive_bound = -offset + 1 - remainder
    upper_exclusive_bound = lower_inclusive_bound + width
    return range(lower_inclusive_bound, upper_exclusive_bound)


def find_y_coordinates(height):
    if height < 0:
        raise ValueError('height must be positive')
    return range(height)


def find_coordinates(width=None, height=_DEFAULT_GENERATIONS):
    if width is None:
        width = width_at_given_generation(generation=height)

    x_values = list(find_x_coordinates(width=width))
    y_values = find_y_coordinates(height=height)

    for y in y_values:
        yield ((x, y) for x in x_values)


def calc_grid(width, height, rule=_DEFAULT_RULE, starting_line=None):
    grid_lines = find_coordinates(width=width, height=height)
    for grid_line in grid_lines:
        yield (find_cell_value(x=cell[0], y=cell[1],
                               rule=rule, starting_line=starting_line)
               for cell in grid_line)


def grid_to_text(grid):
    return '\n'.join(map(symbols_to_string, grid))


def _make_parser():
    parser = argparse.ArgumentParser(
        description='Generate Wolfram elementary cellular automaton patterns.'
    )
    parser.add_argument(
        '-g', '--generations',
        '-e', '--height',
        type=int,
        default=_DEFAULT_GENERATIONS,
        help='Number of generations to run (i.e. the height) '
        f'(default: {_DEFAULT_GENERATIONS}).')
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=None,
        help='Width of the view '
        '(default: dependent on the generations/height).')
    parser.add_argument(
        '-r', '--rule',
        type=_validate_rule_code,
        default=_DEFAULT_RULE,
        help='Which of the Wolfram codes (i.e. rules) to use '
        f'(default: {_DEFAULT_RULE}).')
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='Where to output the SVG to; if unspecified, '
        'the output will be shown on screen.')
    return parser


if __name__ == '__main__':
    parser = _make_parser()
    settings = parser.parse_args()

    grid = calc_grid(
        width=settings.width,
        height=settings.generations,
        rule=settings.rule)

    if settings.output is None:
        print(grid_to_text(grid))
    else:
        svg = '\n'.join(to_svg(grid))
        with open(settings.output, 'w') as f:
            f.write(svg)
