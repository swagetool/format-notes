import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "long.dxf")
body = "A" * 400
pairs = ["0", "SECTION", "2", "ENTITIES",
         "0", "TEXT", "8", "labels", "10", "1.0", "20", "2.0", "30", "0.0",
         "40", "1.0", "1", body,
         "0", "ENDSEC", "0", "EOF"]
open(p, "w").write("\n".join(pairs) + "\n")

for lyr in ogr.Open(p):
    for f in lyr:
        print("written:", len(body), "read:", len(f.GetField("Text")))
