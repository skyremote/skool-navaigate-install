"""One source, every platform: check a post pack before anything is scheduled."""
import json
import re

LIMITS = {'twitter/x': 280, 'x': 280, 'twitter': 280, 'bluesky': 300, 'threads': 500}
TITLE_LIMIT = 70
URL = re.compile(r'https?://\S+')
PROMISE = re.compile(r'\b(comment|reply)\b[^.\n]{0,40}\b(and|&)\b[^.\n]{0,40}\b(send|dm|message)\b', re.I)
PLACEHOLDER = re.compile(r'<[^>\n]{2,}>|\[link\]|example\.com|TODO', re.I)

SAMPLE = {
    'source': 'Northwind Bakery kick-off call (fictional, Acme Studio)',
    'posts': [
        {'platform': 'LinkedIn', 'hooks': [
            'Northwind Bakery takes 40 cake orders a week by phone, and half arrive while they are baking.',
            'We fixed a bakery\'s busiest hour with one page, not a new system.',
            'The first version does one thing: celebration cakes, ordered online.'],
         'body': 'So we started with the phone, because that is where the orders get lost.\n\nThe first version takes online orders for celebration cakes only, and the prices stay the same as the shop.'},
        {'platform': 'Twitter/X', 'hooks': [
            '40 cake orders a week by phone. Half while baking. So we built one page.',
            'One bakery, one booking page, cakes only.',
            'The fix was smaller than the problem.'],
         'body': 'Northwind Bakery took 40 cake orders a week by phone. The first version of their booking page takes celebration cakes online, nothing else.'},
        {'platform': 'YouTube', 'hooks': ['A booking page for a busy bakery', 'Cakes only: the first version', 'Fixing the phone first'],
         'title': 'A booking page for a busy bakery', 'body': 'How Acme Studio scoped the first version of Northwind Bakery\'s booking page.'},
    ],
}


def check(pack):
    problems = []
    posts = pack.get('posts') or []
    if not posts:
        return ['No posts in the pack.']
    for post in posts:
        name = str(post.get('platform', '?'))
        key = name.lower()
        hooks = post.get('hooks') or []
        body = post.get('body') or ''
        if len(hooks) < 3:
            problems.append('%s: give three hook options, not %d.' % (name, len(hooks)))
        if not body.strip():
            problems.append('%s: the post body is empty.' % name)
        limit = LIMITS.get(key)
        if limit:
            for text in hooks + [body]:
                if len(text) > limit:
                    problems.append('%s: %d characters, over the %d limit: "%s..."' % (name, len(text), limit, text[:40]))
        if key == 'youtube':
            title = post.get('title') or ''
            if not title or len(title) > TITLE_LIMIT:
                problems.append('YouTube: a title under %d characters is required.' % TITLE_LIMIT)
        for text in hooks + [body, post.get('title') or '']:
            if PLACEHOLDER.search(text):
                problems.append('%s: a placeholder or made-up link is still in the copy.' % name)
                break
        if PROMISE.search(body) and not post.get('resource_url'):
            problems.append('%s: the post promises to send something for a comment. Add the verified resource_url '
                            'and a working reply route, or drop the promise.' % name)
    return problems


def load(path):
    with open(path) as handle:
        return json.load(handle)
