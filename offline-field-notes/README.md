# Offline Geological Field Notes

A standalone, offline coordinate-capture tool for collecting corrections to the Nigeria geological map. It includes the original reference map and the current shapefile draft, and **does not modify the shapefile**. Notes, coordinates, the automatically captured map source and color for each point, and in-progress work are saved in this browser's local storage.

## Start the tool

### Windows

Double-click `start_offline.bat`. It starts a tiny local web server and opens the tool in your default browser. If Windows asks which app to use, install Python 3 or use the Python command below.

### macOS or Linux

Open a terminal in this folder and run:

```sh
python3 start_offline.py
```

The page opens at `http://127.0.0.1:8765/`. Leave the terminal window running while using the tool; press **Ctrl+C** to stop it. The server only listens on your own computer and serves files from this folder. It makes no internet requests.

You can also open `index.html` directly. If a browser blocks pixel reading from `file://` images, the tool automatically loads bundled canvas-safe copies on the first sample and retries your point—no color code entry or re-click is needed. The included local HTTP launcher is still recommended because some browsers restrict local storage on `file://` pages. Keep using the same browser profile and launcher address to see the same saved notes; local storage belongs to that browser and address.

## Use it

1. Choose **Current draft**, **Original map**, or **Compare**. In compare view, drag the divider to reveal either map.
2. Drag with one finger or the mouse to pan. Use a two-finger pinch/spread on a phone, the mouse wheel, or the zoom buttons to zoom up to **1500%**. The A/B markers stay small and fixed-size as you zoom. Click a location to capture Point A and its longitude/latitude; the map side clicked and its pixel color are captured automatically. Sampling tries a direct pixel, a small image tile, and a downsampled-map fallback, and it retries automatically once the maps finish loading. If the browser blocks local-file pixel access, a bundled canvas-safe copy is loaded automatically and the same point is sampled again. The **Retry Point A color sample** and **Retry Point B color sample** buttons are only for exceptional failures; supported browsers can also use their visual eyedropper, with no typed color code needed. For keyboard use, tab to the map and press Enter or Space to capture its center.
3. Select one of the five edit types. For a join, choose **Pick the second point on the map** to record Point B; its map source and color are captured automatically too. A color mismatch needs an explicit confirmation before saving.
4. Add any context and save the note. Saved notes and unfinished work autosave in this browser.
5. Use **Copy all notes and show prompt** to create instructions to bring back here. **Export backup** downloads a JSON copy; import it in this or another browser to restore notes.

Coordinates are displayed as longitude, latitude in decimal degrees. **WGS 84 is assumed by the map transform; the original source datum is unconfirmed**, so check alignment before editing. Sampled colors are a reference aid, not guaranteed geological class assignments.

## Keep your work safe

Local storage is tied to the browser profile and origin, not copied with this folder. Export a JSON backup before moving the folder, changing browsers, clearing browser data, or using another computer. The map images and app files are bundled here, so once downloaded the tool needs no internet connection.
