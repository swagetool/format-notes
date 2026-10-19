import os, tempfile
from osgeo import ogr

def run(driver, name):
    p = os.path.join(tempfile.mkdtemp(), name)
    ds = ogr.GetDriverByName(driver).CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("when", ogr.OFTDateTime))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("when", 2026, 10, 18, 12, 0, 0, 112)    # flag 112 = UTC+03:00
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    if driver == "MapInfo File":
        p = os.path.join(p, "t.tab")
    src = ogr.Open(p)
    g = next(iter(src.GetLayer(0)))
    print(driver.ljust(13), g.GetFieldAsString("when"))

print("written:      2026-10-18 12:00:00+03")
run("MapInfo File", "mi")
run("GPKG", "t.gpkg")
