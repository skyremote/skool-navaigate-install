"""A fictional sample: Acme Studio's Q3 client review, with its own brand file and logo.

Every name and number here is made up. The logo and the photo stand-in are drawn by this script,
so there is nothing to licence.
"""
import json
from pathlib import Path

DECK = """---
title: Acme Studio: Q3 client review
author: Acme Studio
---
[title]
# Q3 client review
## Acme Studio for Northwind Bakery, October 2026

---
[bullets]
# What we set out to do
- Get more people to book a table online
- Make the menu readable on a phone
- Cut the time staff spend on the phone taking bookings
notes: Remind them these were their three goals from the July kick-off.

---
[stat]
# What changed in twelve weeks
- 38% :: More online bookings
- 2.1 s :: Menu page load on a phone
- 6 h :: Staff phone time saved each week
source: Northwind booking system and Acme analytics, July to September 2026 (fictional sample data)

---
[bars]
# Bookings by channel, September
- Website :: 412
- Phone :: 186
- Walk-in :: 95
- Partner apps :: 61
source: Northwind booking system, September 2026 (fictional sample data)

---
[two-column]
# What worked, and what did not
### Worked
- The one-page booking form
- Photos of real dishes on the menu
### Did not
- The loyalty pop-up: people closed it
- Saturday slots still sell out by Wednesday

---
[image]
# The new booking page
The form now asks four questions instead of eleven, and it remembers returning guests.
![The booking page on a phone, sample image](images/booking-page.png)

---
[quote]
# From the floor
> We stopped missing calls at lunch, and the Friday rush is calmer.
-- Priya, front of house, Northwind Bakery (fictional)

---
[section]
# Next quarter
## Three proposals for October to December

---
[bullets]
# What we propose
- Add a waiting list for sold-out Saturday slots
- Replace the pop-up with a thank-you email after the visit
- Test a lunch pre-order for office groups
notes: Ask which one they want first. Do not price them on the call.

---
[closing]
# Thank you
## hello@acme-studio.example | acme-studio.example
"""

BRAND = {
    'name': 'Acme Studio',
    'footer': 'Acme Studio | Q3 client review | Sample deck',
    'colours': {'background': '#FBFAF7', 'text': '#1F2328', 'muted': '#5B6470', 'accent': '#C2410C',
                'accent_text': '#FFFFFF', 'surface': '#F1EEE8'},
    'fonts': {'heading': 'Georgia', 'body': 'Arial', 'heading_file': '', 'body_file': ''},
    'logo': 'acme-logo.png',
}


def _font(size):
    from PIL import ImageFont
    for path in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf'):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def logo(path):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (720, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 30, 180, 210], radius=36, fill=(194, 65, 12, 255))
    d.polygon([(50, 175), (90, 65), (130, 175)], fill=(255, 255, 255, 255))
    d.text((215, 70), 'Acme Studio', font=_font(84), fill=(31, 35, 40, 255))
    im.save(path)


def phone_image(path):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (900, 1200), (241, 238, 232))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([220, 80, 680, 1120], radius=60, fill=(31, 35, 40))
    d.rounded_rectangle([245, 150, 655, 1050], radius=20, fill=(255, 255, 255))
    d.text((280, 190), 'Book a table', font=_font(44), fill=(31, 35, 40))
    for i, label in enumerate(('Date', 'Time', 'Guests', 'Name')):
        y = 290 + i * 150
        d.text((280, y), label, font=_font(26), fill=(91, 100, 112))
        d.rounded_rectangle([280, y + 40, 620, y + 110], radius=12, outline=(200, 196, 188), width=3)
    d.rounded_rectangle([280, 910, 620, 990], radius=40, fill=(194, 65, 12))
    d.text((360, 928), 'Book now', font=_font(34), fill=(255, 255, 255))
    im.save(path)


def make(folder):
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise ValueError('The sample needs Pillow for its logo: python3 -m pip install --user Pillow')
    folder = Path(folder).expanduser().resolve()
    if (folder / 'deck.md').exists():
        raise ValueError('A deck already exists in %s. Choose an empty folder.' % folder)
    (folder / 'images').mkdir(parents=True, exist_ok=True)
    (folder / 'deck.md').write_text(DECK)
    (folder / 'brand.json').write_text(json.dumps(BRAND, indent=2) + '\n')
    logo(folder / 'acme-logo.png')
    phone_image(folder / 'images/booking-page.png')
    return folder


STARTER = """---
title: {title}
---
[title]
# {title}
## {name}, {month}

---
[bullets]
# The one point of this slide
- First thing to say
- Second thing to say
notes: What you will say out loud.

---
[stat]
# A number that matters
- 42% :: What the number means
source: Whose figures, and when

---
[closing]
# Thank you
## your contact line
"""
