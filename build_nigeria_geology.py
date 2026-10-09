#!/usr/bin/env python3
"""Digitize the supplied Nigeria geology map into a GeoPackage polygon layer.

The source legend contains 86 entries but reuses just 12 fill colors. Since the
raster does not distinguish entries that share a color, the output keeps those
entries together in one multipart feature per visible color instead of guessing
which individual name belongs to a same-colored patch.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

import cv2
import fiona
import numpy as np
import shapely
from affine import Affine
from PIL import Image
from rasterio.features import rasterize, shapes
from shapely.geometry import MultiPolygon, mapping, shape
from shapely.ops import unary_union

LEGENDS = (
    "Alluvium",
    "Amphibole Schist, Amphibolite",
    "Banded Gneiss/Biotite Gneiss",
    "Banded Iron Formation",
    "Basalt",
    "Biotite Garnet Gneiss Schist",
    "Biotite Granite",
    "Biotite Hornblende Gneiss",
    "Biotite and biotite Hornblende granodiorite",
    "Black shale, siltstone and sandstone",
    "Blackshale, Siltstone and Sandstone",
    "Charnockitic Rocks",
    "Clay Grit and Pebbles",
    "Clay and Shale with Limestone Intercalations",
    "Clay clayey sands and shale",
    "Clay, Clayey Sands and Shale",
    "Clays and loose sandstone",
    "Coal sandstone and shale",
    "Coal, Sandstone and Shale",
    "Coal, Shale and Sandstone",
    "Coarse Porphyritic hornblende granite",
    "Coarse porphyritic porphyroblastic mica granite",
    "Coarse, Porphyritic biotite and biotite muscovite granite",
    "Dolerite",
    "False - Bedded Sandstone",
    "Feldspathic sandstone and siltstone",
    "Feldspathic sandstone calcerous sandstone and shelly limestone",
    "Fine-grained biotite granite",
    "Fine-grained flaggy quartzite and Quartz Schist",
    "Gabbro and quartz gabbro and meta intrusives",
    "Granite Gneiss",
    "Granite and Granite Porphyry",
    "Gravel and Sand",
    "Hypersthene quartz-diorite",
    "Ignimbrite",
    "Lignite, Claystone and shale",
    "Limestone",
    "Marble",
    "Medium-to-coarse-Grained Biotite granite",
    "Meta Volcanic Meta Sedimentary including pebbly schist",
    "Meta-conglomerate",
    "Migmatite",
    "Migmatitic Gneiss",
    "Migmatitic augen Gneiss",
    "Mylonites",
    "Mylonites Interlayered with Amphibolites",
    "Pebbles and Grit",
    "Pegmatite",
    "Pelitic Schist/Muscovite Schist",
    "Porphyritic Granite/Coarse porphyritic biotite and biotite hornblende granite",
    "Porphyry/Quartz Porphyry",
    "Quartz feldspathic granulite and gneiss",
    "Quartz porphyry",
    "Quartzite, massive and schistose, also occuring as ridges",
    "Rhyolite",
    "Sand and Clay",
    "Sand, Clay and Swamp",
    "Sands and Pebbles",
    "Sands, Clays, Siltstones and limestones",
    "Sands, Gravels and Clay",
    "Sandstone",
    "Sandstone and Clay",
    "Sandstone and Ironstone",
    "Sandstone and Limestone",
    "Sandstone, Limestone, Coal",
    "Sandstone, Siltstone and Shale",
    "Sandstone, Siltstone, Shale and Ironstone",
    "Sandstone, shale and clay",
    "Sandstone, shale and sandy shale",
    "Sandstones and Clays",
    "Sandstones, Clays and Shale",
    "Shale (Phosphate nodules)",
    "Shale and Limestone",
    "Shale and Limestone with Sandstone Intercalations",
    "Shale and Mudstone",
    "Shale, Limestone and Sandstone",
    "Shale, Sandclay, Calcerous sandstones",
    "Silicified, sheared rocks, large quartz veins",
    "Slate phylite and meta siltstone, locally hornfelstic/carbonaceous",
    "Syenite, Quartz-Syenite and Gabbro",
    "Syenite, mainly of Pyroxenen Diorite composition",
    "Trachy - andesline",
    "Undifferentiated Schists, including Phyllites",
    "Undifferentiated Migmatite and granite, Gneiss porphyroblastic",
    "Younger Basalt",
    "porphroblastic Gneiss",
)

# Centers of the first 12 legend swatches (image pixel coordinates).
SWATCH_CENTERS = (649, 681, 714, 746, 779, 811, 843, 876, 908, 941, 973, 1006)
SWATCH_X = slice(52, 73)
# Map image graticule control points, in source-image pixel coordinates.
X_GRID = ((4.0, 132.0), (8.0, 345.5), (12.0, 558.5))
Y_GRID = ((14.0, 33.5), (10.0, 253.5), (6.0, 471.5))
MAP_CROP = (32, 30, 710, 585)  # left, top, right, bottom
NATURAL_EARTH_ZIP = (
    "https://codeload.github.com/datasets/geo-countries/zip/refs/heads/main"
)


def nigeria_boundary():
    """Return the public-domain Natural Earth Nigeria polygon in EPSG:4326."""
    with urllib.request.urlopen(NATURAL_EARTH_ZIP, timeout=90) as response:
        archive = zipfile.ZipFile(BytesIO(response.read()))
    geojson_path = next(
        name for name in archive.namelist() if name.endswith("/data/countries.geojson")
    )
    collection = json.loads(archive.read(geojson_path))
    feature = next(
        item for item in collection["features"]
        if item["properties"].get("name") == "Nigeria"
    )
    return shape(feature["geometry"])


def make_valid_multipolygon(geometry):
    geometry = shapely.make_valid(geometry)
    if geometry.geom_type == "Polygon":
        return MultiPolygon([geometry])
    if geometry.geom_type == "MultiPolygon":
        return geometry
    polygons = [
        part for part in getattr(geometry, "geoms", ())
        if part.geom_type == "Polygon"
    ]
    return MultiPolygon(polygons)


def digitize(image_path: Path, output_path: Path):
    if len(LEGENDS) != 86:
        raise RuntimeError(f"Expected 86 source legend entries, found {len(LEGENDS)}")

    image = np.asarray(Image.open(image_path).convert("RGB"))
    if image.shape[:2] != (1210, 1700):
        raise ValueError(
            f"Unexpected source image dimensions {image.shape[1]}x{image.shape[0]}; "
            "the map pixel control points are for the supplied 1700x1210 image."
        )

    left, top, right, bottom = MAP_CROP
    width, height = right - left, bottom - top
    source = image[top:bottom, left:right].copy()

    # Fit pixel-per-degree scale to the map's printed graticule.
    px_per_degree_lon = float(
        np.polyfit([point[0] for point in X_GRID], [point[1] for point in X_GRID], 1)[0]
    )
    px_per_degree_lat = float(
        np.polyfit([point[0] for point in Y_GRID], [point[1] for point in Y_GRID], 1)[0]
    )
    lon_at_left = X_GRID[0][0] + (left - X_GRID[0][1]) / px_per_degree_lon
    lat_at_top = Y_GRID[0][0] + (top - Y_GRID[0][1]) / px_per_degree_lat
    x_resolution = 1.0 / px_per_degree_lon
    y_resolution = -1.0 / px_per_degree_lat
    base_transform = Affine(
        x_resolution, 0, lon_at_left,
        0, -y_resolution, lat_at_top,
    )

    boundary = nigeria_boundary()
    country_coarse = rasterize(
        [(boundary, 1)],
        out_shape=(height, width),
        transform=base_transform,
        fill=0,
        all_touched=False,
        dtype="uint8",
    )

    # The source uses a 12-color repeating palette; sample the swatches directly.
    palette = np.asarray(
        [
            np.median(image[y - 6:y + 7, SWATCH_X].reshape(-1, 3), axis=0)
            for y in SWATCH_CENTERS
        ],
        dtype=np.float32,
    )
    distances = np.linalg.norm(
        source[:, :, None, :].astype(np.float32) - palette[None, None, :, :],
        axis=3,
    )
    nearest = distances.argmin(axis=2).astype(np.uint8)
    nearest_distance = distances.min(axis=2)
    saturation = cv2.cvtColor(source, cv2.COLOR_RGB2HSV)[:, :, 1]

    # Suppress graticule line pixels; interpolate their underlying map color from
    # the nearest confident colored pixel. The gray legend swatch is retained when
    # a pixel is close to that swatch's actual light-gray fill.
    confident = ((nearest_distance < 65) & (saturation > 18)) | (
        (nearest == 8) & (nearest_distance < 22)
    )
    for _, grid_x in X_GRID:
        column = int(round(grid_x - left))
        confident[:, max(0, column - 2):min(width, column + 3)] = False
    for _, grid_y in Y_GRID[1:]:
        row = int(round(grid_y - top))
        confident[max(0, row - 2):min(height, row + 3), :] = False

    known = confident & (country_coarse != 0)
    known_counts = np.bincount(nearest[known], minlength=12)
    if np.any(known_counts == 0):
        raise RuntimeError(
            "A visible swatch class has no confident pixels inside the Nigeria mask."
        )

    # Fill graticule strokes, antialiased edge pixels, and small pale gaps by the
    # nearest confident map pixel, while keeping every pixel of Nigeria assigned.
    nearest_distance_px = np.full((height, width), np.inf, dtype=np.float32)
    spatial_label = np.zeros((height, width), dtype=np.uint8)
    for class_id in range(12):
        seed = known & (nearest == class_id)
        distance_input = np.where(seed, 0, 255).astype(np.uint8)
        spatial_distance = cv2.distanceTransform(distance_input, cv2.DIST_L2, 5)
        update = spatial_distance < nearest_distance_px
        nearest_distance_px[update] = spatial_distance[update]
        spatial_label[update] = class_id

    labels = nearest.copy()
    labels[~known] = spatial_label[~known]

    # Supersample and smooth category transitions before polygonization.
    scale = 4
    high_height, high_width = height * scale, width * scale
    labels_up = cv2.resize(
        labels, (high_width, high_height), interpolation=cv2.INTER_NEAREST
    )
    high_transform = Affine(
        x_resolution / scale, 0, lon_at_left,
        0, -y_resolution / scale, lat_at_top,
    )
    country_high = rasterize(
        [(boundary, 1)],
        out_shape=(high_height, high_width),
        transform=high_transform,
        fill=0,
        all_touched=False,
        dtype="uint8",
    )
    country_probability = cv2.GaussianBlur(
        country_high.astype(np.float32), (0, 0), sigmaX=1.8, sigmaY=1.8
    )
    country_high = (country_probability >= 0.5).astype(np.uint8)

    best_probability = np.full((high_height, high_width), -1.0, dtype=np.float32)
    labels_high = np.zeros((high_height, high_width), dtype=np.uint8)
    for class_id in range(12):
        layer = ((labels_up == class_id) & (country_high != 0)).astype(np.float32)
        probability = cv2.GaussianBlur(
            layer, (0, 0), sigmaX=1.8, sigmaY=1.8
        )
        replace = probability > best_probability
        labels_high[replace] = class_id
        best_probability[replace] = probability[replace]

    parts = {class_id: [] for class_id in range(12)}
    for geometry_json, value in shapes(
        labels_high,
        mask=country_high.astype(bool),
        transform=high_transform,
        connectivity=4,
    ):
        parts[int(value)].append(shape(geometry_json))

    geometries = []
    for class_id in range(12):
        if not parts[class_id]:
            raise RuntimeError(f"Visible map color {class_id + 1} produced no polygon.")
        geometries.append(make_valid_multipolygon(unary_union(parts[class_id])))

    # Simplify the polygon coverage without opening gaps or changing shared edges.
    if shapely.coverage_is_valid(geometries):
        simplified = list(
            shapely.coverage_simplify(
                geometries, tolerance=0.0045, simplify_boundary=True
            )
        )
        if (
            all(not geometry.is_empty and geometry.is_valid for geometry in simplified)
            and shapely.coverage_is_valid(simplified)
        ):
            geometries = simplified

    # Verify that the 12 features completely cover the national mask.
    mask_parts = [
        shape(geometry_json)
        for geometry_json, _ in shapes(
            country_high,
            mask=country_high.astype(bool),
            transform=high_transform,
            connectivity=4,
        )
    ]
    mask_geometry = unary_union(mask_parts)
    union_geometry = unary_union(geometries)
    difference_area = mask_geometry.symmetric_difference(union_geometry).area
    if difference_area > 1e-8:
        raise RuntimeError(f"Polygon coverage has a gap/overlap: {difference_area} sq deg")

    names_by_class = [LEGENDS[class_id::12] for class_id in range(12)]
    if sum(map(len, names_by_class)) != 86:
        raise RuntimeError("Legend grouping did not retain all 86 legend entries.")

    if output_path.exists():
        output_path.unlink()
    schema = {
        "geometry": "MultiPolygon",
        "properties": {
            "name": "str:2048",
            "palette_id": "str:3",
            "map_color": "str:7",
            "legend_n": "int",
        },
    }
    with fiona.open(
        output_path,
        mode="w",
        driver="GPKG",
        layer="nigeria_geology",
        schema=schema,
        crs="EPSG:4326",
        encoding="UTF-8",
        SPATIAL_INDEX="YES",
    ) as output:
        for class_id, geometry in enumerate(geometries):
            rgb = np.clip(np.rint(palette[class_id]), 0, 255).astype(int)
            color = "#" + "".join(f"{channel:02X}" for channel in rgb)
            names = names_by_class[class_id]
            output.write(
                {
                    "geometry": mapping(geometry),
                    "properties": {
                        "name": " | ".join(names),
                        "palette_id": f"C{class_id + 1:02d}",
                        "map_color": color,
                        "legend_n": len(names),
                    },
                }
            )

    description = (
        "Nigeria geology raster digitization. 86 source legend entries, grouped "
        "into 12 repeated fill colors; name values are pipe-delimited. EPSG:4326."
    )
    with sqlite3.connect(output_path) as database:
        database.execute(
            "UPDATE gpkg_contents SET identifier=?, description=? WHERE table_name=?",
            ("nigeria_geology", description, "nigeria_geology"),
        )
        database.commit()

    return palette, known_counts, union_geometry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        type=Path,
        default=Path(__file__).with_name("pic geology of nigeria.png"),
        help="input map PNG (default: supplied image beside this script)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("nigeria_geology.gpkg"),
        help="output GeoPackage path",
    )
    args = parser.parse_args()
    palette, known_counts, union = digitize(args.image, args.output)
    print(f"Wrote {args.output} (layer nigeria_geology; EPSG:4326)")
    print(f"Source legend entries: {len(LEGENDS)}; output color features: 12")
    print(f"Confident source pixels by color class: {known_counts.tolist()}")
    print(f"Covered polygon union area: {union.area:.6f} square degrees")
    print("Palette RGB centers:", [tuple(c.astype(int)) for c in palette])


if __name__ == "__main__":
    main()
