from operator import attrgetter, eq
from functools import reduce
from itertools import chain, accumulate
from collections import OrderedDict

# http://en.wikipedia.org/wiki/Elementary_cellular_automaton

def BoolCollectionToBase2Str(boolCollection):
    return ''.join((str(int(bool(item))) for item in boolCollection))

def BoolCollectionToInt(boolCollection):
    return int(BoolCollectionToBase2Str(boolCollection), 2)

class Settings:
    def __init__(self, choices=2, neighbourhoodScope=1):
        self._settableAttributeNames = (
            'choices',
            'neighbourhoodScope',
        )

        self.choices = choices
        self.neighbourhoodScope = neighbourhoodScope

    @property
    def values(self):
        return OrderedDict((name, attrgetter(name)(self)) for name in self._settableAttributeNames)

    def __repr__(self):
        return '%s(%s)' % (__class__.__name__, ', '.join('%s=%d' % (k,v) for k,v in self.values.items()))

    def __eq__(self, other):
        if not isinstance(other, __class__):
            #If sub-classing even happens, then this will have to revisited.
            return False

        objects = self, other
        getter = attrgetter('values')
        values = map(getter, objects)
        return reduce(eq, map(getter, objects))

    @property
    def neighbourhoodSize(self):
        return self.neighbourhoodScope*2 + 1

    @property
    def numNeighhbourHoodConfigurations(self):
        return self.choices**self.neighbourhoodSize

    @property
    def neighhbourHoodConfigurationIndexes(self):
        return range(s.numNeighhbourHoodConfigurations-1, 0-1, -1)

    @property
    def neighhbourHoodConfigurations(self):
        return map(self.IndexToNum, self.neighhbourHoodConfigurationIndexes)

    @property
    def neighhbourHoods(self):
        return map(self.IntToNeighbours, self.neighhbourHoodConfigurationIndexes)

    @property
    def numOfWolframCodes(self):
        return self.choices**self.numNeighhbourHoodConfigurations

    @property
    def lowWolframCode(self):
        return 0

    @property
    def highWolframCode(self):
         return self.numOfWolframCodes - 1

    @property
    def wolframCodes(self):
        return range(self.lowWolframCode, self.numOfWolframCodes)

    def IndexToNum(self, index):
        return self.choices**index

    def IsWolframCodeValid(self, numRule):
        '''http://en.wikipedia.org/wiki/Wolfram_code
        '''
        return numRule in self.wolframCodes

    def WidthAtGivenGeneration(self, generation):
        generation = int(generation)

        if generation < 0:
            raise ValueError('A negative generation is not allowed.')

        return generation*2 + 1

    def IntToNeighbours(self, intNeighbours):
        assert intNeighbours in self.neighhbourHoodConfigurationIndexes
    #bin assumes two choices
        return (bool(int(b)) for b in bin(intNeighbours)[2:])

    def NeighboursToInt(self, neighbours):
        neighbours = tuple(neighbours)
        assert len(neighbours) <= self.neighbourhoodSize

        assert s.choices == 2 #Bool assumed.
        base2Str = BoolCollectionToBase2Str(neighbours)
        return int(base2Str, s.choices)

    def RuleCalc(self, neighbours, wolframCode):
        assert self.IsWolframCodeValid(wolframCode)
        neighbourIndex = self.NeighboursToInt(neighbours)
        assert neighbourIndex in self.neighhbourHoodConfigurationIndexes

        #The real meat of the program.
        return bool(self.IndexToNum(neighbourIndex) & wolframCode)

    def RuleFactory(self, wolframCode):
        #Is checked within RuleCalc itself but here we know as soon as possible that there has been a mistake.
        assert self.IsWolframCodeValid(wolframCode)

        def RuleCalcFixed(neighbours):
            '''Rule Calc for Rule %d.
            ''' % (wolframCode)
            return self.RuleCalc(neighbours, wolframCode)

        RuleCalcFixed.__name__ = 'Rule %d' % (wolframCode)
        RuleCalcFixed.wolframCode = wolframCode

        return RuleCalcFixed

    def AllRuleFuncs(self):
        return map(self.RuleFactory, self.wolframCodes)

s = Settings()

DEFAULT_RULE = s.RuleFactory(30)

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

_charsymbol = {v:k for k,v in _symbolchar.items()}

assert len(_symbolchar) == len(_charsymbol), 'Same Value duplicated in more than one Key in %r.' % (_symbolchar)

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
    preparedLine = CentreSymbols(currentLine, s.neighbourhoodScope * 2, OFF)
    return map(rule, RollingCollection(preparedLine, s.neighbourhoodSize))

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
    #If the lines don't get tupled again the accumulate will flatten the arrangements.
    tupledLines = ((line,) for line in RuleGenerator(*args, **kwargs))
    return accumulate(tupledLines)

def RuleGeneratorArrangementsPadded(*args, **kwargs):
    for diagram in RuleGeneratorArrangements(*args, **kwargs):
        yield (CentreSymbols(item, len(diagram)-i-1) for i, item in enumerate(diagram))

def RuleGeneratorArrangementsPaddedStrings(*args, **kwargs):
    for arrangement in RuleGeneratorArrangementsPadded(*args, **kwargs):
        yield '\n'.join(map(SymbolsToString, arrangement))

def ToSVG(data, side=10, foreground='#FFFFFF', background='#000000'):
        side = int(side)
        if side <= 0:
            raise ValueError('Only strictly positive whole numbers shall be accepted as side lengths.')

        data = tuple(data)
        lineCount = len(data)
        generation = lineCount-1
        width = s.WidthAtGivenGeneration(generation) * side
        height = lineCount * side

        yield '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        yield '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        yield '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%dpx" height="%dpx">' % (width, height)
        yield '\t<rect width="%d" height="%d" fill="%s" />' % (width, height, background)
        #yield '\t<!-- Rule %s, Generation: %d, Side: %d -->' % (self.wolframCode, generation, side)
        yield ''

        yield '\t<g fill="%s">' % (foreground)

        def Rect(width, height):
            def shape(x, y):
                return '\t\t<rect x="%d" y="%d" width="%d" height="%d" />' % (x*width, y*height, width, height)
            return shape

        def Square(dimension):
            return Rect(dimension, dimension)

        Draw = Square(side)

        for y, yItem in enumerate(data):
            yield '\t\t<!-- Line: %d -->' % (y)

            for x, xItem in enumerate(yItem):
                if xItem:
                    yield Draw(x, y)

            yield ''

        yield '\t</g>'

        yield '</svg>'
        yield ''

#testing an idea for showing the surrounding padding
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

if __name__ == '__main__':
    f = RuleGeneratorArrangementsPadded(DEFAULT_RULE)

    for _ in range(12):
        lastArrangement = next(f)

    svg = '\n'.join(ToSVG(lastArrangement))
    print(svg)

    save = True
    if save:
        filename = 'ZZZ.svg'
        with open(filename, 'w') as f:
            f.write(svg)

    #for f in s.AllRuleFuncs():
    #    print(f)

    print(s)
    print(DEFAULT_RULE.__name__)

    ######################


    rgf = RuleGeneratorArrangementsPaddedStrings(DEFAULT_RULE)
    for i in range(4):
        print(next(rgf))
        print()

