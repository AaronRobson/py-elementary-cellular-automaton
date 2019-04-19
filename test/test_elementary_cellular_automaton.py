import unittest

from itertools import islice

import elementary_cellular_automaton as eca


class TestWidthAtGivenGeneration(unittest.TestCase):
    def test(self):
        self.assertEqual(eca.width_at_given_generation(2), 5)


class TestRulesSettings(unittest.TestCase):
    def testSettingsExpected(self):
        self.assertEqual(eca.index_to_num(0), 1)
        self.assertEqual(eca.index_to_num(7), 128)

        self.assertEqual(eca._NUM_NEIGHBOURHOOD_CONFIGURATIONS, 8)

        self.assertEqual(eca.HIGH_WOLFRAM_CODE, 255)

        self.assertEqual(
            len(tuple(eca.NEIGHBOURHOOD_CONFIGURATIONS)),
            eca._NUM_NEIGHBOURHOOD_CONFIGURATIONS)

        self.assertEqual(
            len(eca.WOLFRAM_CODES),
            eca.NUM_OF_WOLFRAM_CODES)


class TestRules(unittest.TestCase):
    def setUp(self):
        self.r30 = eca.rule_factory(30)

    def testBoolCollectionToBase2Str(self):
        self.assertEqual(
            eca.BoolCollectionToBase2Str((True, False, False)),
            '100')
        self.assertEqual(eca.BoolCollectionToBase2Str((1, 0, 1)), '101')

    def testBoolCollectionToInt(self):
        self.assertEqual(eca.BoolCollectionToInt((True, False, False)), 4)
        self.assertEqual(eca.BoolCollectionToInt((1, 0, 1)), 5)

    def testNeighboursToInt(self):
        self.assertEqual(eca.neighbours_to_int((True, False, True)), 5)

    def testIntToNeighbours(self):
        self.assertEqual(tuple(eca.int_to_neighbours(5)), (True, False, True))

    def testR30(self):
        self.assertEqual(
            tuple(map(self.r30, eca.NEIGHBOURHOODS)),
            (False, False, False, True, True, True, True, False))

    def testNextLineSpecifyRule(self):
        self.assertEqual(
            tuple(eca.NextLineSpecifyRule(self.r30, (True, True, True))),
            (True, True, False, False, True))

    def testNextLineFactory(self):
        nifunc = eca.NextLineFactory(self.r30)

        secondLine = tuple(nifunc(eca.STARTING_POINT))
        self.assertEqual(secondLine, (True, True, True))

        thirdLine = tuple(nifunc(secondLine))
        self.assertEqual(thirdLine, (True, True, False, False, True))

    def testRuleGeneratorFullPadded(self):
        arrangements = (
            (
                (True,),
            ),
            (
                (False, True, False),
                (True, True, True)),
            (
                (False, False, True, False, False),
                (False, True, True, True, False),
                (True, True, False, False, True),
            ),
        )

        values = islice(eca.RuleGeneratorArrangementsPadded(self.r30), 3)
        values = tuple(tuple(
            tuple(line) for line in arrangement) for arrangement in values)

        self.assertEqual(arrangements, values)

    def testRuleGeneratorFullPaddedString(self):
        self.assertEqual(
            tuple(islice(
                eca.RuleGeneratorArrangementsPaddedStrings(self.r30), 3)),
            ('1', '010\n111', '00100\n01110\n11001'))


class TestToSVG(unittest.TestCase):
    def test(self):
        GIVEN_DATA = (
            (False, False, True, False, False),
            (False, True, True, True, False),
            (True, True, False, False, True)
        )
        expected = '\n'.join([
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            'width="50px" height="30px">',
            '\t<rect width="50" height="30" fill="#ffffff" />',
            '',
            '\t<g fill="#000000">',
            '\t\t<!-- Line: 0 -->',
            '\t\t<rect x="20" y="0" width="10" height="10" />',
            '',
            '\t\t<!-- Line: 1 -->',
            '\t\t<rect x="10" y="10" width="10" height="10" />',
            '\t\t<rect x="20" y="10" width="10" height="10" />',
            '\t\t<rect x="30" y="10" width="10" height="10" />',
            '',
            '\t\t<!-- Line: 2 -->',
            '\t\t<rect x="0" y="20" width="10" height="10" />',
            '\t\t<rect x="10" y="20" width="10" height="10" />',
            '\t\t<rect x="40" y="20" width="10" height="10" />',
            '',
            '\t</g>',
            '</svg>',
            '',
        ])
        self.maxDiff = None
        actual = '\n'.join(eca.ToSVG(data=GIVEN_DATA))
        self.assertEqual(actual, expected)
