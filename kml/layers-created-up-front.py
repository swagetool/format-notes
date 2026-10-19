import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("KML").CreateDataSource(p)
layers = [ds.CreateLayer(n, geom_type=ogr.wkbPoint) for n in ("a", "b", "c")]
results = []
for lyr in layers:                        # 5 features into each of 3 layers
    for i in range(5):
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
        results.append(lyr.CreateFeature(f))
ds = layers = lyr = f = None

print("CreateFeature return codes:", results)
src = ogr.Open(p)
print({l.GetName(): l.GetFeatureCount() for l in src}, "(15 written)")
