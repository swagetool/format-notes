import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "split.dxf")
# DXF spec: a long text value comes as chunks in code 3 (up to 250
# characters each), with the last piece in code 1.
head, tail = "B" * 250, "C" * 80
pairs = ["0", "SECTION", "2", "ENTITIES",
         "0", "TEXT", "8", "labels", "10", "1.0", "20", "2.0", "30", "0.0",
         "40", "1.0", "3", head, "1", tail,
         "0", "ENDSEC", "0", "EOF"]
open(p, "w").write("\n".join(pairs) + "\n")

for lyr in ogr.Open(p):
    for f in lyr:
        t = f.GetField("Text")
        print("written:", len(head + tail), "read:", len(t), "starts with:", t[:3])
