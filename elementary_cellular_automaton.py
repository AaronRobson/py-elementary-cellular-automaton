import argparse
from functools import lru_cache

# http://en.wikipedia.org/wiki/Elementary_cellular_automaton


def BoolCollectionToBase2Str(boolCollection):
    return ''.join((str(int(bool(item))) for item in boolCollection))


def BoolCollectionToInt(boolCollection):
    return int(BoolCollectionToBase2Str(boolCollection), 2)


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


def int_to_neighbours(intNeighbours):
    assert intNeighbours in _NEIGHBOURHOOD_CONFIGURATION_INDEXES
    # bin assumes two choices
    return (bool(int(b)) for b in bin(intNeighbours)[2:])


def neighbours_to_int(neighbours):
    neighbours = tuple(neighbours)
    assert len(neighbours) <= _NEIGHBOURHOOD_SIZE
    assert _NUMBER_OF_CHOICES == 2  # Bool assumed.
    base2Str = BoolCollectionToBase2Str(neighbours)
    return int(base2Str, _NUMBER_OF_CHOICES)


NEIGHBOURHOOD_CONFIGURATIONS = tuple(
    map(index_to_num, _NEIGHBOURHOOD_CONFIGURATION_INDEXES))

NEIGHBOURHOODS = tuple(
    map(int_to_neighbours, _NEIGHBOURHOOD_CONFIGURATION_INDEXES))

NUM_OF_WOLFRAM_CODES = _NUMBER_OF_CHOICES**_NUM_NEIGHBOURHOOD_CONFIGURATIONS
LOW_WOLFRAM_CODE = 0
HIGH_WOLFRAM_CODE = NUM_OF_WOLFRAM_CODES - 1

WOLFRAM_CODES = tuple(
    range(LOW_WOLFRAM_CODE, NUM_OF_WOLFRAM_CODES))


def is_wolfram_code_valid(numRule):
    '''http://en.wikipedia.org/wiki/Wolfram_code
    '''
    return numRule in WOLFRAM_CODES


def ensureWolframCodeIsValid(wolframCode):
    if not is_wolfram_code_valid(wolframCode):
        raise ValueError(f'Wolfram code {wolframCode} is invalid, '
                         'use values between '
                         f'{LOW_WOLFRAM_CODE} and {HIGH_WOLFRAM_CODE}')


_DEFAULT_RULE = 30

_symbolchar = {
    True: '#',
    False: ' ',
}

for value in _symbolchar.values():
    assert len(value) == 1

_charsymbol = {v: k for k, v in _symbolchar.items()}

assert len(_symbolchar) == len(_charsymbol), 'Same Value duplicated in more ' \
    'than one Key in %r.' % (_symbolchar)


def CharToSymbol(char):
    try:
        return _charsymbol[char]
    except KeyError:
        raise ValueError('%r is not a valid character value.' % char)


def SymbolToChar(symbol):
    try:
        return _symbolchar[symbol]
    except KeyError:
        raise ValueError('%r is not a valid symbol value.' % symbol)


def CharsToSymbols(chars):
    return map(CharToSymbol, chars)


def SymbolsToChars(symbols):
    return map(SymbolToChar, symbols)


def StringToSymbols(inStr):
    chars = tuple(str(inStr))
    return CharsToSymbols(chars)


def SymbolsToString(symbols):
    return ''.join(SymbolsToChars(symbols))


def ToSVG(data, side=10, foreground='#000000', background='#ffffff'):
    side = int(side)
    if side <= 0:
        raise ValueError('Only strictly positive whole numbers shall '
                         'be accepted as side lengths.')

    data = list(map(list, data))
    itemCount = len(data[0])
    lineCount = len(data)
    width = itemCount * side
    height = lineCount * side

    yield '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
    yield '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" ' \
        '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
    yield '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" ' \
        f'width="{width}px" height="{height}px">'
    yield f'\t<rect width="{width}" height="{height}" fill="{background}" />'
    yield ''
    yield f'\t<g fill="{foreground}">'

    def Rect(width, height):
        def shape(x, y):
            xScaled = x*width
            yScaled = y*height
            return f'\t\t<rect x="{xScaled}" y="{yScaled}" ' + \
                f'width="{width}" height="{height}" />'
        return shape

    def Square(dimension):
        return Rect(dimension, dimension)

    Draw = Square(side)

    for y, yItem in enumerate(data):
        yield f'\t\t<!-- Line: {y} -->'

        for x, xItem in enumerate(yItem):
            if xItem:
                yield Draw(x, y)

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
    ensureWolframCodeIsValid(rule)

    if starting_line is None:
        starting_line = a_single_cell

    if y < 0:
        return False

    if y == 0:
        return starting_line(x)

    neighbourValues = (
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

    neighbourIndex = neighbours_to_int(neighbourValues)
    assert neighbourIndex in _NEIGHBOURHOOD_CONFIGURATION_INDEXES

    return bool(index_to_num(neighbourIndex) & rule)


def find_x_coordinates(width):
    if width < 0:
        raise ValueError('width must be positive')

    offset = width // 2
    remainder = width % 2
    lowerInclusiveBound = -offset + 1 - remainder
    upperExclusiveBound = lowerInclusiveBound + width
    return range(lowerInclusiveBound, upperExclusiveBound)


def find_y_coordinates(height):
    if height < 0:
        raise ValueError('height must be positive')
    return range(height)


def find_coordinates(width, height):
    xValues = list(find_x_coordinates(width=width))
    yValues = find_y_coordinates(height=height)

    for y in yValues:
        yield ((x, y) for x in xValues)


def calc_grid(width, height, rule=_DEFAULT_RULE, starting_line=None):
    gridLines = find_coordinates(width=width, height=height)
    for gridLine in gridLines:
        yield (find_cell_value(x=cell[0], y=cell[1],
                               rule=rule, starting_line=starting_line)
               for cell in gridLine)


def grid_to_text(grid):
    return '\n'.join(map(SymbolsToString, grid))


def _make_parser():
    DEFAULT_GENERATIONS = 6
    parser = argparse.ArgumentParser(
        description='Generate Wolfram elementary cellular automaton patterns.'
    )
    parser.add_argument(
        '-g', '--generations',
        '-e', '--height',
        type=int,
        default=DEFAULT_GENERATIONS,
        help='Number of generations to run (i.e. the height) '
        f'(default: {DEFAULT_GENERATIONS}).')
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=None,
        help='Width of the view '
        f'(default: dependent on the generations/height).')
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

    height = settings.generations
    if settings.width is None:
        width = width_at_given_generation(generation=height)
    else:
        width = settings.width

    grid = calc_grid(width=width, height=height, rule=settings.rule)

    if settings.output is None:
        print(grid_to_text(grid))
    else:
        svg = '\n'.join(ToSVG(grid))
        with open(settings.output, 'w') as f:
            f.write(svg)
