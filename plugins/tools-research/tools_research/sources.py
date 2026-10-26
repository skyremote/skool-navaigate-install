"""The sources a normal web search misses: research papers (OpenAlex), Substack, and Reddit on the member's own app."""
import base64
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from . import config

AGENT = 'aios-tools-research/2.0 (a member research tool)'


class SourceError(RuntimeError):
    pass


def get_json(url, headers=None, data=None, opener=urllib.request.urlopen):
    head = {'User-Agent': AGENT, 'Accept': 'application/json'}
    head.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=head, method='POST' if data else 'GET')
    try:
        with opener(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        raise SourceError('%s answered HTTP %d' % (urllib.parse.urlparse(url).netloc, error.code)) from None
    except urllib.error.URLError as error:
        raise SourceError('Could not reach %s: %s' % (urllib.parse.urlparse(url).netloc, error.reason)) from None
    except json.JSONDecodeError:
        raise SourceError('%s did not return JSON' % urllib.parse.urlparse(url).netloc) from None


def text_of(markup, limit=None):
    plain = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', markup or '', flags=re.S | re.I)
    plain = re.sub(r'<br\s*/?>|</p>|</h\d>|</li>', '\n', plain, flags=re.I)
    plain = html.unescape(re.sub(r'<[^>]+>', ' ', plain))
    plain = '\n'.join(' '.join(line.split()) for line in plain.splitlines())
    plain = re.sub(r'\n{3,}', '\n\n', plain).strip()
    return plain[:limit] if limit else plain


# ---------- research papers: OpenAlex (free, no key) ----------
def papers(query, n=8, get=get_json, env=None, most_cited=False):
    params = {'search': query, 'per-page': str(n)}
    if most_cited:
        params['sort'] = 'cited_by_count:desc'
    email = config.get('OPENALEX_EMAIL', 'openalex_email', env=env)
    if email:
        params['mailto'] = email  # OpenAlex's "polite pool": the member's own address, optional
    data = get('https://api.openalex.org/works?' + urllib.parse.urlencode(params))
    rows = []
    for w in data.get('results', []):
        rows.append({'title': w.get('display_name') or '', 'year': w.get('publication_year'),
                     'cited_by': w.get('cited_by_count', 0), 'doi': w.get('doi') or '',
                     'free_pdf': (w.get('open_access') or {}).get('oa_url') or '',
                     'url': w.get('doi') or w.get('id') or ''})
    return rows


# ---------- Substack (free, no key): read a publication or one post ----------
def substack_base(name_or_url):
    value = name_or_url.strip()
    if '://' not in value:
        return 'https://%s.substack.com' % value if '.' not in value else 'https://' + value.rstrip('/')
    parts = urllib.parse.urlparse(value)
    return '%s://%s' % (parts.scheme, parts.netloc)


def substack_slug(url):
    match = re.search(r'/p/([^/?#]+)', url)
    if not match:
        raise SourceError('That is not a Substack post link (it needs /p/<post>).')
    return match.group(1)


def substack_archive(name_or_url, n=10, get=get_json):
    base = substack_base(name_or_url)
    data = get(base + '/api/v1/archive?' + urllib.parse.urlencode({'sort': 'new', 'limit': n}))
    return [{'title': p.get('title', ''), 'date': (p.get('post_date') or '')[:10], 'paid': p.get('audience') != 'everyone',
             'url': p.get('canonical_url') or '%s/p/%s' % (base, p.get('slug', ''))} for p in data if isinstance(p, dict)]


def substack_post(url, get=get_json, limit=20000):
    data = get(substack_base(url) + '/api/v1/posts/' + substack_slug(url))
    body = text_of(data.get('body_html') or '', limit)
    return {'title': data.get('title', ''), 'date': (data.get('post_date') or '')[:10], 'url': data.get('canonical_url') or url,
            'paid': data.get('audience') != 'everyone', 'text': body or '(no free text: this post is for paid subscribers)'}


# ---------- Reddit: the member's own free Reddit app (app-only OAuth) ----------
NO_REDDIT = ('Reddit needs your own free Reddit app now (unsigned requests are blocked).\n'
             'At reddit.com/prefs/apps choose "create another app", type "script", any redirect URL, then copy the id\n'
             'under the app name and the secret. Then either:\n'
             '  Claude Code: /plugin, tools-research, Configure: "Reddit app id" and "Reddit app secret"\n'
             '  Codex or Cursor: export REDDIT_CLIENT_ID=... and REDDIT_CLIENT_SECRET=... in your shell profile')


def reddit_token(env=None, get=get_json):
    cid = config.get('REDDIT_CLIENT_ID', 'reddit_client_id', env=env)
    secret = config.get('REDDIT_CLIENT_SECRET', 'reddit_client_secret', env=env)
    if not cid or not secret:
        raise SourceError(NO_REDDIT)
    basic = base64.b64encode(('%s:%s' % (cid, secret)).encode()).decode()
    data = get('https://www.reddit.com/api/v1/access_token', headers={'Authorization': 'Basic ' + basic},
               data=b'grant_type=client_credentials')
    if not data.get('access_token'):
        raise SourceError('Reddit did not give a token. Check the app id and secret.')
    return data['access_token']


def reddit_search(query, n=10, period='year', subreddit=None, token=None, get=get_json, env=None):
    token = token or reddit_token(env, get)
    path = '/r/%s/search' % subreddit if subreddit else '/search'
    params = {'q': query, 'limit': n, 'sort': 'relevance', 't': period, 'type': 'link'}
    if subreddit:
        params['restrict_sr'] = 'on'
    data = get('https://oauth.reddit.com%s?%s' % (path, urllib.parse.urlencode(params)), headers={'Authorization': 'bearer ' + token})
    rows = []
    for child in (data.get('data') or {}).get('children', []):
        d = child.get('data') or {}
        rows.append({'title': d.get('title', ''), 'subreddit': d.get('subreddit', ''), 'score': d.get('score', 0),
                     'comments': d.get('num_comments', 0), 'url': 'https://reddit.com' + d.get('permalink', ''), 'id': d.get('id', '')})
    return rows


def reddit_thread(post_id, n=10, token=None, get=get_json, env=None):
    token = token or reddit_token(env, get)
    post_id = re.sub(r'.*/comments/([a-z0-9]+).*', r'\1', post_id)
    data = get('https://oauth.reddit.com/comments/%s?%s' % (post_id, urllib.parse.urlencode({'limit': n, 'sort': 'top', 'depth': 1})),
               headers={'Authorization': 'bearer ' + token})
    post = data[0]['data']['children'][0]['data'] if data else {}
    comments = [c['data'] for c in data[1]['data']['children'] if c.get('kind') == 't1'] if len(data) > 1 else []
    return {'title': post.get('title', ''), 'text': post.get('selftext', ''), 'url': 'https://reddit.com' + post.get('permalink', ''),
            'top_comments': [{'score': c.get('score', 0), 'text': c.get('body', '')} for c in comments[:n]]}
