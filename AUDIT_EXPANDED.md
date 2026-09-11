# Audit of `expanded/` — 114 files, 6,235 sections, 6,286,453 words

**Method.** `expanded/001.md` is the confirmed reference and has never been modified. Its
skeleton was encoded as `tools/quran-audit/validate.py`, which is now the structural gate for
the corpus. Content was verified against `initial/` (the ground-truth translation and
per-verse classical commentary) and `translation/*.txt` (a second translation used to
distinguish real substitutions from paraphrase). Every count in this report is the output of
a committed checker, not an estimate.

---

## 1. Current gate status

```
$ python3 tools/quran-audit/validate.py
PASSED: 114/114      FAILED: 0

$ python3 tools/quran-audit/check_translations.py
checked: 6235 sections   (no translation line: 0)
flagged (<0.45 against BOTH initial/ and translation/): 7

$ python3 tools/quran-audit/check_offtopic.py
files: 114   sections examined: 5551   threshold: <15% echo
flagged: 12
```

The 7 translation flags are register variants, each verified side-by-side against both
reference translations: `010.md` v91, `020.md` v1, `021.md` vv 73–76/78/97, `050.md` v25,
`068.md` vv 3/10/13/24/25, `094.md` v7, `102.md` v3, `108.md` v3. None is a wrong-verse
substitution and none was altered.

---

## 2. Repaired defect classes

| Defect class | Files affected | Status |
|---|---|---|
| Canonical-skeleton divergence | 114 files | **0 remaining** |
| Leaked `[System Memory Check]` drafting scaffolding | `074.md` (54/56 sections, 61% of file) | **0 remaining** — 17,334 w stripped |
| Whole-file template boilerplate | `036.md` (83/83 sections, 13 sentences ×83) | **0 remaining** — 16,483 w stripped, all 83 sections rebuilt |
| Cross-sūrah verse substitution | `037.md` (117 sections), `011.md` (13), `007.md` (1), `040.md` (1) | **0 remaining** — 132 translations restored |
| Translation-line-only drift | `040.md` vv 31/48/50/63/73 | **0 remaining** |
| Appended text / run-on translation lines | `026.md` ×6, `011.md` v117 | **0 remaining** |
| Template-filler phrases (4 regex patterns) | 141 phrases across the corpus | **0 remaining** |
| Off-topic sections (<15% echo) | 25 flagged | **12 remaining** |

A corpus-wide boilerplate scan confirmed the template class affected exactly two files:
`036.md` at 100% and `074.md` at 96%. Every other file scored 0%.

---

## 3. `036.md` — rebuilt in full

The file's 83 sections were entirely template-generated. The boilerplate was stripped first
(16,483 words), then every section was rebuilt verse by verse from the apparatus in
`initial/036.md`, in 21 batches of 4 (`content_036_a.py` … `content_036_u.py`).

| Metric | Value |
|---|---|
| Sections | 83 |
| Total words | 43,738 |
| Min / median / max | 419 / **516** / 721 |
| Sections with duprate ≥ 0.030 | **0** |
| Off-topic flags | **0** |
| Translation flags | **0** |

The rebuild runs at a median of 516 words, deliberately below the 976-word corpus healthy
figure because this sūrah's apparatus in `initial/` is thinner than that of `011.md`,
`021.md`, or `040.md`. Depth was matched to what the source material can support rather than
padded to a number.

Eight sections initially tripped the duplication gate (vv 18, 28, 36, 45, 47, 65, 66, 78) for
the same reason each time: quoting the verse translation verbatim in the opening prose. The
10-grams of the quoted verse alone trip the detector. Each was fixed by paraphrasing the
opening and leaving the quotation to the `> **…**` line.

---

## 4. Translation-defect history, all resolved

**Whole section substituted** — the commentary belonged to a different verse:
`011.md` vv 105–116 and 118 (each mapped to 81:1, 55:17, 25:61, 10:5, 30:30, 80:1, 37:179,
37:126, 109:1, 81:28, 69:39, 48:7, 37:179); `007.md` v170; `040.md` v74.

**Translation line only:** `040.md` vv 31, 48, 50, 63, 73.

**Appended text / run-on:** `026.md` vv 124, 132, 146, 181, 185, 208; `011.md` v117.

`037.md`'s defect was the largest: of 182 sections, 63 matched `initial/`, 2 matched
`translation/`, and **117 matched neither**. The cause was that vv 57–177 were 21,326 words
of unheaded content which `normalize.py` had promoted into 121 new verse headings; 97 of the
121 quoted other sūrahs. All 119 substitute translations were replaced, and the file now
scores 0 of 182 mismatch.

---

## 5. Complete files

| File | Sections | Median words | Notes |
|---|---|---|---|
| `001.md` | 112 | — | confirmed reference, never modified |
| `011.md` | 123 | 914 | 0 translation defects, 0 filler |
| `021.md` | 112 | 1,037 | 121,660 w; vv 73–76/78/97 are legitimate variants |
| `026.md` | 227 | 258 | 0 translation defects; depth outstanding |
| `036.md` | 83 | 516 | rebuilt in full this pass |
| `040.md` | 85 | 937 | 0 translation defects |
| `007.md` | 206 | 730 | |
| `037.md` | 182 | 231 | correctness complete; depth outstanding |

---

## 6. Outstanding

**Depth.** Six files sit below a 400-word median section:

| File | Sections | Min | Median | Max | Words |
|---|---|---|---|---|---|
| `037.md` | 182 | 139 | 231 | 899 | 43,186 |
| `026.md` | 227 | 65 | 258 | 874 | 70,109 |
| `069.md` | 52 | 245 | 323 | 415 | 17,329 |
| `075.md` | 40 | 287 | 360 | 909 | 15,504 |
| `073.md` | 20 | 302 | 370 | 1,240 | 8,387 |
| `067.md` | 30 | 318 | 392 | 571 | 12,228 |

**Off-topic flags — 12.** `018.md` v75 · `026.md` vv 132, 176 · `037.md` vv 50, 61, 62, 66,
85, 87, 182 · `040.md` v3 · `067.md` v10. The `037.md` hits are depth artifacts — bodies of
88–161 words under-echo by construction — not subject drift. Each needs reading before any
change.

**`074.md`.** Structurally valid and correct after the scaffolding strip, but now thin:
min 392 / median 436 / max 793 across 25,610 words. It needs depth rebuilt from
`initial/074.md`.

**`045.md`.** 6.17 emphasis runs per 1,000 words against a corpus norm near 1. Translations
are exact. Left in place by decision — the pattern is the file's own style.

---

## 7. Reproducing the gates

```
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/check_translations.py [--sura N] [--verbose]
python3 tools/quran-audit/check_offtopic.py     [--sura N] [--verbose]
python3 tools/quran-audit/extract_source.py <sura> <lo> <hi>
python3 tools/quran-audit/fix_translation.py <sura> <verse...> --dry-run
```

Restore any file from history with `git checkout <sha> -- expanded/`.
