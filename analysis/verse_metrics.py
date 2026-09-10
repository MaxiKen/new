#!/usr/bin/env python3
"""
verse_metrics.py — Structural metrics for the expanded Qur'an commentary.

Computes, for EVERY chapter in `expanded/`, three headline metrics:

    * Average words per verse
    * Average paragraphs per verse
    * Average bold mini-headings per verse

...using the actual verse-section content found in the files (not the source
`initial/` text and not the plain `translation/` text).

Definitions (documented so the numbers are reproducible and auditable)
---------------------------------------------------------------------
verse section   A block of the file that begins at a level-2 heading (line
                starting with "## ") whose heading carries a chapter:verse
                reference, in either of the two formats present in the corpus:

                    ## Sūrah al-Baqarah 2:1        (plain  — 6,054 sections)
                    ## Sūrah al-Ṣaffāt [37:1]      (bracket —    61 sections)

                The front-matter block (## Introduction to the Sūrah, etc.)
                that precedes the first verse heading is reported separately and
                is NOT part of any verse average.

word            Any whitespace-separated token containing at least one letter
                or digit after Markdown decoration is removed (headings, ">",
                "*", "_", "`", links, image syntax, HTML tags). Pure punctuation
                tokens ("—", "*", "|") are not words.

paragraph       A maximal run of consecutive non-blank lines inside a verse
                section, skipping structural separators: the "---" horizontal
                rules, the standalone "**Expanded Commentary**" label, and the
                end-of-sūrah marker lines. Blockquote lines count as paragraphs
                (a quotation is a paragraph); consecutive "> ..." lines form one
                paragraph, exactly as they form one blockquote.

bold mini-heading
                A standalone line whose entire content is bold, i.e. matches
                    **Heading**
                with an optional trailing ":" or ".".
                EXCLUDED (they are structural labels, not mini-headings):
                    - "**Expanded Commentary**"
                    - "**Verse Translation**" / "**Verse Translation:**"
                    - bracketed machine markers, e.g. "[End of the commentary…]"
                NOT COUNTED (they are inline labels inside a paragraph, not
                standalone headings): lines such as
                    **Modern Parallel:** In an age of disorder ...
                These are tallied separately in `inline_bold_labels` as a
                diagnostic, because a few chapters (e.g. 037) use that style
                instead of standalone mini-headings.

Usage:  python3 analysis/verse_metrics.py [--dir expanded] [--out analysis]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Iterable

# --------------------------------------------------------------------------
# Canonical Qur'an metadata (chapter names + canonical verse counts, 6236 total)
# --------------------------------------------------------------------------
CANONICAL_VERSES = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111,
    110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83,
    182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96,
    29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31,
    50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5,
    8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6,
]

CHAPTER_NAMES = [
    "Al-Fātiḥah", "Al-Baqarah", "Āl ʿImrān", "Al-Nisāʾ", "Al-Māʾidah", "Al-Anʿām",
    "Al-Aʿrāf", "Al-Anfāl", "Al-Tawbah", "Yūnus", "Hūd", "Yūsuf", "Al-Raʿd",
    "Ibrāhīm", "Al-Ḥijr", "Al-Naḥl", "Al-Isrāʾ", "Al-Kahf", "Maryam", "Ṭā Hā",
    "Al-Anbiyāʾ", "Al-Ḥajj", "Al-Muʾminūn", "Al-Nūr", "Al-Furqān", "Al-Shuʿarāʾ",
    "Al-Naml", "Al-Qaṣaṣ", "Al-ʿAnkabūt", "Al-Rūm", "Luqmān", "Al-Sajdah",
    "Al-Aḥzāb", "Sabaʾ", "Fāṭir", "Yā Sīn", "Al-Ṣaffāt", "Ṣād", "Al-Zumar",
    "Ghāfir", "Fuṣṣilat", "Al-Shūrā", "Al-Zukhruf", "Al-Dukhān", "Al-Jāthiyah",
    "Al-Aḥqāf", "Muḥammad", "Al-Fatḥ", "Al-Ḥujurāt", "Qāf", "Al-Dhāriyāt",
    "Al-Ṭūr", "Al-Najm", "Al-Qamar", "Al-Raḥmān", "Al-Wāqiʿah", "Al-Ḥadīd",
    "Al-Mujādilah", "Al-Ḥashr", "Al-Mumtaḥanah", "Al-Ṣaff", "Al-Jumuʿah",
    "Al-Munāfiqūn", "Al-Taghābun", "Al-Ṭalāq", "Al-Taḥrīm", "Al-Mulk", "Al-Qalam",
    "Al-Ḥāqqah", "Al-Maʿārij", "Nūḥ", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir",
    "Al-Qiyāmah", "Al-Insān", "Al-Mursalāt", "Al-Nabaʾ", "Al-Nāziʿāt", "ʿAbasa",
    "Al-Takwīr", "Al-Infiṭār", "Al-Muṭaffifīn", "Al-Inshiqāq", "Al-Burūj",
    "Al-Ṭāriq", "Al-Aʿlā", "Al-Ghāshiyah", "Al-Fajr", "Al-Balad", "Al-Shams",
    "Al-Layl", "Al-Ḍuḥā", "Al-Sharḥ", "Al-Tīn", "Al-ʿAlaq", "Al-Qadr",
    "Al-Bayyinah", "Al-Zalzalah", "Al-ʿĀdiyāt", "Al-Qāriʿah", "Al-Takāthur",
    "Al-ʿAṣr", "Al-Humazah", "Al-Fīl", "Quraysh", "Al-Māʿūn", "Al-Kawthar",
    "Al-Kāfirūn", "Al-Naṣr", "Al-Masad", "Al-Ikhlāṣ", "Al-Falaq", "Al-Nās",
]

# --------------------------------------------------------------------------
# Regexes
# --------------------------------------------------------------------------
H2_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)
VERSE_HEAD_PLAIN = re.compile(r"^(?P<name>.+?)\s+(?P<ch>\d{1,3}):(?P<vs>\d{1,3})$")
VERSE_HEAD_BRACKET = re.compile(r"^(?P<name>.+?)\s*\[(?P<ch>\d{1,3}):(?P<vs>\d{1,3})\]$")
BOLD_FULL_LINE = re.compile(r"^\*\*(?P<body>.+?)\*\*[:.\u2014-]?\s*$")
HR_RE = re.compile(r"^\s*(?:-{3,}|_{3,}|\*{3,})\s*$")
MARKDOWN_STRIP = [
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), " "),      # images
    (re.compile(r"\[([^\]]*)\]\([^)]*\)"), r"\1"),   # links -> label
    (re.compile(r"<[^>]{1,120}>"), " "),             # html tags
    (re.compile(r"[`*_~|#>]+"), " "),                # md decoration
]
TOKEN_HAS_WORD = re.compile(r"[0-9A-Za-z\u00C0-\u024F\u0370-\u03FF\u0400-\u04FF\u0590-\u06FF\u0900-\u097F\u4E00-\u9FFF\u1E00-\u1EFF\u2019]")

STRUCTURAL_LABELS = {
    "expanded commentary",
    "expanded commentary:",
    "verse translation",
    "verse translation:",
    "translation",
    "introduction",
    "introduction to the sūrah",
}


# --------------------------------------------------------------------------
# Dataclasses
# --------------------------------------------------------------------------
@dataclass
class VerseSection:
    chapter: int
    verse: int
    heading: str
    heading_format: str          # "plain" | "bracket"
    words: int
    words_no_translation: int
    paragraphs: int
    bold_headings: int
    inline_bold_labels: int
    blockquotes: int
    chars: int

    def as_row(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class ChapterMetrics:
    chapter: int
    name: str
    file: str
    canonical_verses: int
    verse_sections_found: int
    complete: bool
    missing_verses: int
    heading_format: str
    intro_words: int
    intro_paragraphs: int
    intro_bold_headings: int
    total_words: int
    total_paragraphs: int
    total_bold_headings: int
    total_inline_bold_labels: int
    avg_words_per_verse: float
    avg_paragraphs_per_verse: float
    avg_bold_headings_per_verse: float
    words_per_paragraph: float
    words_per_bold_heading: float
    words_per_verse_median: float
    min_words_verse: int
    max_words_verse: int
    stdev_words_verse: float
    verses_with_content: int = 0
    empty_verse_stubs: int = 0
    avg_words_per_verse_content: float = 0.0
    avg_paragraphs_per_verse_content: float = 0.0
    avg_bold_headings_per_verse_content: float = 0.0
    verses_on_target: int = 0        # filled after base is declared
    verses: list = field(default_factory=list, repr=False)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def read_text(path: str) -> str:
    with open(path, "rb") as fh:
        raw = fh.read()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc).replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def count_words(text: str) -> int:
    for rx, rep in MARKDOWN_STRIP:
        text = rx.sub(rep, text)
    parts = text.split()
    return sum(1 for p in parts if TOKEN_HAS_WORD.search(p))


def split_h2_sections(text: str) -> list[tuple[str, str]]:
    """Return [(heading_title, body_text)] for every '## ' section."""
    matches = list(H2_RE.finditer(text))
    out = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group("title"), text[start:end]))
    return out


def parse_verse_heading(title: str) -> tuple[int, int, str] | None:
    m = VERSE_HEAD_BRACKET.match(title)
    if m:
        return int(m.group("ch")), int(m.group("vs")), "bracket"
    m = VERSE_HEAD_PLAIN.match(title)
    if m:
        return int(m.group("ch")), int(m.group("vs")), "plain"
    return None


def body_lines(body: str) -> list[str]:
    lines = body.split("\n")
    # trim leading/trailing blanks
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def is_separator_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    return bool(HR_RE.match(s))


def is_structural_label(line: str) -> bool:
    s = line.strip()
    if s in ("**Expanded Commentary**", "**Expanded Commentary:**"):
        return True
    m = BOLD_FULL_LINE.match(s)
    if not m:
        return False
    body = m.group("body").strip().rstrip(":.").strip().lower()
    if body in STRUCTURAL_LABELS:
        return True
    if body.startswith("[") or body.startswith("end of"):
        return True
    return False


def measure_body(body: str) -> dict:
    """Words / paragraphs / bold mini-headings for one verse section body."""
    lines = body_lines(body)

    kept: list[str] = []
    for ln in lines:
        if not ln.strip():
            kept.append("")                     # keep blank as paragraph break
            continue
        if is_separator_line(ln):
            kept.append("")                     # '---' breaks the paragraph too
            continue
        if is_structural_label(ln):             # '**Expanded Commentary**' etc.
            kept.append("")
            continue
        kept.append(ln)

    # ---- paragraphs (maximal runs of non-blank lines) ----
    paragraphs, cur = 0, 0
    for ln in kept:
        if ln.strip():
            cur += 1
        else:
            if cur:
                paragraphs += 1
            cur = 0
    if cur:
        paragraphs += 1

    # ---- bold mini-headings (standalone fully-bold lines) ----
    headings = inline_labels = blockquotes = 0
    translation_words = 0
    seen_content = False             # leading blockquote run == the verse translation
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith(">"):
            blockquotes += 1
            if not seen_content:         # still inside the opening translation block
                translation_words += count_words(re.sub(r"^>\s*", "", s))
        else:
            seen_content = True
        m = BOLD_FULL_LINE.match(s)
        if m:
            if s.startswith(">"):               # blockquoted => label/quotation
                continue
            if is_structural_label(s):
                continue
            if re.match(r"^\*\*\[.*\]\*\*$", s):  # machine marker
                continue
            headings += 1
        else:
            # inline bold label at line start, e.g. '**Modern Parallel:** text'
            if re.match(r"^\*\*[^*]{1,80}[:.]\*\*\s+\S", s):
                inline_labels += 1

    body_text = "\n".join(lines)
    return {
        "words": count_words(body_text),
        "words_no_translation": max(0, count_words(body_text) - translation_words),
        "paragraphs": paragraphs,
        "bold_headings": headings,
        "inline_bold_labels": inline_labels,
        "blockquotes": blockquotes,
        "chars": len(body_text),
    }


# --------------------------------------------------------------------------
# Main analysis
# --------------------------------------------------------------------------
def analyse(directory: str) -> tuple[list[ChapterMetrics], list[VerseSection]]:
    files = sorted(f for f in os.listdir(directory) if f.endswith(".md"))
    chapters: list[ChapterMetrics] = []
    all_verses: list[VerseSection] = []

    for fname in files:
        m = re.search(r"(\d+)", fname)
        if not m:
            continue
        ch = int(m.group(1))
        path = os.path.join(directory, fname)
        text = read_text(path)
        sections = split_h2_sections(text)

        verse_objs: list[VerseSection] = []
        intro = {"words": 0, "paragraphs": 0, "bold_headings": 0}
        saw_verse = False
        fmt = "-"

        for title, body in sections:
            parsed = parse_verse_heading(title)
            if parsed is None:
                if not saw_verse:                     # front matter
                    mm = measure_body(body)
                    intro["words"] += mm["words"]
                    intro["paragraphs"] += mm["paragraphs"]
                    intro["bold_headings"] += mm["bold_headings"]
                continue
            c, v, f = parsed
            if c != ch:
                continue
            saw_verse = True
            fmt = f if fmt == "-" else ("mixed" if fmt != f else fmt)
            mm = measure_body(body)
            vs = VerseSection(
                chapter=ch, verse=v, heading=title, heading_format=f,
                words=mm["words"], words_no_translation=mm["words_no_translation"],
                paragraphs=mm["paragraphs"], bold_headings=mm["bold_headings"],
                inline_bold_labels=mm["inline_bold_labels"],
                blockquotes=mm["blockquotes"], chars=mm["chars"],
            )
            verse_objs.append(vs)

        if not verse_objs:
            continue

        n = len(verse_objs)
        words = [v.words for v in verse_objs]
        canon = CANONICAL_VERSES[ch - 1] if 1 <= ch <= 114 else 0
        cm = ChapterMetrics(
            chapter=ch,
            name=CHAPTER_NAMES[ch - 1] if 1 <= ch <= 114 else f"Chapter {ch}",
            file=os.path.join(directory, fname),
            canonical_verses=canon,
            verse_sections_found=n,
            complete=(n == canon),
            missing_verses=max(0, canon - n),
            heading_format=fmt,
            intro_words=intro["words"],
            intro_paragraphs=intro["paragraphs"],
            intro_bold_headings=intro["bold_headings"],
            total_words=sum(words),
            total_paragraphs=sum(v.paragraphs for v in verse_objs),
            total_bold_headings=sum(v.bold_headings for v in verse_objs),
            total_inline_bold_labels=sum(v.inline_bold_labels for v in verse_objs),
            avg_words_per_verse=round(statistics.fmean(words), 1),
            avg_paragraphs_per_verse=round(statistics.fmean([v.paragraphs for v in verse_objs]), 2),
            avg_bold_headings_per_verse=round(statistics.fmean([v.bold_headings for v in verse_objs]), 2),
            words_per_paragraph=0.0,
            words_per_bold_heading=0.0,
            words_per_verse_median=round(statistics.median(words), 1),
            min_words_verse=min(words),
            max_words_verse=max(words),
            stdev_words_verse=round(statistics.pstdev(words), 1) if n > 1 else 0.0,
            verses=verse_objs,
        )
        stamped = [v for v in verse_objs if v.words > 0]
        cm.verses_with_content = len(stamped)
        cm.empty_verse_stubs = n - len(stamped)
        if stamped:
            cm.avg_words_per_verse_content = round(statistics.fmean([v.words for v in stamped]), 1)
            cm.avg_paragraphs_per_verse_content = round(statistics.fmean([v.paragraphs for v in stamped]), 2)
            cm.avg_bold_headings_per_verse_content = round(statistics.fmean([v.bold_headings for v in stamped]), 2)
        tp = cm.total_paragraphs or 1
        tb = cm.total_bold_headings or 1
        cm.words_per_paragraph = round(cm.total_words / tp, 1)
        cm.words_per_bold_heading = round(cm.total_words / tb, 1)
        chapters.append(cm)
        all_verses.extend(verse_objs)

    return chapters, all_verses


def corpus_stats(chapters: list[ChapterMetrics], verses: list[VerseSection]) -> dict:
    def agg(attr: str, weighted_by_verses: bool = True):
        if weighted_by_verses:
            return statistics.fmean(getattr(v, attr) for v in verses)
        return statistics.fmean(getattr(c, attr) for c in chapters)

    w = [v.words for v in verses]
    p = [v.paragraphs for v in verses]
    b = [v.bold_headings for v in verses]
    per_chapter = {
        "avg_words_per_verse": [c.avg_words_per_verse for c in chapters],
        "avg_paragraphs_per_verse": [c.avg_paragraphs_per_verse for c in chapters],
        "avg_bold_headings_per_verse": [c.avg_bold_headings_per_verse for c in chapters],
    }

    def quants(xs: list[float]) -> dict:
        xs = sorted(xs)
        n = len(xs)

        def q(pct: float) -> float:
            if n == 1:
                return round(xs[0], 2)
            k = pct * (n - 1)
            lo, hi = int(k), min(int(k) + 1, n - 1)
            return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 2)

        return {
            "min": round(xs[0], 2), "p10": q(.10), "p25": q(.25),
            "median": round(statistics.median(xs), 2), "p75": q(.75),
            "p90": q(.90), "max": round(xs[-1], 2),
            "mean": round(statistics.fmean(xs), 2),
        }

    return {
        "n_chapters": len(chapters),
        "n_verse_sections": len(verses),
        "n_verses_canonical": sum(CANONICAL_VERSES),
        "verse_weighted": {
            "words_per_verse": round(statistics.fmean(w), 1),
            "paragraphs_per_verse": round(statistics.fmean(p), 2),
            "bold_headings_per_verse": round(statistics.fmean(b), 2),
            "median_words_per_verse": round(statistics.median(w), 1),
        },
        "chapter_level": {
            k: {"mean_of_chapter_averages": round(statistics.fmean(v), 2), **quants(v)}
            for k, v in per_chapter.items()
        },
        "totals": {
            "total_words": sum(c.total_words for c in chapters),
            "total_paragraphs": sum(c.total_paragraphs for c in chapters),
            "total_bold_headings": sum(c.total_bold_headings for c in chapters),
            "total_inline_bold_labels": sum(c.total_inline_bold_labels for c in chapters),
        },
    }


CSV_FIELDS = [
    "chapter", "name", "file", "canonical_verses", "verse_sections_found", "complete",
    "missing_verses", "heading_format",
    "avg_words_per_verse", "avg_paragraphs_per_verse", "avg_bold_headings_per_verse",
    "avg_words_per_verse_no_translation",
    "verses_with_content", "empty_verse_stubs",
    "avg_words_per_verse_content", "avg_paragraphs_per_verse_content",
    "avg_bold_headings_per_verse_content",
    "total_words", "total_paragraphs", "total_bold_headings",
    "words_per_paragraph", "words_per_bold_heading",
    "verse_median_words", "verse_min_words", "verse_max_words", "verse_stdev_words",
    "inline_bold_labels", "intro_words", "intro_paragraphs", "intro_bold_headings",
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="expanded")
    ap.add_argument("--out", default="analysis")
    args = ap.parse_args()

    chapters, verses = analyse(args.dir)
    os.makedirs(args.out, exist_ok=True)

    # ---- CSV ----
    csv_path = os.path.join(args.out, "expanded_chapter_metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for c in chapters:
            vs = c.verses
            writer.writerow({
                "chapter": c.chapter, "name": c.name, "file": c.file,
                "canonical_verses": c.canonical_verses,
                "verse_sections_found": c.verse_sections_found,
                "complete": c.complete, "missing_verses": c.missing_verses,
                "heading_format": c.heading_format,
                "avg_words_per_verse": c.avg_words_per_verse,
                "avg_paragraphs_per_verse": c.avg_paragraphs_per_verse,
                "avg_bold_headings_per_verse": c.avg_bold_headings_per_verse,
                "avg_words_per_verse_no_translation": round(
                    statistics.fmean([v.words_no_translation for v in vs]), 1),
                "verses_with_content": c.verses_with_content,
                "empty_verse_stubs": c.empty_verse_stubs,
                "avg_words_per_verse_content": c.avg_words_per_verse_content,
                "avg_paragraphs_per_verse_content": c.avg_paragraphs_per_verse_content,
                "avg_bold_headings_per_verse_content": c.avg_bold_headings_per_verse_content,
                "total_words": c.total_words, "total_paragraphs": c.total_paragraphs,
                "total_bold_headings": c.total_bold_headings,
                "words_per_paragraph": c.words_per_paragraph,
                "words_per_bold_heading": c.words_per_bold_heading,
                "verse_median_words": c.words_per_verse_median,
                "verse_min_words": c.min_words_verse, "verse_max_words": c.max_words_verse,
                "verse_stdev_words": c.stdev_words_verse,
                "inline_bold_labels": c.total_inline_bold_labels,
                "intro_words": c.intro_words, "intro_paragraphs": c.intro_paragraphs,
                "intro_bold_headings": c.intro_bold_headings,
            })

    # ---- per-verse CSV ----
    v_path = os.path.join(args.out, "expanded_verse_metrics.csv")
    with open(v_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["chapter", "verse", "heading_format", "words", "words_no_translation",
                    "paragraphs", "bold_headings", "inline_bold_labels", "blockquotes", "chars"])
        for v in verses:
            w.writerow([v.chapter, v.verse, v.heading_format, v.words,
                        v.words_no_translation, v.paragraphs, v.bold_headings,
                        v.inline_bold_labels, v.blockquotes, v.chars])

    # ---- JSON ----
    js_path = os.path.join(args.out, "expanded_metrics.json")
    with open(js_path, "w", encoding="utf-8") as fh:
        json.dump({
            "generated_from": args.dir,
            "corpus_stats": corpus_stats(chapters, verses),
            "chapters": [{k: v for k, v in asdict(c).items() if k != "verses"} for c in chapters],
        }, fh, ensure_ascii=False, indent=2)

    # ---- console summary ----
    cs = corpus_stats(chapters, verses)
    print(f"chapters: {cs['n_chapters']}   verse sections: {cs['n_verse_sections']}")
    print(f"verse-weighted  words/verse {cs['verse_weighted']['words_per_verse']:>7.1f}   "
          f"paras/verse {cs['verse_weighted']['paragraphs_per_verse']:>5.2f}   "
          f"headings/verse {cs['verse_weighted']['bold_headings_per_verse']:>5.2f}")
    for k, v in cs["chapter_level"].items():
        print(f"{k:>28}: mean {v['mean_of_chapter_averages']:>7.2f}  "
              f"median {v['median']:>7.2f}  p25 {v['p25']:>7.2f}  p75 {v['p75']:>7.2f}  "
              f"min {v['min']:>6.2f}  max {v['max']:>7.2f}")
    print("wrote:", csv_path, v_path, js_path, sep="\n  ")


if __name__ == "__main__":
    main()
