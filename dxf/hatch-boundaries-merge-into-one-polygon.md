# A DXF hatch with several separate boundaries is read as one polygon with holes outside it

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A HATCH entity can hold several separate boundary paths. GDAL 3.10.3 returns such a hatch as one polygon. The first path becomes the shell and every other path becomes an interior ring, even when it lies far outside the shell. In the snippet two squares 100 units apart come back as one polygon with two rings. The reader prints nothing. The polygon is invalid, and the only message below comes from our own `IsValid()` call.

Any area, overlay or point-in-polygon work on that geometry is wrong, because the second square is treated as a hole in the first.

The issue below was fixed in GDAL master in October 2025 and backported to 3.11. We have not run a version with the fix.

## Reproduce

Snippet file: `hatch-boundaries-merge-into-one-polygon.py`

```python
import os, tempfile
from osgeo import ogr

def pairs(*items):
    return "".join("%s\n%s\n" % (c, v) for c, v in items)

def boundary(x0, y0, x1, y1):
    verts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = [(92, 3), (72, 0), (73, 1), (93, 4)]
    for x, y in verts:
        out += [(10, x), (20, y)]
    return out + [(97, 0)]

# One HATCH entity with two separate square boundaries, far apart.
hatch = [(0, "HATCH"), (8, "H"), (10, 0), (20, 0), (30, 0), (210, 0), (220, 0), (230, 1),
         (2, "SOLID"), (70, 1), (71, 0), (91, 2)]
hatch += boundary(0, 0, 10, 10) + boundary(100, 100, 110, 110)
hatch += [(75, 0), (76, 1), (98, 0)]

p = os.path.join(tempfile.mkdtemp(), "hatch.dxf")
with open(p, "w") as fh:
    fh.write(pairs((0, "SECTION"), (2, "ENTITIES")) + pairs(*hatch) + pairs((0, "ENDSEC"), (0, "EOF")))

src = ogr.Open(p)
lyr = src.GetLayer(0)
for f in lyr:
    g = f.GetGeometryRef()
    print(g.GetGeometryName(), "rings:", g.GetGeometryCount(), "valid:", bool(g.IsValid()))
    print(g.ExportToWkt())
```

Output, as printed (standard output first, then standard error):

```
POLYGON rings: 2 valid: False
POLYGON ((0 0,10 0,10 10,0 10,0 0),(100 100,110 100,110 110,100 110,100 100))
[stderr] Warning 1: Hole lies outside shell at or near point 100 100
```

## What to do

After reading a DXF with hatches, test the polygons for validity and look for interior rings that lie outside the shell. If you find them, split the polygon into one polygon per ring that is not inside another. A GDAL version with the fix removes the cause.

## Sources

- [GDAL issue 13230](https://github.com/OSGeo/gdal/issues/13230), "DXF: Incorrect Hatch converting to Feature": a hatch made of several separate areas is returned as one Polygon with the extra areas as holes. Closed as completed.
- [GDAL pull request 13244](https://github.com/OSGeo/gdal/pull/13244): changes `OGRBuildPolygonFromEdges()` to return a multipolygon when appropriate, fixes reading some DXF HATCH. Merged 19 October 2025, with a backport to release 3.11.
- The [GDAL DXF driver page](https://gdal.org/en/stable/drivers/vector/dxf.html) says only that line and arc boundaries are collected as a polygon geometry. It does not describe several boundaries in one hatch.
