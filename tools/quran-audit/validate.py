#!/usr/bin/env python3
"""Strict validator: every expanded/*.md must match 001.md's skeleton exactly."""
import os, re, sys, glob, collections
EC='**Expanded Commentary**'
VH=re.compile(r'^## Sūrah (.+?) (\d+):(\d+)$')
ENDM=re.compile(r'^\*\*\[End of the commentary on Sūrah (.+?)\]\*\*$')
fails=collections.defaultdict(list); ok=[]
for f in sorted(glob.glob('expanded/*.md')):
    fn=os.path.basename(f); num=int(fn[:3]); E=fails[fn]
    raw=open(f,'rb').read()
    if b'\r' in raw: E.append('CR present')
    if not raw.endswith(b'\n') or raw.endswith(b'\n\n'): E.append('trailing newline wrong')
    L=raw.decode('utf-8').split('\n')
    L=L[:-1] if L and L[-1]=='' else L
    m=re.match(r'^# Sūrah (.+?) \(Chapter (\d+)\) — Expanded Verse-by-Verse Commentary$', L[0])
    if not m: E.append(f'H1 non-canonical: {L[0][:70]!r}'); name=None
    else:
        name=m.group(1)
        if int(m.group(2))!=num: E.append(f'H1 chapter {m.group(2)} != {num}')
    if L[1]!='' : E.append('L2 not blank')
    if L[2]!='## Introduction to the Sūrah': E.append(f'L3 not intro heading: {L[2][:60]!r}')
    if L[3]!='' : E.append('L4 not blank')
    if L[4]!=EC: E.append(f'L5 not EC: {L[4][:60]!r}')
    # verse sections
    idx=[i for i,l in enumerate(L) if VH.match(l)]
    if not idx: E.append('no canonical verse headings')
    nums=[]
    for k,i in enumerate(idx):
        mm=VH.match(L[i]); nums.append(int(mm.group(3)))
        if mm.group(1)!=name: E.append(f'v{mm.group(3)}: heading name {mm.group(1)!r} != H1 {name!r}')
        if int(mm.group(2))!=num: E.append(f'v{mm.group(3)}: heading chapter {mm.group(2)}')
        if L[i-1]!='---': E.append(f'v{mm.group(3)}: not preceded by --- (prev={L[i-1][:30]!r})')
        if i>=2 and L[i-2]!='': E.append(f'v{mm.group(3)}: no blank before ---')
        if L[i+1]!='' : E.append(f'v{mm.group(3)}: no blank after heading')
        tr=L[i+2]
        if not re.match(r'^> \*\*.+\*\*$', tr): E.append(f'v{mm.group(3)}: translation line non-canonical: {tr[:60]!r}')
        if L[i+3]!='' : E.append(f'v{mm.group(3)}: no blank after translation')
        if L[i+4]!=EC: E.append(f'v{mm.group(3)}: no EC marker (got {L[i+4][:40]!r})')
        if L[i+5]!='' : E.append(f'v{mm.group(3)}: no blank after EC')
    dups=[n for n,c in collections.Counter(nums).items() if c>1]
    if dups: E.append(f'duplicate verses {sorted(dups)}')
    if nums:
        miss=[n for n in range(1,max(nums)+1) if n not in nums]
        if miss: E.append(f'missing verses {miss[:12]}{"..." if len(miss)>12 else ""} ({len(miss)} total)')
        if sorted(nums)!=nums: E.append('verses out of order')

    # ---- horizontal rules -------------------------------------------------
    # 001.md carries exactly one rule per boundary (one before each verse
    # heading, one before the end marker) and none anywhere else. A rule is
    # therefore legal only as the line immediately preceding a boundary. The
    # per-verse checks above test L[i-1] and L[i-2] relative to a heading, so a
    # duplicated rule satisfied both and went undetected; this closes that gap.
    rule_targets=set(idx) | ({len(L)-1} if ENDM.match(L[-1]) else set())
    stray=[i for i,l in enumerate(L) if l.strip() in ('---','***') and (i+1) not in rule_targets]
    if stray:
        kinds=collections.Counter()
        for i in stray:
            j=i+1
            while j<len(L) and L[j].strip()=='': j+=1
            nxt=L[j].strip() if j<len(L) else '<EOF>'
            kinds['duplicate' if nxt in ('---','***') else 'internal']+=1
        summary=', '.join(f'{v} {k}' for k,v in sorted(kinds.items()))
        E.append(f'stray horizontal rule x{len(stray)} ({summary}) at lines '
                 f'{[i+1 for i in stray[:6]]}{"..." if len(stray)>6 else ""}')
    # ---- heading inventory ------------------------------------------------
    # Only the H1, the introduction H2 and the verse H2s may exist; everything
    # below that level is a bold mini-heading (system_instructions.md sec. 4).
    extra=[(i+1,L[i][:50]) for i,l in enumerate(L)
           if l.startswith('## ') and i not in set(idx) and i!=2]
    if extra: E.append(f'non-canonical H2 x{len(extra)}: {extra[:4]}')
    deep=[(i+1,L[i][:40]) for i,l in enumerate(L) if re.match(r'^#{3,6}\s',l)]
    if deep: E.append(f'H3+ heading x{len(deep)}: {deep[:4]}')
    # ---- bold mini-heading form -------------------------------------------
    # Canonical is **Text**. Four or more leading asterisks is malformed and
    # does not reliably render as bold. Exactly three is legitimate ("***Term*:
    # the rest**" is bold opening with a nested italic) and is not flagged.
    mal=[i+1 for i,l in enumerate(L) if re.match(r'^\*{4,}',l)]
    if mal: E.append(f'malformed bold mini-heading x{len(mal)} at lines {mal[:6]}'
                     f'{"..." if len(mal)>6 else ""}')
    # ---- orphan connector between two blockquotes -------------------------
    # A bare short word alone on a line between two blockquoted sources is the
    # remnant of a lead-in reduced to nothing but its conjunction. The corpus
    # norm is adjacent quotations with no connector. Short lines ending in a
    # colon ("and:", "God says:") are valid lead-ins and are not flagged.
    orph=[i+1 for i in range(2,len(L)-2)
          if re.match(r"^[A-Za-zʿ’\-']{1,3}$",L[i].strip())
          and not L[i-1].strip() and not L[i+1].strip()
          and L[i-2].startswith('> ') and L[i+2].startswith('> ')]
    if orph: E.append(f'orphan connector x{len(orph)} at lines {orph[:6]}'
                      f'{"..." if len(orph)>6 else ""}')
    # end
    if not ENDM.match(L[-1]): E.append(f'end marker non-canonical: {L[-1][:60]!r}')
    else:
        if ENDM.match(L[-1]).group(1)!=name: E.append('end marker name != H1 name')
        if L[-2]!='---': E.append(f'end not preceded by --- ({L[-2][:30]!r})')
    if not E: ok.append(fn)
print(f"PASSED: {len(ok)}/114")
bad={k:v for k,v in fails.items() if v}
print(f"FAILED: {len(bad)}")
for fn in sorted(bad):
    print(f"\n{fn}:")
    seen=collections.Counter()
    for e in bad[fn]:
        key=re.sub(r'v\d+','vN',e); seen[key]+=1
    for k,c in seen.most_common(8): print(f"   x{c}: {k[:130]}")
