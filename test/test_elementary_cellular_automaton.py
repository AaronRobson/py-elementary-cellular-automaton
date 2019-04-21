import unittest

from itertools import islice

import elementary_cellular_automaton as eca


class TestWidthAtGivenGeneration(unittest.TestCase):
    def test(self):
        self.assertEqual(eca.width_at_given_generation(2), 5)


class TestIndexToNum(unittest.TestCase):
    def test_min(self):
        self.assertEqual(eca.index_to_num(0), 1)

    def test_max(self):
        self.assertEqual(eca.index_to_num(7), 128)


class TestConstants(unittest.TestCase):
    def test(self):
        self.assertEqual(eca._NUM_NEIGHBOURHOOD_CONFIGURATIONS, 8)

        self.assertEqual(eca.HIGH_WOLFRAM_CODE, 255)

        self.assertEqual(
            len(tuple(eca.NEIGHBOURHOOD_CONFIGURATIONS)),
            eca._NUM_NEIGHBOURHOOD_CONFIGURATIONS)

        self.assertEqual(
            len(eca.WOLFRAM_CODES),
            eca.NUM_OF_WOLFRAM_CODES)


class TestBoolCollectionToBase2Str(unittest.TestCase):
    def test_bools(self):
        self.assertEqual(
            eca.BoolCollectionToBase2Str((True, False, False)),
            '100')

    def test_ints(self):
        self.assertEqual(eca.BoolCollectionToBase2Str((1, 0, 1)), '101')


class TestBoolCollectionToInt(unittest.TestCase):
    def test_bools(self):
        self.assertEqual(eca.BoolCollectionToInt((True, False, False)), 4)

    def test_ints(self):
        self.assertEqual(eca.BoolCollectionToInt((1, 0, 1)), 5)


class TestNeighboursToInt(unittest.TestCase):
    def test(self):
        self.assertEqual(eca.neighbours_to_int((True, False, True)), 5)


class TestIntToNeighbours(unittest.TestCase):
    def test(self):
        self.assertEqual(tuple(eca.int_to_neighbours(5)), (True, False, True))


class TestFindCellValue(unittest.TestCase):
    def test_starting_cell(self):
        self.assertTrue(eca.find_cell_value(x=0, y=0, rule=30))

    def test_starting_row(self):
        self.assertFalse(eca.find_cell_value(x=1, y=0, rule=30))

    def test_before_starting_cell(self):
        self.assertFalse(eca.find_cell_value(x=0, y=-1, rule=30))

    def test_before_starting_row(self):
        self.assertFalse(eca.find_cell_value(x=1, y=-1, rule=30))

    def test_rule3(self):
        self.assertTrue(eca.find_cell_value(x=123, y=1, rule=3))
        self.assertFalse(eca.find_cell_value(x=123, y=2, rule=3))

    def test_rule30(self):
        #first line
        self.assertFalse(eca.find_cell_value(x=-1, y=0, rule=30))
        self.assertTrue(eca.find_cell_value(x=0, y=0, rule=30))
        self.assertFalse(eca.find_cell_value(x=1, y=0, rule=30))

        # second line
        self.assertFalse(eca.find_cell_value(x=-2, y=1, rule=30))
        self.assertTrue(eca.find_cell_value(x=-1, y=1, rule=30))
        self.assertTrue(eca.find_cell_value(x=0, y=1, rule=30))
        self.assertTrue(eca.find_cell_value(x=1, y=1, rule=30))
        self.assertFalse(eca.find_cell_value(x=2, y=1, rule=30))

        # third line
        self.assertFalse(eca.find_cell_value(x=-3, y=2, rule=30))
        self.assertTrue(eca.find_cell_value(x=-2, y=2, rule=30))
        self.assertTrue(eca.find_cell_value(x=-1, y=2, rule=30))
        self.assertFalse(eca.find_cell_value(x=0, y=2, rule=30))
        self.assertFalse(eca.find_cell_value(x=1, y=2, rule=30))
        self.assertTrue(eca.find_cell_value(x=2, y=2, rule=30))
        self.assertFalse(eca.find_cell_value(x=3, y=2, rule=30))


class TestFindXCoordinates(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            eca.find_x_coordinates(-1)

    def test_zero(self):
        self.assertEqual(list(eca.find_x_coordinates(0)), [])

    def test_odd(self):
        self.assertEqual(list(eca.find_x_coordinates(5)), [-2, -1, 0, 1, 2])

    def test_even(self):
        self.assertEqual(list(eca.find_x_coordinates(4)), [-2, -1, 0, 1])


class TestFindYCoordinates(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            eca.find_y_coordinates(-1)

    def test_zero(self):
        self.assertEqual(list(eca.find_y_coordinates(0)), [])

    def test_strictly_positive(self):
        self.assertEqual(list(eca.find_y_coordinates(1)), [0])


class TestFindCoordinates(unittest.TestCase):
    def normalise_to_lists(self, values):
        return list(map(list, values))

    def test(self):
        actual = self.normalise_to_lists(
            eca.find_coordinates(width=3, height=2))
        expected = [
            [(-1, 0), (0, 0), (1, 0)],
            [(-1, 1), (0, 1), (1, 1)],
        ]
        self.assertEqual(actual, expected)


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.middle_and_the_one_to_the_left_on_first_line = lambda x: x in [-1, 0]

    def f(self, rule, expected, starting_line=None):
        actual = eca.grid_to_text(
            eca.calc_grid(
                width=11,
                height=6,
                rule=rule,
                starting_line=starting_line))
        self.assertEqual(actual, expected)

    def test_rule_0(self):
        self.f(rule=0, expected='\n'.join([
            '     #     ',
            '           ',
            '           ',
            '           ',
            '           ',
            '           ',
        ]))

    def test_rule_1(self):
        self.f(rule=1, expected='\n'.join([
            '     #     ',
            '####   ####',
            '     #     ',
            '####   ####',
            '     #     ',
            '####   ####',
        ]))

    def test_rule_2(self):
        self.f(rule=2, expected='\n'.join([
            '     #     ',
            '    #      ',
            '   #       ',
            '  #        ',
            ' #         ',
            '#          ',
        ]))

    def test_rule_3(self):
        self.f(rule=3, expected = '\n'.join([
            '     #     ',
            '#####  ####',
            '      #    ',
            '######  ###',
            '       #   ',
            '#######  ##',
        ]))

    def test_rule_4(self):
        self.f(rule=4, expected = '\n'.join([
            '     #     ',
            '     #     ',
            '     #     ',
            '     #     ',
            '     #     ',
            '     #     ',
        ]))

    def test_rule_5(self):
        self.f(rule=5, expected = '\n'.join([
            '     #     ',
            '#### # ####',
            '     #     ',
            '#### # ####',
            '     #     ',
            '#### # ####',
        ]))

    def test_rule_6(self):
        self.f(rule=6, expected = '\n'.join([
            '     #     ',
            '    ##     ',
            '   #       ',
            '  ##       ',
            ' #         ',
            '##         ',
        ]))

    def test_rule_7(self):
        self.f(rule=7, expected = '\n'.join([
            '    ##     ',
            '####   ####',
            '     ##    ',
            '#####   ###',
            '      ##   ',
            '######   ##',
        ]),
        starting_line=self.middle_and_the_one_to_the_left_on_first_line)

    def test_rule_8(self):
        self.f(rule=8, expected = '\n'.join([
            '    ##     ',
            '    #      ',
            '           ',
            '           ',
            '           ',
            '           ',
        ]),
        starting_line=self.middle_and_the_one_to_the_left_on_first_line)

    def test_rule_9(self):
        self.f(rule=9, expected = '\n'.join([
            '     #     ',
            '####   ####',
            '     # #   ',
            '####     ##',
            '     ### # ',
            '#### #     ',
        ]))

    def test_rule_10(self):
        self.f(rule=10, expected = '\n'.join([
            '     #     ',
            '    #      ',
            '   #       ',
            '  #        ',
            ' #         ',
            '#          ',
        ]))

    def test_rule_11(self):
        self.f(rule=11, expected = '\n'.join([
            '     #     ',
            '#####  ####',
            '      ##   ',
            '#######  ##',
            '        ## ',
            '#########  ',
        ]))

    def test_rule_12(self):
        self.f(rule=12, expected = '\n'.join([
            '     #     ',
            '     #     ',
            '     #     ',
            '     #     ',
            '     #     ',
            '     #     ',
        ]))

    def test_rule_13(self):
        self.f(rule=13, expected = '\n'.join([
            '     #     ',
            '#### # ####',
            '     # #   ',
            '#### # # ##',
            '     # # # ',
            '#### # # # ',
        ]))

    def test_rule_14(self):
        self.f(rule=14, expected = '\n'.join([
            '     #     ',
            '    ##     ',
            '   ##      ',
            '  ##       ',
            ' ##        ',
            '##         ',
        ]))

    def test_rule_15(self):
        self.f(rule=15, expected = '\n'.join([
            '     #     ',
            '###### ####',
            '       #   ',
            '######## ##',
            '         # ',
            '########## ',
        ]))

    def test_rule_16(self):
        self.f(rule=16, expected = '\n'.join([
            '     #     ',
            '      #    ',
            '       #   ',
            '        #  ',
            '         # ',
            '          #',
        ]))

    def test_rule_17(self):
        self.f(rule=17, expected = '\n'.join([
            '     #     ',
            '####  #####',
            '    #      ',
            '###  ######',
            '   #       ',
            '##  #######',
        ]))

    def test_rule_18(self):
        self.f(rule=18, expected = '\n'.join([
            '     #     ',
            '    # #    ',
            '   #   #   ',
            '  # # # #  ',
            ' #       # ',
            '# #     # #',
        ]))

    def test_rule_19(self):
        self.f(rule=19, expected = '\n'.join([
            '    ##     ',
            '####  #####',
            '    ##     ',
            '####  #####',
            '    ##     ',
            '####  #####',
        ]),
        starting_line=self.middle_and_the_one_to_the_left_on_first_line)

    def test_rule_20(self):
        self.f(rule=20, expected = '\n'.join([
            '     #     ',
            '     ##    ',
            '       #   ',
            '       ##  ',
            '         # ',
            '         ##',
        ]))

    def test_rule_21(self):
        self.f(rule=21, expected = '\n'.join([
            '    ##     ',
            '###   #####',
            '   ##      ',
            '##   ######',
            '  ##       ',
            '#   #######',
        ]),
        starting_line=self.middle_and_the_one_to_the_left_on_first_line)

    def test_rule_22(self):
        self.f(rule=22, expected = '\n'.join([
            '     #     ',
            '    ###    ',
            '   #   #   ',
            '  ### ###  ',
            ' #       # ',
            '###     ###',
        ]))

    def test_rule_23(self):
        self.f(rule=23, expected = '\n'.join([
            '    ##     ',
            '####  #####',
            '    ##     ',
            '####  #####',
            '    ##     ',
            '####  #####',
        ]),
        starting_line=self.middle_and_the_one_to_the_left_on_first_line)

    def test_rule_24(self):
        self.f(rule=24, expected = '\n'.join([
            '     #     ',
            '      #    ',
            '       #   ',
            '        #  ',
            '         # ',
            '          #',
        ]))

    def test_rule_25(self):
        self.f(rule=25, expected = '\n'.join([
            '     #     ',
            '####  #####',
            '    # #    ',
            '###    ####',
            '   ### #   ',
            '## #    ###',
        ]))

    def test_rule_26(self):
        self.f(rule=26, expected = '\n'.join([
            '     #     ',
            '    # #    ',
            '   #   #   ',
            '  # # # #  ',
            ' #       # ',
            '# #     # #',
        ]))

    def test_rule_27(self):
        self.f(rule=27, expected = '\n'.join([
            '     #     ',
            '##### #####',
            '      #    ',
            '###### ####',
            '       #   ',
            '####### ###',
        ]))

    def test_rule_28(self):
        self.f(rule=28, expected = '\n'.join([
            '     #     ',
            '     ##    ',
            '     # #   ',
            '     # ##  ',
            '     # # # ',
            '     # # ##',
        ]))

    def test_rule_29(self):
        self.f(rule=29, expected = '\n'.join([
            '     #     ',
            '#### ######',
            '     #     ',
            '#### ######',
            '     #     ',
            '#### ######',
        ]))

    def test_rule_30(self):
        self.f(rule=30, expected = '\n'.join([
            '     #     ',
            '    ###    ',
            '   ##  #   ',
            '  ## ####  ',
            ' ##  #   # ',
            '## #### ###',
        ]))

    def test_rule_45(self):
        self.f(rule=45, expected = '\n'.join([
            '     #     ',
            '#### # ####',
            '    ####   ',
            '### #    ##',
            '   ## ## # ',
            '## # ## ## ',
        ]))

    def test_rule_57(self):
        self.f(rule=57, expected = '\n'.join([
            '     #     ',
            '####  #####',
            '    # #    ',
            '###  # ####',
            '   #  ##   ',
            '##  # # ###',
        ]))

    def test_rule_90(self):
        self.f(rule=90, expected = '\n'.join([
            '     #     ',
            '    # #    ',
            '   #   #   ',
            '  # # # #  ',
            ' #       # ',
            '# #     # #',
        ]))

    def test_rule_105(self):
        self.f(rule=105, expected = '\n'.join([
            '     #     ',
            '####   ####',
            '   # # #   ',
            '##  # #  ##',
            ' #   #   # ',
            '   #   #   ',
        ]))

    def test_rule_109(self):
        self.f(rule=109, expected = '\n'.join([
            '     #     ',
            '#### # ####',
            '   #####   ',
            '## #   # ##',
            ' ### # ### ',
            ' # ##### # ',
        ]))

    def test_rule_128(self):
        seven_cells_on_first_line = lambda x: abs(x) <= 3
        self.f(rule=128, expected = '\n'.join([
            '  #######  ',
            '   #####   ',
            '    ###    ',
            '     #     ',
            '           ',
            '           ',
        ]),
        starting_line=seven_cells_on_first_line)

    def test_rule_137(self):
        self.f(rule=137, expected = '\n'.join([
            '     #     ',
            '####   ####',
            '###  # ####',
            '##     ####',
            '#  ### ####',
            '   ##  ####',
        ]))

    def test_rule_225(self):
        self.f(rule=225, expected = '\n'.join([
            '     #     ',
            '####   ####',
            '#### #  ###',
            '#####    ##',
            '##### ##  #',
            '###### #   ',
        ]))

    def test_rule_250(self):
        self.f(rule=250, expected = '\n'.join([
            '     #     ',
            '    # #    ',
            '   # # #   ',
            '  # # # #  ',
            ' # # # # # ',
            '# # # # # #',
        ]))

    def test_rule_251(self):
        four_cells_with_spaces = lambda x: x in [-3, -1, 1, 3]
        self.f(rule=251, expected = '\n'.join([
            '  # # # #  ',
            '## # # # ##',
            '### # # ###',
            '#### # ####',
            '##### #####',
            '###########',
        ]),
        starting_line=four_cells_with_spaces)

    def test_rule_252(self):
        self.f(rule=252, expected = '\n'.join([
            '     #     ',
            '     ##    ',
            '     ###   ',
            '     ####  ',
            '     ##### ',
            '     ######',
        ]))

    def test_rule_253(self):
        self.f(rule=253, expected = '\n'.join([
            '     #     ',
            '#### ######',
            '###########',
            '###########',
            '###########',
            '###########',
        ]))

    def test_rule_254(self):
        self.f(rule=254, expected = '\n'.join([
            '     #     ',
            '    ###    ',
            '   #####   ',
            '  #######  ',
            ' ######### ',
            '###########',
        ]))

    def test_rule_255(self):
        self.f(rule=255, expected = '\n'.join([
            '     #     ',
            '###########',
            '###########',
            '###########',
            '###########',
            '###########',
        ]))


class TestToSVG(unittest.TestCase):
    def test(self):
        # Rule 30
        GIVEN_DATA = [
            [False, False, False, True, False, False, False],
            [False, False, True, True, True, False, False],
            [False, True, True, False, False, True, False],
        ]
        expected = '\n'.join([
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            'width="70px" height="30px">',
            '\t<rect width="70" height="30" fill="#ffffff" />',
            '',
            '\t<g fill="#000000">',
            '\t\t<!-- Line: 0 -->',
            '\t\t<rect x="30" y="0" width="10" height="10" />',
            '',
            '\t\t<!-- Line: 1 -->',
            '\t\t<rect x="20" y="10" width="10" height="10" />',
            '\t\t<rect x="30" y="10" width="10" height="10" />',
            '\t\t<rect x="40" y="10" width="10" height="10" />',
            '',
            '\t\t<!-- Line: 2 -->',
            '\t\t<rect x="10" y="20" width="10" height="10" />',
            '\t\t<rect x="20" y="20" width="10" height="10" />',
            '\t\t<rect x="50" y="20" width="10" height="10" />',
            '',
            '\t</g>',
            '</svg>',
            '',
        ])
        self.maxDiff = None
        actual = '\n'.join(eca.ToSVG(data=GIVEN_DATA))
        self.assertEqual(actual, expected)
