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
