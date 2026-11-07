"""Check the static site's local links, metadata and image delivery."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import json

ROOT = Path(__file__).resolve().parents[1]
soup = BeautifulSoup((ROOT / 'index.html').read_text(encoding='utf-8'), 'html.parser')
ids = [element['id'] for element in soup.select('[id]')]
assert len(ids) == len(set(ids)), 'Duplicate IDs'
assert len(soup.select('h1')) == 1, 'Expected one main heading'
for element in soup.select('a[href]'):
    href = element['href']
    if href.startswith('#'):
        assert href[1:] in ids, f'Missing anchor: {href}'
    if element.get('target') == '_blank':
        assert 'noopener' in element.get('rel', []), href
for attribute in ('src', 'href', 'srcset'):
    for element in soup.select(f'[{attribute}]'):
        value = element[attribute]
        if not value.startswith(('http:', 'https:', '#', 'tel:', 'mailto:')):
            assert (ROOT / value.split('?')[0]).is_file(), f'Missing asset: {value}'
for element in soup.select('img'):
    assert element.has_attr('alt'), 'Missing alt text'
    assert element.has_attr('width') and element.has_attr('height'), element['src']
    if element['src'].endswith('.svg'):
        continue
    with Image.open(ROOT / element['src']) as image:
        assert image.size == (int(element['width']), int(element['height'])), element['src']
json.loads(soup.select_one('script[type="application/ld+json"]').string)
assert Image.open(ROOT / 'img/web/ogp-financiers.jpg').size == (1200, 630)
assert soup.select_one('[data-line-link]')['href'] == 'https://lin.ee/HF5uIlw'
for selector in ('.header-line', '.line-banner .button', '.lunch-discovery .button', '.contact-actions .line-button', '.mobile-quick-links .quick-line'):
    assert soup.select_one(selector)['href'] == 'https://lin.ee/HF5uIlw', selector
for selector in ('.hero-actions .hotpepper-button', '.access-hotpepper', '.mobile-quick-links .quick-hotpepper'):
    assert soup.select_one(selector)['href'] == 'https://www.hotpepper.jp/strJ004612649/', selector
assert soup.select_one('#news h2').get_text(strip=True) == 'お知らせ'
assert len(soup.select('#news .news-row')) == 7
assert soup.select_one('#community .event-story')
sections = [section.get('id') for section in soup.select('main > section')]
assert sections.index('weekly-lunch') < sections.index('news') < sections.index('menu')
assert not soup.select('#weekly-content, #weekly-expired, [data-weekly-heading]')
assert soup.select_one('.lunch-discovery a[href="https://x.com/cafe_polyphony"]')
assert soup.select_one('.lunch-discovery a[href="https://www.instagram.com/cafe_polyphony/"]')
assert '掲載記録' in soup.select_one('.lunch-archive summary').get_text()
assert '南堀江' in soup.title.text and 'GRAND OPEN' not in soup.title.text
assert 'に誕生する' not in soup.select_one('meta[name="description"]')['content']
assert 'Patishie' not in soup.get_text()
assert '夜の貸し切りイベントの予約も承っています' not in soup.get_text()
for picture in soup.select('picture'):
    assert picture.select_one('source[type="image/webp"]')
    assert picture.select_one('img[src$=".jpg"]')
print('PASS: assets, anchors, images, metadata, prominent LINE / Hot Pepper links, independent news list, evergreen lunch and dated archive')
original = (ROOT / 'img/matcha-parfait.png').stat().st_size
optimized = (ROOT / 'img/web/matcha-parfait.webp').stat().st_size
print(f'Parfait: {original:,} -> {optimized:,} bytes ({1 - optimized / original:.1%} smaller)')
