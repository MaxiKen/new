"""The sheet's own printed block grid, in source-pixel space.

Version 1 ships a gridded view whose letters (A..K) and numbers (1..11) are
the surveyor's block grid, tied to the printed graticule: meridian 3E..14E and
parallel 4N..13N, with the top and bottom blocks closed by the neatline. The
positions below were measured from ``NGSA_map_geology_legend_gridded.png``
(whose offset to the source photograph is +10 in x and -10 in y) so that block
IDs used here are identical to the IDs the reviewer reads off the sheet.
"""
import numpy as np

MERIDIAN_X = [407.0, 736.0, 1065.0, 1393.0, 1722.0, 2050.0, 2378.0, 2707.0,
              3035.0, 3364.0, 3691.0, 4019.5]
PARALLEL_Y = [483.0, 811.3, 1139.6, 1467.9, 1796.2, 2124.5, 2452.8, 2781.1,
              3109.4, 3437.7]
NEATLINE_TOP, NEATLINE_BOTTOM = 186.0, 3579.0
LETTERS = 'ABCDEFGHIJK'

ROW_Y = [NEATLINE_TOP] + PARALLEL_Y + [NEATLINE_BOTTOM]


def columns():
    return [(LETTERS[i], MERIDIAN_X[i], MERIDIAN_X[i + 1]) for i in range(11)]


def rows():
    return [(r + 1, ROW_Y[r], ROW_Y[r + 1]) for r in range(11)]


def cells():
    """Yield (name, letter, number, x0, y0, x1, y1) in review order.

    Review order is A1, B1, C1 ... across the top row, then the next row down,
    which is the order the sheet is read in.
    """
    for number, y0, y1 in rows():
        for letter, x0, x1 in columns():
            yield f'{letter}{number}', letter, number, x0, y0, x1, y1


def neighbours(letter, number):
    """The eight surrounding blocks that exist on the sheet."""
    i, j = LETTERS.index(letter), number - 1
    out = []
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            ni, nj = i + di, j + dj
            if 0 <= ni < 11 and 0 <= nj < 11:
                out.append(f'{LETTERS[ni]}{nj + 1}')
    return out


def bbox_of(name):
    letter, number = name[0], int(name[1:])
    _, x0, x1 = columns()[LETTERS.index(letter)]
    _, y0, y1 = rows()[number - 1]
    return x0, y0, x1, y1


def box_array(shape):
    """Per-pixel block index array (-1 outside the grid), for vectorised work."""
    h, w = shape
    ys, xs = np.mgrid[0:h, 0:w]
    col = np.full((h, w), -1, np.int16)
    row = np.full((h, w), -1, np.int16)
    edges = np.array(MERIDIAN_X)
    row_edges = np.array(ROW_Y)
    col[:] = np.clip(np.searchsorted(edges, xs, side='right') - 1, -1, 11)
    col[(xs < edges[0]) | (xs > edges[-1])] = -1
    row[:] = np.clip(np.searchsorted(row_edges, ys, side='right') - 1, -1, 11)
    row[(ys < row_edges[0]) | (ys > row_edges[-1])] = -1
    return col, row
