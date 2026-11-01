# The GDAL DXF writer declares inches over data in metres

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The DXF writer copies the header from a template, and the template says the drawing is in inches. The snippet writes one line with UTM coordinates (metres) and no CRS. The file header says `$INSUNITS = 1`, which is inches, and `$MEASUREMENT = 0`. A CAD program that trusts the header reads 500 000 inches. The coordinates are not changed, only the declared unit is wrong.

The driver page says the same about the template. It also lists two options, `INSUNITS` and `MEASUREMENT`, added in GDAL 3.11. With the default `AUTO`, the unit is taken from the CRS of the layer if that CRS is projected. Without a projected CRS the template value, inches, stays. We ran only 3.10.3 by hand. The CI workflow of this repository runs the snippet on 3.13.3 as well, and its report shows whether the output differs.

## Reproduce

Snippet file: `writer-declares-inches.py`

```python
import os, tempfile
from osgeo import ogr

# Coordinates in metres (UTM easting and northing).
p = os.path.join(tempfile.mkdtemp(), "t.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities")
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("LINESTRING (500000 4000000, 500100 4000100)"))
lyr.CreateFeature(f)
ds = lyr = f = None

lines = open(p, encoding="latin-1").read().split("\n")
for i, line in enumerate(lines):
    if line.strip() in ("$INSUNITS", "$MEASUREMENT", "$LUNITS"):
        print(line.strip(), "=", lines[i + 2].strip())
```

Output, as printed (standard output first, then standard error):

```
$LUNITS = 2
$MEASUREMENT = 0
$INSUNITS = 1
```

## What to do

On GDAL 3.10 or older, rewrite the `$INSUNITS` value in the file after writing (6 is metres in the DXF reference), or tell the recipient the unit. On 3.11 or newer, give the layer a projected CRS or set `INSUNITS=METERS` in the creation options. Never leave the choice to the template.

## Sources

- [GDAL DXF driver page](https://gdal.org/en/stable/drivers/vector/dxf.html): the `INSUNITS` and `MEASUREMENT` creation options (GDAL 3.11 and later), the `AUTO` rule, and the sentence that the header template value is `INCHES`.
- We did not find a GDAL issue about this.
