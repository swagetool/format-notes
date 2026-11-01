# DXF objects on a layout sheet come in the same layer as the model

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A DXF holds the drawing itself (model space) and one or more layout sheets (paper space) with frames, title blocks and viewports. GDAL returns the entities of both spaces from the same `entities` layer. The only difference is the field `PaperSpace`: set for an object on a sheet, empty otherwise. The snippet has a hand-written DXF with two road lines in model space and a frame and a title block on a sheet. All four come back, and the frame and the title block carry a layer name of their own, which does not mark them as sheet objects.

Anything that takes the geometry of the layer as data puts the sheet frame on the map next to the roads. Sheet coordinates are those of the paper, and they have nothing to do with the CRS of the drawing.

## Reproduce

Snippet file: `paper-space-objects-in-the-same-layer.py`

```python
import os, tempfile
from osgeo import ogr

def line(layer, x, paper):
    pairs = [0, "LINE", 8, layer]
    if paper:
        pairs += [67, 1]          # group 67 = 1 puts the entity on a layout sheet
    return pairs + [10, x, 20, 0, 11, x + 10, 21, 10]

pairs = ([0, "SECTION", 2, "ENTITIES"] + line("ROAD", 0, False) + line("ROAD", 100, False)
         + line("FRAME", 0, True) + line("TITLEBLOCK", 5, True) + [0, "ENDSEC", 0, "EOF"])
path = os.path.join(tempfile.mkdtemp(), "t.dxf")
open(path, "w").write("".join("%s\n" % p for p in pairs))

back = ogr.Open(path)
lyr = back.GetLayer(0)
print("layers:", back.GetLayerCount(), "features:", lyr.GetFeatureCount())
for f in lyr:
    print(f.GetField("Layer").ljust(11), "PaperSpace =", f.GetField("PaperSpace"), f.GetGeometryRef().ExportToWkt())
```

Output, as printed (standard output first, then standard error):

```
layers: 1 features: 4
ROAD        PaperSpace = None LINESTRING (0 0,10 10)
ROAD        PaperSpace = None LINESTRING (100 0,110 10)
FRAME       PaperSpace = True LINESTRING (0 0,10 10)
TITLEBLOCK  PaperSpace = True LINESTRING (5 0,15 10)
```

## What to do

Read the `PaperSpace` field and keep sheet objects out of the data layers, or keep them apart under their own name. Tell the user how many were left out.

## Sources

- [GDAL DXF driver page](https://gdal.org/en/stable/drivers/vector/dxf.html): "PaperSpace: 1 if the entity is located on a layout (paper space), NULL otherwise."
- We did not find a GDAL issue about this.
