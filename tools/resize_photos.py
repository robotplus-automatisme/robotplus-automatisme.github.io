#!/usr/bin/env python3
"""Prepare photos for the website: turn them upright, resize them, remove the camera data
(including GPS position) and save them as web-friendly JPEG files with simple names.

Add photos to a gallery (they are shown in file-name order, new ones go at the end):
    python3 tools/resize_photos.py ~/Desktop/new/*.jpg --to assets/photos/convoyeurs

Replace the picture of a category (page header + homepage card or tile), e.g. "convoyeurs":
    python3 tools/resize_photos.py ~/Desktop/convoyeur.jpg --category convoyeurs

Then run:  python3 tools/update_site.py
Keep your full-resolution originals outside the website folder.
Needs Pillow:  python3 -m pip install Pillow
"""
import argparse, io, os, re, sys, unicodedata

try:
    from PIL import Image, ImageCms, ImageOps
except ImportError:
    sys.exit('Pillow is missing: python3 -m pip install Pillow')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = ('.jpg', '.jpeg', '.png', '.heic', '.tif', '.tiff', '.webp')


def slug(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'photo'


def load(path):
    im = Image.open(path)
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im)
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            if 'srgb' not in ImageCms.getProfileDescription(src).lower():
                im = ImageCms.profileToProfile(im.convert('RGB'), src, ImageCms.createProfile('sRGB'), outputMode='RGB')
        except Exception:
            pass
    return im.convert('RGB')


def save(im, out, max_width=None, max_side=None, quality=80):
    w, h = im.size
    scale = 1.0
    if max_width and w > max_width:
        scale = min(scale, max_width / w)
    if max_side and max(w, h) > max_side:
        scale = min(scale, max_side / max(w, h))
    if scale < 1:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, 'JPEG', quality=quality, optimize=True, progressive=True)   # no EXIF is written
    print(f'  {os.path.relpath(out, ROOT)}  {im.size[0]}x{im.size[1]}  {os.path.getsize(out) // 1024} KB')


def sources(items):
    files = []
    for item in items:
        if os.path.isdir(item):
            files += sorted(os.path.join(item, f) for f in os.listdir(item) if f.lower().endswith(EXTS))
        elif os.path.isfile(item):
            files.append(item)
        else:
            sys.exit(f'not found: {item}')
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('photos', nargs='+', help='photo files or folders')
    ap.add_argument('--to', help='gallery folder, e.g. assets/photos/convoyeurs')
    ap.add_argument('--category', help='page name whose category picture is replaced, e.g. convoyeurs')
    ap.add_argument('--max', type=int, default=1600, help='longest side of gallery photos in pixels (default 1600)')
    args = ap.parse_args()
    files = sources(args.photos)
    if bool(args.to) == bool(args.category):
        sys.exit('give either --to FOLDER or --category NAME')
    if args.category:
        if len(files) != 1:
            sys.exit('--category takes exactly one photo')
        im = load(files[0])
        base = os.path.join(ROOT, 'assets/photos/categories', slug(args.category))
        save(im, base + '.jpg', max_width=1400, quality=80)
        save(im, base + '-thumb.jpg', max_width=800, quality=78)
        return
    folder = os.path.join(ROOT, args.to) if not os.path.isabs(args.to) else args.to
    os.makedirs(folder, exist_ok=True)
    numbers = [int(m.group(1)) for f in os.listdir(folder) if (m := re.match(r'(\d+)-', f))]
    n = max(numbers, default=0)
    for path in files:
        n += 1
        save(load(path), os.path.join(folder, f'{n:02d}-{slug(os.path.splitext(os.path.basename(path))[0])}.jpg'), max_side=args.max)
    print('Now run: python3 tools/update_site.py')


if __name__ == '__main__':
    main()
