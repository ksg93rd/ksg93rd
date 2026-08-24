"""Read/write Markdown files with YAML-subset frontmatter. Canonical format."""
import io
import os
import tempfile

from . import yamlite

DELIM = "---"


class FrontmatterError(ValueError):
    pass


def parse(text):
    """Return (metadata_dict, body_str)."""
    if not text.startswith(DELIM):
        return {}, text
    lines = text.split("\n")
    if lines[0].strip() != DELIM:
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == DELIM:
            head = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1:])
            try:
                meta = yamlite.loads(head) or {}
            except yamlite.YamliteError as exc:
                raise FrontmatterError(str(exc))
            if not isinstance(meta, dict):
                raise FrontmatterError("frontmatter must be a mapping")
            return meta, body.lstrip("\n")
    raise FrontmatterError("unterminated frontmatter block (missing closing '---')")


def render(meta, body):
    head = yamlite.dumps(meta or {})
    body = (body or "").rstrip("\n")
    return "%s\n%s%s\n\n%s\n" % (DELIM, head, DELIM, body)


def read(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return parse(fh.read())


def write_atomic(path, meta, body):
    """Atomic write. Matters doubly inside a synchronized folder."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    if not os.path.isdir(directory):
        os.makedirs(directory)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".vault-tmp-", suffix=".md")
    try:
        with io.open(fd, "w", encoding="utf-8") as fh:
            fh.write(render(meta, body))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return path
