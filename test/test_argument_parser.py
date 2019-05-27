import unittest

from elementary_cellular_automaton import _make_parser


class TestMakeParser(unittest.TestCase):
    def test(self):
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
