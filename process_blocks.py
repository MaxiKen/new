import cv2
import numpy as np
import scipy.ndimage as ndi
import json
import time
import os

def main():
    start_time = time.time()
    print("=== Loading High-Resolution Geological Maps ===")
    iso_path = 'NGSA_map_geology_legend_isolated.png'
    ngsa_path = 'pic NGSA geological-map-of-nigeria-.jpg'

    iso = cv2.imread(iso_path)
    ngsa = cv2.imread(ngsa_path)

    h_iso, w_iso = iso.shape[:2]
    crop_ngsa = ngsa[96:96+3540, 120:120+6268].copy()

    # Extract legend swatches
    legend_iso = iso[:, 4150:]
    legend_mask = ~((legend_iso[:,:,0]>240) & (legend_iso[:,:,1]>240) & (legend_iso[:,:,2]>240)) & \
                  ~((legend_iso[:,:,0]<30) & (legend_iso[:,:,1]<30) & (legend_iso[:,:,2]<30))

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(legend_mask.astype(np.uint8))
    swatches = []
    for i in range(1, num_labels):
        w, h, area = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT], stats[i, cv2.CC_STAT_AREA]
        if 20 <= w <= 150 and 10 <= h <= 100 and area > 200:
            mask_i = labels == i
            color = np.median(legend_iso[mask_i], axis=0).astype(np.uint8)
            swatches.append(color)

    palette = np.unique(np.array(swatches), axis=0)
    print(f"Extracted {len(palette)} canonical geology swatches from legend.")

    # Map ROI: y in [92, 3428], x in [68, 4155]
    y_min, y_max = 92, 3428
    x_min, x_max = 68, 4155

    map_iso = iso[y_min:y_max, x_min:x_max].copy()
    map_ngsa = crop_ngsa[y_min:y_max, x_min:x_max].copy()

    # 1. Segment Outside Nigeria vs Inside Nigeria (Nigeria Territory + Ocean)
    white_mask = (map_iso[:,:,0] == 255) & (map_iso[:,:,1] == 255) & (map_iso[:,:,2] == 255)
    num_l, labs, sts, _ = cv2.connectedComponentsWithStats(white_mask.astype(np.uint8))

    outside_mask = np.zeros_like(white_mask)
    for i in range(1, num_l):
        if sts[i, cv2.CC_STAT_AREA] > 10000:
            outside_mask |= (labs == i)

    inside_nigeria = ~outside_mask
    print(f"Territory segmented: Inside Nigeria & Ocean = {np.sum(inside_nigeria):,} pixels, Outside Isolated = {np.sum(outside_mask):,} pixels.")

    # 2. Dark non-geology masks (text, road lines, state boundaries, fault symbols, grid ticks)
    gray_ngsa = cv2.cvtColor(map_ngsa, cv2.COLOR_BGR2GRAY)
    gray_iso = cv2.cvtColor(map_iso, cv2.COLOR_BGR2GRAY)
    is_dark_ngsa = gray_ngsa < 90
    is_dark_iso = gray_iso < 90

    # 3. Detect features from NGSA
    # Water bodies: B > R + 35 and B > 140 and G > 120
    is_water_ngsa = (map_ngsa[:,:,0].astype(int) - map_ngsa[:,:,2].astype(int) > 35) & \
                    (map_ngsa[:,:,0] > 140) & (map_ngsa[:,:,1] > 120) & \
                    (~is_dark_ngsa) & inside_nigeria

    # Younger Granite Ring Complexes (magenta/pink/purple):
    is_magenta_ngsa = (map_ngsa[:,:,2] > 160) & (map_ngsa[:,:,0] > 140) & (map_ngsa[:,:,1] < 140) & \
                      (~is_dark_ngsa) & inside_nigeria

    # Volcanics / Newer Basalts:
    is_volcanic_ngsa = (map_ngsa[:,:,1] > 140) & (map_ngsa[:,:,1] < 200) & (map_ngsa[:,:,0] < 110) & (map_ngsa[:,:,2] < 110) & \
                       (~is_dark_ngsa) & inside_nigeria

    # Initialize Version 2 Map
    v2_map = map_iso.copy()

    water_swatch = np.array([204, 182, 108], dtype=np.uint8)
    magenta_swatch = np.array([253, 2, 220], dtype=np.uint8)
    volcanic_swatch = np.array([52, 193, 115], dtype=np.uint8)

    v2_map[is_water_ngsa] = water_swatch
    v2_map[is_magenta_ngsa] = magenta_swatch
    v2_map[is_volcanic_ngsa] = volcanic_swatch

    # Inpaint internal holes & dark lines using morphological nearest valid geology
    needs_fill = ((white_mask & inside_nigeria) | (is_dark_iso & inside_nigeria) | (is_dark_ngsa & inside_nigeria)) & \
                 (~is_water_ngsa) & (~is_magenta_ngsa) & (~is_volcanic_ngsa)
    valid_geology = (~needs_fill) & inside_nigeria

    print(f"Inpainting {np.sum(needs_fill):,} non-geology pixels across Nigeria map...")
    dist, (idx_y, idx_x) = ndi.distance_transform_edt(~valid_geology, return_indices=True)
    v2_map[needs_fill] = v2_map[idx_y[needs_fill], idx_x[needs_fill]]

    # Grid columns and rows
    cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    col_bounds = [int(x) for x in np.linspace(0, map_iso.shape[1], 13)]
    row_bounds = [int(y) for y in np.linspace(0, map_iso.shape[0], 11)]

    # Directional kernels for feature reconnection
    kernels = []
    for angle in [0, 45, 90, 135]:
        rad = np.deg2rad(angle)
        dx, dy = int(round(6 * np.cos(rad))), int(round(6 * np.sin(rad)))
        k = np.zeros((abs(dy)*2+1, abs(dx)*2+1), dtype=np.uint8)
        cv2.line(k, (k.shape[1]//2 - dx, k.shape[0]//2 - dy),
                    (k.shape[1]//2 + dx, k.shape[0]//2 + dy), 1, thickness=1)
        kernels.append(k)

    # Process all 120 blocks
    block_records = []
    print("\n==================== PROCESSING ALL 120 BLOCKS (A1 to L10) ====================")

    for r in range(10):
        for c in range(12):
            b_name = f"{cols[c]}{r+1}"
            x0, x1 = col_bounds[c], col_bounds[c+1]
            y0, y1 = row_bounds[r], row_bounds[r+1]

            b_orig = map_iso[y0:y1, x0:x1]
            b_v2 = v2_map[y0:y1, x0:x1]
            b_inside = inside_nigeria[y0:y1, x0:x1]
            b_fill = needs_fill[y0:y1, x0:x1]

            coverage_pct = float(np.mean(b_inside) * 100.0)

            # Block feature reconnection
            bridged_count = 0
            if coverage_pct > 1.0:
                # Find distinct colors present in this block
                b_colors = b_v2[b_inside]
                if len(b_colors) > 0:
                    u_colors, counts = np.unique(b_colors, axis=0, return_counts=True)
                    for col_val, cnt in zip(u_colors, counts):
                        if 30 < cnt < (b_v2.shape[0]*b_v2.shape[1] * 0.7):
                            col_mask = (b_v2[:,:,0] == col_val[0]) & (b_v2[:,:,1] == col_val[1]) & (b_v2[:,:,2] == col_val[2]) & b_inside
                            col_u8 = col_mask.astype(np.uint8)
                            for k in kernels:
                                closed = cv2.morphologyEx(col_u8, cv2.MORPH_CLOSE, k)
                                bridge = (closed == 1) & (~col_mask) & b_inside & b_fill
                                if np.sum(bridge) > 0:
                                    b_v2[bridge] = col_val
                                    bridged_count += int(np.sum(bridge))

            # Restored pixels count
            restored_geo = int(np.sum(is_water_ngsa[y0:y1, x0:x1] | is_magenta_ngsa[y0:y1, x0:x1] | is_volcanic_ngsa[y0:y1, x0:x1]))
            inpainted_px = int(np.sum(b_fill))

            # Classify Geological Units
            geo_units = []
            if coverage_pct > 1.0:
                b_colors = b_v2[b_inside]
                if len(b_colors) > 0:
                    if np.any((b_colors[:,0] > 180) & (b_colors[:,2] < 120)):
                        geo_units.append("Water Bodies (Lakes / Rivers)")
                    if np.any((b_colors[:,2] > 160) & (b_colors[:,0] > 140) & (b_colors[:,1] < 140)):
                        geo_units.append("Younger Granites (Jurassic Ring Complexes)")
                    if np.any((b_colors[:,1] > 140) & (b_colors[:,0] < 110) & (b_colors[:,2] < 110)):
                        geo_units.append("Volcanics / Newer Basalts")
                    if np.any((b_colors[:,0] > 150) & (b_colors[:,1] > 150) & (b_colors[:,2] > 200)):
                        geo_units.append("Basement Complex (Migmatites, Gneisses, Schists)")
                    if np.any((b_colors[:,0] < 120) & (b_colors[:,1] > 180) & (b_colors[:,2] > 180)):
                        geo_units.append("Cretaceous Sediments (Benue, Bida, Sokoto Basins)")
                    if np.any((b_colors[:,0] < 140) & (b_colors[:,1] > 200) & (b_colors[:,2] < 140)):
                        geo_units.append("Tertiary / Quaternary Sediments (Chad / Coastal Sands)")
                    if np.any((b_colors[:,0] > 220) & (b_colors[:,1] > 200) & (b_colors[:,2] < 170)):
                        geo_units.append("Coastal Deltaic Alluvium / Ocean")

            if len(geo_units) == 0:
                if coverage_pct < 1.0:
                    geo_units.append("Surrounding Border Region (White isolated)")
                else:
                    geo_units.append("Undifferentiated Basement Complex")

            # 8-Neighbors list
            neighbor_names = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 10 and 0 <= nc < 12:
                        neighbor_names.append(f"{cols[nc]}{nr+1}")

            record = {
                "block": b_name,
                "col": cols[c],
                "row": r + 1,
                "coverage_pct": round(coverage_pct, 1),
                "geological_units": geo_units,
                "restored_geo_pixels": restored_geo,
                "inpainted_pixels": inpainted_px,
                "bridged_features_px": bridged_count,
                "neighbors_connected": neighbor_names
            }
            block_records.append(record)

            status_str = f"Block {b_name:3s} [Row {r+1:2d}, Col {cols[c]}]: Coverage={coverage_pct:5.1f}% | Restored={restored_geo:5d} px | Inpainted={inpainted_px:5d} px | Bridged={bridged_count:4d} px | Neighbors={len(neighbor_names)} connected"
            print(status_str)

    # Outside Nigeria remains pure white [255, 255, 255]
    v2_map[outside_mask] = [255, 255, 255]

    # Clean border lines: non-gridded inside map
    print("\n=== Removing Grid Lines & Polishing Frame Borders ===")
    v2_full = iso.copy()
    v2_full[y_min:y_max, x_min:x_max] = v2_map

    # Clean map frame outer rectangle
    cv2.rectangle(v2_full, (x_min, y_min), (x_max, y_max), (0, 0, 0), 2)

    # Save output files
    out_file1 = 'NGSA_map_geology_legend_isolated_v2.png'
    out_file2 = 'isolated_v2.png'
    cv2.imwrite(out_file1, v2_full)
    cv2.imwrite(out_file2, v2_full)

    with open('block_records.json', 'w') as f:
        json.dump(block_records, f, indent=2)

    print(f"\nDeliverable successfully written: {out_file1} ({v2_full.shape[1]}x{v2_full.shape[0]} px, PNG format)")
    print(f"Total processing time: {time.time() - start_time:.2f} seconds.")

if __name__ == '__main__':
    main()
