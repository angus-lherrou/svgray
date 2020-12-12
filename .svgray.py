import re
from typing import Tuple

import colorsys


colors_hex_str = r"(?:#|0x)(?:[a-f0-9]{3}|[a-f0-9]{6})\b"
colors_func_str = r"(?:rgb|hsl)a?\([^)]*\)"

colors_hex = re.compile(colors_hex_str, re.IGNORECASE)
colors_func = re.compile(colors_func_str, re.IGNORECASE)
colors = re.compile(colors_hex_str + r"|" + colors_func_str, re.IGNORECASE)


def parse_color_to_rgb(color: str) -> Tuple[float, float, float, float, str]:
    a = None
    if colors_hex.match(color) is not None:
        if color.startswith('#'):
            color = color[1:]
        elif color.startswith('0x'):
            color = color[2:]
        assert len(color) in {3, 6}, f'bad color length {len(color)} for color #{color}'
        kind = f'hex{len(color)}'
        if len(color) == 3:
            color = ''.join(val*2 for val in color)
        rgb = int(color, 16)
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
    elif colors_func.match(color) is not None:
        kind = 'func'
        values = eval(color[color.index('('):])
        if color[3] == 'a':
            assert len(values) == 4, 'rgba/hsla'
        else:
            assert len(values) == 3, 'rgb/hsl'
        if color.startswith('rgb'):
            r, g, b = values[:3]
        else:
            h, s, l = values[:3]
            r, g, b = colorsys.hls_to_rgb(h, l, s)
        if len(values) == 4:
            a = values[3]
    else:
        assert colors.match(color) is None
        raise ValueError(f'bad color "{color}"')
    return r, g, b, a, kind


def colmod(r, g, b):
    # ITU-R Recommendation BT.709
    # l = 0.2125 * r + 0.7154 * g + 0.0721 * b
    # NTSC and PAL
    l = 0.299 * r + 0.587 * g + 0.114 * b
    ig = int(round(l))
    # coloreffect.debug('gs '+hex(r)+' '+hex(g)+' '+hex(b)+'%02x%02x%02x' % (ig,ig,ig))
    return ig


def convert(color):
    r, g, b, a, kind = parse_color_to_rgb(color)
    ig = colmod(r, g, b)
    if kind == 'hex6':
        return '#%02x%02x%02x' % (ig, ig, ig)
    if kind == 'hex3':
        ig = ig//16
        return '#%01x%01x%01x' % (ig, ig, ig)
    if a is not None:
        return f'rgba({ig}, {ig}, {ig}, {a})'
    else:
        return f'rgb({ig}, {ig}, {ig})'


def main(file):
    with open(file, encoding='utf8') as svg:
        return colors.sub(lambda color: convert(color.group()), svg.read())


if __name__ == '__main__':
    import sys
    sys.stdout.write(main(sys.argv[1])+'\n')
