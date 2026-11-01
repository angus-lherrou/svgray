import re
from typing import Tuple

import colorsys


colors_hex_str = r"(?:#|0x)(?:[a-f0-9]{3}|[a-f0-9]{6})\b"
colors_func_str = r"(?:rgb|hsl)a?\([^)]*\)"

colors_hex = re.compile(colors_hex_str, re.IGNORECASE)
colors_func = re.compile(colors_func_str, re.IGNORECASE)
colors = re.compile(colors_hex_str + r"|" + colors_func_str, re.IGNORECASE)


_number = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?(%|deg)?", re.IGNORECASE)


def _parse_func_args(color: str) -> list:
    """Parse the arguments of rgb()/rgba()/hsl()/hsla() as plain numbers.

    Accepts comma- or space-separated values, percentages, a "deg" unit on the
    hue and a "/" before alpha. Anything else raises ValueError. The arguments
    come from the SVG being converted, which may be untrusted, so they must
    never be evaluated as Python code.
    """
    inner = color[color.index('(') + 1:color.rindex(')')]
    values = []
    for part in re.split(r"[\s,/]+", inner.strip()):
        if not part:
            continue
        m = _number.fullmatch(part)
        if m is None:
            raise ValueError(f'bad color "{color}"')
        number = float(part[:m.start(1)] if m.group(1) else part)
        values.append((number, (m.group(1) or '').lower()))
    return values


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


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
        values = _parse_func_args(color)
        if color[3] == 'a' or len(values) == 4:
            if len(values) != 4:
                raise ValueError(f'bad color "{color}": rgba/hsla need 4 values')
        elif len(values) != 3:
            raise ValueError(f'bad color "{color}": rgb/hsl need 3 values')
        if color.lower().startswith('rgb'):
            r, g, b = (_clamp(v * 2.55 if unit == '%' else v, 0, 255) for v, unit in values[:3])
        else:
            (h, _), (s, _), (l, _) = values[:3]
            r, g, b = (c * 255 for c in colorsys.hls_to_rgb(
                (h % 360) / 360, _clamp(l, 0, 100) / 100, _clamp(s, 0, 100) / 100))
        if len(values) == 4:
            alpha, unit = values[3]
            a = _clamp(alpha / 100 if unit == '%' else alpha, 0, 1)
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
    try:
        r, g, b, a, kind = parse_color_to_rgb(color)
    except ValueError:
        return color  # leave colors we can't parse untouched
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
