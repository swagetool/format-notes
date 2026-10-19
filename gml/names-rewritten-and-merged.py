import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.gml")
ds = ogr.GetDriverByName("GML").CreateDataSource(p)
for name in ("road-a", "road_a"):
    lyr = ds.CreateLayer(name, geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("max-speed", ogr.OFTInteger))
    for i in range(3):
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField(0, 50)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        lyr.CreateFeature(f)
ds = lyr = f = None

back = ogr.Open(p)
print("layers written: ['road-a', 'road_a'], 6 features")
for l in back:
    d = l.GetLayerDefn()
    print("layer read:", l.GetName(), "features:", l.GetFeatureCount(),
          "fields:", [d.GetFieldDefn(i).GetName() for i in range(d.GetFieldCount())])
