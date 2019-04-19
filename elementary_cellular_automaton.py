from itertools import chain, accumulate
import argparse

# http://en.wikipedia.org/wiki/Elementary_cellular_automaton


def BoolCollectionToBase2Str(boolCollection):
    return ''.join((str(int(bool(item))) for item in boolCollection))


def BoolCollectionToInt(boolCollection):
    return int(BoolCollectionToBase2Str(boolCollection), 2)


def width_at_given_generation(generation):
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


def rule_calc(neighbours, wolframCode):
    assert is_wolfram_code_valid(wolframCode)
    neighbourIndex = neighbours_to_int(neighbours)
    assert neighbourIndex in _NEIGHBOURHOOD_CONFIGURATION_INDEXES

    # The real meat of the program.
    return bool(index_to_num(neighbourIndex) & wolframCode)


def rule_factory(wolframCode):
    '''Is checked within RuleCalc itself but here we know as soon as
    possible that there has been a mistake.
    '''
    assert is_wolfram_code_valid(wolframCode)

    def RuleCalcFixed(neighbours):
        f'''Rule Calc for Rule {wolframCode}.'''
        return rule_calc(neighbours, wolframCode)

    RuleCalcFixed.__name__ = f'Rule {wolframCode}'
    RuleCalcFixed.wolframCode = wolframCode

    return RuleCalcFixed


def AllRuleFuncs():
    return map(rule_factory, WOLFRAM_CODES)


_DEFAULT_RULE = 30
DEFAULT_RULE = rule_factory(_DEFAULT_RULE)

ON = True
OFF = False
OUT = None

_symbolchar = {
    ON: '1',
    OFF: '0',
    OUT: ' ',
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


def CentreSymbols(line, paddingEachSide=1, padWith=OUT):
    pad = (padWith,) * paddingEachSide
    return chain(pad, line, pad)


STARTING_POINT = (ON,)


def NextLineSpecifyRule(rule, currentLine):
    preparedLine = CentreSymbols(currentLine, _NEIGHBOURHOOD_SCOPE * 2, OFF)
    return map(rule, RollingCollection(preparedLine, _NEIGHBOURHOOD_SIZE))


def NextLineFactory(rule):
    def NextLine(currentLine):
        return NextLineSpecifyRule(rule, currentLine)

    return NextLine


def RuleGenerator(rule=DEFAULT_RULE, start=STARTING_POINT, includeStart=True):
    value = start

    if includeStart:
        yield value

    f = NextLineFactory(rule)
    while True:
        value = tuple(f(value))
        yield value


def RuleGeneratorArrangements(*args, **kwargs):
    '''If the lines don't get tupled again the accumulate will flatten
    the arrangements.
    '''
    tupledLines = ((line,) for line in RuleGenerator(*args, **kwargs))
    return accumulate(tupledLines)


def RuleGeneratorArrangementsPadded(*args, **kwargs):
    for diagram in RuleGeneratorArrangements(*args, **kwargs):
        yield (CentreSymbols(item, len(diagram)-i-1)
               for i, item in enumerate(diagram))


def RuleGeneratorArrangementsPaddedStrings(*args, **kwargs):
    for arrangement in RuleGeneratorArrangementsPadded(*args, **kwargs):
        yield '\n'.join(map(SymbolsToString, arrangement))


def ToSVG(data, side=10, foreground='#FFFFFF', background='#000000'):
    side = int(side)
    if side <= 0:
        raise ValueError('Only strictly positive whole numbers shall '
                         'be accepted as side lengths.')

    data = tuple(data)
    lineCount = len(data)
    generation = lineCount-1
    width = width_at_given_generation(generation) * side
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


# testing an idea for showing the surrounding padding
def RollingCollection(items, sampleSize, pad=0, padValue=None):
    if sampleSize < 1:
        raise ValueError('Sample Size must be at least 1.')

    if pad < 0:
        raise ValueError('Padding should be at least 0.')

    paddingItems = (padValue,) * pad
    items = chain(paddingItems, items, paddingItems)

    items = tuple(items)

    for i in range(len(items)-sampleSize+1):
        yield items[i:i+sampleSize]


def _validate_rule_code(rule):
    value = int(rule)
    min = 0
    max = 0xff
    if not (0 <= value <= 0xff):
        raise argparse.ArgumentTypeError(
            f'Rule {value} must be between {min} and {max} inclusive.')
    return value


def _make_parser():
    DEFAULT_GENERATIONS = 10
    parser = argparse.ArgumentParser(
        description='Generate Wolfram elementary cellular automaton patterns.'
    )
    parser.add_argument(
        '-g', '--generations',
        type=int,
        default=DEFAULT_GENERATIONS,
        help='Number of generations (i.e. interations) to run '
        f'(default: {DEFAULT_GENERATIONS}).')
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

    rule_func = rule_factory(settings.rule)
    f = RuleGeneratorArrangementsPadded(rule_func)

    for _ in range(settings.generations):
        lastArrangement = next(f)

    if settings.output is None:
        # print(rule_func.__name__)
        rgf = RuleGeneratorArrangementsPaddedStrings(rule_func)
        for i in range(settings.generations):
            pattern = next(rgf)
        print(pattern)
    else:
        svg = '\n'.join(ToSVG(lastArrangement))
        with open(settings.output, 'w') as f:
            f.write(svg)

    '''
    for f in s.AllRuleFuncs():
        print(f.__name__)
    '''
