import os, tempfile
from osgeo import ogr

d = tempfile.mkdtemp()
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource(d)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint25D)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT Z (500000 5400000 12.5)"))
lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(os.path.join(d, "t.tab"))
for f in src.GetLayer(0):
    print("written: POINT Z (500000 5400000 12.5)")
    print("read:   ", f.GetGeometryRef().ExportToIsoWkt())
