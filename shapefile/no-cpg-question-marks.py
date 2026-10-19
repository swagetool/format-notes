import os, tempfile
from osgeo import ogr

text = "Улица Ленина, дом 5"
for opts in ([], ["ENCODING=UTF-8"]):
    d = tempfile.mkdtemp()
    ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(os.path.join(d, "t.shp"))
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=opts)
    lyr.CreateField(ogr.FieldDefn("addr", ogr.OFTString))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("addr", text)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(os.path.join(d, "t.shp"))
    got = next(iter(src.GetLayer(0))).GetField("addr")
    print("options:", opts or "none", "| files:", sorted(os.listdir(d)))
    print("  read:", got)
