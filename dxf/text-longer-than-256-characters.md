# GDAL reads at most 256 characters of a DXF TEXT, and only the last piece of a split one

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Two separate effects, both silent.

1. A TEXT whose value sits in a single group 1 line of 400 characters comes back with 256.
2. A long TEXT can be written as chunks in group 3 (250 characters each) with the final piece in group 1. GDAL builds the `Text` field from group 1 only, so you get the tail. Here 330 characters were written and 80 came back, starting with the second part.

Object counts stay correct, so a count check on input and output does not see this.

## Reproduce

```python
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
```

Output, as printed (standard output first, then standard error):

```
written: 400 read: 256
```

```python
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
```

Output, as printed (standard output first, then standard error):

```
written: 330 read: 80 starts with: CCC
```

## What to do

If long labels matter, read the group code pairs of the DXF yourself for TEXT, ATTRIB and ATTDEF and join group 3 pieces with the group 1 tail. Compare the longest text length in the file against what GDAL returns.
