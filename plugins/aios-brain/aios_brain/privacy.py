"""Best-effort credential redaction before storage and safe subprocess environments."""
import os
import re

_PROVIDER = re.compile(r'\b(?:sk-[A-Za-z0-9_-]{8,}|sk_(?:live|test)_[A-Za-z0-9]+|xai-[A-Za-z0-9_-]{8,}|sd_[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]{8,}|AKIA[A-Z0-9]{16})\b')
_JWT = re.compile(r'\beyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\b')
_FIELD = r'(?:[A-Za-z0-9_]*(?:api[_-]?key|token|secret|password|credential)[A-Za-z0-9_]*)'
_QUOTED = re.compile(r'(?i)(\b'+_FIELD+r'["\']?\s*[:=]\s*)(["\'])([^\r\n]*?)\2')
_ASSIGN = re.compile(r'(?i)(\b'+_FIELD+r'["\']?\s*[:=]\s*)(?!["\'])([^\s,;"\'<>]+)')
_BEARER = re.compile(r'(?i)\bBearer[ \t]+[A-Za-z0-9._~+/=-]+')
_PRIVATE = re.compile(r'-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----.*?-----END (?:[A-Z ]*PRIVATE KEY)-----',re.S)


def redact(text):
    if not isinstance(text,str):
        return text
    for name,value in os.environ.items():
        if re.search(r'(?:TOKEN|API_KEY|SECRET|PASSWORD)$',name) and len(value)>=8:
            text=text.replace(value,'[REDACTED]')
    text=_PRIVATE.sub('[REDACTED PRIVATE KEY]',text)
    text=_PROVIDER.sub('[REDACTED]',text)
    text=_JWT.sub('[REDACTED]',text)
    text=_BEARER.sub('Bearer [REDACTED]',text)
    text=_QUOTED.sub(lambda m:m[1]+m[2]+'[REDACTED]'+m[2],text)
    return _ASSIGN.sub(lambda m:m[1]+'[REDACTED]',text)


def subprocess_env(subscription=False):
    allowed={'HOME','PATH','TMPDIR','TMP','TEMP','LANG','LC_ALL','LC_CTYPE','TERM',
             'XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','SSL_CERT_FILE','SSL_CERT_DIR'}
    if subscription:
        allowed.update({'CLAUDE_CONFIG_DIR','CLAUDE_CODE_OAUTH_TOKEN'})
    return {key:value for key,value in os.environ.items() if key in allowed}
