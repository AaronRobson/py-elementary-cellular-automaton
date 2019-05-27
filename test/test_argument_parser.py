import unittest

from elementary_cellular_automaton import _make_parser


class TestMakeParser(unittest.TestCase):
    def test_short_options(self):
        parser = _make_parser()
        settings = parser.parse_args(
            [
                '-g', '6',
                '-r', '30',
                '-o', 'a.svg'
            ])
        self.assertEqual(settings.generations, 6)
        self.assertEqual(settings.rule, 30)
        self.assertEqual(settings.output, 'a.svg')

    def test_long_options(self):
        parser = _make_parser()
        settings = parser.parse_args(
            [
                '--generations', '10',
                '--rule', '35',
                '--output', 'b.svg'
            ])
        self.assertEqual(settings.generations, 10)
        self.assertEqual(settings.rule, 35)
        self.assertEqual(settings.output, 'b.svg')
