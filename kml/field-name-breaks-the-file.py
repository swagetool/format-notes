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
