import os, tempfile
from osgeo import ogr

name = "Udostępniane granice terenów"
head = "0\nSECTION\n2\nHEADER\n9\n$DWGCODEPAGE\n3\nANSI_1250\n0\nENDSEC\n"
ents = "0\nSECTION\n2\nENTITIES\n0\nPOINT\n8\n%s\n10\n1.0\n20\n2.0\n30\n0.0\n0\nENDSEC\n0\nEOF\n" % name
p = os.path.join(tempfile.mkdtemp(), "lodz.dxf")
open(p, "wb").write((head + ents).encode("utf-8"))   # header says 1250, bytes are UTF-8

for lyr in ogr.Open(p):
    for f in lyr:
        got = f.GetField("Layer")
        print("read:    ", got)
        # The repair: encode back with the declared page, decode as UTF-8.
        print("repaired:", got.encode("cp1250").decode("utf-8"))

# GDAL has a switch to force the encoding. It works here.
from osgeo import gdal
gdal.SetConfigOption("DXF_ENCODING", "UTF-8")
src = ogr.Open(p)
for lyr in src:
    for f in lyr:
        print("with DXF_ENCODING=UTF-8:", f.GetField("Layer"))
