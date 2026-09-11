#!/usr/bin/env python3
"""Repair 007.md's degenerate prose by stripping formulaic frames, not by
deleting content.

007.md's duplication is a different defect from 017.md's. 017.md carried
inserted blocks that restated real material; 007.md carries machine-generated
nominalisations that recurse on themselves -- 39% of the words in its 100
flagged sections. Three distinct things are going on and each needs a different
repair.

  (a) FRAMED KERNELS. "The logic of the vow is the logic that is worth stating:
      Iblis knows that the straight path is the means of the salvation, and he
      attacks the means, not the end." The clause after the colon is real
      commentary. Repair: drop the frame, keep the kernel. Recursively -- the
      kernel can itself be a loop, in which case it goes.

  (b) PURE LOOPS. "...are the people who are in the state of the one who are the
      ones who are the objects of the punishment of God the torment from the
      heaven." No information content at any point. Repair: delete. Guarded --
      a sentence is deleted only if it matches a loop template AND contains no
      quotation, no verse citation and no scholar name, so nothing informative
      can be lost.

  (c) FRAMED OPENERS. "The verse states the act of the people who did wrong, and
      the act is the act that is the substitution of the word: <quote>." The
      quotation must survive and the section must still open. Repair: replace
      the frame with a plain lead-in, preserving the quote.

Nothing here rewrites scholarship. Sections left too thin to stand are reported
for authoring rather than padded -- automated trimming that damages coherence
was already tried and rejected on 017.md (REMAINING_ISSUES.md H5a), and this
tool is deliberately narrower: it only touches sentences that are already
incoherent.

Usage:
    repair_degen.py --dry-run [--verse N ...]
    repair_degen.py --apply   [--verse N ...]
    repair_degen.py --show N                   # full before/after for a section
"""
import collections
import re
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from check_degeneracy import sections, degen_score  # noqa: E402

TARGET = 'expanded/007.md'

# (a) frame-then-kernel: strip everything up to and including the first colon
FRAME_KERNEL = [
    re.compile(r'^The logic of .{0,80}? is the logic that is worth stating'
               r'(?: in full| in the form of the principle)?\s*:\s*', re.I),
    re.compile(r'^The logic of .{0,80}? is the logic that is the form of '
               r'.{0,60}?\s*:\s*', re.I),
    re.compile(r"^The logic of .{0,80}? is the logic that the Qur'an states "
               r'in the same form in several places\s*:\s*', re.I),
    re.compile(r'^The verse, in its .{0,60}?, is the form of the statement of '
               r'.{0,60}?\s*:\s*', re.I),
]

# (b) pure recursion, no information
LOOP = [
    r'are the people who are in the state of the one who are',
    r'is the man who is in the (?:condition|one) of the',
    r'who are in the state of the one who are the ones who',
    r'who is in the one who is the object of',
    r'are the ones who are the objects of',
    r'is the wrong that is the wrong that is',
    r'are the sorcerers who are in the ones who are',
    r'the state of the man is the state of the',
    r'is the form of the statement of the state of the',
    r'the answer that is the answer that is',
    r'the form of the introduction of the statement of',
    r'is the form that says\b',
    r'the earth is the earth that God has established',
    r'is the request that is the asking of',
    r'the two forms are the two forms of the same act',
]
RE_LOOP = [re.compile(p, re.I) for p in LOOP]

# (c) framed opener carrying a quotation
FRAME_OPENER = re.compile(
    r'^The verse states the act of (?P<who>.{0,90}?)\s*,\s*and the act is the '
    r'act that is the (?P<what>.{0,90}?)\s*:\s*(?P<quote>[*"].*)$', re.S)

# guards: a loop sentence must carry none of these to be deletable
HAS_QUOTE = re.compile(r'[*"“”]')
HAS_CITE = re.compile(r'\b\d{1,3}:\d{1,3}\b')
SCHOLARS = re.compile(r'(al-Ṭabarī|al-Rāzī|al-Qurṭubī|Ibn Kathīr|al-Zamakhsharī|'
                      r'al-Suyūṭī|al-Wāḥidī|al-Jaṣṣāṣ|al-Bukhārī|Muslim|'
                      r'Abū Dāwūd|al-Tirmidhī|Ibn ʿAbbās|Mujāhid|Qatādah|'
                      r'al-Ḥasan|Ibn Masʿūd|al-Suddī|al-Baghawī|Exodus|'
                      r'Gospel|Torah|Psalms)', re.I)

SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z*">])')
WORDS = re.compile(r"[\w'’\-]+")


def cap(s):
    s = s.strip()
    return s[0].upper() + s[1:] if s else s


def dethe(s):
    """Light cleanup of the article pile-up the generator produces."""
    return re.sub(r'\bthe (\w+) of the \1\b', r'the \1', s, flags=re.I)


def squash(s):
    """Normalise for containment tests: drop markup, punctuation and case."""
    s = re.sub(r'[*>"“”‘’\'`]', '', s)
    return re.sub(r'[^a-z0-9\u00c0-\u024f\u1e00-\u1eff ]', '',
                  s.lower()).strip()


def translation_line(body):
    """The section's own '> **verse text**' line, squashed."""
    for line in body.split('\n'):
        p = line.strip()
        if p.startswith('>') and '**' in p:
            return squash(p)
    return ''


def quote_is_own_translation(quote, trans):
    """True if the quoted text is (part of) the section's own verse translation.

    The skeleton puts the full translation in a '> **...**' line under every
    heading, so a body sentence that quotes the same words adds nothing and only
    inflates the duplication score.
    """
    q = squash(quote)
    if not q or not trans:
        return False
    return q in trans


def repair_sentence(s, depth=0, trans=''):
    """Return (new_text, action); action in keep/unframe/delete/reopen."""
    t = s.strip()
    if not t:
        return s, 'keep'

    # (c) framed opener with a quotation. The quote is the section's own verse
    # text, which the "> **...**" translation line already carries in full --
    # re-quoting it is what keeps the duprate up (a known gate trap). The frame
    # carries no information beyond the heading, so the sentence goes and the
    # real commentary that follows becomes the opener. quote_ok lets a caller
    # keep the quote where it is NOT the section's own translation.
    m = FRAME_OPENER.match(t)
    if m:
        if quote_is_own_translation(m.group('quote'), trans):
            return '', 'delete'
        what = dethe(m.group('what').strip().rstrip('.'))
        return f'The {what} is stated plainly: {m.group("quote").strip()}', 'reopen'

    # (a) framed kernel -- keep what follows the colon, then re-test it
    for rx in FRAME_KERNEL:
        m = rx.match(t)
        if m:
            kernel = dethe(cap(t[m.end():]))
            if len(WORDS.findall(kernel)) >= 6:
                if depth < 3:
                    inner, act = repair_sentence(kernel, depth + 1, trans)
                    if act == 'delete':
                        return '', 'delete'
                    return inner, 'unframe'
                return kernel, 'unframe'
            return '', 'delete'          # the frame was the whole sentence

    # (b) pure loop -- delete only if nothing informative is in it
    if any(rx.search(t) for rx in RE_LOOP):
        if not (HAS_QUOTE.search(t) or HAS_CITE.search(t) or SCHOLARS.search(t)):
            return '', 'delete'

    return s, 'keep'


def repair_body(body):
    out, actions = [], collections.Counter()
    trans = translation_line(body)
    for para in body.split('\n'):
        p = para.strip()
        if not p or p == '---' or p.startswith('#') or p.startswith('>') \
                or re.fullmatch(r'\*\*.+?\*\*', p):
            out.append(para)
            continue
        kept = []
        for sp in SENT.split(p):
            new, act = repair_sentence(sp, 0, trans)
            actions[act] += 1
            if act == 'delete':
                continue
            kept.append(new if act in ('unframe', 'reopen') else sp)
        out.append(' '.join(x.strip() for x in kept if x and x.strip()))
    text = '\n\n'.join(x.strip() for x in out if x.strip())
    return re.sub(r'\n{3,}', '\n\n', text), actions


def main():
    args = sys.argv[1:]
    apply_ = '--apply' in args
    show = '--show' in args
    verses = [int(a) for a in args if a.isdigit()]

    secs = sections(TARGET)
    targets = verses or [v for v in sorted(secs)
                         if degen_score(secs[v][1])[0] >= 0.030]

    if show:
        for v in targets:
            ln, body = secs[v]
            new, acts = repair_body(body)
            print(f'===== v{v}  {degen_score(body)[0]:.3f} -> '
                  f'{degen_score(new)[0]:.3f}   {dict(acts)} =====')
            print(new)
            print()
        return 0

    report, tot = [], collections.Counter()
    for v in sorted(targets):
        ln, body = secs[v]
        new, acts = repair_body(body)
        tot.update(acts)
        report.append((v, ln, degen_score(body)[0], degen_score(new)[0],
                       len(WORDS.findall(body)), len(WORDS.findall(new))))

    if apply_:
        lines = open(TARGET, encoding='utf-8').read().split('\n')
        # bottom-up so earlier line offsets stay valid
        for v, ln, before, after, wb, wa in sorted(report, key=lambda r: -r[1]):
            if after < before:
                body = secs[v][1]
                new, _ = repair_body(body)
                s = ln - 1
                lines[s:s + len(body.split('\n'))] = new.split('\n')
        res = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).rstrip('\n') + '\n'
        open(TARGET, 'w', encoding='utf-8', newline='\n').write(res)

    cleared = sum(1 for r in report if r[3] < 0.030)
    thin = [(r[0], r[5]) for r in report if r[5] < 400]
    worse = [(r[0], r[2], r[3]) for r in report if r[3] > r[2]]
    print(f'sections processed : {len(report)}')
    print(f'actions            : {dict(tot)}')
    print(f'cleared the gate   : {cleared}')
    print(f'still over         : {len(report) - cleared}')
    print(f'duprate got WORSE  : {len(worse)} -> {worse[:10]}')
    print(f'left under 400 w   : {len(thin)} -> {thin[:16]}')
    print(f'words              : {sum(r[4] for r in report):,} -> '
          f'{sum(r[5] for r in report):,}')
    print('(dry run -- nothing written)' if not apply_ else '(written)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
