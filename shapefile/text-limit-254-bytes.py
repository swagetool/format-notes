import os, tempfile
from osgeo import gdal, ogr

gdal.PushErrorHandler("CPLQuietErrorHandler")   # GDAL warns about the cut, here we count it ourselves

def roundtrip(text):
    d = tempfile.mkdtemp()
    ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(os.path.join(d, "t.shp"))
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=["ENCODING=UTF-8"])
    fd = ogr.FieldDefn("v", ogr.OFTString)
    fd.SetWidth(254)
    lyr.CreateField(fd)
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("v", text)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(os.path.join(d, "t.shp"))
    return next(iter(src.GetLayer(0))).GetField("v")

for label, text in (("latin", "a" * 300), ("cyrillic", "ж" * 200)):
    got = roundtrip(text)
    print(label, "written:", len(text), "chars,", len(text.encode()), "bytes | read:",
          len(got), "chars,", len(got.encode()), "bytes")
