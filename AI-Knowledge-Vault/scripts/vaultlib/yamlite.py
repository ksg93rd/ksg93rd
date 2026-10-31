"""yamlite - a deliberately small, dependency-free YAML subset reader/writer.

WHY THIS EXISTS
---------------
The vault must run on a stock macOS Python with no `pip install` step, and
PyYAML is not part of the standard library. Rather than make the whole vault
fragile, we support only the small, unambiguous YAML subset the vault actually
writes, and we write files in exactly that subset.

SUPPORTED
  key: scalar                 (str, int, float, true/false, null/~, quoted)
  key:                        followed by an indented block map
  key:                        followed by "- " list items (scalars or maps)
  key: []                     empty inline list
  key: {}                     empty inline map
  key: [a, b, c]              simple inline list of scalars
  # comments (whole line, or trailing " #" outside quotes)

NOT SUPPORTED (by design; raises YamliteError)
  anchors/aliases, multi-line block scalars, flow maps with content,
  multiple documents, complex keys, tags.
"""

class YamliteError(ValueError):
    pass


_TRUE = ("true", "yes", "on")
_FALSE = ("false", "no", "off")
_NULL = ("null", "~", "")


def _strip_comment(line):
    out = []
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < len(line):
                out.append(line[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
        else:
            if ch in ("'", '"'):
                quote = ch
                out.append(ch)
            elif ch == "#" and (not out or out[-1] in (" ", "\t")):
                break
            else:
                out.append(ch)
        i += 1
    return "".join(out).rstrip()


def parse_scalar(raw):
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        body = s[1:-1]
        if s[0] == '"':
            body = body.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
        else:
            body = body.replace("''", "'")
        return body
    low = s.lower()
    if low in _NULL:
        return None
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(p) for p in _split_inline(inner)]
    if s in ("{}",):
        return {}
    try:
        if s.startswith(("0x", "-0x")):
            raise ValueError
        return int(s)
    except ValueError:
        pass
    try:
        f = float(s)
        # keep bare version-like or id-like strings as strings
        if s.lower() in ("nan", "inf", "-inf"):
            return s
        return f
    except ValueError:
        pass
    return s


def _split_inline(inner):
    parts, buf, quote, depth = [], [], None, 0
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch == "[":
            depth += 1
            buf.append(ch)
        elif ch == "]":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip() != ""]


def _lines(text):
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("#"):
            continue
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if "\t" in line[:indent]:
            raise YamliteError("line %d: tabs are not allowed for indentation" % n)
        out.append((n, indent, line.strip()))
    return out


def loads(text):
    """Parse a YAML-subset document into python data. Returns {} for empty."""
    items = _lines(text or "")
    if not items:
        return {}
    value, idx = _parse_block(items, 0, items[0][1])
    if idx != len(items):
        raise YamliteError("line %d: unexpected content %r" % (items[idx][0], items[idx][2]))
    return value


def _parse_block(items, idx, indent):
    if items[idx][2].startswith("- "):
        return _parse_list(items, idx, indent)
    return _parse_map(items, idx, indent)


def _parse_list(items, idx, indent):
    result = []
    while idx < len(items):
        n, ind, line = items[idx]
        if ind < indent:
            break
        if ind > indent:
            raise YamliteError("line %d: unexpected indentation in list" % n)
        if not line.startswith("- "):
            if line == "-":
                raise YamliteError("line %d: empty list item is not supported" % n)
            break
        body = line[2:].strip()
        idx += 1
        if ":" in body and not _is_scalar_with_colon(body):
            key, _, rest = body.partition(":")
            item = {}
            rest = rest.strip()
            child_indent = ind + 2
            if rest:
                item[key.strip()] = parse_scalar(rest)
            else:
                if idx < len(items) and items[idx][1] > ind:
                    sub, idx = _parse_block(items, idx, items[idx][1])
                    item[key.strip()] = sub
                else:
                    item[key.strip()] = None
            while idx < len(items) and items[idx][1] >= child_indent and not items[idx][2].startswith("- "):
                sub, idx = _parse_map(items, idx, items[idx][1])
                item.update(sub)
                break
            result.append(item)
        else:
            result.append(parse_scalar(body))
    return result, idx


def _is_scalar_with_colon(body):
    """'https://x' or a quoted string is a scalar even though it contains ':'."""
    b = body.strip()
    if b[:1] in ("'", '"'):
        return True
    key, sep, rest = b.partition(":")
    if not sep:
        return True
    if rest and not rest.startswith(" "):
        return True
    if " " in key.strip():
        return False
    return False


def _parse_map(items, idx, indent):
    result = {}
    while idx < len(items):
        n, ind, line = items[idx]
        if ind < indent:
            break
        if ind > indent:
            raise YamliteError("line %d: unexpected indentation %r" % (n, line))
        if line.startswith("- "):
            break
        if ":" not in line:
            raise YamliteError("line %d: expected 'key: value', got %r" % (n, line))
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        idx += 1
        if rest:
            result[key] = parse_scalar(rest)
            continue
        if idx < len(items) and items[idx][1] > ind:
            sub, idx = _parse_block(items, idx, items[idx][1])
            result[key] = sub
        elif idx < len(items) and items[idx][1] == ind and items[idx][2].startswith("- "):
            sub, idx = _parse_list(items, idx, ind)
            result[key] = sub
        else:
            result[key] = None
    return result, idx


_NEEDS_QUOTE_PREFIX = ("-", "?", ":", ",", "[", "]", "{", "}", "#", "&", "*", "!",
                       "|", ">", "'", '"', "%", "@", "`")


def dump_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return repr(value)
    s = str(value)
    if s == "":
        return '""'
    if "\n" in s:
        return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    if s[0] in _NEEDS_QUOTE_PREFIX or s[-1] in (" ",) or s.strip() != s:
        return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')
    if s.lower() in _TRUE + _FALSE + ("null", "~"):
        return '"%s"' % s
    try:
        float(s)
        return '"%s"' % s
    except ValueError:
        pass
    if ": " in s or s.endswith(":"):
        return '"%s"' % s.replace('"', '\\"')
    return s


def dumps(data, indent=0):
    """Serialize python data to the supported YAML subset."""
    pad = " " * indent
    out = []
    if isinstance(data, dict):
        if not data:
            return pad + "{}\n" if indent else ""
        for key, value in data.items():
            if isinstance(value, dict):
                if not value:
                    out.append("%s%s: {}\n" % (pad, key))
                else:
                    out.append("%s%s:\n" % (pad, key))
                    out.append(dumps(value, indent + 2))
            elif isinstance(value, (list, tuple)):
                if not value:
                    out.append("%s%s: []\n" % (pad, key))
                else:
                    out.append("%s%s:\n" % (pad, key))
                    out.append(dumps(list(value), indent + 2))
            else:
                out.append("%s%s: %s\n" % (pad, key, dump_scalar(value)))
        return "".join(out)
    if isinstance(data, (list, tuple)):
        for item in data:
            if isinstance(item, dict):
                if not item:
                    out.append("%s- {}\n" % pad)
                    continue
                first = True
                for key, value in item.items():
                    prefix = "%s- " % pad if first else "%s  " % pad
                    first = False
                    if isinstance(value, (dict, list, tuple)) and value:
                        out.append("%s%s:\n" % (prefix, key))
                        out.append(dumps(value if isinstance(value, dict) else list(value), indent + 4))
                    elif isinstance(value, (dict, list, tuple)):
                        out.append("%s%s: %s\n" % (prefix, key, "{}" if isinstance(value, dict) else "[]"))
                    else:
                        out.append("%s%s: %s\n" % (prefix, key, dump_scalar(value)))
            else:
                out.append("%s- %s\n" % (pad, dump_scalar(item)))
        return "".join(out)
    return pad + dump_scalar(data) + "\n"
