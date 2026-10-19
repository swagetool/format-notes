import os, tempfile
from osgeo import ogr

names = ("Название", "Ulica_główna", "street_name_long")
p = os.path.join(tempfile.mkdtemp(), "t.shp")
ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=["ENCODING=UTF-8"])
for name in names:
    lyr.CreateField(ogr.FieldDefn(name, ogr.OFTString))
ds = lyr = None

src = ogr.Open(p)
defn = src.GetLayer(0).GetLayerDefn()
for i, written in enumerate(names):
    got = defn.GetFieldDefn(i).GetName()
    print(repr(written), "->", repr(got), "| bytes:", len(got.encode("utf-8", "surrogateescape")))
