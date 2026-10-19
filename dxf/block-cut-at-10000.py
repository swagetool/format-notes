import os, tempfile
from osgeo import ogr

def build(n):
    pairs = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "0", "ENDSEC",
             "0", "SECTION", "2", "BLOCKS", "0", "BLOCK", "8", "0", "2", "BIG", "70", "0",
             "10", "0", "20", "0", "30", "0"]
    for i in range(n):
        pairs += ["0", "LINE", "8", "0", "10", str(i), "20", "0", "30", "0",
                  "11", str(i + 0.5), "21", "0", "31", "0"]
    pairs += ["0", "ENDBLK", "8", "0", "0", "ENDSEC",
              "0", "SECTION", "2", "ENTITIES",
              "0", "INSERT", "8", "0", "2", "BIG", "10", "0", "20", "0", "30", "0",
              "0", "ENDSEC", "0", "EOF"]
    p = os.path.join(tempfile.mkdtemp(), "block.dxf")
    open(p, "w").write("\n".join(pairs) + "\n")
    return p

for n in (9000, 10000, 12000):
    src = ogr.Open(build(n))
    parts = 0
    for lyr in src:
        for f in lyr:
            parts += f.GetGeometryRef().GetGeometryCount()
    print("lines in the block:", n, "| parts GDAL returned:", parts)
