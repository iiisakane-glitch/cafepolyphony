"""Prepare the supplied photos without changing the original files."""
from pathlib import Path
from PIL import Image, ImageOps
import io
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'img' / 'web'
OUT.mkdir(parents=True, exist_ok=True)
ARCHIVE = Path.home() / 'Downloads' / 'cafepolyphony_website_images.zip'

def save_pair(image, name, width=1200):
    image = ImageOps.exif_transpose(image).convert('RGB')
    image.thumbnail((width, 1600), Image.Resampling.LANCZOS)
    image.save(OUT / f'{name}.webp', quality=83, method=6)
    image.save(OUT / f'{name}.jpg', quality=86, optimize=True, progressive=True)

with zipfile.ZipFile(ARCHIVE) as archive:
    selected = {
        '02_weekly_lunch/weekly_20261109_13_source': 'weekly-20261109',
        '04_event_nishiku_matsuri/product_reference_01': 'financiers',
        '04_event_nishiku_matsuri/event_photo_01': 'community-event',
    }
    for source, name in selected.items():
        for ext in ('webp', 'jpg'):
            (OUT / f'{name}.{ext}').write_bytes(archive.read(f'website_images/{source}.{ext}'))
    (OUT / 'ogp-financiers.jpg').write_bytes(archive.read('website_images/05_ogp/ogp_financier_1200x630.jpg'))
    # Use just the food photograph, excluding the dated story's opening hours.
    bento = Image.open(io.BytesIO(archive.read('website_images/03_bento_examples/local_20261105_yurinchi.jpg')))
    save_pair(bento.crop((40, 425, 500, 890)), 'bento', 700)

save_pair(Image.open(ROOT / 'img/lunch-hamburg.jpg'), 'lunch', 1000)
save_pair(Image.open(ROOT / 'img/IMG_5886.jpg').crop((0, 330, 525, 920)), 'chiffon', 700)
save_pair(Image.open(ROOT / 'img/main0512.jpg'), 'storefront', 1000)
save_pair(Image.open(ROOT / 'img/matcha-parfait.png'), 'matcha-parfait', 1055)
save_pair(Image.open(ROOT / 'img/menu-baked.png'), 'baked-menu', 1000)
save_pair(Image.open(ROOT / 'img/IMG_5886.jpg'), 'cafe-menu', 1055)
save_pair(Image.open(ROOT / 'img/IMG_5887.jpg'), 'lunch-menu', 1055)

for path in sorted(OUT.glob('*.webp')):
    print(f'{path.name}: {path.stat().st_size:,} bytes')
