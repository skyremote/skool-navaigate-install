"""The member's own Composio account: list connected Gmail accounts, and send a reminder to themselves only."""
import json
import urllib.error
import urllib.request

from . import config

BASE = 'https://backend.composio.dev/api/v3'
NO_KEY = ('No Composio API key found.\n'
          'Create a free account at composio.dev, connect your Gmail inside Composio, then copy your API key\n'
          'from the dashboard. Then either:\n'
          '  Claude Code: /plugin, tools-inbox, Configure, paste it as "Composio API key"\n'
          '  Codex or Cursor: export COMPOSIO_API_KEY=... in your shell profile\n'
          'Never paste the key into a chat.')


class ComposioError(RuntimeError):
    pass


def api_key(env=None):
    key = config.get('COMPOSIO_API_KEY', 'composio_api_key', env=env)
    if not key:
        raise ComposioError(NO_KEY)
    return key


def request(method, path, key, body=None, opener=urllib.request.urlopen):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={
        'x-api-key': key, 'Content-Type': 'application/json', 'User-Agent': 'aios-tools-inbox/2.0'})
    try:
        with opener(req, timeout=60) as response:
            return json.loads(response.read().decode() or '{}')
    except urllib.error.HTTPError as error:
        hint = {401: 'the key was refused, or the Gmail connection expired; reconnect it in Composio',
                404: 'Composio retired this address; update the pack'}.get(error.code, 'see the Composio dashboard')
        raise ComposioError('Composio said HTTP %d: %s' % (error.code, hint)) from None
    except urllib.error.URLError as error:
        raise ComposioError('Could not reach Composio: %s' % error.reason) from None


def toolkit_of(item):
    toolkit = item.get('toolkit')
    if isinstance(toolkit, dict):
        return toolkit.get('slug') or toolkit.get('name') or ''
    return toolkit or item.get('appName') or ''


def accounts(key, call=request):
    data = call('GET', '/connected_accounts?limit=100', key)
    rows = []
    for item in data.get('items') or data.get('data') or []:
        rows.append({'id': item.get('id', ''), 'toolkit': str(toolkit_of(item)).lower(),
                     'status': str(item.get('status', '')).upper(), 'user_id': item.get('user_id') or ''})
    return rows


def gmail_account(key, call=request, account_id=None):
    active = [a for a in accounts(key, call) if a['toolkit'] == 'gmail' and a['status'] == 'ACTIVE']
    if account_id:
        active = [a for a in active if a['id'] == account_id]
    if not active:
        raise ComposioError('No ACTIVE Gmail connection in your Composio account. Connect Gmail in Composio first.')
    if len(active) > 1 and not account_id:
        raise ComposioError('More than one Gmail is connected. Pick one with --account <ca_...> (see tools-inbox accounts).')
    return active[0]


def remind(key, subject, body, call=request, account_id=None, to=None):
    """Send one email to the member's own connected address. Anything else is refused."""
    account = gmail_account(key, call, account_id)
    own = account['user_id']
    if '@' not in own:
        raise ComposioError('Composio does not show the Gmail address for this connection, so the reminder cannot '
                            'prove it is going to you. Set the Composio user id to your Gmail address.')
    if to and to.lower() != own.lower():
        raise ComposioError('Refused: reminders only go to your own address (%s). This pack never emails anyone else.' % own)
    result = call('POST', '/tools/execute/GMAIL_SEND_EMAIL', key, {
        'user_id': own, 'connected_account_id': account['id'],
        'arguments': {'recipient_email': own, 'subject': subject, 'body': body, 'is_html': False}})
    if not result.get('successful', result.get('successfull')):
        raise ComposioError('Composio did not send it: ' + str(result.get('error') or 'no reason given'))
    return own
