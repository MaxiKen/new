#!/usr/bin/env python3
"""Extract / replace a single verse section inside expanded/NNN.md without touching the rest.

Usage:
    section.py get 007:18                  # print the section to stdout
    section.py get 007:18 out/18.md        # write the section to a file
    section.py put 007:18 out/18.md        # replace the section with the file's contents
    section.py put 007:18 out/18.md --dry  # show what would change

A section runs from its `## Sūrah ... C:V` heading up to (not including) the next
`## Sūrah` heading. The heading of the replacement file is ignored; the original
heading and the `---` separators around the section are preserved.
"""
import re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEAD = re.compile(r'^## Sūrah .+? (\d+):(\d+)\s*$')

def locate(lines, ch, v):
    idx = [i for i, l in enumerate(lines) if HEAD.match(l.strip())]
    for k, i in enumerate(idx):
        m = HEAD.match(lines[i].strip())
        if int(m.group(1)) == ch and int(m.group(2)) == v:
            end = idx[k + 1] if k + 1 < len(idx) else len(lines)
            return i, end
    raise SystemExit('verse not found: %d:%d' % (ch, v))

def main():
    cmd, ref = sys.argv[1], sys.argv[2]
    ch, v = (int(x) for x in ref.split(':'))
    path = os.path.join(ROOT, 'expanded', '%03d.md' % ch)
    lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    i, end = locate(lines, ch, v)
    if cmd == 'get':
        text = '\n'.join(lines[i:end]).rstrip('\n') + '\n'
        if len(sys.argv) > 3:
            open(sys.argv[3], 'w', encoding='utf-8').write(text)
            print('wrote %s (%d lines)' % (sys.argv[3], text.count('\n')))
        else:
            sys.stdout.write(text)
    elif cmd == 'put':
        new = open(sys.argv[3], encoding='utf-8').read().replace('\r\n', '\n').rstrip('\n') + '\n'
        # keep the canonical heading from the original file
        new = HEAD.sub(lines[i], new, count=1) if HEAD.match(new.split('\n')[0].strip()) else lines[i] + '\n' + new
        if '--dry' in sys.argv:
            print('would replace lines %d-%d (%d -> %d lines)' % (i + 1, end, end - i, new.count('\n')))
            return
        out = lines[:i] + new.split('\n')[:-1] + lines[end:]
        open(path, 'w', encoding='utf-8').write('\n'.join(out))
        print('replaced %03d.md %d:%d: lines %d-%d, now %d lines (file %d -> %d lines)'
              % (ch, ch, v, i + 1, end, new.count('\n'), len(lines), len(out)))
    else:
        raise SystemExit(__doc__)

def split_parts(block):
    """Return (prefix, suffix) around the body: prefix keeps the heading, the
    translation blockquote and the **Expanded Commentary** marker; suffix keeps
    the trailing separator lines."""
    lines = block
    marker = None
    for i, l in enumerate(lines):
        if l.strip() == '**Expanded Commentary**':
            marker = i
            break
    if marker is None:
        raise SystemExit('no **Expanded Commentary** marker in section')
    j = len(lines)
    while j > marker + 1 and lines[j - 1].strip() in ('', '---'):
        j -= 1
    return lines[:marker + 1], lines[j:]


def main_body():
    ref = sys.argv[2]
    ch, v = (int(x) for x in ref.split(':'))
    src = sys.argv[3]
    path = os.path.join(ROOT, 'expanded', '%03d.md' % ch)
    lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    i, end = locate(lines, ch, v)
    prefix, suffix = split_parts(lines[i:end])
    body = open(src, encoding='utf-8').read().replace('\r\n', '\n').strip('\n').split('\n')
    body = [b for b in body if b.strip() != '---']
    while body and body[-1].strip() == '':
        body.pop()
    out = lines[:i] + prefix + [''] + body + [''] + (suffix or ['---']) + lines[end:]
    if '--dry' in sys.argv:
        print('would rewrite body of %d:%d (%d body lines)' % (ch, v, len(body)))
        return
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    print('body replaced %03d.md %d:%d (file %d -> %d lines)' % (ch, ch, v, len(lines), len(out)))


if sys.argv[1] == 'putbody':
    main_body()
elif sys.argv[1] in ('get', 'put'):
    main()
else:
    main()
