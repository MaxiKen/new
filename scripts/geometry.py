"""Small independently testable primitives used by the map build."""
import numpy as np
from scipy import ndimage as ndi
import shapely as sh
from shapely.geometry import LineString


def fill_labels(seeds, footprint):
    """Assign unknown cells to nearest seed; never invent a zero/black class."""
    if not np.any(seeds[footprint] > 0):
        raise ValueError('No reliable interior seeds')
    seeds = np.where(footprint, seeds, 0)
    _, indices = ndi.distance_transform_edt(seeds == 0, return_indices=True)
    result = seeds[indices[0], indices[1]]
    result[~footprint] = 0
    return result


def no_black_palette(colors):
    """Reject black AND near-black fills, not only the literal #000000."""
    return all(max(int(c[j:j + 2], 16) for j in (1, 3, 5)) >= 80 for c in colors)


def smooth_samples(a, sigma, closed):
    if closed:
        b = ndi.gaussian_filter1d(a[:-1], sigma, axis=0, mode='wrap')
        return np.vstack([b, b[0]])
    b = ndi.gaussian_filter1d(a, sigma, axis=0, mode='nearest')
    t = np.linspace(0, 1, len(a))[:, None]
    b += (1 - t) * (a[0] - b[0]) + t * (a[-1] - b[-1])
    b[0], b[-1] = a[0], a[-1]
    return b


def validate_coverage(polygons):
    assert all(p.geom_type == 'Polygon' and p.is_valid and not p.is_empty for p in polygons)
    assert sh.coverage_is_valid(polygons), 'Shared edges do not match'
    union = sh.coverage_union_all(polygons)
    parts = [union] if union.geom_type == 'Polygon' else list(union.geoms)
    assert sum(len(p.interiors) for p in parts) == 0, 'Internal unassigned holes'
    assert abs(float(sh.area(polygons).sum()) - union.area) < max(1e-8, union.area * 1e-10)
    return union
