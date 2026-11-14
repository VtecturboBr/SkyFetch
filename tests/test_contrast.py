from pathlib import Path
import re


def test_small_text_has_aa_contrast_against_white():
    css = (Path(__file__).resolve().parents[1] / 'static/css/style.css').read_text()
    for selector in ['.search-form input::placeholder', '.meta-label', '.results-footer', '.dataset-note', '.footer-inner']:
        block = re.search(re.escape(selector) + r'\s*\{([^}]+)', css).group(1)
        color = re.search(r'(?:^|;)\s*color:\s*#([0-9a-f]{6})', block).group(1)
        channels = [int(color[i:i+2], 16) / 255 for i in (0, 2, 4)]
        linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels]
        luminance = sum(a*b for a,b in zip(linear, [.2126,.7152,.0722]))
        assert 1.05/(luminance+.05) >= 4.5, selector
