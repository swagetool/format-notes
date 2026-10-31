# File Geodatabase stores coordinates on a grid and moves a vertex by up to half a step

Kind: format limit

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A File Geodatabase keeps every coordinate as an integer number of steps from an origin. GDAL's default step is 0.0001 of the unit in a projected system (a tenth of a millimetre in metres), 0.000000001 degree in a geographic one, and 0.0001 of the file's unit without a coordinate system. In US survey feet (EPSG:3734) it was 0.00003048 ft. A point at `512345.1234567891 5612345.987654321` in EPSG:32633 came back 0.0000457 m away. The layer creation option `XYSCALE` sets a finer grid: with `XYSCALE=1000000000` the same point moved 0.000000166 m. `XYTOLERANCE` changes only the tolerance ArcGIS uses for editing, not the stored coordinates. GDAL prints nothing in any case.

## Reproduce

Snippet file: `coordinate-grid.py`

```python
import os, tempfile
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
for epsg, (x, y) in ((32633, (512345.1234567891, 5612345.987654321)),
                     (4326, (30.123456789012345, 50.987654321098765))):
    for options in ([], ["XYSCALE=1000000000"]):
        p = os.path.join(tempfile.mkdtemp(), "t.gdb")
        ds = ogr.GetDriverByName("OpenFileGDB").CreateDataSource(p)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        lyr = ds.CreateLayer("t", srs, ogr.wkbPoint, options=options)
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt(f"POINT ({x!r} {y!r})"))
        lyr.CreateFeature(f)
        ds = lyr = f = None
        src = ogr.Open(p)
        layer = src.GetLayer(0)
        step = layer.GetLayerDefn().GetGeomFieldDefn(0).GetCoordinatePrecision().GetXYResolution()
        feat = next(iter(layer))
        g = feat.GetGeometryRef()
        print(f"EPSG:{epsg} {(options or ['default'])[0]:<20} step {step:g} "
              f"moved {max(abs(g.GetX() - x), abs(g.GetY() - y)):.3g}")
```

Output, as printed:

```
EPSG:32633 default              step 0.0001 moved 4.57e-05
EPSG:32633 XYSCALE=1000000000   step 1e-09 moved 1.66e-07
EPSG:4326 default              step 1e-09 moved 9.88e-11
EPSG:4326 XYSCALE=1000000000   step 1e-09 moved 9.88e-11
```

## What to do

For survey data the default step is far below the accuracy of the source, and it is the grid ArcGIS expects for editing and topology. If a check compares coordinates exactly, allow half a step. If more digits must survive, set `XYSCALE`, knowing that ArcGIS then works on a grid that is not its default.

## Sources

- GDAL documentation of the driver, section "Geometry coordinate precision" and the layer creation options `XYSCALE`, `XYTOLERANCE`: https://gdal.org/en/release-3.10/drivers/vector/openfilegdb.html
- The step per coordinate system kind is what GDAL 3.10.3 wrote, read back with `GetCoordinatePrecision` (also in `scripts/fg1_probe_grid.py` of our repository).
