#!/usr/bin/env python3
"""Corpus census: depth and duplication ground truth for expanded/.

Answers the two open audit questions with measured numbers, not estimates:

  Group A (depth)       -- per-file section length distribution, and for every
                           thin section whether initial/ carries source
                           apparatus to rebuild from (abbreviation-aware).
  Group B (duplication) -- sections scoring >= a 10-gram duprate threshold.

Usage:
    census.py                     # summary tables for the whole corpus
    census.py --thin 400          # list every section under 400 words
    census.py --dup 0.030         # list every section at/above the duprate
    census.py --sura 37           # restrict to one file
    census.py --json out.json     # machine-readable dump
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VH = re.compile(r'^## Sūrah (.+?) (\d+):(\d+)$')
EC = '**Expanded Commentary**'


# --------------------------------------------------------------------------
# expanded/ parsing
# --------------------------------------------------------------------------
def sections_of(path):
    """Return {verse: {'line': n, 'translation': str, 'body': str, 'words': int}}.

    The body is the section text after the ``**Expanded Commentary**`` marker,
    with fully-bold mini-heading lines retained -- dropping them under-counts
    the verse's own vocabulary (the bug fixed in check_offtopic.py).
    """
    lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    idx = [i for i, l in enumerate(lines) if VH.match(l)]
    out = {}
    for k, i in enumerate(idx):
        v = int(VH.match(lines[i]).group(3))
        e = idx[k + 1] if k + 1 < len(idx) else len(lines)
        blk = lines[i + 1:e]
        tr = ''
        for l in blk:
            m = re.match(r'^> \*\*(.+?)\*\*\s*$', l.strip())
            if m:
                tr = m.group(1)
                break
        # body starts after the Expanded Commentary marker
        try:
            j = blk.index(EC) + 1
        except ValueError:
            j = 0
        body = '\n'.join(blk[j:])
        # stop before the trailing canonical end block
        body = re.split(r'^---\s*$', body, flags=re.M)[0]
        # Whole-section text, heading through body, with the trailing rule
        # dropped. This is the span check_degeneracy.py scores, and it is the
        # span the Group B duplication figures in REMAINING_ISSUES.md are
        # measured on -- a body-only span gives materially different counts
        # (151 vs 269 at the 0.030 gate) and must not be substituted silently.
        whole = '\n'.join(l for l in lines[i:e] if l.strip() != '---')
        out[v] = {
            'line': i + 1,
            'translation': tr,
            'body': body,
            'whole': whole,
            'words': len(re.findall(r"[\w'’\-]+", body)),
        }
    return out


# --------------------------------------------------------------------------
# initial/ parsing (abbreviation-aware, per REMAINING_ISSUES.md A1)
# --------------------------------------------------------------------------
def source_notes(sura):
    """Return {verse: [(tag, note_text), ...]} from initial/<sura>.md."""
    path = os.path.join(ROOT, 'initial', f'{sura:03d}.md')
    if not os.path.exists(path):
        return {}
    lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    notes = {}
    i = 0
    while i < len(lines):
        m = re.match(r'^\*\*(\d+)(?:[–-](\d+))?\*\*\s*(.*)$', lines[i])
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            # **124-28** means 124-128; restore elided leading digits or the
            # range inverts and the note is silently dropped.
            if b < a:
                sa, sb = str(a), str(b)
                b = int(sa[:len(sa) - len(sb)] + sb)
            buf = [m.group(3).strip()]
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not re.match(r'^\*\*\d', lines[i])
                   and not lines[i].startswith(('>', '***', '#'))):
                buf.append(lines[i].strip())
                i += 1
            text = ' '.join(x for x in buf if x)
            tag = f'{a}–{b}' if b > a else str(a)
            for v in range(a, b + 1):
                notes.setdefault(v, []).append((tag, text))
        else:
            i += 1
    return notes


# --------------------------------------------------------------------------
# duplication (10-gram duprate, same measure as check_degeneracy.py)
# --------------------------------------------------------------------------
def duprate(text, n=10):
    """Fraction of 10-gram positions that duplicate an earlier position.

    ``text`` must be the WHOLE section (heading through body, trailing rule
    dropped) to match check_degeneracy.py and the Group B figures. Sections
    under 80 tokens score 0.0.
    """
    words = re.findall(r"[\w'’\-]+", text.lower())
    if len(words) < 80:
        return 0.0, 0, None
    grams = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
    if not grams:
        return 0.0, 0, None
    c = collections.Counter(grams)
    dupes = sum(v - 1 for v in c.values() if v > 1)
    worst = max(c.items(), key=lambda kv: kv[1])
    worst_gram = ' '.join(worst[0]) if worst[1] > 1 else None
    return dupes / len(grams), dupes, worst_gram


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sura', type=int)
    ap.add_argument('--thin', type=int, help='list sections under N words')
    ap.add_argument('--dup', type=float, help='list sections at/above this duprate')
    ap.add_argument('--json')
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, 'expanded', '*.md')))
    if args.sura:
        files = [f for f in files if os.path.basename(f) == f'{args.sura:03d}.md']

    rows, thin_rows, dup_rows = [], [], []
    for f in files:
        name = os.path.basename(f)
        sura = int(name[:3])
        secs = sections_of(f)
        notes = source_notes(sura)
        ws = sorted(s['words'] for s in secs.values())
        if not ws:
            continue
        rows.append({
            'file': name, 'sura': sura, 'sections': len(ws),
            'min': ws[0], 'median': int(statistics.median(ws)), 'max': ws[-1],
            'words': sum(ws),
            'under260': sum(1 for w in ws if w < 260),
            'under400': sum(1 for w in ws if w < 400),
        })
        for v in sorted(secs):
            s = secs[v]
            nn = notes.get(v, [])
            groundable = bool(nn)
            if args.thin is not None and s['words'] < args.thin:
                thin_rows.append({
                    'file': name, 'verse': v, 'line': s['line'],
                    'words': s['words'], 'groundable': groundable,
                    'note_tag': nn[0][0] if nn else None,
                    'note_words': len(re.findall(r"[\w'’\-]+", ' '.join(t for _, t in nn))),
                    'translation': s['translation'],
                })
            sc, dupes, gram = duprate(s['whole'])
            if args.dup is not None and sc >= args.dup:
                dup_rows.append({
                    'file': name, 'verse': v, 'line': s['line'],
                    'words': s['words'], 'duprate': round(sc, 4),
                    'dupes': dupes, 'worst': gram,
                })

    rows.sort(key=lambda r: r['median'])
    total_sections = sum(r['sections'] for r in rows)
    total_words = sum(r['words'] for r in rows)

    print(f'files: {len(rows)}   sections: {total_sections}   words: {total_words:,}')
    print(f'corpus-wide: {sum(r["under260"] for r in rows)} sections < 260 w, '
          f'{sum(r["under400"] for r in rows)} sections < 400 w\n')

    if args.thin is not None:
        g = sum(1 for r in thin_rows if r['groundable'])
        print(f'--- thin sections (< {args.thin} w): {len(thin_rows)} '
              f'-- groundable {g}, ungroudable {len(thin_rows) - g} ---')
        for r in thin_rows:
            flag = '' if r['groundable'] else '  UNGROUNDED'
            print(f"  {r['file']} v{r['verse']:<4} {r['words']:>4} w "
                  f"note[{r['note_tag']}] {r['note_words']} w{flag}")

    if args.dup is not None:
        byfile = collections.Counter(r['file'] for r in dup_rows)
        print(f'\n--- duplication >= {args.dup}: {len(dup_rows)} sections '
              f'in {len(byfile)} files ---')
        for fn, c in byfile.most_common():
            worst = max((r for r in dup_rows if r['file'] == fn),
                        key=lambda r: r['duprate'])
            print(f"  {fn}: {c:>3}   worst {worst['duprate']:.3f} (v{worst['verse']})")
        for r in sorted(dup_rows, key=lambda r: -r['duprate'])[:15]:
            print(f"\n  {r['file']} v{r['verse']}  {r['duprate']:.3f}  "
                  f"{r['words']} w\n     \"{r['worst']}\"")

    if not args.thin and not args.dup:
        print('--- depth, lowest median first ---')
        print(f"{'file':<10}{'sec':>5}{'min':>6}{'med':>6}{'max':>6}"
              f"{'words':>10}{'<260':>6}{'<400':>6}")
        for r in rows[:20]:
            print(f"{r['file']:<10}{r['sections']:>5}{r['min']:>6}{r['median']:>6}"
                  f"{r['max']:>6}{r['words']:>10,}{r['under260']:>6}{r['under400']:>6}")

    if args.json:
        json.dump({'files': rows, 'thin': thin_rows, 'dup': dup_rows},
                  open(args.json, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(f'\nwrote {args.json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
