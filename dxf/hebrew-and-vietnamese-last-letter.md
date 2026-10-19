# GDAL loses the last character of DXF text under ANSI_1255 and ANSI_1258

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

With `$DWGCODEPAGE` set to `ANSI_1255` (Hebrew) the last letter of a text value is dropped. With `ANSI_1258` (Vietnamese) the same happens even to plain ASCII: `Ha Noi` comes back as `Ha No`. `ANSI_1252` is fine. Setting `DXF_ENCODING` to the same page does not help. GDAL prints no message.

## Reproduce

Snippet file: `hebrew-and-vietnamese-last-letter.py`

```python
import os, tempfile
from osgeo import ogr

def read_text(page, codec, text):
    pairs = ["0", "SECTION", "2", "HEADER", "9", "$DWGCODEPAGE", "3", page, "0", "ENDSEC",
             "0", "SECTION", "2", "ENTITIES",
             "0", "TEXT", "8", "t", "10", "1", "20", "2", "30", "0", "40", "1", "1", text,
             "0", "ENDSEC", "0", "EOF"]
    raw = "\n".join(pairs).encode(codec) + b"\n"
    p = os.path.join(tempfile.mkdtemp(), "t.dxf")
    open(p, "wb").write(raw)
    for lyr in ogr.Open(p):
        for f in lyr:
            return f.GetField("Text")

for page, codec, text in [("ANSI_1255", "cp1255", "רחוב ראשי"),
                          ("ANSI_1258", "cp1258", "Ha Noi"),
                          ("ANSI_1252", "cp1252", "Hanoi")]:
    got = read_text(page, codec, text)
    print(page, "written:", repr(text), "read:", repr(got))

# Does forcing the encoding help? Same file, same last-letter loss?
from osgeo import gdal
gdal.SetConfigOption("DXF_ENCODING", "CP1255")
print("DXF_ENCODING=CP1255:", repr(read_text("ANSI_1255", "cp1255", "רחוב ראשי")))
gdal.SetConfigOption("DXF_ENCODING", "CP1258")
print("DXF_ENCODING=CP1258:", repr(read_text("ANSI_1258", "cp1258", "Ha Noi")))
```

Output, as printed (standard output first, then standard error):

```
ANSI_1255 written: 'רחוב ראשי' read: 'רחוב ראש'
ANSI_1258 written: 'Ha Noi' read: 'Ha No'
ANSI_1252 written: 'Hanoi' read: 'Hanoi'
DXF_ENCODING=CP1255: 'רחוב ראש'
DXF_ENCODING=CP1258: 'Ha No'
```

## What to do

Do not write these two pages. When reading, expect the last character to be missing and compare a known value. Converting the file text to UTF-8 yourself before GDAL opens it should avoid the loss, but we have not tested that here.

## Sources

- [GDAL DXF driver page](https://gdal.org/en/stable/drivers/vector/dxf.html), section Character Encodings: describes `$DWGCODEPAGE` and `DXF_ENCODING` (an iconv name). It says nothing about dropped characters.
- We did not find a GDAL issue about this.
