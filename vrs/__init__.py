import base64
import dns.resolver
import json
import logging
import shlex


logger = logging.getLogger('pyvrs')


def resolve(name, resolver='ovon.directory'):
    """Resolve <name>"""
    answers = dns.resolver.resolve(f'{name}.ovon.directory', 'TXT')
    logger.info(f'querying: {answers.qname}')
    return [decode(a) for a in answers]


def decode(rdata):
    txt = rdata.to_text()
    if is_simple(txt):
        return dict(i.split("=") for i in shlex.split(shlex.split(txt)[0]))
    elif is_base64(txt):
        return str(base64.b64decode(txt), 'utf8').strip()
    elif is_json(txt):
        return json.loads(txt)
    else:
        return rdata.strings


def is_simple(s):
    required = ['dest', 'name', 'country']
    return all([r in s for r in required])


def is_base64(s):
    """Return True if input string is base64, false otherwise."""
    s = s.strip("'\"")
    try:
        if isinstance(s, str):
            sb_bytes = bytes(s, 'ascii')
        elif isinstance(s, bytes):
            sb_bytes = s
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False


def is_json(s):
    try:
        json.loads(s)
    except ValueError:
        return False
    return True
