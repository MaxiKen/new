#!/usr/bin/env python3
"""Normalize expanded/*.md to the confirmed-correct format of expanded/001.md.

Strategy: read -> clean -> parse into (preamble, [verse sections]) -> reserialize canonically.
Never mutates 001.md.
"""
import os, re, sys, json, collections

ROOT = "/home/user/new"; EXP = os.path.join(ROOT, "expanded")
ARABIC = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
EC   = '**Expanded Commentary**'
SMC  = re.compile(r'^>\s*\*\*\[System Memory Check\]\*\*')
VH   = re.compile(r'^##\s+Sūra[th]\s+(.+?)\s*\[?(\d+):(\d+)\]?\s*$')
ENDM = re.compile(r'^\*\*\[End of the commentary on (.+?)\]\*\*$')
VARIANT_END = re.compile(r'^(?:\*|—|–|-)*\s*End (?:of|of the expanded commentary on)\b.*$', re.I)


class Fixer:
    def __init__(self, num):
        self.num = num; self.fn = f"{num:03d}.md"; self.path = os.path.join(EXP, self.fn)
        self.log = collections.Counter(); self.notes = []

    def n(self, kind, msg=''):
        self.log[kind] += 1
        if msg: self.notes.append(f"{kind}: {msg}")

    # ---------- stage 1: textual clean-up ----------
    def clean(self, txt):
        raw = txt
        if '\r\n' in txt:
            self.n('crlf', f"{txt.count(chr(13)+chr(10))} CRLF -> LF"); txt = txt.replace('\r\n', '\n')
        if '\r' in txt: txt = txt.replace('\r', '\n')
        out = []
        for ln in txt.split('\n'):
            if SMC.match(ln.strip()) or 'system_instructions.md` loaded and verified' in ln:
                self.n('leak', 'removed [System Memory Check] directive'); continue
            out.append(ln)
        txt = '\n'.join(out)
        # unglue headings that are welded to the end of a previous line
        def unglue(m):
            self.n('glued', f'split heading glued mid-line: {m.group(1)[:45]!r}')
            return '\n\n---\n\n' + m.group(0)
        txt = re.sub(r'(?m)(?<=\S)(#{2,6}\s+Sūra[th]\s+[^\n#]{1,90}?(?:\[\d+:\d+\]|\d+:\d+)\s*)$', unglue, txt)
        # drop leaked unexpanded template token
        if 'Verse ${n}' in txt or '${n}' in txt:
            self.n('template', 'file contains unexpanded ${n} template token (left for regeneration)')
        return txt

    # ---------- stage 2: parse ----------
    def parse(self, txt):
        lines = txt.split('\n')
        idx = [i for i, l in enumerate(lines) if VH.match(l.strip()) and l.lstrip().startswith('## ')]
        pre = lines[:idx[0]] if idx else lines
        secs = []
        for k, i in enumerate(idx):
            end = idx[k+1] if k+1 < len(idx) else len(lines)
            m = VH.match(lines[i].strip())
            secs.append({'chap': int(m.group(2)), 'v': int(m.group(3)),
                         'name': m.group(1).strip(), 'body': lines[i+1:end]})
        return pre, secs

    # ---------- stage 2b: strip generation-process meta from the preamble ----------
    META_H2  = re.compile(r'^##\s+.*(Editorial|Source Note|Source and Method|Method(?:ology)? Note)\b', re.I)
    META_BH  = re.compile(r'^\*\*\s*(?:How This Commentary Reads the Source|Source, quotation, and interpretive conventions|'
                          r'What is preserved and what is newly written|Editorial and Source Note)\s*\*\*\s*$', re.I)
    META_TXT = re.compile(r'`initial/\d{3}\.md`|the (?:complete )?workspace source|No online research or external database was used|'
                          r'retained locally in numerical order|the chapter file was assembled only after|'
                          r'in the style and at the depth of the expanded commentary on', re.I)

    def strip_meta(self, lines):
        out = []; i = 0; removed = []
        while i < len(lines):
            ln = lines[i]
            s = ln.strip()
            # an italic/paragraph task description sitting directly under the H1
            if i <= 3 and self.META_TXT.search(s) and not s.startswith('#'):
                removed.append(s[:60]); i += 1; continue
            # a whole H2 meta section
            if self.META_H2.match(s):
                j = i + 1
                while j < len(lines) and not lines[j].startswith('## '):
                    j += 1
                removed.append(s[:60]); i = j; continue
            # a bold mini-heading meta block: heading + paragraphs until next heading/rule
            if self.META_BH.match(s):
                j = i + 1
                while j < len(lines):
                    t = lines[j].strip()
                    if lines[j].startswith('#') or self.META_BH.match(t) or t == '---':
                        break
                    if re.match(r'^\*\*[^*]+\*\*\s*$', t) and not self.META_TXT.search(t):
                        break
                    j += 1
                removed.append(s[:60]); i = j; continue
            out.append(ln); i += 1
        if removed:
            self.n('meta', f'removed {len(removed)} generation-process meta block(s): {removed[:3]}')
        return out

    # ---------- stage 3: preamble ----------
    def fix_preamble(self, pre, name):
        lines = self.strip_meta([l.rstrip() for l in pre])
        if not lines or not lines[0].startswith('# '):
            lines.insert(0, '')
        # H1
        want_h1 = f"# Sūrah {name} (Chapter {self.num}) — Expanded Verse-by-Verse Commentary"
        if lines[0] != want_h1:
            self.n('h1', f'H1 -> {want_h1}')
            lines[0] = want_h1
        # Sūrat -> Sūrah in any heading
        for i, l in enumerate(lines):
            if l.startswith('#') and 'Sūrat ' in l:
                lines[i] = l.replace('Sūrat ', 'Sūrah '); self.n('surat', 'Sūrat -> Sūrah')
        # canonical intro heading
        canon = '## Introduction to the Sūrah'
        ii = None
        for i, l in enumerate(lines):
            s = l.strip()
            if s == canon: ii = i; break
            if re.match(r'^##\s+Introduction to the Sūrah\b.+$', s):
                body = s[len('## Introduction to the Sūrah'):].lstrip(' —-–:').strip()
                lines[i] = canon
                if body:
                    lines[i+1:i+1] = ['', EC, '', body]
                    self.n('intro', 'intro heading carried body text -> split into heading + body')
                else:
                    self.n('intro', 'intro heading normalised')
                ii = i; break
            if re.match(r'^##\s+(Introduction|Overview|Preface|About)\b', s) or \
               re.match(r'^##\s+Expanded Verse-by-Verse Commentary\s*$', s):
                lines[i] = canon; self.n('intro', f'intro heading {s[:40]!r} -> {canon}'); ii = i; break
        if ii is None:
            lines[1:1] = ['', canon]
            ii = 2; self.n('intro', f'inserted {canon}')
        # Expanded Commentary after intro heading
        nxt = [j for j in range(ii+1, min(ii+10, len(lines))) if lines[j].strip()]
        if not nxt or lines[nxt[0]].strip() != EC:
            lines[ii+1:ii+1] = ['', EC]
            self.n('intro-ec', f'added {EC} after intro heading')
        # strip a stray italic preamble note / basmalah block that sits above the first ---
        # (kept: content, not a format defect)
        return lines

    # ---------- stage 4: verse sections ----------
    def fix_section(self, s, name):
        v = s['v']; body = [l.rstrip() for l in s['body']]
        canon_hd = f"## Sūrah {name} {self.num}:{v}"
        if s['name'] != name or s['chap'] != self.num:
            self.n('heading', f'v{v}: heading -> {canon_hd}')

        nb = [b for b in body if b.strip()]
        # collect leading blockquote block
        bi = 0
        while bi < len(body) and body[bi].strip() == '': bi += 1
        bs = bi
        while bi < len(body) and body[bi].lstrip().startswith('>'): bi += 1
        block = body[bs:bi]
        parts = []
        for b in block:
            t = re.sub(r'^\s*>\s?', '', b).strip()
            if not t: continue
            if ARABIC.search(t):
                self.n('arabic', f'v{v}: dropped Arabic-script translation line'); continue
            # label OUTSIDE the bold span:  **Verse Translation:** text
            t = re.sub(r'^\*\*\s*(?:Verse Translation|Translation|Text and Translation|The Verse|Verse)\s*\*\*\s*:?\s*',
                       '', t, flags=re.I)
            # label INSIDE the bold span:  **Verse Translation: text**
            t = re.sub(r'^\*\*\s*(?:Verse Translation|Translation|Text and Translation|The Verse|Verse)\s*:\s*',
                       '**', t, flags=re.I)
            t = re.sub(r'^\*\*\s*\d+\s*\*\*\s*', '', t)
            parts.append(t)
        transl = ' '.join(parts).strip()
        transl = re.sub(r'^\*\*(.+?)\*\*$', r'\1', transl).strip()
        transl = transl.replace('**', '').strip()
        # drop an italic wrapper: 001.md's canonical translation line is bold only
        while len(transl) > 2 and transl.startswith('*') and transl.endswith('*'):
            transl = transl[1:-1].strip(); self.n('italics', f'v{v}: removed italic wrapper from translation')
        # repair stray unbalanced quote marks left by generation
        if transl.count('"') == 1 and transl.endswith("'"):
            transl = transl[:-1] + '"'; self.n('quote', f'v{v}: repaired trailing quote mark')
        if transl.count('"') == 1 and not transl.endswith('"'):
            transl = transl + '"'; self.n('quote', f'v{v}: closed unclosed quotation mark')

        rest = body[bi:] if bi > bs else body
        # A verse-translation blockquote buried inside the section (below EC / a mini-heading)
        # must be hoisted to its canonical place directly under the verse heading.
        if not transl:
            for q, b in enumerate(rest):
                bs2 = b.strip()
                if re.match(r'^>\s*\*\*\s*\d+\s*\*\*', bs2):
                    t = re.sub(r'^>\s*\*\*\s*\d+\s*\*\*\s*', '', bs2)
                    t = t.replace('*', '').strip()
                    if t:
                        transl = t
                        del rest[q]
                        self.n('hoist', f'v{v}: hoisted buried verse-translation blockquote to canonical position')
                    break
        # drop a leading '**Expanded Commentary**' from rest (we re-emit it)
        j = 0
        while j < len(rest) and rest[j].strip() == '': j += 1
        if j < len(rest) and rest[j].strip() == EC:
            rest = rest[j+1:]
        # remove duplicate/empty heading remnants
        rest = [l for l in rest if not VH.match(l.strip())]
        # collapse 3+ blank lines
        out = []
        for l in rest:
            if l == '' and out and out[-1] == '': continue
            out.append(l)
        while out and out[0] == '': out.pop(0)
        while out and out[-1] == '': out.pop()
        # strip a trailing --- that belonged to the old separator
        while out and out[-1].strip() in ('---', '***'):
            out.pop()
            while out and out[-1] == '': out.pop()

        if not transl and not out:
            self.n('empty', f'v{v}: section is empty (needs regeneration)')
        elif not transl:
            self.n('no-transl', f'v{v}: heading + commentary but no translation line')

        sec = [canon_hd, '']
        if transl: sec += [f'> **{transl}**', '']
        sec += [EC, '']
        sec += out
        return sec

    # ---------- run ----------
    def run(self):
        raw = open(self.path, 'rb').read()
        txt = self.clean(raw.decode('utf-8'))
        pre, secs = self.parse(txt)

        name = None
        for s in secs:
            if s['chap'] == self.num: name = s['name']; break
        if name is None:
            m = re.match(r'^#\s+Sūra[th]\s+(.+?)\s*\(Chapter\s+\d+\)', txt.split('\n')[0])
            name = m.group(1).strip() if m else None
        if name is None:
            m = re.match(r'^#\s+(?:\d+\.\s*)?Sūra[th]?\s+(.+)$', txt.split('\n')[0])
            name = re.sub(r'\s*\([^)]*\)\s*$', '', m.group(1)).strip() if m else f'Chapter {self.num}'
        self.name = name

        # duplicate verse headings (e.g. 018's welded repeat)
        seen = {}
        keep = []
        for s in secs:
            if s['v'] in seen:
                prev = keep[seen[s['v']]]
                prev_has = any(b.strip() for b in prev['body'])
                cur_has  = any(b.strip() for b in s['body'])
                if not cur_has:
                    self.n('dup', f'v{s["v"]}: dropped empty duplicate heading'); continue
                if not prev_has:
                    self.n('dup', f'v{s["v"]}: dropped empty duplicate heading')
                    keep[seen[s['v']]] = s; continue
                self.n('dup', f'v{s["v"]}: duplicate heading with content in both (kept first)'); continue
            seen[s['v']] = len(keep); keep.append(s)
        secs = keep

        preamble = self.fix_preamble(pre, name)

        parts = []
        pl = [l for l in preamble]
        # drop a stray horizontal rule sitting above the intro heading
        try:
            hi = pl.index('## Introduction to the Sūrah')
            if any(x.strip() == '---' for x in pl[:hi]):
                pl = [x for k, x in enumerate(pl) if not (k < hi and x.strip() == '---')]
                self.n('rule', 'removed stray --- above the intro heading')
        except ValueError:
            pass
        while pl and pl[-1] == '': pl.pop()
        parts += pl
        for s in secs:
            parts += ['', '---'] + self.fix_section(s, name)
        # end marker
        while parts and parts[-1] == '': parts.pop()
        want = f'**[End of the commentary on Sūrah {name}]**'
        if parts and ENDM.match(parts[-1].strip()):
            if parts[-1].strip() != want:
                self.n('end', f'end marker -> {want}')
                parts[-1] = want
        elif parts and VARIANT_END.match(parts[-1].strip()):
            self.n('end', f'variant end marker {parts[-1][:50]!r} -> {want}')
            parts[-1] = want
        elif parts and parts[-1].strip() in ('---', '***'):
            self.n('end', f'added end marker {want} after existing rule')
            parts[-1] = want
        else:
            self.n('end', f'added end marker {want}')
            parts.append(want)
        # ensure the end marker is preceded by a horizontal rule
        if len(parts) >= 2 and parts[-2].strip() != '---':
            self.n('end-rule', 'inserted --- before end marker')
            parts[-1:-1] = ['', '---']
        # collapse 2+ consecutive blank lines (001.md has none)
        ded = []
        for l in parts:
            if l == '' and ded and ded[-1] == '':
                self.n('blanks', 'collapsed consecutive blank lines'); continue
            ded.append(l)
        parts = ded
        res = '\n'.join(parts).rstrip('\n') + '\n'
        if res.encode('utf-8') != raw:
            with open(self.path, 'w', encoding='utf-8', newline='\n') as f: f.write(res)
            self.log['files_written'] = 1
        return self.fn, dict(self.log), self.notes


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    nums = [int(a) for a in args] if args else list(range(1, 115))
    total = collections.Counter(); per = {}; allnotes = {}
    for n in nums:
        if n == 1: continue            # never touch the confirmed reference
        fn, log, notes = Fixer(n).run()
        per[fn] = log; total.update(log)
        if notes: allnotes[fn] = notes
    json.dump({'total': dict(total), 'per_file': per, 'notes': allnotes},
              open(os.path.join(ROOT, 'tools/quran-audit/last_fixlog.json'), 'w'), ensure_ascii=False, indent=1)
    print("=== TOTAL CHANGES ===")
    for k, v in sorted(total.items(), key=lambda x: -x[1]): print(f"  {v:6d}  {k}")
    print(f"\nfiles written: {total.get('files_written',0)}")

main()
