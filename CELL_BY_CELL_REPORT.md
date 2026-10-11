# NGSA geological map — v1 → v2 cell-by-cell comparison atlas

**Grid:** columns **A–L** (12), rows **1–7** (7) — 84 cells, Excel style, applied over the full
**6268 × 3540** px canvas. Cell size **522.3 × 505.7 px**.

Because `pic NGSA geological-map-of-nigeria-.jpg` is the *same* rendering, merely cropped at
offset **(dx = +120, dy = +96)**, the NGSA reference was cropped to that identical frame
(`pic_NGSA_grid.png`) so that **cell A1 means the same pixels in all three pictures**.

## What v2 changes

| item | value |
|---|---|
| geology (mapped) pixels | 9,413,388 (42.42%) |
| no-data (unmapped / non-geology sheet area) | 12,775,332 (57.58%) |
| overlay removed (graticule, labels, roads, edge fringe) | 1,014,171 (4.57%) |
| interior gaps filled | 97,777 (0.44%) |
| total pixels changed vs v1 | 1,523,857 (6.87%) |
| structural agreement v2 ↔ NGSA | **79.70%** |
| v2 shows geology where NGSA does not | 23,203 px (½-res) |
| NGSA shows geology where v2 does not | 315,551 px (½-res) |

**Legend for the per-cell connection lines**

- `aligned` — a unit sits on *both* sides of the shared cell edge at the *same* place:
  the feature is continuous across the border → **connection established**. Length in px of the shared edge segment.
- `offset` — the unit occurs on both sides of the border but not opposite itself: same unit continues
  into the neighbour, displaced. Check the neighbour to confirm.
- `ends` — the unit reaches the border of this cell but is **absent from the neighbour entirely**:
  the feature genuinely terminates at the cell edge.

---

## Unit palette (canonical flat colours taken from the map, ranked by area)

| id | colour | swatch | % of map area |
|---|---|---|---|
| U01 | `rgb(152, 218, 242)` | #98DAF2 | 12.158% |
| U02 | `rgb(240, 255, 90)` | #F0FF5A | 10.121% |
| U03 | `rgb(222, 211, 119)` | #DED377 | 9.892% |
| U04 | `rgb(255, 121, 127)` | #FF797F | 7.891% |
| U05 | `rgb(236, 255, 101)` | #ECFF65 | 5.635% |
| U06 | `rgb(255, 180, 76)` | #FFB44C | 5.123% |
| U07 | `rgb(121, 222, 176)` | #79DEB0 | 4.373% |
| U08 | `rgb(223, 196, 119)` | #DFC477 | 4.158% |
| U09 | `rgb(121, 193, 217)` | #79C1D9 | 2.807% |
| U10 | `rgb(253, 253, 190)` | #FDFDBE | 2.658% |
| U11 | `rgb(255, 142, 186)` | #FF8EBA | 2.629% |
| U12 | `rgb(236, 255, 77)` | #ECFF4D | 2.588% |
| U13 | `rgb(254, 253, 101)` | #FEFD65 | 2.324% |
| U14 | `rgb(218, 160, 0)` | #DAA000 | 2.030% |
| U15 | `rgb(163, 240, 102)` | #A3F066 | 1.552% |
| U16 | `rgb(155, 227, 89)` | #9BE359 | 1.321% |
| U17 | `rgb(138, 172, 95)` | #8AAC5F | 1.268% |
| U18 | `rgb(228, 229, 125)` | #E4E57D | 1.235% |
| U19 | `rgb(95, 163, 58)` | #5FA33A | 1.184% |
| U20 | `rgb(206, 255, 166)` | #CEFFA6 | 1.107% |
| U21 | `rgb(178, 227, 112)` | #B2E370 | 1.009% |
| U22 | `rgb(114, 193, 50)` | #72C132 | 0.864% |
| U23 | `rgb(156, 214, 189)` | #9CD6BD | 0.862% |
| U24 | `rgb(242, 246, 0)` | #F2F600 | 0.853% |
| U25 | `rgb(150, 170, 255)` | #96AAFF | 0.836% |
| U26 | `rgb(152, 214, 79)` | #98D64F | 0.824% |
| U27 | `rgb(158, 185, 230)` | #9EB9E6 | 0.693% |
| U28 | `rgb(255, 201, 224)` | #FFC9E0 | 0.681% |
| U29 | `rgb(132, 125, 252)` | #847DFC | 0.665% |
| U30 | `rgb(255, 112, 87)` | #FF7057 | 0.662% |
| U31 | `rgb(210, 244, 88)` | #D2F458 | 0.575% |
| U32 | `rgb(178, 209, 129)` | #B2D181 | 0.562% |
| U33 | `rgb(255, 155, 171)` | #FF9BAB | 0.559% |
| U34 | `rgb(218, 138, 227)` | #DA8AE3 | 0.552% |
| U35 | `rgb(229, 255, 168)` | #E5FFA8 | 0.526% |
| U36 | `rgb(252, 251, 77)` | #FCFB4D | 0.508% |
| U37 | `rgb(204, 223, 108)` | #CCDF6C | 0.504% |
| U38 | `rgb(218, 177, 49)` | #DAB131 | 0.479% |
| U39 | `rgb(121, 185, 255)` | #79B9FF | 0.457% |
| U40 | `rgb(188, 200, 184)` | #BCC8B8 | 0.420% |
| U41 | `rgb(214, 255, 133)` | #D6FF85 | 0.389% |
| U42 | `rgb(223, 255, 68)` | #DFFF44 | 0.356% |
| U43 | `rgb(216, 216, 252)` | #D8D8FC | 0.333% |
| U44 | `rgb(197, 244, 176)` | #C5F4B0 | 0.321% |
| U45 | `rgb(240, 255, 130)` | #F0FF82 | 0.306% |
| U46 | `rgb(255, 199, 212)` | #FFC7D4 | 0.306% |
| U47 | `rgb(185, 224, 109)` | #B9E06D | 0.300% |
| U48 | `rgb(223, 186, 116)` | #DFBA74 | 0.300% |
| U49 | `rgb(163, 252, 194)` | #A3FCC2 | 0.247% |
| U50 | `rgb(114, 223, 254)` | #72DFFE | 0.217% |
| U51 | `rgb(189, 236, 155)` | #BDEC9B | 0.168% |
| U52 | `rgb(179, 253, 183)` | #B3FDB7 | 0.166% |
| U53 | `rgb(217, 138, 225)` | #D98AE1 | 0.165% |
| U54 | `rgb(216, 178, 90)` | #D8B25A | 0.164% |
| U55 | `rgb(255, 115, 87)` | #FF7357 | 0.153% |
| U56 | `rgb(114, 215, 51)` | #72D733 | 0.149% |
| U57 | `rgb(182, 227, 151)` | #B6E397 | 0.146% |
| U58 | `rgb(204, 216, 108)` | #CCD86C | 0.141% |
| U59 | `rgb(177, 125, 68)` | #B17D44 | 0.132% |
| U60 | `rgb(255, 201, 69)` | #FFC945 | 0.130% |
| U61 | `rgb(231, 187, 248)` | #E7BBF8 | 0.089% |
| U62 | `rgb(193, 109, 39)` | #C16D27 | 0.069% |
| U63 | `rgb(122, 163, 255)` | #7AA3FF | 0.053% |
| U64 | `rgb(103, 116, 255)` | #6774FF | 0.051% |

---

## Cells, in working order (A1 → B1 → C1 … → L7)

### A1  —  x 0–522, y 0–506

- mapped geology **0.5%**, no-data **99.5%**, distinct units **1**
- v1 → v2: **15,956 px** changed (overlay removed 8,062, gaps filled 441)
- agreement with NGSA reference: **48.4%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 1,324 | 0.50% | 2 | 789 |

- **S → A2**
  - aligned (continuous): U01 8px
- **E → B1**
  - aligned (continuous): — none —
- **SE → B2**
  - *corner contact only (no shared edge)*
  - unit also present in the B2 corner: — none —

### B1  —  x 522–1045, y 0–506

- mapped geology **55.2%**, no-data **44.8%**, distinct units **7**
- v1 → v2: **17,381 px** changed (overlay removed 9,464, gaps filled 5,116)
- agreement with NGSA reference: **81.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U13 | #FEFD65 `rgb(254, 253, 101)` | 115,175 | 43.52% | 2 | 113,837 |
| U47 | #B9E06D `rgb(185, 224, 109)` | 17,812 | 6.73% | 3 | 9,750 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 6,252 | 2.36% | 4 | 2,960 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 3,061 | 1.16% | 5 | 953 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 2,202 | 0.83% | 1 | 2,201 |
| U23 | #9CD6BD `rgb(156, 214, 189)` | 1,297 | 0.49% | 1 | 1,297 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 158 | 0.06% | 0 | 74 |

- **W → A1**
  - aligned (continuous): — none —
- **SW → A2**
  - *corner contact only (no shared edge)*
  - unit also present in the A2 corner: — none —
- **S → B2**
  - aligned (continuous): U13 319px, U15 79px, U05 53px, U23 44px
- **E → C1**
  - aligned (continuous): U47 246px, U32 58px, U23 45px, U15 26px, U13 20px
- **SE → C2**
  - *corner contact only (no shared edge)*
  - unit also present in the C2 corner: U23

### C1  —  x 1045–1567, y 0–506

- mapped geology **66.9%**, no-data **33.1%**, distinct units **15**
- v1 → v2: **24,087 px** changed (overlay removed 17,351, gaps filled 5,652)
- agreement with NGSA reference: **75.3%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U23 | #9CD6BD `rgb(156, 214, 189)` | 52,463 | 19.86% | 2 | 41,205 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 33,129 | 12.54% | 5 | 13,562 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 23,961 | 9.07% | 2 | 23,469 |
| U49 | #A3FCC2 `rgb(163, 252, 194)` | 17,688 | 6.70% | 1 | 17,688 |
| U47 | #B9E06D `rgb(185, 224, 109)` | 11,893 | 4.50% | 4 | 9,998 |
| U51 | #BDEC9B `rgb(189, 236, 155)` | 10,827 | 4.10% | 1 | 10,827 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 8,643 | 3.27% | 2 | 7,265 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 6,457 | 2.44% | 7 | 2,218 |
| U13 | #FEFD65 `rgb(254, 253, 101)` | 4,967 | 1.88% | 4 | 2,335 |
| U39 | #79B9FF `rgb(121, 185, 255)` | 1,879 | 0.71% | 2 | 1,555 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 1,517 | 0.57% | 2 | 772 |
| U04 | #FF797F `rgb(255, 121, 127)` | 1,506 | 0.57% | 1 | 1,506 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 1,144 | 0.43% | 1 | 944 |
| U03 | #DED377 `rgb(222, 211, 119)` | 354 | 0.13% | 1 | 228 |

- **W → B1**
  - aligned (continuous): U47 246px, U32 58px, U23 45px, U15 26px, U13 20px
- **SW → B2**
  - *corner contact only (no shared edge)*
  - unit also present in the B2 corner: U23
- **S → C2**
  - aligned (continuous): U06 116px, U32 79px, U23 59px, U15 52px, U49 44px, U11 41px
- **E → D1**
  - aligned (continuous): U04 57px, U11 33px, U06 29px, U15 8px
- **SE → D2**
  - *corner contact only (no shared edge)*
  - unit also present in the D2 corner: U04, U11

### D1  —  x 1567–2089, y 0–506

- mapped geology **34.4%**, no-data **65.6%**, distinct units **9**
- v1 → v2: **18,895 px** changed (overlay removed 10,343, gaps filled 4)
- agreement with NGSA reference: **76.3%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U15 | #A3F066 `rgb(163, 240, 102)` | 37,182 | 14.08% | 1 | 36,967 |
| U04 | #FF797F `rgb(255, 121, 127)` | 35,057 | 13.27% | 3 | 30,691 |
| U03 | #DED377 `rgb(222, 211, 119)` | 5,856 | 2.22% | 1 | 5,850 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 4,603 | 1.74% | 1 | 4,603 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 3,535 | 1.34% | 3 | 2,267 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 1,870 | 0.71% | 2 | 1,293 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 1,402 | 0.53% | 1 | 1,401 |
| U02 | #F0FF5A `rgb(240, 255, 90)` | 1,060 | 0.40% | 1 | 1,060 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 210 | 0.08% | 1 | 210 |

- **W → C1**
  - aligned (continuous): U04 57px, U11 33px, U06 29px, U15 8px
- **SW → C2**
  - *corner contact only (no shared edge)*
  - unit also present in the C2 corner: U04, U11
  - not carried into C2 corner: U27
- **S → D2**
  - aligned (continuous): U04 317px, U27 70px, U03 33px, U33 29px, U02 27px, U11 22px
- **E → E1**
  - aligned (continuous): U15 78px, U02 56px
- **SE → E2**
  - *corner contact only (no shared edge)*
  - unit also present in the E2 corner: U02

### E1  —  x 2089–2612, y 0–506

- mapped geology **18.9%**, no-data **81.1%**, distinct units **7**
- v1 → v2: **23,320 px** changed (overlay removed 9,161, gaps filled 3,967)
- agreement with NGSA reference: **65.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 45,489 | 17.19% | 1 | 45,489 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 1,814 | 0.69% | 1 | 1,810 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 1,326 | 0.50% | 1 | 1,307 |
| U04 | #FF797F `rgb(255, 121, 127)` | 787 | 0.30% | 1 | 786 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 319 | 0.12% | 1 | 253 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 178 | 0.07% | 0 | 178 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 141 | 0.05% | 0 | 141 |

- **W → D1**
  - aligned (continuous): U15 78px, U02 56px
  - ends at edge (absent from D1): U04
- **SW → D2**
  - *corner contact only (no shared edge)*
  - unit also present in the D2 corner: U02
- **S → E2**
  - aligned (continuous): U02 523px
- **E → F1**
  - aligned (continuous): U02 143px, U34 44px
- **SE → F2**
  - *corner contact only (no shared edge)*
  - unit also present in the F2 corner: U02

### F1  —  x 2612–3134, y 0–506

- mapped geology **45.1%**, no-data **54.9%**, distinct units **4**
- v1 → v2: **8,540 px** changed (overlay removed 3,953, gaps filled 2)
- agreement with NGSA reference: **79.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 60,497 | 22.90% | 3 | 54,840 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 57,158 | 21.64% | 1 | 57,158 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 1,460 | 0.55% | 1 | 1,460 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 64 | 0.02% | 0 | 37 |

- **W → E1**
  - aligned (continuous): U02 143px, U34 44px
- **SW → E2**
  - *corner contact only (no shared edge)*
  - unit also present in the E2 corner: U02
- **S → F2**
  - aligned (continuous): U05 319px, U02 196px
- **E → G1**
  - aligned (continuous): U05 138px, U02 82px
- **SE → G2**
  - *corner contact only (no shared edge)*
  - unit also present in the G2 corner: U05

### G1  —  x 3134–3656, y 0–506

- mapped geology **45.4%**, no-data **54.6%**, distinct units **4**
- v1 → v2: **19,396 px** changed (overlay removed 9,493, gaps filled 6,742)
- agreement with NGSA reference: **84.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 86,189 | 32.63% | 2 | 78,654 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 25,838 | 9.78% | 1 | 25,838 |
| U01 | #98DAF2 `rgb(152, 218, 242)` | 7,905 | 2.99% | 1 | 7,905 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 88 | 0.03% | 0 | 88 |

- **W → F1**
  - aligned (continuous): U05 138px, U02 82px
- **SW → F2**
  - *corner contact only (no shared edge)*
  - unit also present in the F2 corner: U05
- **S → G2**
  - aligned (continuous): U02 458px, U05 64px
- **E → H1**
  - aligned (continuous): U02 280px, U01 132px
- **SE → H2**
  - *corner contact only (no shared edge)*
  - unit also present in the H2 corner: U02

### H1  —  x 3656–4179, y 0–506

- mapped geology **61.8%**, no-data **38.2%**, distinct units **2**
- v1 → v2: **32,573 px** changed (overlay removed 45,231, gaps filled 10,607)
- agreement with NGSA reference: **86.6%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 127,872 | 48.32% | 4 | 125,995 |
| U02 | #F0FF5A `rgb(240, 255, 90)` | 35,801 | 13.53% | 3 | 29,009 |

- **W → G1**
  - aligned (continuous): U02 280px, U01 132px
- **SW → G2**
  - *corner contact only (no shared edge)*
  - unit also present in the G2 corner: U02
- **S → H2**
  - aligned (continuous): U02 292px, U01 75px
- **E → I1**
  - aligned (continuous): — none —
- **SE → I2**
  - *corner contact only (no shared edge)*
  - unit also present in the I2 corner: — none —

### I1  —  x 4179–4701, y 0–506

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J1  —  x 4701–5223, y 0–506

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K1  —  x 5223–5746, y 0–506

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L1  —  x 5746–6268, y 0–506

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### A2  —  x 0–522, y 506–1011

- mapped geology **8.9%**, no-data **91.1%**, distinct units **6**
- v1 → v2: **22,340 px** changed (overlay removed 17,391, gaps filled 3,888)
- agreement with NGSA reference: **63.5%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U15 | #A3F066 `rgb(163, 240, 102)` | 8,507 | 3.23% | 1 | 8,407 |
| U13 | #FEFD65 `rgb(254, 253, 101)` | 6,023 | 2.28% | 1 | 6,015 |
| U01 | #98DAF2 `rgb(152, 218, 242)` | 5,906 | 2.24% | 5 | 4,108 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 1,591 | 0.60% | 1 | 1,591 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 938 | 0.36% | 1 | 436 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 453 | 0.17% | 1 | 453 |

- **N → A1**
  - aligned (continuous): U01 8px
- **S → A3**
  - aligned (continuous): — none —
  - offset (same unit, displaced): U15
- **NE → B1**
  - *corner contact only (no shared edge)*
  - unit also present in the B1 corner: — none —
- **E → B2**
  - aligned (continuous): U13 265px, U15 178px, U14 35px, U18 4px
- **SE → B3**
  - *corner contact only (no shared edge)*
  - unit also present in the B3 corner: U15
  - not carried into B3 corner: U14

### B2  —  x 522–1045, y 506–1011

- mapped geology **99.6%**, no-data **0.4%**, distinct units **28**
- v1 → v2: **15,284 px** changed (overlay removed 22,788, gaps filled 0)
- agreement with NGSA reference: **72.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U13 | #FEFD65 `rgb(254, 253, 101)` | 85,271 | 32.29% | 3 | 84,438 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 53,869 | 20.40% | 4 | 38,021 |
| U25 | #96AAFF `rgb(150, 170, 255)` | 27,325 | 10.35% | 1 | 27,303 |
| U03 | #DED377 `rgb(222, 211, 119)` | 22,793 | 8.63% | 3 | 11,976 |
| U23 | #9CD6BD `rgb(156, 214, 189)` | 18,376 | 6.96% | 1 | 18,375 |
| U56 | #72D733 `rgb(114, 215, 51)` | 14,041 | 5.32% | 4 | 7,429 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 11,078 | 4.19% | 15 | 2,764 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 8,483 | 3.21% | 2 | 8,219 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 4,508 | 1.71% | 4 | 2,742 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 3,588 | 1.36% | 1 | 3,588 |
| U51 | #BDEC9B `rgb(189, 236, 155)` | 2,893 | 1.10% | 1 | 2,893 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 1,994 | 0.75% | 3 | 645 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 1,892 | 0.72% | 3 | 847 |
| U04 | #FF797F `rgb(255, 121, 127)` | 1,183 | 0.45% | 1 | 1,183 |

- **NW → A1**
  - *corner contact only (no shared edge)*
  - unit also present in the A1 corner: — none —
  - not carried into A1 corner: U13
- **W → A2**
  - aligned (continuous): U13 265px, U15 178px, U14 35px, U18 4px
- **SW → A3**
  - *corner contact only (no shared edge)*
  - unit also present in the A3 corner: U15, U48
  - not carried into A3 corner: U06, U54
- **N → B1**
  - aligned (continuous): U13 319px, U15 79px, U05 53px, U23 44px
- **S → B3**
  - aligned (continuous): U07 83px, U09 83px, U46 50px, U15 46px, U08 40px, U25 34px
  - offset (same unit, displaced): U42
- **NE → C1**
  - *corner contact only (no shared edge)*
  - unit also present in the C1 corner: U23
- **E → C2**
  - aligned (continuous): U03 121px, U51 71px, U39 58px, U11 54px, U23 41px, U32 38px
- **SE → C3**
  - *corner contact only (no shared edge)*
  - unit also present in the C3 corner: U03

### C2  —  x 1045–1567, y 506–1011

- mapped geology **99.9%**, no-data **0.1%**, distinct units **23**
- v1 → v2: **13,886 px** changed (overlay removed 22,550, gaps filled 0)
- agreement with NGSA reference: **74.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U06 | #FFB44C `rgb(255, 180, 76)` | 68,482 | 25.98% | 8 | 37,710 |
| U39 | #79B9FF `rgb(121, 185, 255)` | 39,733 | 15.07% | 14 | 18,006 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 38,510 | 14.61% | 15 | 11,533 |
| U03 | #DED377 `rgb(222, 211, 119)` | 28,489 | 10.81% | 5 | 10,976 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 20,004 | 7.59% | 3 | 17,574 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 15,318 | 5.81% | 1 | 15,317 |
| U04 | #FF797F `rgb(255, 121, 127)` | 8,597 | 3.26% | 2 | 5,959 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 7,489 | 2.84% | 3 | 4,672 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 6,584 | 2.50% | 2 | 6,253 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 5,414 | 2.05% | 8 | 1,168 |
| U49 | #A3FCC2 `rgb(163, 252, 194)` | 4,641 | 1.76% | 1 | 4,641 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 4,060 | 1.54% | 2 | 2,601 |
| U23 | #9CD6BD `rgb(156, 214, 189)` | 3,552 | 1.35% | 2 | 2,958 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 2,885 | 1.09% | 3 | 1,667 |

- **NW → B1**
  - *corner contact only (no shared edge)*
  - unit also present in the B1 corner: U23
- **W → B2**
  - aligned (continuous): U03 121px, U51 71px, U39 58px, U11 54px, U23 41px, U32 38px
- **SW → B3**
  - *corner contact only (no shared edge)*
  - unit also present in the B3 corner: U03, U09
  - not carried into B3 corner: U50
- **N → C1**
  - aligned (continuous): U06 116px, U32 79px, U23 59px, U15 52px, U49 44px, U11 41px
- **S → C3**
  - aligned (continuous): U03 181px, U06 172px, U11 72px, U25 33px, U08 26px, U48 10px
- **NE → D1**
  - *corner contact only (no shared edge)*
  - unit also present in the D1 corner: U04, U11
- **E → D2**
  - aligned (continuous): U27 152px, U04 106px, U06 96px, U25 74px, U03 42px, U48 7px
  - offset (same unit, displaced): U40
- **SE → D3**
  - *corner contact only (no shared edge)*
  - unit also present in the D3 corner: U25
  - not carried into D3 corner: U04

### D2  —  x 1567–2089, y 506–1011

- mapped geology **100.0%**, no-data **0.0%**, distinct units **18**
- v1 → v2: **9,661 px** changed (overlay removed 19,848, gaps filled 0)
- agreement with NGSA reference: **76.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 81,063 | 30.75% | 6 | 51,419 |
| U04 | #FF797F `rgb(255, 121, 127)` | 65,269 | 24.76% | 16 | 14,945 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 38,586 | 14.64% | 11 | 17,051 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 26,540 | 10.07% | 4 | 13,349 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 24,515 | 9.30% | 2 | 20,565 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 5,862 | 2.22% | 7 | 1,703 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 5,288 | 2.01% | 9 | 1,658 |
| U02 | #F0FF5A `rgb(240, 255, 90)` | 4,663 | 1.77% | 1 | 4,663 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 4,189 | 1.59% | 3 | 2,287 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 3,579 | 1.36% | 1 | 3,579 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 1,551 | 0.59% | 2 | 331 |
| U25 | #96AAFF `rgb(150, 170, 255)` | 891 | 0.34% | 1 | 891 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 494 | 0.19% | 1 | 300 |
| U54 | #D8B25A `rgb(216, 178, 90)` | 371 | 0.14% | 0 | 144 |

- **NW → C1**
  - *corner contact only (no shared edge)*
  - unit also present in the C1 corner: U04, U11
  - not carried into C1 corner: U27
- **W → C2**
  - aligned (continuous): U27 152px, U04 106px, U06 96px, U25 74px, U03 42px, U48 7px
  - offset (same unit, displaced): U40
- **SW → C3**
  - *corner contact only (no shared edge)*
  - unit also present in the C3 corner: U25
  - not carried into C3 corner: U03
- **N → D1**
  - aligned (continuous): U04 317px, U27 70px, U03 33px, U33 29px, U02 27px, U11 22px
  - ends at edge (absent from D1): U45
- **S → D3**
  - aligned (continuous): U04 165px, U06 119px, U03 117px, U09 39px, U11 32px, U33 22px
- **NE → E1**
  - *corner contact only (no shared edge)*
  - unit also present in the E1 corner: U02
- **E → E2**
  - aligned (continuous): U04 320px, U02 98px, U33 48px, U11 10px
- **SE → E3**
  - *corner contact only (no shared edge)*
  - unit also present in the E3 corner: U04

### E2  —  x 2089–2612, y 506–1011

- mapped geology **99.8%**, no-data **0.2%**, distinct units **18**
- v1 → v2: **6,434 px** changed (overlay removed 11,786, gaps filled 0)
- agreement with NGSA reference: **77.3%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 126,355 | 47.84% | 2 | 124,628 |
| U04 | #FF797F `rgb(255, 121, 127)` | 74,347 | 28.15% | 4 | 68,001 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 28,199 | 10.68% | 4 | 16,347 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 14,129 | 5.35% | 3 | 10,676 |
| U03 | #DED377 `rgb(222, 211, 119)` | 11,800 | 4.47% | 2 | 9,858 |
| U53 | #D98AE1 `rgb(217, 138, 225)` | 2,718 | 1.03% | 5 | 878 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 2,569 | 0.97% | 6 | 458 |
| U40 | #BCC8B8 `rgb(188, 200, 184)` | 621 | 0.24% | 1 | 207 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 514 | 0.19% | 1 | 418 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 507 | 0.19% | 0 | 113 |
| U59 | #B17D44 `rgb(177, 125, 68)` | 431 | 0.16% | 1 | 431 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 395 | 0.15% | 0 | 138 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 314 | 0.12% | 1 | 314 |
| U61 | #E7BBF8 `rgb(231, 187, 248)` | 264 | 0.10% | 1 | 264 |

- **NW → D1**
  - *corner contact only (no shared edge)*
  - unit also present in the D1 corner: U02
- **W → D2**
  - aligned (continuous): U04 320px, U02 98px, U33 48px, U11 10px
- **SW → D3**
  - *corner contact only (no shared edge)*
  - unit also present in the D3 corner: U04
- **N → E1**
  - aligned (continuous): U02 523px
- **S → E3**
  - aligned (continuous): U04 227px, U11 168px, U61 35px, U34 21px, U06 19px, U33 19px
- **NE → F1**
  - *corner contact only (no shared edge)*
  - unit also present in the F1 corner: U02
- **E → F2**
  - aligned (continuous): U02 207px, U05 144px, U04 123px, U34 29px
- **SE → F3**
  - *corner contact only (no shared edge)*
  - unit also present in the F3 corner: U04, U34

### F2  —  x 2612–3134, y 506–1011

- mapped geology **100.0%**, no-data **0.0%**, distinct units **9**
- v1 → v2: **1,886 px** changed (overlay removed 4,722, gaps filled 0)
- agreement with NGSA reference: **82.9%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 115,344 | 43.76% | 4 | 65,340 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 64,578 | 24.50% | 3 | 58,666 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 53,358 | 20.24% | 2 | 33,673 |
| U04 | #FF797F `rgb(255, 121, 127)` | 15,147 | 5.75% | 1 | 15,147 |
| U35 | #E5FFA8 `rgb(229, 255, 168)` | 7,084 | 2.69% | 2 | 6,355 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 5,841 | 2.22% | 1 | 5,769 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 1,291 | 0.49% | 1 | 1,291 |
| U22 | #72C132 `rgb(114, 193, 50)` | 811 | 0.31% | 1 | 750 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 63 | 0.02% | 0 | 63 |

- **NW → E1**
  - *corner contact only (no shared edge)*
  - unit also present in the E1 corner: U02
- **W → E2**
  - aligned (continuous): U02 207px, U05 144px, U04 123px, U34 29px
- **SW → E3**
  - *corner contact only (no shared edge)*
  - unit also present in the E3 corner: U34
- **N → F1**
  - aligned (continuous): U05 319px, U02 196px
- **S → F3**
  - aligned (continuous): U12 219px, U04 90px, U35 83px, U22 46px, U07 36px, U34 16px
  - offset (same unit, displaced): U19
- **NE → G1**
  - *corner contact only (no shared edge)*
  - unit also present in the G1 corner: U05
- **E → G2**
  - aligned (continuous): U02 299px, U07 124px, U05 68px, U19 7px
  - offset (same unit, displaced): U22
- **SE → G3**
  - *corner contact only (no shared edge)*
  - unit also present in the G3 corner: U07, U22
  - not carried into G3 corner: U19

### G2  —  x 3134–3656, y 506–1011

- mapped geology **100.0%**, no-data **0.0%**, distinct units **12**
- v1 → v2: **1,411 px** changed (overlay removed 2,605, gaps filled 0)
- agreement with NGSA reference: **83.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 219,880 | 83.41% | 1 | 219,880 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 24,071 | 9.13% | 1 | 24,071 |
| U04 | #FF797F `rgb(255, 121, 127)` | 7,021 | 2.66% | 2 | 3,705 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 5,794 | 2.20% | 1 | 5,794 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 2,761 | 1.05% | 1 | 2,761 |
| U29 | #847DFC `rgb(132, 125, 252)` | 2,666 | 1.01% | 1 | 2,657 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 700 | 0.27% | 1 | 642 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 218 | 0.08% | 0 | 121 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 126 | 0.05% | 0 | 49 |
| U37 | #CCDF6C `rgb(204, 223, 108)` | 125 | 0.05% | 0 | 75 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 103 | 0.04% | 0 | 62 |
| U22 | #72C132 `rgb(114, 193, 50)` | 58 | 0.02% | 0 | 53 |

- **NW → F1**
  - *corner contact only (no shared edge)*
  - unit also present in the F1 corner: U05
- **W → F2**
  - aligned (continuous): U02 299px, U07 124px, U05 68px, U19 7px
  - offset (same unit, displaced): U22
- **SW → F3**
  - *corner contact only (no shared edge)*
  - unit also present in the F3 corner: U07, U19, U22
- **N → G1**
  - aligned (continuous): U02 458px, U05 64px
- **S → G3**
  - aligned (continuous): U12 190px, U17 120px, U29 101px, U04 54px, U07 31px, U14 6px
- **NE → H1**
  - *corner contact only (no shared edge)*
  - unit also present in the H1 corner: U02
- **E → H2**
  - aligned (continuous): U02 480px, U12 25px
- **SE → H3**
  - *corner contact only (no shared edge)*
  - unit also present in the H3 corner: U12

### H2  —  x 3656–4179, y 506–1011

- mapped geology **76.3%**, no-data **23.7%**, distinct units **6**
- v1 → v2: **14,051 px** changed (overlay removed 8,396, gaps filled 6,503)
- agreement with NGSA reference: **82.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U02 | #F0FF5A `rgb(240, 255, 90)` | 197,184 | 74.66% | 3 | 193,716 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 1,691 | 0.64% | 1 | 1,691 |
| U01 | #98DAF2 `rgb(152, 218, 242)` | 1,091 | 0.41% | 2 | 728 |
| U04 | #FF797F `rgb(255, 121, 127)` | 684 | 0.26% | 1 | 579 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 575 | 0.22% | 1 | 575 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 134 | 0.05% | 0 | 102 |

- **NW → G1**
  - *corner contact only (no shared edge)*
  - unit also present in the G1 corner: U02
- **W → G2**
  - aligned (continuous): U02 480px, U12 25px
- **SW → G3**
  - *corner contact only (no shared edge)*
  - unit also present in the G3 corner: U12
- **N → H1**
  - aligned (continuous): U02 292px, U01 75px
- **S → H3**
  - aligned (continuous): U07 90px, U02 55px, U04 52px, U12 39px, U33 4px
- **NE → I1**
  - *corner contact only (no shared edge)*
  - unit also present in the I1 corner: — none —
- **E → I2**
  - aligned (continuous): — none —
- **SE → I3**
  - *corner contact only (no shared edge)*
  - unit also present in the I3 corner: — none —

### I2  —  x 4179–4701, y 506–1011

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J2  —  x 4701–5223, y 506–1011

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K2  —  x 5223–5746, y 506–1011

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L2  —  x 5746–6268, y 506–1011

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### A3  —  x 0–522, y 1011–1517

- mapped geology **8.4%**, no-data **91.6%**, distinct units **11**
- v1 → v2: **22,227 px** changed (overlay removed 17,989, gaps filled 2,843)
- agreement with NGSA reference: **70.9%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U04 | #FF797F `rgb(255, 121, 127)` | 10,991 | 4.16% | 3 | 4,961 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 4,671 | 1.77% | 2 | 3,842 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 2,074 | 0.79% | 1 | 1,871 |
| U03 | #DED377 `rgb(222, 211, 119)` | 1,721 | 0.65% | 1 | 1,645 |
| U50 | #72DFFE `rgb(114, 223, 254)` | 1,328 | 0.50% | 1 | 1,328 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 639 | 0.24% | 1 | 444 |
| U54 | #D8B25A `rgb(216, 178, 90)` | 205 | 0.08% | 1 | 205 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 185 | 0.07% | 0 | 139 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 163 | 0.06% | 0 | 163 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 131 | 0.05% | 0 | 131 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 80 | 0.03% | 0 | 61 |

- **N → A2**
  - aligned (continuous): — none —
  - offset (same unit, displaced): U15
- **S → A4**
  - aligned (continuous): U38 76px, U04 34px, U50 20px, U14 15px, U54 9px, U06 4px
- **NE → B2**
  - *corner contact only (no shared edge)*
  - unit also present in the B2 corner: U15, U48
- **E → B3**
  - aligned (continuous): U48 120px, U06 109px, U04 44px, U11 26px, U50 16px
  - offset (same unit, displaced): U15
- **SE → B4**
  - *corner contact only (no shared edge)*
  - unit also present in the B4 corner: U06, U14
  - not carried into B4 corner: U50

### B3  —  x 522–1045, y 1011–1517

- mapped geology **96.6%**, no-data **3.4%**, distinct units **21**
- v1 → v2: **18,417 px** changed (overlay removed 26,480, gaps filled 56)
- agreement with NGSA reference: **76.5%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U07 | #79DEB0 `rgb(121, 222, 176)` | 69,147 | 26.13% | 4 | 43,518 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 54,443 | 20.57% | 9 | 46,125 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 34,493 | 13.03% | 4 | 14,613 |
| U03 | #DED377 `rgb(222, 211, 119)` | 21,643 | 8.18% | 4 | 12,867 |
| U54 | #D8B25A `rgb(216, 178, 90)` | 10,764 | 4.07% | 2 | 7,262 |
| U25 | #96AAFF `rgb(150, 170, 255)` | 10,629 | 4.02% | 3 | 9,920 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 9,686 | 3.66% | 6 | 2,348 |
| U04 | #FF797F `rgb(255, 121, 127)` | 8,154 | 3.08% | 4 | 3,661 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 6,528 | 2.47% | 7 | 1,882 |
| U55 | #FF7357 `rgb(255, 115, 87)` | 5,431 | 2.05% | 5 | 2,158 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 5,318 | 2.01% | 6 | 2,726 |
| U50 | #72DFFE `rgb(114, 223, 254)` | 5,136 | 1.94% | 6 | 1,424 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 3,415 | 1.29% | 2 | 2,560 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 2,599 | 0.98% | 4 | 1,434 |

- **NW → A2**
  - *corner contact only (no shared edge)*
  - unit also present in the A2 corner: U15
  - not carried into A2 corner: U06, U48
- **W → A3**
  - aligned (continuous): U48 120px, U06 109px, U04 44px, U11 26px, U50 16px
  - offset (same unit, displaced): U15
- **SW → A4**
  - *corner contact only (no shared edge)*
  - unit also present in the A4 corner: U06
- **N → B2**
  - aligned (continuous): U07 83px, U09 83px, U46 50px, U15 46px, U08 40px, U25 34px
  - offset (same unit, displaced): U42
- **S → B4**
  - aligned (continuous): U07 184px, U03 121px, U06 97px, U55 57px, U08 48px, U09 9px
  - ends at edge (absent from B4): U48
- **NE → C2**
  - *corner contact only (no shared edge)*
  - unit also present in the C2 corner: U03, U09
  - not carried into C2 corner: U08
- **E → C3**
  - aligned (continuous): U07 262px, U03 127px, U11 57px, U04 26px, U09 25px
  - offset (same unit, displaced): U08
  - ends at edge (absent from C3): U50
- **SE → C4**
  - *corner contact only (no shared edge)*
  - unit also present in the C4 corner: U07

### C3  —  x 1045–1567, y 1011–1517

- mapped geology **100.0%**, no-data **0.0%**, distinct units **27**
- v1 → v2: **13,211 px** changed (overlay removed 22,828, gaps filled 0)
- agreement with NGSA reference: **78.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 62,003 | 23.47% | 4 | 48,817 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 51,312 | 19.43% | 2 | 50,905 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 29,547 | 11.19% | 10 | 13,276 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 25,817 | 9.77% | 7 | 11,138 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 23,445 | 8.88% | 2 | 22,399 |
| U04 | #FF797F `rgb(255, 121, 127)` | 17,478 | 6.62% | 17 | 4,433 |
| U60 | #FFC945 `rgb(255, 201, 69)` | 12,309 | 4.66% | 2 | 11,906 |
| U25 | #96AAFF `rgb(150, 170, 255)` | 8,183 | 3.10% | 2 | 5,607 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 7,560 | 2.86% | 2 | 6,790 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 5,582 | 2.11% | 3 | 3,450 |
| U63 | #7AA3FF `rgb(122, 163, 255)` | 5,173 | 1.96% | 3 | 3,055 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 4,420 | 1.67% | 4 | 1,943 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 2,306 | 0.87% | 4 | 764 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 2,046 | 0.77% | 4 | 643 |

- **NW → B2**
  - *corner contact only (no shared edge)*
  - unit also present in the B2 corner: U03
  - not carried into B2 corner: U08, U09, U50
- **W → B3**
  - aligned (continuous): U07 262px, U03 127px, U11 57px, U04 26px, U09 25px
  - offset (same unit, displaced): U08
- **SW → B4**
  - *corner contact only (no shared edge)*
  - unit also present in the B4 corner: U07
- **N → C2**
  - aligned (continuous): U03 181px, U06 172px, U11 72px, U25 33px, U08 26px, U48 10px
- **S → C4**
  - aligned (continuous): U07 307px, U04 84px, U46 67px, U08 34px, U05 11px, U09 4px
- **NE → D2**
  - *corner contact only (no shared edge)*
  - unit also present in the D2 corner: U25
- **E → D3**
  - aligned (continuous): U04 132px, U09 102px, U25 93px, U03 90px, U08 32px, U11 24px
- **SE → D4**
  - *corner contact only (no shared edge)*
  - unit also present in the D4 corner: U04
  - not carried into D4 corner: U46

### D3  —  x 1567–2089, y 1011–1517

- mapped geology **100.0%**, no-data **0.0%**, distinct units **17**
- v1 → v2: **9,044 px** changed (overlay removed 16,574, gaps filled 0)
- agreement with NGSA reference: **80.7%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 104,823 | 39.69% | 3 | 90,151 |
| U04 | #FF797F `rgb(255, 121, 127)` | 47,763 | 18.08% | 18 | 9,601 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 47,239 | 17.88% | 4 | 39,824 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 18,323 | 6.94% | 10 | 9,848 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 15,861 | 6.00% | 5 | 6,734 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 6,910 | 2.62% | 2 | 5,177 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 6,471 | 2.45% | 5 | 5,219 |
| U25 | #96AAFF `rgb(150, 170, 255)` | 4,297 | 1.63% | 5 | 2,433 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 3,719 | 1.41% | 2 | 2,254 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 2,492 | 0.94% | 1 | 2,198 |
| U53 | #D98AE1 `rgb(217, 138, 225)` | 2,124 | 0.80% | 1 | 1,932 |
| U61 | #E7BBF8 `rgb(231, 187, 248)` | 1,359 | 0.51% | 1 | 1,359 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 1,081 | 0.41% | 2 | 616 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 602 | 0.23% | 1 | 602 |

- **NW → C2**
  - *corner contact only (no shared edge)*
  - unit also present in the C2 corner: U25
  - not carried into C2 corner: U03
- **W → C3**
  - aligned (continuous): U04 132px, U09 102px, U25 93px, U03 90px, U08 32px, U11 24px
- **SW → C4**
  - *corner contact only (no shared edge)*
  - unit also present in the C4 corner: U04
- **N → D2**
  - aligned (continuous): U04 165px, U06 119px, U03 117px, U09 39px, U11 32px, U33 22px
- **S → D4**
  - aligned (continuous): U09 143px, U04 142px, U03 90px, U06 53px, U27 48px, U34 29px
  - ends at edge (absent from D4): U33
- **NE → E2**
  - *corner contact only (no shared edge)*
  - unit also present in the E2 corner: U04
- **E → E3**
  - aligned (continuous): U03 266px, U04 68px, U34 56px, U27 35px, U46 32px, U61 18px
- **SE → E4**
  - *corner contact only (no shared edge)*
  - unit also present in the E4 corner: U34

### E3  —  x 2089–2612, y 1011–1517

- mapped geology **98.8%**, no-data **1.2%**, distinct units **17**
- v1 → v2: **23,111 px** changed (overlay removed 33,108, gaps filled 0)
- agreement with NGSA reference: **70.9%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U04 | #FF797F `rgb(255, 121, 127)` | 86,360 | 32.63% | 13 | 25,829 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 67,961 | 25.68% | 12 | 52,108 |
| U03 | #DED377 `rgb(222, 211, 119)` | 26,534 | 10.03% | 4 | 16,502 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 22,492 | 8.50% | 5 | 17,713 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 20,419 | 7.72% | 4 | 18,095 |
| U53 | #D98AE1 `rgb(217, 138, 225)` | 9,958 | 3.76% | 9 | 2,305 |
| U61 | #E7BBF8 `rgb(231, 187, 248)` | 6,977 | 2.64% | 4 | 4,422 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 5,542 | 2.09% | 4 | 1,825 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 4,010 | 1.52% | 3 | 1,672 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 3,046 | 1.15% | 1 | 3,007 |
| U59 | #B17D44 `rgb(177, 125, 68)` | 2,366 | 0.89% | 3 | 947 |
| U29 | #847DFC `rgb(132, 125, 252)` | 2,360 | 0.89% | 2 | 1,453 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 1,661 | 0.63% | 3 | 368 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 1,122 | 0.42% | 2 | 259 |

- **NW → D2**
  - *corner contact only (no shared edge)*
  - unit also present in the D2 corner: U04
- **W → D3**
  - aligned (continuous): U03 266px, U04 68px, U34 56px, U27 35px, U46 32px, U61 18px
- **SW → D4**
  - *corner contact only (no shared edge)*
  - unit also present in the D4 corner: U34
  - not carried into D4 corner: U27
- **N → E2**
  - aligned (continuous): U04 227px, U11 168px, U61 35px, U34 21px, U06 19px, U33 19px
- **S → E4**
  - aligned (continuous): U34 139px, U04 124px, U46 75px, U03 53px, U06 53px, U29 17px
- **NE → F2**
  - *corner contact only (no shared edge)*
  - unit also present in the F2 corner: U34
  - not carried into F2 corner: U04
- **E → F3**
  - aligned (continuous): U04 238px, U06 137px, U59 75px, U03 33px, U33 9px, U34 8px
- **SE → F4**
  - *corner contact only (no shared edge)*
  - unit also present in the F4 corner: U03

### F3  —  x 2612–3134, y 1011–1517

- mapped geology **100.0%**, no-data **0.0%**, distinct units **20**
- v1 → v2: **5,739 px** changed (overlay removed 12,433, gaps filled 0)
- agreement with NGSA reference: **78.6%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U12 | #ECFF4D `rgb(236, 255, 77)` | 122,853 | 46.51% | 1 | 122,662 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 42,817 | 16.21% | 3 | 37,724 |
| U35 | #E5FFA8 `rgb(229, 255, 168)` | 33,243 | 12.59% | 8 | 16,296 |
| U04 | #FF797F `rgb(255, 121, 127)` | 24,128 | 9.13% | 6 | 18,500 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 15,183 | 5.75% | 4 | 11,202 |
| U22 | #72C132 `rgb(114, 193, 50)` | 9,836 | 3.72% | 8 | 2,184 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 4,798 | 1.82% | 2 | 3,969 |
| U59 | #B17D44 `rgb(177, 125, 68)` | 4,364 | 1.65% | 3 | 2,146 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 3,274 | 1.24% | 4 | 1,346 |
| U15 | #A3F066 `rgb(163, 240, 102)` | 1,189 | 0.45% | 1 | 1,189 |
| U03 | #DED377 `rgb(222, 211, 119)` | 773 | 0.29% | 1 | 773 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 432 | 0.16% | 1 | 332 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 333 | 0.13% | 0 | 197 |
| U29 | #847DFC `rgb(132, 125, 252)` | 309 | 0.12% | 1 | 309 |

- **NW → E2**
  - *corner contact only (no shared edge)*
  - unit also present in the E2 corner: U04, U34
- **W → E3**
  - aligned (continuous): U04 238px, U06 137px, U59 75px, U03 33px, U33 9px, U34 8px
- **SW → E4**
  - *corner contact only (no shared edge)*
  - unit also present in the E4 corner: U03
  - not carried into E4 corner: U12
- **N → F2**
  - aligned (continuous): U12 219px, U04 90px, U35 83px, U22 46px, U07 36px, U34 16px
  - offset (same unit, displaced): U19
- **S → F4**
  - aligned (continuous): U17 282px, U12 102px, U35 71px, U23 20px, U05 16px, U03 14px
- **NE → G2**
  - *corner contact only (no shared edge)*
  - unit also present in the G2 corner: U07, U19, U22
- **E → G3**
  - aligned (continuous): U17 280px, U22 86px, U07 77px, U04 24px, U29 10px, U35 4px
  - ends at edge (absent from G3): U15
- **SE → G4**
  - *corner contact only (no shared edge)*
  - unit also present in the G4 corner: U17

### G3  —  x 3134–3656, y 1011–1517

- mapped geology **100.0%**, no-data **0.0%**, distinct units **18**
- v1 → v2: **6,327 px** changed (overlay removed 13,736, gaps filled 109)
- agreement with NGSA reference: **85.7%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U04 | #FF797F `rgb(255, 121, 127)` | 80,711 | 30.56% | 10 | 69,430 |
| U03 | #DED377 `rgb(222, 211, 119)` | 59,980 | 22.71% | 1 | 59,980 |
| U29 | #847DFC `rgb(132, 125, 252)` | 46,948 | 17.77% | 2 | 44,551 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 27,036 | 10.24% | 5 | 14,278 |
| U22 | #72C132 `rgb(114, 193, 50)` | 18,098 | 6.85% | 6 | 13,699 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 10,683 | 4.04% | 4 | 5,888 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 4,809 | 1.82% | 2 | 3,284 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 4,579 | 1.73% | 4 | 2,474 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 3,008 | 1.14% | 3 | 1,617 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 2,034 | 0.77% | 4 | 395 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 1,959 | 0.74% | 2 | 1,450 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 1,637 | 0.62% | 1 | 1,421 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 1,306 | 0.49% | 1 | 1,122 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 596 | 0.23% | 1 | 449 |

- **NW → F2**
  - *corner contact only (no shared edge)*
  - unit also present in the F2 corner: U07, U22
- **W → F3**
  - aligned (continuous): U17 280px, U22 86px, U07 77px, U04 24px, U29 10px, U35 4px
  - ends at edge (absent from F3): U40
- **SW → F4**
  - *corner contact only (no shared edge)*
  - unit also present in the F4 corner: U05, U17
- **N → G2**
  - aligned (continuous): U12 190px, U17 120px, U29 101px, U04 54px, U07 31px, U14 6px
- **S → G4**
  - aligned (continuous): U22 222px, U05 162px, U03 98px, U04 24px, U17 7px
- **NE → H2**
  - *corner contact only (no shared edge)*
  - unit also present in the H2 corner: U12
  - not carried into H2 corner: U04
- **E → H3**
  - aligned (continuous): U04 466px, U12 7px
- **SE → H4**
  - *corner contact only (no shared edge)*
  - unit also present in the H4 corner: — none —
  - not carried into H4 corner: U04

### H3  —  x 3656–4179, y 1011–1517

- mapped geology **16.5%**, no-data **83.5%**, distinct units **7**
- v1 → v2: **22,125 px** changed (overlay removed 17,978, gaps filled 6,233)
- agreement with NGSA reference: **78.4%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U04 | #FF797F `rgb(255, 121, 127)` | 38,819 | 14.67% | 3 | 35,946 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 1,496 | 0.57% | 2 | 1,028 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 1,465 | 0.55% | 1 | 1,465 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 700 | 0.26% | 1 | 699 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 679 | 0.26% | 3 | 240 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 311 | 0.12% | 1 | 311 |
| U02 | #F0FF5A `rgb(240, 255, 90)` | 282 | 0.11% | 1 | 249 |

- **NW → G2**
  - *corner contact only (no shared edge)*
  - unit also present in the G2 corner: U12
  - not carried into G2 corner: U04
- **W → G3**
  - aligned (continuous): U04 466px, U12 7px
- **SW → G4**
  - *corner contact only (no shared edge)*
  - unit also present in the G4 corner: — none —
- **N → H2**
  - aligned (continuous): U07 90px, U02 55px, U04 52px, U12 39px, U33 4px
- **S → H4**
  - aligned (continuous): — none —
- **NE → I2**
  - *corner contact only (no shared edge)*
  - unit also present in the I2 corner: — none —
- **E → I3**
  - aligned (continuous): — none —
- **SE → I4**
  - *corner contact only (no shared edge)*
  - unit also present in the I4 corner: — none —

### I3  —  x 4179–4701, y 1011–1517

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J3  —  x 4701–5223, y 1011–1517

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K3  —  x 5223–5746, y 1011–1517

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L3  —  x 5746–6268, y 1011–1517

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### A4  —  x 0–522, y 1517–2023

- mapped geology **53.9%**, no-data **46.1%**, distinct units **15**
- v1 → v2: **16,532 px** changed (overlay removed 16,089, gaps filled 1,339)
- agreement with NGSA reference: **76.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U11 | #FF8EBA `rgb(255, 142, 186)` | 55,240 | 20.91% | 4 | 49,591 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 33,402 | 12.65% | 8 | 18,242 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 10,772 | 4.08% | 5 | 3,616 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 10,051 | 3.81% | 4 | 5,540 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 7,521 | 2.85% | 3 | 3,711 |
| U50 | #72DFFE `rgb(114, 223, 254)` | 7,452 | 2.82% | 3 | 5,649 |
| U03 | #DED377 `rgb(222, 211, 119)` | 5,750 | 2.18% | 3 | 2,283 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 4,505 | 1.71% | 1 | 4,505 |
| U04 | #FF797F `rgb(255, 121, 127)` | 3,346 | 1.27% | 3 | 1,946 |
| U55 | #FF7357 `rgb(255, 115, 87)` | 1,874 | 0.71% | 1 | 1,683 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 1,125 | 0.43% | 1 | 1,125 |
| U54 | #D8B25A `rgb(216, 178, 90)` | 725 | 0.27% | 2 | 397 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 340 | 0.13% | 0 | 138 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 244 | 0.09% | 0 | 85 |

- **N → A3**
  - aligned (continuous): U38 76px, U04 34px, U50 20px, U14 15px, U54 9px, U06 4px
- **S → A5**
  - aligned (continuous): U09 95px, U50 70px, U11 42px, U14 35px, U03 33px, U30 32px
- **NE → B3**
  - *corner contact only (no shared edge)*
  - unit also present in the B3 corner: U06
  - not carried into B3 corner: U14
- **E → B4**
  - aligned (continuous): U14 143px, U38 123px, U03 98px, U09 56px, U55 45px, U06 21px
- **SE → B5**
  - *corner contact only (no shared edge)*
  - unit also present in the B5 corner: U03
  - not carried into B5 corner: U50

### B4  —  x 522–1045, y 1517–2023

- mapped geology **100.0%**, no-data **0.0%**, distinct units **28**
- v1 → v2: **12,180 px** changed (overlay removed 21,864, gaps filled 0)
- agreement with NGSA reference: **75.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 74,103 | 28.00% | 4 | 65,472 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 36,151 | 13.66% | 6 | 16,329 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 33,502 | 12.66% | 2 | 32,751 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 30,965 | 11.70% | 8 | 22,736 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 20,250 | 7.65% | 6 | 9,443 |
| U04 | #FF797F `rgb(255, 121, 127)` | 15,071 | 5.69% | 13 | 3,553 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 12,508 | 4.73% | 8 | 6,373 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 6,840 | 2.58% | 4 | 2,544 |
| U55 | #FF7357 `rgb(255, 115, 87)` | 6,533 | 2.47% | 2 | 5,419 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 6,219 | 2.35% | 2 | 5,759 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 5,169 | 1.95% | 5 | 2,656 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 3,202 | 1.21% | 1 | 3,105 |
| U50 | #72DFFE `rgb(114, 223, 254)` | 2,837 | 1.07% | 1 | 2,837 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 2,539 | 0.96% | 2 | 1,641 |

- **NW → A3**
  - *corner contact only (no shared edge)*
  - unit also present in the A3 corner: U06, U14
- **W → A4**
  - aligned (continuous): U14 143px, U38 123px, U03 98px, U09 56px, U55 45px, U06 21px
- **SW → A5**
  - *corner contact only (no shared edge)*
  - unit also present in the A5 corner: U03
  - not carried into A5 corner: U06
- **N → B3**
  - aligned (continuous): U07 184px, U03 121px, U06 97px, U55 57px, U08 48px, U09 9px
- **S → B5**
  - aligned (continuous): U03 292px, U04 69px, U09 69px, U06 30px, U14 26px, U48 8px
- **NE → C3**
  - *corner contact only (no shared edge)*
  - unit also present in the C3 corner: U07
- **E → C4**
  - aligned (continuous): U07 177px, U03 114px, U04 83px, U27 72px, U39 21px, U23 16px
- **SE → C5**
  - *corner contact only (no shared edge)*
  - unit also present in the C5 corner: U03

### C4  —  x 1045–1567, y 1517–2023

- mapped geology **100.0%**, no-data **0.0%**, distinct units **19**
- v1 → v2: **10,066 px** changed (overlay removed 17,955, gaps filled 0)
- agreement with NGSA reference: **80.3%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U07 | #79DEB0 `rgb(121, 222, 176)` | 141,189 | 53.45% | 2 | 140,891 |
| U03 | #DED377 `rgb(222, 211, 119)` | 52,478 | 19.87% | 6 | 26,389 |
| U04 | #FF797F `rgb(255, 121, 127)` | 17,752 | 6.72% | 13 | 6,145 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 13,711 | 5.19% | 4 | 9,054 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 11,784 | 4.46% | 1 | 11,698 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 7,586 | 2.87% | 6 | 3,538 |
| U23 | #9CD6BD `rgb(156, 214, 189)` | 4,965 | 1.88% | 10 | 588 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 3,414 | 1.29% | 2 | 2,267 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 3,038 | 1.15% | 3 | 2,078 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 1,917 | 0.73% | 1 | 1,617 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 1,651 | 0.63% | 3 | 599 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 1,568 | 0.59% | 2 | 1,247 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 1,497 | 0.57% | 1 | 1,393 |
| U50 | #72DFFE `rgb(114, 223, 254)` | 925 | 0.35% | 1 | 925 |

- **NW → B3**
  - *corner contact only (no shared edge)*
  - unit also present in the B3 corner: U07
  - not carried into B3 corner: U23
- **W → B4**
  - aligned (continuous): U07 177px, U03 114px, U04 83px, U27 72px, U39 21px, U23 16px
- **SW → B5**
  - *corner contact only (no shared edge)*
  - unit also present in the B5 corner: U03, U59
- **N → C3**
  - aligned (continuous): U07 307px, U04 84px, U46 67px, U08 34px, U05 11px, U09 4px
- **S → C5**
  - aligned (continuous): U03 184px, U09 80px, U06 68px, U27 65px, U07 49px, U04 40px
- **NE → D3**
  - *corner contact only (no shared edge)*
  - unit also present in the D3 corner: U04
- **E → D4**
  - aligned (continuous): U07 234px, U03 142px, U04 101px, U23 16px
- **SE → D5**
  - *corner contact only (no shared edge)*
  - unit also present in the D5 corner: U07

### D4  —  x 1567–2089, y 1517–2023

- mapped geology **100.0%**, no-data **0.0%**, distinct units **23**
- v1 → v2: **11,680 px** changed (overlay removed 19,793, gaps filled 0)
- agreement with NGSA reference: **76.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 67,312 | 25.48% | 7 | 30,511 |
| U04 | #FF797F `rgb(255, 121, 127)` | 24,790 | 9.39% | 14 | 7,897 |
| U40 | #BCC8B8 `rgb(188, 200, 184)` | 23,738 | 8.99% | 3 | 15,692 |
| U25 | #96AAFF `rgb(150, 170, 255)` | 23,681 | 8.97% | 6 | 14,738 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 21,423 | 8.11% | 5 | 12,605 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 19,942 | 7.55% | 1 | 19,942 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 15,162 | 5.74% | 6 | 5,334 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 10,885 | 4.12% | 2 | 9,564 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 9,148 | 3.46% | 3 | 4,115 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 8,674 | 3.28% | 2 | 7,520 |
| U31 | #D2F458 `rgb(210, 244, 88)` | 8,385 | 3.17% | 4 | 4,763 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 7,647 | 2.90% | 3 | 5,759 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 7,301 | 2.76% | 4 | 5,838 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 4,812 | 1.82% | 3 | 3,357 |

- **NW → C3**
  - *corner contact only (no shared edge)*
  - unit also present in the C3 corner: U04
- **W → C4**
  - aligned (continuous): U07 234px, U03 142px, U04 101px, U23 16px
- **SW → C5**
  - *corner contact only (no shared edge)*
  - unit also present in the C5 corner: U07
- **N → D3**
  - aligned (continuous): U09 143px, U04 142px, U03 90px, U06 53px, U27 48px, U34 29px
- **S → D5**
  - aligned (continuous): U05 213px, U16 109px, U07 93px, U31 69px, U41 11px
- **NE → E3**
  - *corner contact only (no shared edge)*
  - unit also present in the E3 corner: U34
  - not carried into E3 corner: U03
- **E → E4**
  - aligned (continuous): U06 134px, U16 86px, U03 78px, U40 76px, U34 42px, U11 39px
- **SE → E5**
  - *corner contact only (no shared edge)*
  - unit also present in the E5 corner: U16

### E4  —  x 2089–2612, y 1517–2023

- mapped geology **99.7%**, no-data **0.3%**, distinct units **24**
- v1 → v2: **12,974 px** changed (overlay removed 21,318, gaps filled 0)
- agreement with NGSA reference: **75.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 61,723 | 23.32% | 5 | 34,328 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 38,955 | 14.72% | 4 | 20,962 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 29,791 | 11.26% | 4 | 27,351 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 23,942 | 9.05% | 7 | 12,547 |
| U26 | #98D64F `rgb(152, 214, 79)` | 21,250 | 8.03% | 4 | 9,934 |
| U34 | #DA8AE3 `rgb(218, 138, 227)` | 16,737 | 6.32% | 3 | 14,758 |
| U21 | #B2E370 `rgb(178, 227, 112)` | 13,912 | 5.26% | 2 | 13,297 |
| U04 | #FF797F `rgb(255, 121, 127)` | 13,726 | 5.19% | 7 | 6,735 |
| U40 | #BCC8B8 `rgb(188, 200, 184)` | 8,983 | 3.39% | 1 | 8,616 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 8,298 | 3.14% | 3 | 5,696 |
| U29 | #847DFC `rgb(132, 125, 252)` | 6,583 | 2.49% | 5 | 3,812 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 5,886 | 2.22% | 1 | 5,660 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 4,795 | 1.81% | 4 | 2,311 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 3,470 | 1.31% | 1 | 3,469 |

- **NW → D3**
  - *corner contact only (no shared edge)*
  - unit also present in the D3 corner: U34
  - not carried into D3 corner: U03
- **W → D4**
  - aligned (continuous): U06 134px, U16 86px, U03 78px, U40 76px, U34 42px, U11 39px
- **SW → D5**
  - *corner contact only (no shared edge)*
  - unit also present in the D5 corner: U16
- **N → E3**
  - aligned (continuous): U34 139px, U04 124px, U46 75px, U03 53px, U06 53px, U29 17px
- **S → E5**
  - aligned (continuous): U26 179px, U19 157px, U05 75px, U16 57px, U21 27px, U43 17px
  - offset (same unit, displaced): U17
- **NE → F3**
  - *corner contact only (no shared edge)*
  - unit also present in the F3 corner: U03
- **E → F4**
  - aligned (continuous): U07 120px, U05 114px, U19 63px, U26 44px, U04 36px, U03 33px
- **SE → F5**
  - *corner contact only (no shared edge)*
  - unit also present in the F5 corner: U19

### F4  —  x 2612–3134, y 1517–2023

- mapped geology **100.0%**, no-data **0.0%**, distinct units **21**
- v1 → v2: **6,140 px** changed (overlay removed 10,903, gaps filled 0)
- agreement with NGSA reference: **85.5%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 72,949 | 27.62% | 1 | 72,948 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 56,204 | 21.28% | 5 | 53,565 |
| U04 | #FF797F `rgb(255, 121, 127)` | 27,458 | 10.40% | 4 | 25,577 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 25,909 | 9.81% | 4 | 21,133 |
| U22 | #72C132 `rgb(114, 193, 50)` | 24,695 | 9.35% | 3 | 20,412 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 24,396 | 9.24% | 2 | 23,062 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 10,328 | 3.91% | 1 | 10,328 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 6,019 | 2.28% | 1 | 6,019 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 5,511 | 2.09% | 1 | 5,479 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 2,500 | 0.95% | 1 | 2,500 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 2,240 | 0.85% | 2 | 1,172 |
| U26 | #98D64F `rgb(152, 214, 79)` | 1,462 | 0.55% | 1 | 1,462 |
| U23 | #9CD6BD `rgb(156, 214, 189)` | 1,167 | 0.44% | 2 | 539 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 965 | 0.37% | 2 | 561 |

- **NW → E3**
  - *corner contact only (no shared edge)*
  - unit also present in the E3 corner: U03
  - not carried into E3 corner: U12
- **W → E4**
  - aligned (continuous): U07 120px, U05 114px, U19 63px, U26 44px, U04 36px, U03 33px
- **SW → E5**
  - *corner contact only (no shared edge)*
  - unit also present in the E5 corner: U19
- **N → F3**
  - aligned (continuous): U17 282px, U12 102px, U35 71px, U23 20px, U05 16px, U03 14px
- **S → F5**
  - aligned (continuous): U08 385px, U19 71px, U04 34px, U14 31px
- **NE → G3**
  - *corner contact only (no shared edge)*
  - unit also present in the G3 corner: U05, U17
- **E → G4**
  - aligned (continuous): U08 257px, U04 119px, U22 63px, U05 47px, U07 11px, U17 6px
- **SE → G5**
  - *corner contact only (no shared edge)*
  - unit also present in the G5 corner: U08

### G4  —  x 3134–3656, y 1517–2023

- mapped geology **65.2%**, no-data **34.8%**, distinct units **18**
- v1 → v2: **21,332 px** changed (overlay removed 17,971, gaps filled 7,614)
- agreement with NGSA reference: **78.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 46,084 | 17.45% | 1 | 46,082 |
| U04 | #FF797F `rgb(255, 121, 127)` | 28,441 | 10.77% | 7 | 11,302 |
| U22 | #72C132 `rgb(114, 193, 50)` | 27,120 | 10.27% | 3 | 14,290 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 24,171 | 9.15% | 2 | 23,845 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 23,225 | 8.79% | 2 | 20,755 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 6,657 | 2.52% | 1 | 6,657 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 5,977 | 2.26% | 1 | 5,870 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 3,596 | 1.36% | 2 | 3,085 |
| U03 | #DED377 `rgb(222, 211, 119)` | 2,543 | 0.96% | 1 | 2,543 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 1,513 | 0.57% | 3 | 705 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 1,415 | 0.54% | 1 | 1,268 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 527 | 0.20% | 0 | 194 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 301 | 0.11% | 0 | 120 |
| U23 | #9CD6BD `rgb(156, 214, 189)` | 297 | 0.11% | 0 | 171 |

- **NW → F3**
  - *corner contact only (no shared edge)*
  - unit also present in the F3 corner: U17
  - not carried into F3 corner: U05
- **W → F4**
  - aligned (continuous): U08 257px, U04 119px, U22 63px, U05 47px, U07 11px, U17 6px
- **SW → F5**
  - *corner contact only (no shared edge)*
  - unit also present in the F5 corner: U08
- **N → G3**
  - aligned (continuous): U22 222px, U05 162px, U03 98px, U04 24px, U17 7px
- **S → G5**
  - aligned (continuous): U08 173px, U04 18px, U17 4px
- **NE → H3**
  - *corner contact only (no shared edge)*
  - unit also present in the H3 corner: — none —
  - not carried into H3 corner: U04
- **E → H4**
  - aligned (continuous): — none —
  - offset (same unit, displaced): U01
- **SE → H5**
  - *corner contact only (no shared edge)*
  - unit also present in the H5 corner: — none —
  - not carried into H5 corner: U04

### H4  —  x 3656–4179, y 1517–2023

- mapped geology **0.9%**, no-data **99.1%**, distinct units **1**
- v1 → v2: **9,975 px** changed (overlay removed 11,263, gaps filled 33)
- agreement with NGSA reference: **74.7%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 2,355 | 0.89% | 1 | 2,183 |

- **NW → G3**
  - *corner contact only (no shared edge)*
  - unit also present in the G3 corner: — none —
- **W → G4**
  - aligned (continuous): — none —
  - offset (same unit, displaced): U01
- **SW → G5**
  - *corner contact only (no shared edge)*
  - unit also present in the G5 corner: — none —
- **N → H3**
  - aligned (continuous): — none —
- **S → H5**
  - aligned (continuous): — none —
- **NE → I3**
  - *corner contact only (no shared edge)*
  - unit also present in the I3 corner: — none —
- **E → I4**
  - aligned (continuous): — none —
- **SE → I5**
  - *corner contact only (no shared edge)*
  - unit also present in the I5 corner: — none —

### I4  —  x 4179–4701, y 1517–2023

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J4  —  x 4701–5223, y 1517–2023

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K4  —  x 5223–5746, y 1517–2023

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L4  —  x 5746–6268, y 1517–2023

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### A5  —  x 0–522, y 2023–2529

- mapped geology **61.4%**, no-data **38.6%**, distinct units **21**
- v1 → v2: **17,833 px** changed (overlay removed 21,366, gaps filled 111)
- agreement with NGSA reference: **71.5%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 47,535 | 18.00% | 3 | 37,178 |
| U44 | #C5F4B0 `rgb(197, 244, 176)` | 23,272 | 8.81% | 1 | 23,272 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 22,866 | 8.66% | 3 | 17,622 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 18,906 | 7.16% | 3 | 14,533 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 14,098 | 5.34% | 2 | 13,180 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 10,661 | 4.04% | 3 | 9,154 |
| U35 | #E5FFA8 `rgb(229, 255, 168)` | 7,563 | 2.86% | 2 | 6,528 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 4,724 | 1.79% | 1 | 4,666 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 3,762 | 1.42% | 2 | 3,327 |
| U50 | #72DFFE `rgb(114, 223, 254)` | 2,463 | 0.93% | 3 | 1,645 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 1,936 | 0.73% | 3 | 869 |
| U04 | #FF797F `rgb(255, 121, 127)` | 898 | 0.34% | 2 | 683 |
| U01 | #98DAF2 `rgb(152, 218, 242)` | 801 | 0.30% | 1 | 801 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 592 | 0.22% | 1 | 592 |

- **N → A4**
  - aligned (continuous): U09 95px, U50 70px, U11 42px, U14 35px, U03 33px, U30 32px
- **S → A6**
  - aligned (continuous): U05 262px, U01 56px, U10 10px
- **NE → B4**
  - *corner contact only (no shared edge)*
  - unit also present in the B4 corner: U03
  - not carried into B4 corner: U31, U50
- **E → B5**
  - aligned (continuous): U03 346px, U05 77px, U10 34px, U44 34px, U58 12px
- **SE → B6**
  - *corner contact only (no shared edge)*
  - unit also present in the B6 corner: U05

### B5  —  x 522–1045, y 2023–2529

- mapped geology **99.9%**, no-data **0.1%**, distinct units **33**
- v1 → v2: **24,658 px** changed (overlay removed 36,039, gaps filled 0)
- agreement with NGSA reference: **66.9%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 86,631 | 32.74% | 12 | 37,343 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 43,554 | 16.46% | 4 | 19,669 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 22,589 | 8.54% | 4 | 15,122 |
| U04 | #FF797F `rgb(255, 121, 127)` | 16,724 | 6.32% | 13 | 3,198 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 13,525 | 5.11% | 6 | 6,204 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 12,616 | 4.77% | 3 | 7,713 |
| U62 | #C16D27 `rgb(193, 109, 39)` | 6,646 | 2.51% | 4 | 2,492 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 6,431 | 2.43% | 3 | 4,152 |
| U20 | #CEFFA6 `rgb(206, 255, 166)` | 5,920 | 2.24% | 2 | 3,946 |
| U44 | #C5F4B0 `rgb(197, 244, 176)` | 5,780 | 2.18% | 2 | 5,428 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 5,698 | 2.15% | 2 | 3,089 |
| U46 | #FFC7D4 `rgb(255, 199, 212)` | 5,627 | 2.13% | 3 | 2,550 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 5,599 | 2.12% | 7 | 1,888 |
| U37 | #CCDF6C `rgb(204, 223, 108)` | 5,059 | 1.91% | 1 | 4,712 |

- **NW → A4**
  - *corner contact only (no shared edge)*
  - unit also present in the A4 corner: U03
  - not carried into A4 corner: U06
- **W → A5**
  - aligned (continuous): U03 346px, U05 77px, U10 34px, U44 34px, U58 12px
- **SW → A6**
  - *corner contact only (no shared edge)*
  - unit also present in the A6 corner: U05
- **N → B4**
  - aligned (continuous): U03 292px, U04 69px, U09 69px, U06 30px, U14 26px, U48 8px
  - ends at edge (absent from B4): U33
- **S → B6**
  - aligned (continuous): U10 265px, U05 188px, U35 19px, U40 16px, U27 11px, U09 9px
  - ends at edge (absent from B6): U18
- **NE → C4**
  - *corner contact only (no shared edge)*
  - unit also present in the C4 corner: U03, U59
- **E → C5**
  - aligned (continuous): U03 312px, U10 38px, U20 35px, U59 33px, U06 32px, U37 30px
  - ends at edge (absent from C5): U04
- **SE → C6**
  - *corner contact only (no shared edge)*
  - unit also present in the C6 corner: U10

### C5  —  x 1045–1567, y 2023–2529

- mapped geology **100.0%**, no-data **0.0%**, distinct units **26**
- v1 → v2: **13,147 px** changed (overlay removed 19,446, gaps filled 0)
- agreement with NGSA reference: **76.4%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U03 | #DED377 `rgb(222, 211, 119)` | 84,957 | 32.16% | 3 | 81,904 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 36,000 | 13.63% | 3 | 18,334 |
| U28 | #FFC9E0 `rgb(255, 201, 224)` | 21,226 | 8.04% | 1 | 21,226 |
| U20 | #CEFFA6 `rgb(206, 255, 166)` | 21,137 | 8.00% | 5 | 17,329 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 15,249 | 5.77% | 4 | 8,276 |
| U37 | #CCDF6C `rgb(204, 223, 108)` | 15,055 | 5.70% | 1 | 14,795 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 13,849 | 5.24% | 7 | 5,797 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 13,594 | 5.15% | 3 | 11,826 |
| U31 | #D2F458 `rgb(210, 244, 88)` | 11,306 | 4.28% | 3 | 7,975 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 10,991 | 4.16% | 1 | 10,991 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 7,042 | 2.67% | 2 | 5,032 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 3,294 | 1.25% | 2 | 2,056 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 3,079 | 1.17% | 1 | 3,079 |
| U41 | #D6FF85 `rgb(214, 255, 133)` | 2,752 | 1.04% | 2 | 1,957 |

- **NW → B4**
  - *corner contact only (no shared edge)*
  - unit also present in the B4 corner: U03
  - not carried into B4 corner: U04, U59
- **W → B5**
  - aligned (continuous): U03 312px, U10 38px, U20 35px, U59 33px, U06 32px, U37 30px
- **SW → B6**
  - *corner contact only (no shared edge)*
  - unit also present in the B6 corner: U10
- **N → C4**
  - aligned (continuous): U03 184px, U09 80px, U06 68px, U27 65px, U07 49px, U04 40px
- **S → C6**
  - aligned (continuous): U10 287px, U28 152px, U05 80px
- **NE → D4**
  - *corner contact only (no shared edge)*
  - unit also present in the D4 corner: U07
- **E → D5**
  - aligned (continuous): U05 237px, U20 60px, U41 49px, U09 47px, U14 39px, U07 34px
  - ends at edge (absent from D5): U31
- **SE → D6**
  - *corner contact only (no shared edge)*
  - unit also present in the D6 corner: U05

### D5  —  x 1567–2089, y 2023–2529

- mapped geology **100.0%**, no-data **0.0%**, distinct units **22**
- v1 → v2: **7,541 px** changed (overlay removed 14,865, gaps filled 0)
- agreement with NGSA reference: **74.6%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U20 | #CEFFA6 `rgb(206, 255, 166)` | 61,675 | 23.35% | 1 | 61,675 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 58,094 | 21.99% | 3 | 49,040 |
| U41 | #D6FF85 `rgb(214, 255, 133)` | 31,883 | 12.07% | 3 | 22,340 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 23,716 | 8.98% | 5 | 11,082 |
| U31 | #D2F458 `rgb(210, 244, 88)` | 22,952 | 8.69% | 2 | 16,940 |
| U52 | #B3FDB7 `rgb(179, 253, 183)` | 14,345 | 5.43% | 2 | 13,945 |
| U21 | #B2E370 `rgb(178, 227, 112)` | 13,265 | 5.02% | 7 | 7,726 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 9,566 | 3.62% | 4 | 7,371 |
| U37 | #CCDF6C `rgb(204, 223, 108)` | 9,185 | 3.48% | 1 | 9,063 |
| U26 | #98D64F `rgb(152, 214, 79)` | 8,745 | 3.31% | 2 | 7,728 |
| U57 | #B6E397 `rgb(182, 227, 151)` | 3,220 | 1.22% | 1 | 3,183 |
| U07 | #79DEB0 `rgb(121, 222, 176)` | 1,684 | 0.64% | 1 | 1,683 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 1,675 | 0.63% | 4 | 437 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 1,526 | 0.58% | 2 | 1,226 |

- **NW → C4**
  - *corner contact only (no shared edge)*
  - unit also present in the C4 corner: U07
- **W → C5**
  - aligned (continuous): U05 237px, U20 60px, U41 49px, U09 47px, U14 39px, U07 34px
- **SW → C6**
  - *corner contact only (no shared edge)*
  - unit also present in the C6 corner: U05
  - not carried into C6 corner: U37
- **N → D4**
  - aligned (continuous): U05 213px, U16 109px, U07 93px, U31 69px, U41 11px
- **S → D6**
  - aligned (continuous): U19 171px, U37 72px, U26 65px, U20 47px, U16 41px, U31 41px
  - offset (same unit, displaced): U40
- **NE → E4**
  - *corner contact only (no shared edge)*
  - unit also present in the E4 corner: U16
- **E → E5**
  - aligned (continuous): U21 216px, U16 171px, U26 55px, U32 37px, U19 9px
- **SE → E6**
  - *corner contact only (no shared edge)*
  - unit also present in the E6 corner: U26

### E5  —  x 2089–2612, y 2023–2529

- mapped geology **95.3%**, no-data **4.7%**, distinct units **23**
- v1 → v2: **9,294 px** changed (overlay removed 18,500, gaps filled 2)
- agreement with NGSA reference: **76.6%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U21 | #B2E370 `rgb(178, 227, 112)` | 64,307 | 24.30% | 9 | 22,750 |
| U04 | #FF797F `rgb(255, 121, 127)` | 30,507 | 11.53% | 9 | 10,298 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 28,616 | 10.81% | 6 | 22,619 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 27,132 | 10.25% | 2 | 25,697 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 18,039 | 6.82% | 4 | 13,597 |
| U26 | #98D64F `rgb(152, 214, 79)` | 16,278 | 6.15% | 4 | 8,722 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 15,668 | 5.92% | 1 | 15,105 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 13,745 | 5.19% | 2 | 13,087 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 11,453 | 4.33% | 3 | 9,236 |
| U03 | #DED377 `rgb(222, 211, 119)` | 11,323 | 4.28% | 2 | 5,805 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 4,531 | 1.71% | 6 | 1,004 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 2,056 | 0.78% | 1 | 2,056 |
| U42 | #DFFF44 `rgb(223, 255, 68)` | 1,778 | 0.67% | 1 | 1,725 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 1,676 | 0.63% | 2 | 768 |

- **NW → D4**
  - *corner contact only (no shared edge)*
  - unit also present in the D4 corner: U16
- **W → D5**
  - aligned (continuous): U21 216px, U16 171px, U26 55px, U32 37px, U19 9px
- **SW → D6**
  - *corner contact only (no shared edge)*
  - unit also present in the D6 corner: U26
- **N → E4**
  - aligned (continuous): U26 179px, U19 157px, U05 75px, U16 57px, U21 27px, U43 17px
  - offset (same unit, displaced): U17
- **S → E6**
  - aligned (continuous): U06 110px, U26 66px, U30 53px, U04 27px, U09 27px, U03 23px
- **NE → F4**
  - *corner contact only (no shared edge)*
  - unit also present in the F4 corner: U19
- **E → F5**
  - aligned (continuous): U14 271px, U19 66px, U38 10px
- **SE → F6**
  - *corner contact only (no shared edge)*
  - unit also present in the F6 corner: — none —

### F5  —  x 2612–3134, y 2023–2529

- mapped geology **80.3%**, no-data **19.7%**, distinct units **10**
- v1 → v2: **8,396 px** changed (overlay removed 11,709, gaps filled 562)
- agreement with NGSA reference: **86.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 121,882 | 46.14% | 1 | 121,881 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 30,716 | 11.63% | 1 | 30,714 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 19,772 | 7.49% | 1 | 19,745 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 16,729 | 6.33% | 1 | 16,729 |
| U04 | #FF797F `rgb(255, 121, 127)` | 10,489 | 3.97% | 9 | 3,423 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 8,859 | 3.35% | 3 | 6,959 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 2,773 | 1.05% | 1 | 2,773 |
| U38 | #DAB131 `rgb(218, 177, 49)` | 497 | 0.19% | 1 | 235 |
| U11 | #FF8EBA `rgb(255, 142, 186)` | 247 | 0.09% | 1 | 247 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 87 | 0.03% | 0 | 28 |

- **NW → E4**
  - *corner contact only (no shared edge)*
  - unit also present in the E4 corner: U19
- **W → E5**
  - aligned (continuous): U14 271px, U19 66px, U38 10px
- **SW → E6**
  - *corner contact only (no shared edge)*
  - unit also present in the E6 corner: — none —
- **N → F4**
  - aligned (continuous): U08 385px, U19 71px, U04 34px, U14 31px
- **S → F6**
  - aligned (continuous): — none —
- **NE → G4**
  - *corner contact only (no shared edge)*
  - unit also present in the G4 corner: U08
- **E → G5**
  - aligned (continuous): U08 328px, U43 21px
- **SE → G6**
  - *corner contact only (no shared edge)*
  - unit also present in the G6 corner: — none —

### G5  —  x 3134–3656, y 2023–2529

- mapped geology **14.9%**, no-data **85.1%**, distinct units **5**
- v1 → v2: **18,021 px** changed (overlay removed 13,969, gaps filled 5,700)
- agreement with NGSA reference: **79.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 27,197 | 10.30% | 3 | 26,651 |
| U04 | #FF797F `rgb(255, 121, 127)` | 8,930 | 3.38% | 2 | 8,477 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 1,485 | 0.56% | 1 | 1,485 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 1,439 | 0.54% | 2 | 883 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 282 | 0.11% | 1 | 282 |

- **NW → F4**
  - *corner contact only (no shared edge)*
  - unit also present in the F4 corner: U08
- **W → F5**
  - aligned (continuous): U08 328px, U43 21px
- **SW → F6**
  - *corner contact only (no shared edge)*
  - unit also present in the F6 corner: — none —
- **N → G4**
  - aligned (continuous): U08 173px, U04 18px, U17 4px
- **S → G6**
  - aligned (continuous): U08 4px
- **NE → H4**
  - *corner contact only (no shared edge)*
  - unit also present in the H4 corner: — none —
- **E → H5**
  - aligned (continuous): — none —
- **SE → H6**
  - *corner contact only (no shared edge)*
  - unit also present in the H6 corner: — none —

### H5  —  x 3656–4179, y 2023–2529

- mapped geology **0.0%**, no-data **100.0%**, distinct units **1**
- v1 → v2: **9,916 px** changed (overlay removed 9,865, gaps filled 56)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 56 | 0.02% | 0 | 13 |

- **NW → G4**
  - *corner contact only (no shared edge)*
  - unit also present in the G4 corner: — none —
- **W → G5**
  - aligned (continuous): — none —
- **SW → G6**
  - *corner contact only (no shared edge)*
  - unit also present in the G6 corner: — none —
- **N → H4**
  - aligned (continuous): — none —
- **S → H6**
  - aligned (continuous): — none —
- **NE → I4**
  - *corner contact only (no shared edge)*
  - unit also present in the I4 corner: — none —
  - not carried into I4 corner: U01
- **E → I5**
  - aligned (continuous): — none —
- **SE → I6**
  - *corner contact only (no shared edge)*
  - unit also present in the I6 corner: — none —

### I5  —  x 4179–4701, y 2023–2529

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J5  —  x 4701–5223, y 2023–2529

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K5  —  x 5223–5746, y 2023–2529

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L5  —  x 5746–6268, y 2023–2529

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### A6  —  x 0–522, y 2529–3034

- mapped geology **85.5%**, no-data **14.5%**, distinct units **4**
- v1 → v2: **14,918 px** changed (overlay removed 33,786, gaps filled 57)
- agreement with NGSA reference: **92.7%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 208,809 | 79.21% | 2 | 207,032 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 16,308 | 6.19% | 2 | 13,997 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 72 | 0.03% | 0 | 24 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 64 | 0.02% | 0 | 64 |

- **N → A5**
  - aligned (continuous): U05 262px, U01 56px, U10 10px
- **S → A7**
  - aligned (continuous): U01 456px
- **NE → B5**
  - *corner contact only (no shared edge)*
  - unit also present in the B5 corner: U05
- **E → B6**
  - aligned (continuous): U01 485px, U05 20px
- **SE → B7**
  - *corner contact only (no shared edge)*
  - unit also present in the B7 corner: U01

### B6  —  x 522–1045, y 2529–3034

- mapped geology **100.0%**, no-data **0.0%**, distinct units **10**
- v1 → v2: **15,436 px** changed (overlay removed 37,793, gaps filled 0)
- agreement with NGSA reference: **90.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 211,463 | 80.06% | 1 | 211,463 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 33,150 | 12.55% | 2 | 31,652 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 9,201 | 3.48% | 1 | 9,201 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 7,083 | 2.68% | 1 | 6,876 |
| U24 | #F2F600 `rgb(242, 246, 0)` | 1,730 | 0.66% | 1 | 1,730 |
| U40 | #BCC8B8 `rgb(188, 200, 184)` | 813 | 0.31% | 2 | 517 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 237 | 0.09% | 0 | 139 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 203 | 0.08% | 1 | 203 |
| U35 | #E5FFA8 `rgb(229, 255, 168)` | 140 | 0.05% | 0 | 140 |
| U27 | #9EB9E6 `rgb(158, 185, 230)` | 65 | 0.02% | 0 | 64 |

- **NW → A5**
  - *corner contact only (no shared edge)*
  - unit also present in the A5 corner: U05
  - not carried into A5 corner: U01
- **W → A6**
  - aligned (continuous): U01 485px, U05 20px
- **SW → A7**
  - *corner contact only (no shared edge)*
  - unit also present in the A7 corner: U01
- **N → B5**
  - aligned (continuous): U10 265px, U05 188px, U35 19px, U40 16px, U27 11px, U09 9px
- **S → B7**
  - aligned (continuous): U01 523px
- **NE → C5**
  - *corner contact only (no shared edge)*
  - unit also present in the C5 corner: U10
- **E → C6**
  - aligned (continuous): U01 159px, U05 129px, U24 79px, U45 77px, U10 53px
- **SE → C7**
  - *corner contact only (no shared edge)*
  - unit also present in the C7 corner: U01

### C6  —  x 1045–1567, y 2529–3034

- mapped geology **100.0%**, no-data **0.0%**, distinct units **10**
- v1 → v2: **7,128 px** changed (overlay removed 14,903, gaps filled 0)
- agreement with NGSA reference: **77.3%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U18 | #E4E57D `rgb(228, 229, 125)` | 85,688 | 32.51% | 1 | 85,688 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 72,696 | 27.58% | 2 | 62,967 |
| U36 | #FCFB4D `rgb(252, 251, 77)` | 43,175 | 16.38% | 3 | 33,335 |
| U24 | #F2F600 `rgb(242, 246, 0)` | 26,621 | 10.10% | 2 | 26,197 |
| U28 | #FFC9E0 `rgb(255, 201, 224)` | 12,025 | 4.56% | 3 | 9,805 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 9,152 | 3.47% | 1 | 9,112 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 8,628 | 3.27% | 3 | 4,779 |
| U01 | #98DAF2 `rgb(152, 218, 242)` | 5,073 | 1.92% | 1 | 5,073 |
| U40 | #BCC8B8 `rgb(188, 200, 184)` | 404 | 0.15% | 0 | 172 |
| U13 | #FEFD65 `rgb(254, 253, 101)` | 106 | 0.04% | 0 | 39 |

- **NW → B5**
  - *corner contact only (no shared edge)*
  - unit also present in the B5 corner: U10
- **W → B6**
  - aligned (continuous): U01 159px, U05 129px, U24 79px, U45 77px, U10 53px
- **SW → B7**
  - *corner contact only (no shared edge)*
  - unit also present in the B7 corner: U01
- **N → C5**
  - aligned (continuous): U10 287px, U28 152px, U05 80px
- **S → C7**
  - aligned (continuous): U18 359px, U01 64px, U24 42px, U45 20px, U36 19px
  - ends at edge (absent from C7): U10
- **NE → D5**
  - *corner contact only (no shared edge)*
  - unit also present in the D5 corner: U05
- **E → D6**
  - aligned (continuous): U10 252px, U28 145px, U05 82px, U36 14px, U18 9px
  - ends at edge (absent from D6): U24
- **SE → D7**
  - *corner contact only (no shared edge)*
  - unit also present in the D7 corner: U10, U24, U36

### D6  —  x 1567–2089, y 2529–3034

- mapped geology **99.9%**, no-data **0.1%**, distinct units **24**
- v1 → v2: **15,852 px** changed (overlay removed 25,330, gaps filled 0)
- agreement with NGSA reference: **72.9%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U10 | #FDFDBE `rgb(253, 253, 190)` | 64,936 | 24.63% | 2 | 61,992 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 34,544 | 13.10% | 2 | 27,739 |
| U28 | #FFC9E0 `rgb(255, 201, 224)` | 26,941 | 10.22% | 1 | 26,941 |
| U26 | #98D64F `rgb(152, 214, 79)` | 25,223 | 9.57% | 9 | 5,056 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 17,647 | 6.69% | 8 | 5,375 |
| U37 | #CCDF6C `rgb(204, 223, 108)` | 16,496 | 6.26% | 4 | 10,167 |
| U31 | #D2F458 `rgb(210, 244, 88)` | 12,170 | 4.62% | 9 | 6,756 |
| U20 | #CEFFA6 `rgb(206, 255, 166)` | 12,149 | 4.61% | 6 | 5,745 |
| U48 | #DFBA74 `rgb(223, 186, 116)` | 11,902 | 4.52% | 2 | 10,415 |
| U57 | #B6E397 `rgb(182, 227, 151)` | 11,358 | 4.31% | 3 | 4,544 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 9,740 | 3.69% | 2 | 7,529 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 5,137 | 1.95% | 1 | 5,137 |
| U33 | #FF9BAB `rgb(255, 155, 171)` | 3,338 | 1.27% | 2 | 2,134 |
| U06 | #FFB44C `rgb(255, 180, 76)` | 3,130 | 1.19% | 1 | 3,130 |

- **NW → C5**
  - *corner contact only (no shared edge)*
  - unit also present in the C5 corner: U05
  - not carried into C5 corner: U28
- **W → C6**
  - aligned (continuous): U10 252px, U28 145px, U05 82px, U36 14px, U18 9px
- **SW → C7**
  - *corner contact only (no shared edge)*
  - unit also present in the C7 corner: U24
  - not carried into C7 corner: U10, U36
- **N → D5**
  - aligned (continuous): U19 171px, U37 72px, U26 65px, U20 47px, U16 41px, U31 41px
  - offset (same unit, displaced): U40
- **S → D7**
  - aligned (continuous): U10 427px, U05 60px, U36 9px, U24 7px, U40 6px
- **NE → E5**
  - *corner contact only (no shared edge)*
  - unit also present in the E5 corner: U26
  - not carried into E5 corner: U19, U32
- **E → E6**
  - aligned (continuous): U14 127px, U26 92px, U06 75px, U16 52px, U19 49px, U10 23px
- **SE → E7**
  - *corner contact only (no shared edge)*
  - unit also present in the E7 corner: U10

### E6  —  x 2089–2612, y 2529–3034

- mapped geology **33.3%**, no-data **66.7%**, distinct units **20**
- v1 → v2: **22,501 px** changed (overlay removed 22,729, gaps filled 2,969)
- agreement with NGSA reference: **80.8%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U06 | #FFB44C `rgb(255, 180, 76)` | 29,171 | 11.04% | 3 | 15,961 |
| U19 | #5FA33A `rgb(95, 163, 58)` | 19,615 | 7.43% | 1 | 19,611 |
| U08 | #DFC477 `rgb(223, 196, 119)` | 11,221 | 4.25% | 1 | 11,219 |
| U04 | #FF797F `rgb(255, 121, 127)` | 9,082 | 3.44% | 5 | 5,261 |
| U26 | #98D64F `rgb(152, 214, 79)` | 4,630 | 1.75% | 2 | 3,503 |
| U16 | #9BE359 `rgb(155, 227, 89)` | 4,023 | 1.52% | 1 | 4,023 |
| U30 | #FF7057 `rgb(255, 112, 87)` | 2,417 | 0.92% | 1 | 2,417 |
| U14 | #DAA000 `rgb(218, 160, 0)` | 2,096 | 0.79% | 1 | 2,096 |
| U43 | #D8D8FC `rgb(216, 216, 252)` | 1,430 | 0.54% | 2 | 1,125 |
| U20 | #CEFFA6 `rgb(206, 255, 166)` | 1,012 | 0.38% | 1 | 1,012 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 901 | 0.34% | 1 | 900 |
| U17 | #8AAC5F `rgb(138, 172, 95)` | 631 | 0.24% | 1 | 321 |
| U31 | #D2F458 `rgb(210, 244, 88)` | 487 | 0.18% | 1 | 390 |
| U09 | #79C1D9 `rgb(121, 193, 217)` | 309 | 0.12% | 1 | 309 |

- **NW → D5**
  - *corner contact only (no shared edge)*
  - unit also present in the D5 corner: U26
  - not carried into D5 corner: U32
- **W → D6**
  - aligned (continuous): U14 127px, U26 92px, U06 75px, U16 52px, U19 49px, U10 23px
- **SW → D7**
  - *corner contact only (no shared edge)*
  - unit also present in the D7 corner: U10
- **N → E5**
  - aligned (continuous): U06 110px, U26 66px, U30 53px, U04 27px, U09 27px, U03 23px
- **S → E7**
  - aligned (continuous): U10 46px, U17 9px
  - ends at edge (absent from E7): U23
- **NE → F5**
  - *corner contact only (no shared edge)*
  - unit also present in the F5 corner: — none —
- **E → F6**
  - aligned (continuous): — none —
- **SE → F7**
  - *corner contact only (no shared edge)*
  - unit also present in the F7 corner: — none —

### F6  —  x 2612–3134, y 2529–3034

- mapped geology **0.0%**, no-data **100.0%**, distinct units **0**
- v1 → v2: **10,012 px** changed (overlay removed 10,301, gaps filled 1)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|

- **NW → E5**
  - *corner contact only (no shared edge)*
  - unit also present in the E5 corner: — none —
- **W → E6**
  - aligned (continuous): — none —
- **SW → E7**
  - *corner contact only (no shared edge)*
  - unit also present in the E7 corner: — none —
- **N → F5**
  - aligned (continuous): — none —
- **S → F7**
  - aligned (continuous): — none —
- **NE → G5**
  - *corner contact only (no shared edge)*
  - unit also present in the G5 corner: — none —
- **E → G6**
  - aligned (continuous): — none —
- **SE → G7**
  - *corner contact only (no shared edge)*
  - unit also present in the G7 corner: — none —

### G6  —  x 3134–3656, y 2529–3034

- mapped geology **0.1%**, no-data **99.9%**, distinct units **1**
- v1 → v2: **10,966 px** changed (overlay removed 10,907, gaps filled 141)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 141 | 0.05% | 0 | 141 |

- **NW → F5**
  - *corner contact only (no shared edge)*
  - unit also present in the F5 corner: — none —
- **W → F6**
  - aligned (continuous): — none —
- **SW → F7**
  - *corner contact only (no shared edge)*
  - unit also present in the F7 corner: — none —
- **N → G5**
  - aligned (continuous): U08 4px
- **S → G7**
  - aligned (continuous): — none —
- **NE → H5**
  - *corner contact only (no shared edge)*
  - unit also present in the H5 corner: — none —
- **E → H6**
  - aligned (continuous): — none —
- **SE → H7**
  - *corner contact only (no shared edge)*
  - unit also present in the H7 corner: — none —

### H6  —  x 3656–4179, y 2529–3034

- mapped geology **0.0%**, no-data **100.0%**, distinct units **1**
- v1 → v2: **9,959 px** changed (overlay removed 9,908, gaps filled 56)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 56 | 0.02% | 0 | 13 |

- **NW → G5**
  - *corner contact only (no shared edge)*
  - unit also present in the G5 corner: — none —
- **W → G6**
  - aligned (continuous): — none —
- **SW → G7**
  - *corner contact only (no shared edge)*
  - unit also present in the G7 corner: — none —
- **N → H5**
  - aligned (continuous): — none —
- **S → H7**
  - aligned (continuous): — none —
- **NE → I5**
  - *corner contact only (no shared edge)*
  - unit also present in the I5 corner: — none —
- **E → I6**
  - aligned (continuous): — none —
- **SE → I7**
  - *corner contact only (no shared edge)*
  - unit also present in the I7 corner: — none —
  - not carried into I7 corner: U08

### I6  —  x 4179–4701, y 2529–3034

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J6  —  x 4701–5223, y 2529–3034

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K6  —  x 5223–5746, y 2529–3034

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L6  —  x 5746–6268, y 2529–3034

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### A7  —  x 0–522, y 3034–3540

- mapped geology **68.6%**, no-data **31.4%**, distinct units **1**
- v1 → v2: **14,885 px** changed (overlay removed 16,279, gaps filled 61)
- agreement with NGSA reference: **98.1%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 181,127 | 68.57% | 1 | 181,066 |

- **N → A6**
  - aligned (continuous): U01 456px
- **NE → B6**
  - *corner contact only (no shared edge)*
  - unit also present in the B6 corner: U01
- **E → B7**
  - aligned (continuous): U01 397px

### B7  —  x 522–1045, y 3034–3540

- mapped geology **78.5%**, no-data **21.5%**, distinct units **1**
- v1 → v2: **11,440 px** changed (overlay removed 21,489, gaps filled 73)
- agreement with NGSA reference: **98.5%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 207,747 | 78.50% | 1 | 207,674 |

- **NW → A6**
  - *corner contact only (no shared edge)*
  - unit also present in the A6 corner: U01
- **W → A7**
  - aligned (continuous): U01 397px
- **N → B6**
  - aligned (continuous): U01 523px
- **NE → C6**
  - *corner contact only (no shared edge)*
  - unit also present in the C6 corner: U01
- **E → C7**
  - aligned (continuous): U01 397px

### C7  —  x 1045–1567, y 3034–3540

- mapped geology **78.5%**, no-data **21.5%**, distinct units **6**
- v1 → v2: **14,379 px** changed (overlay removed 42,403, gaps filled 41)
- agreement with NGSA reference: **83.5%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 128,057 | 48.48% | 1 | 128,016 |
| U24 | #F2F600 `rgb(242, 246, 0)` | 40,843 | 15.46% | 1 | 40,842 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 23,079 | 8.74% | 2 | 22,331 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 14,920 | 5.65% | 3 | 13,048 |
| U36 | #FCFB4D `rgb(252, 251, 77)` | 247 | 0.09% | 0 | 136 |
| U12 | #ECFF4D `rgb(236, 255, 77)` | 104 | 0.04% | 0 | 104 |

- **NW → B6**
  - *corner contact only (no shared edge)*
  - unit also present in the B6 corner: U01
- **W → B7**
  - aligned (continuous): U01 397px
- **N → C6**
  - aligned (continuous): U18 359px, U01 64px, U24 42px, U45 20px, U36 19px
- **NE → D6**
  - *corner contact only (no shared edge)*
  - unit also present in the D6 corner: U24
- **E → D7**
  - aligned (continuous): U01 217px, U24 150px, U45 29px

### D7  —  x 1567–2089, y 3034–3540

- mapped geology **78.3%**, no-data **21.7%**, distinct units **10**
- v1 → v2: **17,578 px** changed (overlay removed 40,090, gaps filled 77)
- agreement with NGSA reference: **84.4%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 132,128 | 50.02% | 1 | 131,990 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 35,023 | 13.26% | 4 | 30,453 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 29,534 | 11.18% | 2 | 29,099 |
| U24 | #F2F600 `rgb(242, 246, 0)` | 7,878 | 2.98% | 1 | 7,877 |
| U45 | #F0FF82 `rgb(240, 255, 130)` | 1,466 | 0.56% | 1 | 1,118 |
| U40 | #BCC8B8 `rgb(188, 200, 184)` | 430 | 0.16% | 0 | 105 |
| U36 | #FCFB4D `rgb(252, 251, 77)` | 191 | 0.07% | 0 | 110 |
| U58 | #CCD86C `rgb(204, 216, 108)` | 92 | 0.03% | 0 | 53 |
| U18 | #E4E57D `rgb(228, 229, 125)` | 75 | 0.03% | 0 | 74 |
| U32 | #B2D181 `rgb(178, 209, 129)` | 52 | 0.02% | 0 | 44 |

- **NW → C6**
  - *corner contact only (no shared edge)*
  - unit also present in the C6 corner: U10, U24, U36
- **W → C7**
  - aligned (continuous): U01 217px, U24 150px, U45 29px
- **N → D6**
  - aligned (continuous): U10 427px, U05 60px, U36 9px, U24 7px, U40 6px
- **NE → E6**
  - *corner contact only (no shared edge)*
  - unit also present in the E6 corner: U10
  - not carried into E6 corner: U05
- **E → E7**
  - aligned (continuous): U01 325px, U10 38px, U05 23px

### E7  —  x 2089–2612, y 3034–3540

- mapped geology **35.1%**, no-data **64.9%**, distinct units **3**
- v1 → v2: **48,906 px** changed (overlay removed 36,828, gaps filled 23,236)
- agreement with NGSA reference: **86.2%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 90,275 | 34.11% | 4 | 87,093 |
| U10 | #FDFDBE `rgb(253, 253, 190)` | 2,212 | 0.84% | 1 | 2,212 |
| U05 | #ECFF65 `rgb(236, 255, 101)` | 246 | 0.09% | 1 | 246 |

- **NW → D6**
  - *corner contact only (no shared edge)*
  - unit also present in the D6 corner: U10
- **W → D7**
  - aligned (continuous): U01 325px, U10 38px, U05 23px
- **N → E6**
  - aligned (continuous): U10 46px, U17 9px
- **NE → F6**
  - *corner contact only (no shared edge)*
  - unit also present in the F6 corner: — none —
- **E → F7**
  - aligned (continuous): U01 21px

### F7  —  x 2612–3134, y 3034–3540

- mapped geology **1.3%**, no-data **98.7%**, distinct units **1**
- v1 → v2: **13,024 px** changed (overlay removed 6,081, gaps filled 3,352)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 3,352 | 1.27% | 2 | 3,044 |

- **NW → E6**
  - *corner contact only (no shared edge)*
  - unit also present in the E6 corner: — none —
- **W → E7**
  - aligned (continuous): U01 21px
- **N → F6**
  - aligned (continuous): — none —
- **NE → G6**
  - *corner contact only (no shared edge)*
  - unit also present in the G6 corner: — none —
- **E → G7**
  - aligned (continuous): — none —

### G7  —  x 3134–3656, y 3034–3540

- mapped geology **0.0%**, no-data **100.0%**, distinct units **1**
- v1 → v2: **11,274 px** changed (overlay removed 7,562, gaps filled 68)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U01 | #98DAF2 `rgb(152, 218, 242)` | 68 | 0.03% | 0 | 17 |

- **NW → F6**
  - *corner contact only (no shared edge)*
  - unit also present in the F6 corner: — none —
- **W → F7**
  - aligned (continuous): — none —
- **N → G6**
  - aligned (continuous): — none —
- **NE → H6**
  - *corner contact only (no shared edge)*
  - unit also present in the H6 corner: — none —
- **E → H7**
  - aligned (continuous): — none —

### H7  —  x 3656–4179, y 3034–3540

- mapped geology **0.0%**, no-data **100.0%**, distinct units **1**
- v1 → v2: **10,734 px** changed (overlay removed 7,017, gaps filled 65)
- agreement with NGSA reference: **0.0%**

| unit | colour | area px | % cell | polygons ≥200 px | largest |
|---|---|---|---|---|---|
| U08 | #DFC477 `rgb(223, 196, 119)` | 65 | 0.02% | 0 | 17 |

- **NW → G6**
  - *corner contact only (no shared edge)*
  - unit also present in the G6 corner: — none —
- **W → G7**
  - aligned (continuous): — none —
- **N → H6**
  - aligned (continuous): — none —
- **NE → I6**
  - *corner contact only (no shared edge)*
  - unit also present in the I6 corner: — none —
- **E → I7**
  - aligned (continuous): — none —

### I7  —  x 4179–4701, y 3034–3540

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### J7  —  x 4701–5223, y 3034–3540

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### K7  —  x 5223–5746, y 3034–3540

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

### L7  —  x 5746–6268, y 3034–3540

**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.

---

## Summary matrix — mapped-geology coverage (%)

| | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | 1 | 55 | 67 | 34 | 19 | 45 | 45 | 62 | 0 | 0 | 0 | 0 |
| **2** | 9 | 100 | 100 | 100 | 100 | 100 | 100 | 76 | 0 | 0 | 0 | 0 |
| **3** | 8 | 97 | 100 | 100 | 99 | 100 | 100 | 17 | 0 | 0 | 0 | 0 |
| **4** | 54 | 100 | 100 | 100 | 100 | 100 | 65 | 1 | 0 | 0 | 0 | 0 |
| **5** | 61 | 100 | 100 | 100 | 95 | 80 | 15 | 0 | 0 | 0 | 0 | 0 |
| **6** | 85 | 100 | 100 | 100 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **7** | 69 | 79 | 78 | 78 | 35 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## Summary matrix — agreement with NGSA (%)

| | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | 48 | 82 | 75 | 76 | 66 | 80 | 85 | 87 | — | — | — | — |
| **2** | 63 | 73 | 75 | 76 | 77 | 83 | 84 | 82 | — | — | — | — |
| **3** | 71 | 76 | 78 | 81 | 71 | 79 | 86 | 78 | — | — | — | — |
| **4** | 77 | 75 | 80 | 77 | 76 | 85 | 79 | 75 | — | — | — | — |
| **5** | 72 | 67 | 76 | 75 | 77 | 86 | 79 | — | — | — | — | — |
| **6** | 93 | 90 | 77 | 73 | 81 | — | — | — | — | — | — | — |
| **7** | 98 | 98 | 83 | 84 | 86 | — | — | — | — | — | — | — |
