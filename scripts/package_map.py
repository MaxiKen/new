from pathlib import Path
import json, zipfile, shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/map';WEB=ROOT/'public/data'
report=json.loads((OUT/'validation.json').read_text())
assert report['allValid'] and report['internalGapCount']==0 and report['noBlackOrNearBlackFills']
shutil.copyfile(ROOT/'docs/NOTES.md',OUT/'README.md')
shutil.copyfile(ROOT/'docs/NOTES.md',WEB/'NOTES.md')
destination=WEB/'NGSA_geology_v8.zip'
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(OUT.iterdir()):
        if file.is_file():z.write(file,arcname='NGSA_geology_v8/'+file.name)
    z.write(WEB/'source.jpg',arcname='NGSA_geology_v8/source_reference.jpg')
with zipfile.ZipFile(destination) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.shp')])==3
print(f'Validated GIS package: {destination.relative_to(ROOT)} ({destination.stat().st_size/1024**2:.2f} MiB)')
