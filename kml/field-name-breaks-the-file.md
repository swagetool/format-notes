# A KML written with a quote, ampersand or less-than sign in a field name cannot be opened

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Both KML drivers (`KML` and `LIBKML`) write a field name into the file without escaping it. For `"`, `&` and `<` the result is not well-formed XML. The write call returns 0 and prints nothing. Opening the file afterwards returns `None` with "not well-formed (invalid token)". The features are in the file, but GDAL will not read them. `>` and ordinary names are fine.

The plain KML driver shows the cause in the file: the line is `<SimpleField name="a&b" type="string">`, with the `&` as it was given.

## Reproduce

Snippet file: `field-name-breaks-the-file.py`

```python
import os, tempfile
from osgeo import gdal, ogr

# A fresh directory and a relative name keep the messages free of random paths.
os.chdir(tempfile.mkdtemp())
for driver in ("KML", "LIBKML"):
    for name in ("speed", "a>b", 'a"b', "a&b", "a<b"):
        ds = ogr.GetDriverByName(driver).CreateDataSource("t.kml")
        lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
        lyr.CreateField(ogr.FieldDefn(name, ogr.OFTString))
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField(0, "v")
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        written = lyr.CreateFeature(f)
        ds = lyr = f = None
        msgs = []
        gdal.PushErrorHandler(lambda c, n, m: msgs.append(m))
        back = ogr.Open("t.kml")
        gdal.PopErrorHandler()
        print(driver.ljust(7), repr(name).ljust(8), "write returned", written,
              "| opens:", back is not None, "|", msgs[0] if msgs else "no message")
        back = None
```

Output, as printed (standard output first, then standard error):

```
KML     'speed'  write returned 0 | opens: True | no message
KML     'a>b'    write returned 0 | opens: True | no message
KML     'a"b'    write returned 0 | opens: False | ERROR parsing kml t.kml :not well-formed (invalid token) on line 5 at offset 22
KML     'a&b'    write returned 0 | opens: False | ERROR parsing kml t.kml :not well-formed (invalid token) on line 5 at offset 23
KML     'a<b'    write returned 0 | opens: False | ERROR parsing kml t.kml :not well-formed (invalid token) on line 5 at offset 21
LIBKML  'speed'  write returned 0 | opens: True | no message
LIBKML  'a>b'    write returned 0 | opens: True | no message
LIBKML  'a"b'    write returned 0 | opens: False | ERROR parsing kml t.kml :not well-formed (invalid token) on line 5 at offset 27
LIBKML  'a&b'    write returned 0 | opens: False | ERROR parsing kml t.kml :not well-formed (invalid token) on line 5 at offset 28
LIBKML  'a<b'    write returned 0 | opens: False | ERROR parsing kml t.kml :not well-formed (invalid token) on line 5 at offset 26
```

## What to do

Remove or replace `"`, `&` and `<` in field names before writing KML, and keep a mapping to the original names. After writing, open the file once to check it, because the write call does not report the problem.

## Sources

- No link. The [GDAL KML driver page](https://gdal.org/en/stable/drivers/vector/kml.html) and the [LIBKML driver page](https://gdal.org/en/stable/drivers/vector/libkml.html) do not mention field-name characters. The label "driver bug" is ours: the file the writer produces is not valid XML while the write reports success.
- We did not find a GDAL issue about this.
