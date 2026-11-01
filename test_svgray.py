import importlib.util
import pathlib
import time
import unittest

_spec = importlib.util.spec_from_file_location(
    "svgray", pathlib.Path(__file__).with_name(".svgray.py"))
svgray = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(svgray)


class ConvertTest(unittest.TestCase):
    def test_hex(self):
        self.assertEqual(svgray.convert("#ff0000"), "#4c4c4c")
        self.assertEqual(svgray.convert("#f00"), "#444")

    def test_rgb_functions(self):
        self.assertEqual(svgray.convert("rgb(255,0,0)"), "rgb(76, 76, 76)")
        self.assertEqual(svgray.convert("rgb(100%, 0%, 0%)"), "rgb(76, 76, 76)")
        self.assertEqual(svgray.convert("rgba(255, 0, 0, 0.5)"), "rgba(76, 76, 76, 0.5)")
        self.assertEqual(svgray.convert("rgb(255 0 0 / 50%)"), "rgba(76, 76, 76, 0.5)")

    def test_hsl_functions(self):
        self.assertEqual(svgray.convert("hsl(120, 100%, 50%)"), "rgb(150, 150, 150)")
        self.assertEqual(svgray.convert("hsla(120deg 100% 25% / .3)"), "rgba(75, 75, 75, 0.3)")

    def test_color_arguments_are_not_evaluated(self):
        # Used to be passed to eval(): this pinned a CPU core indefinitely.
        start = time.monotonic()
        self.assertEqual(svgray.convert("rgb(9**9**9, 0, 0)"), "rgb(9**9**9, 0, 0)")
        self.assertLess(time.monotonic() - start, 1)
        self.assertEqual(svgray.convert("rgb(__import__, 1, 1)"), "rgb(__import__, 1, 1)")

    def test_main_leaves_unparseable_colors(self):
        svg = '<svg><rect fill="rgb(9**9**9, 0, 0)"/><rect fill="#00ff00"/></svg>'
        out = svgray.colors.sub(lambda m: svgray.convert(m.group()), svg)
        self.assertIn('rgb(9**9**9, 0, 0)', out)
        self.assertIn('#969696', out)


if __name__ == "__main__":
    unittest.main()
