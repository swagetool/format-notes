import os, tempfile
from osgeo import gdal, ogr

p = os.path.join(tempfile.mkdtemp(), "t.gml")
ds = ogr.GetDriverByName("GML").CreateDataSource(p)
for name, gt, wkt in (("flat", ogr.wkbLineString, "LINESTRING (1 2, 3 4)"),
                      ("tall", ogr.wkbLineString25D, "LINESTRING Z (1 2 3, 4 5 6)")):
    lyr = ds.CreateLayer(name, geom_type=gt)
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
for lyr in src:
    gdal.ErrorReset()
    n = sum(1 for _ in lyr)
    print(lyr.GetName(), "features read:", n, "| last error:", gdal.GetLastErrorMsg() or "none")
