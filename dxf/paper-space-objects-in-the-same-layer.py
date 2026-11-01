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
