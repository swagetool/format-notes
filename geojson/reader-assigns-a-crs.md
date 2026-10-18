# GDAL gives a GeoJSON without a CRS the CRS EPSG:4326, or EPSG:4979 if any point has Z

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The file says nothing about a CRS. The reader reports EPSG:4326 for 2D coordinates and EPSG:4979 as soon as a point has a Z, even Z = 0. A check that "the output CRS equals the input CRS" now sees a CRS that nobody wrote.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

def crs_of(coords):
    p = os.path.join(tempfile.mkdtemp(), "t.geojson")
    open(p, "w").write('{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},'
                       '"geometry":{"type":"Point","coordinates":%s}}]}' % coords)
    src = ogr.Open(p)
    srs = src.GetLayer(0).GetSpatialRef()
    return srs.GetAuthorityName(None) + ":" + srs.GetAuthorityCode(None)

print("no CRS written, 2D point:      reader says", crs_of("[30, 50]"))
print("no CRS written, Z = 100:       reader says", crs_of("[30, 50, 100]"))
print("no CRS written, Z = 0:         reader says", crs_of("[30, 50, 0]"))
```

Output, as printed (standard output first, then standard error):

```
no CRS written, 2D point:      reader says EPSG:4326
no CRS written, Z = 100:       reader says EPSG:4979
no CRS written, Z = 0:         reader says EPSG:4979
```

## What to do

Remember that the CRS came from the reader and was not stored in the file. For projected coordinates in GeoJSON, put the real CRS where the receiver can see it, or reproject to WGS 84.
