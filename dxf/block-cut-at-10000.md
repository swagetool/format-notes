# GDAL stops reading a DXF block after 10 000 entities

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

An INSERT of a block with 12 000 lines comes back as a collection of 10 000 parts. GDAL prints one warning and carries on. The warning names the switch `DXF_FEATURE_LIMIT_PER_BLOCK`. Nothing marks the object as cut, so anything that only looks at the returned objects will take it as complete.

## Reproduce

```python
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
```

Output, as printed (standard output first, then standard error):

```
lines in the block: 9000 | parts GDAL returned: 9000
lines in the block: 10000 | parts GDAL returned: 10000
lines in the block: 12000 | parts GDAL returned: 10000
[stderr] Warning 1: Limit of 10000 features for block BIG reached. If you need more, set the DXF_FEATURE_LIMIT_PER_BLOCK configuration option to the maximum value (or -1 for no limit)
```

## What to do

Count entities inside block definitions on your own and compare. The message suggests setting `DXF_FEATURE_LIMIT_PER_BLOCK` higher, or to -1 for no limit. We did not run that variant here.
