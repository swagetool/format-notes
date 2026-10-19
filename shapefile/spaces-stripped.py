import os, tempfile
from osgeo import ogr

def roundtrip(driver, name, text):
    p = os.path.join(tempfile.mkdtemp(), name)
    ds = ogr.GetDriverByName(driver).CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("v", text)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    return next(iter(src.GetLayer(0))).GetField("v")

for text in (" lead", "trail ", " both "):
    print(repr(text).ljust(9), "shapefile:", repr(roundtrip("ESRI Shapefile", "t.shp", text)),
          " gpkg:", repr(roundtrip("GPKG", "t.gpkg", text)))
