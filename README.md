# svgray
Simple script to convert svg files to grayscale.

The replacement uses a simple regex so if you have text containing SVG color codes in your SVGs, this will replace them, sorry. My first draft of this script used BeautifulSoup and avoided this issue but I decided against requiring external dependencies.

Note: the script does not currently handle _named_ colors; that's planned for the future.

## Installation
- Make sure `python3` is in your `PATH`
- Put `svgray` and `.svgray.py` in the same directory somewhere in your `PATH` or wherever you intend to use it
- `chmod +x svgray`

## Usage
`svgray [-q] FILE`
