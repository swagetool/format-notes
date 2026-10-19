import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("KML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)          # no CRS given
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (500123.5 4500000)"))   # UTM metres
lyr.CreateFeature(f)
ds = lyr = f = None

print("in the file:", [l.strip() for l in open(p) if "<coordinates>" in l])
src = ogr.Open(p)
for g in src.GetLayer(0):
    print("written: POINT (500123.5 4500000)")
    print("read:   ", g.GetGeometryRef().ExportToWkt())
