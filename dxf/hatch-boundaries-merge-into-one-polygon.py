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
