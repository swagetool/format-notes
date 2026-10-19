# GDAL reads at most 256 characters of a DXF TEXT, and only the last piece of a split one

Kind: format limit

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Two separate effects. GDAL prints no warning for either of them by default.

1. A TEXT whose value sits in a single group 1 line of 400 characters comes back with 256.
2. A long TEXT can be written as chunks in group 3 (250 characters each) with the final piece in group 1. GDAL builds the `Text` field from group 1 only, so you get the tail. Here 330 characters were written and 80 came back, starting with the second part.

Object counts stay correct, so a count check on input and output does not see this.

## Reproduce

Snippet file: `text-longer-than-256-characters-1.py`

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

Snippet file: `text-longer-than-256-characters-2.py`

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

## Sources

- [GDAL issue 8527](https://github.com/OSGeo/gdal/issues/8527): a GDAL maintainer quotes the DXF R12 note that the maximum DXF string length is 256 characters, and says the reader truncates longer lines and prints a message only with `CPL_DEBUG=ON`. That covers effect 1. The report was made on GDAL 3.4.3 and was closed because newer versions behaved better on that file.
- Effect 2 (a value split between group 3 and group 1) is not described on the [GDAL DXF driver page](https://gdal.org/en/stable/drivers/vector/dxf.html) or in any issue we found. We checked it only by running the snippet.
