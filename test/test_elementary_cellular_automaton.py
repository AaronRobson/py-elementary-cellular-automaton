import unittest
from copy import copy

from itertools import islice

import elementary_cellular_automaton as eca


class TestRulesSettings(unittest.TestCase):
    def setUp(self):
        self.s = eca.Settings()

    def testSettingsExpected(self):
        self.assertEqual(self.s.IndexToNum(0), 1)
        self.assertEqual(self.s.IndexToNum(7), 128)

        self.assertEqual(self.s.numNeighhbourHoodConfigurations, 8)

        self.assertEqual(self.s.highWolframCode, 255)

        self.assertEqual(
            len(tuple(self.s.neighhbourHoodConfigurations)),
            self.s.numNeighhbourHoodConfigurations)

        self.assertEqual(
            len(tuple(self.s.wolframCodes)),
            self.s.numOfWolframCodes)

        self.assertEqual(self.s.WidthAtGivenGeneration(2), 5)

    def testCopying(self):
        obj = self.s
        a = copy(obj)
        b = copy(a)

        self.assertEqual(a, b)
        self.assertEqual(repr(a), repr(b))

        origChoice = a.choices
        a.choices = 5
        self.assertNotEqual(a, b)
        self.assertNotEqual(repr(a), repr(b))

        a.choices = origChoice
        self.assertEqual(a, b)
        self.assertEqual(repr(a), repr(b))

        a.neighbourhoodScope = 6
        self.assertNotEqual(a, b)
        self.assertNotEqual(repr(a), repr(b))


class TestRules(unittest.TestCase):
    def setUp(self):
        self.s = eca.Settings()
        self.r30 = eca.s.RuleFactory(30)
        self.STARTING_POINT = eca.STARTING_POINT

    def testBoolCollectionToBase2Str(self):
        self.assertEqual(
            eca.BoolCollectionToBase2Str((True, False, None)),
            '100')
        self.assertEqual(eca.BoolCollectionToBase2Str((1, 0, 1)), '101')

    def testBoolCollectionToInt(self):
        self.assertEqual(eca.BoolCollectionToInt((True, False, None)), 4)
        self.assertEqual(eca.BoolCollectionToInt((1, 0, 1)), 5)

    def testNeighboursToInt(self):
        self.assertEqual(eca.s.NeighboursToInt((True, False, True)), 5)

    def testIntToNeighbours(self):
        self.assertEqual(tuple(eca.s.IntToNeighbours(5)), (True, False, True))

    def testR30(self):
        self.assertEqual(
            tuple(map(self.r30, self.s.neighhbourHoods)),
            (False, False, False, True, True, True, True, False))

    def testNextLineSpecifyRule(self):
        self.assertEqual(
            tuple(eca.NextLineSpecifyRule(self.r30, (True, True, True))),
            (True, True, False, False, True))

    def testNextLineFactory(self):
        nifunc = eca.NextLineFactory(self.r30)

        secondLine = tuple(nifunc(self.STARTING_POINT))
        self.assertEqual(secondLine, (True, True, True))

        thirdLine = tuple(nifunc(secondLine))
        self.assertEqual(thirdLine, (True, True, False, False, True))

    def testRuleGeneratorFullPadded(self):
        arrangements = (
            (
                (True,),
            ),
            (
                (None, True, None),
                (True, True, True)),
            (
                (None, None, True, None, None),
                (None, True, True, True, None),
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
            ('1', ' 1 \n111', '  1  \n 111 \n11001'))


if __name__ == '__main__':
    unittest.main()
