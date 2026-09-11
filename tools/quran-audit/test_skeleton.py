#!/usr/bin/env python3
"""Regression test for the canonical-skeleton artifacts found in this pass.

Covers two defect classes that every gate reported green while 107 of 114 files
carried them:

  1. stray horizontal rules -- 219 across the corpus (134 duplicated boundary
     rules, 85 orphaned inside a section body). validate.py tested L[i-1] and
     L[i-2] relative to a heading, so "--- blank --- heading" satisfied both.
  2. non-canonical H2 headings -- 11 across 10 files (3 introduction
     subdivisions in 004.md, 8 concluding reflections).

Root causes, all in normalize.py:
  * run() kept the rule at the end of the preamble slice, then re-emitted
    ['', '---'] before the first section  -> duplicated intro->v1 boundary.
  * run() tested only parts[-2] before inserting the closing rule, missing one
    at parts[-3]                           -> duplicated end boundary.
  * clean()'s unglue inserted '\\n\\n---\\n\\n' before a welded heading; the
    heading was later dropped as a remnant, orphaning the rule inside the body.

The test injects each artifact into a scratch copy, asserts the hardened gate
rejects it, asserts normalize.py repairs it, and asserts the pre-hardening gate
would have accepted it (so the gap stays documented).

Usage: python3 tools/quran-audit/test_skeleton.py
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VH = re.compile(r'^## Sūrah (.+?) (\d+):(\d+)$')
ENDM = re.compile(r'^\*\*\[End of the commentary on Sūrah .+\]\*\*$')

failures = []


def check(cond, msg):
    print(f'  {"PASS" if cond else "FAIL"}  {msg}')
    if not cond:
        failures.append(msg)


def stray_rules(lines):
    """Rules not immediately followed by a verse heading or the end marker."""
    targets = {i for i, l in enumerate(lines)
               if VH.match(l.rstrip()) or ENDM.match(l.rstrip())}
    return [i for i, l in enumerate(lines)
            if l.strip() in ('---', '***') and (i + 1) not in targets]


def extra_h2(lines):
    keep = {2}  # '## Introduction to the Sūrah'
    keep |= {i for i, l in enumerate(lines) if VH.match(l.rstrip())}
    return [i for i, l in enumerate(lines) if l.startswith('## ') and i not in keep]


def run_validator(script, cwd):
    r = subprocess.run([sys.executable, script], cwd=cwd,
                       capture_output=True, text=True)
    return r.stdout + r.stderr


def main():
    print('=== 1. the shipped corpus is canonical ===')
    for f in sorted(glob.glob(os.path.join(ROOT, 'expanded', '*.md'))):
        lines = open(f, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
        sr, eh = stray_rules(lines), extra_h2(lines)
        if sr or eh:
            failures.append(f'{os.path.basename(f)}: {len(sr)} stray rules, {len(eh)} extra H2')
    check(not failures, f'all 114 files free of stray rules and extra H2s')

    print('\n=== 2. reference 001.md defines the invariant ===')
    ref = open(os.path.join(ROOT, 'expanded/001.md'), encoding='utf-8').read().split('\n')
    nrule = sum(1 for l in ref if l.strip() == '---')
    nh2 = sum(1 for l in ref if l.startswith('## '))
    nverse = sum(1 for l in ref if VH.match(l.rstrip()))
    check(nrule == nverse + 1, f'001.md has exactly one rule per boundary '
                               f'({nrule} == {nverse} verses + 1 end marker)')
    check(nh2 == nverse + 1, f'001.md H2 count == intro + verses ({nh2})')
    check(not stray_rules(ref) and not extra_h2(ref), '001.md itself is canonical')

    print('\n=== 3. injected artifacts: gate rejects, normalize repairs ===')
    tmp = tempfile.mkdtemp()
    try:
        shutil.copytree(os.path.join(ROOT, 'expanded'), os.path.join(tmp, 'expanded'))
        shutil.copytree(os.path.join(ROOT, 'tools'), os.path.join(tmp, 'tools'))
        shutil.copytree(os.path.join(ROOT, 'initial'), os.path.join(tmp, 'initial'))

        target = os.path.join(tmp, 'expanded', '114.md')
        clean = open(target, encoding='utf-8').read()
        t = clean
        # (a) duplicated rule at the intro -> v1 boundary
        t = t.replace('\n---\n## Sūrah an-Nās 114:1\n',
                      '\n---\n\n---\n## Sūrah an-Nās 114:1\n', 1)
        # (b) TRIPLE rule at the end boundary
        t = t.replace('\n---\n**[End of the commentary',
                      '\n---\n\n---\n\n---\n**[End of the commentary', 1)
        # (c) orphaned rule + (d) non-canonical H2 inside a section body
        h = '## Sūrah an-Nās 114:3'
        i = t.index(h)
        t = t[:i] + '---\n\n## A Stray Concluding H2\n\nConcluding prose.\n\n' + t[i:]
        assert t != clean, 'injection did not apply'
        open(target, 'w', encoding='utf-8', newline='\n').write(t)

        inj = t.split('\n')
        check(len(stray_rules(inj)) == 5, f'injection produced 5 stray rules '
                                          f'(got {len(stray_rules(inj))})')
        check(len(extra_h2(inj)) == 1, 'injection produced 1 non-canonical H2')

        new_gate = os.path.join(tmp, 'tools/quran-audit/validate.py')
        out_new = run_validator(new_gate, tmp)
        check('FAILED: 1' in out_new, 'hardened validate.py REJECTS the injected file')
        check('stray horizontal rule x5' in out_new,
              'hardened gate reports all 5 stray rules')
        check('non-canonical H2 x1' in out_new,
              'hardened gate reports the non-canonical H2')

        # The pre-hardening gate, for comparison. HEAD cannot be used as the
        # reference: once the hardening is committed, HEAD *is* the hardened
        # gate and this check inverts. Locate a revision of validate.py that
        # predates the new checks, and SKIP rather than fail if none is
        # reachable (shallow clone, squash merge, or history rewritten) -- the
        # gap is documented in REMAINING_ISSUES.md Group G either way, and a
        # test that fails for want of git history would be a false alarm.
        old = None
        for ref in ('HEAD~1', '6eb8b1f'):
            got = subprocess.run(['git', '-C', ROOT, 'show',
                                  f'{ref}:tools/quran-audit/validate.py'],
                                 capture_output=True, text=True)
            if got.returncode == 0 and 'stray horizontal rule' not in got.stdout:
                old = got.stdout
                break
        if old is None:
            print('  SKIP  PRE-hardening gate comparison (no pre-hardening '
                  'revision of validate.py reachable)')
        else:
            old_path = os.path.join(tmp, 'old_validate.py')
            open(old_path, 'w', encoding='utf-8').write(old)
            out_old = run_validator(old_path, tmp)
            check('stray horizontal rule' not in out_old
                  and 'non-canonical H2' not in out_old,
                  'PRE-hardening gate did NOT report either class (the documented gap)')

        subprocess.run([sys.executable,
                        os.path.join(tmp, 'tools/quran-audit/normalize.py'), '114'],
                       cwd=tmp, capture_output=True, text=True)
        fixed = open(target, encoding='utf-8').read().split('\n')
        check(not stray_rules(fixed), 'normalize.py removed every stray rule')
        check(not extra_h2(fixed), 'normalize.py demoted the non-canonical H2')
        check('**A Stray Concluding H2**' in open(target, encoding='utf-8').read(),
              'demotion preserved the heading text as a bold mini-heading')
        check('Concluding prose.' in open(target, encoding='utf-8').read(),
              'demotion preserved the body prose (no content deleted)')

        out = run_validator(new_gate, tmp)
        check('PASSED: 114/114' in out and 'FAILED: 0' in out,
              'hardened gate accepts the normalized file')

        # idempotence: a second normalize pass must change nothing
        subprocess.run([sys.executable,
                        os.path.join(tmp, 'tools/quran-audit/normalize.py'), '114'],
                       cwd=tmp, capture_output=True, text=True)
        check(open(target, encoding='utf-8').read().split('\n') == fixed,
              'normalize.py is idempotent on its own output')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print('\n=== 4. fix_separators.py guarantees content preservation ===')
    r = subprocess.run([sys.executable,
                        os.path.join(ROOT, 'tools/quran-audit/fix_separators.py'),
                        '--dry-run'], cwd=ROOT, capture_output=True, text=True)
    check('files affected: 0/114' in r.stdout,
          'fix_separators.py finds nothing left to repair')

    print()
    if failures:
        print(f'{len(failures)} CHECK(S) FAILED:')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('ALL CHECKS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
