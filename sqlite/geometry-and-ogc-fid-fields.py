import os, tempfile
from osgeo import gdal, ogr

os.chdir(tempfile.mkdtemp())
for name, kind in (("speed", ogr.OFTInteger), ("geometry", ogr.OFTString),
                   ("OGC_FID", ogr.OFTString), ("OGC_FID", ogr.OFTInteger)):
    msgs = []
    gdal.PushErrorHandler(lambda c, n, m: msgs.append(m))
    ds = ogr.GetDriverByName("SQLite").CreateDataSource("t.sqlite")
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    field = lyr.CreateField(ogr.FieldDefn(name, kind))
    f = ogr.Feature(lyr.GetLayerDefn())
    if lyr.GetLayerDefn().GetFieldCount():
        f.SetField(0, 5 if kind == ogr.OFTInteger else "5")
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    written = lyr.CreateFeature(f)
    ds = lyr = f = None
    back = ogr.Open("t.sqlite")
    gdal.PopErrorHandler()
    layers = back.GetLayerCount()
    count = back.GetLayer(0).GetFeatureCount() if layers else 0
    print("%s %s: CreateField %d, CreateFeature %d, layers read %d, features read %d"
          % (name, ogr.GetFieldTypeName(kind), field, written, layers, count))
    for m in msgs:
        print("   ", m)
    back = None
    os.remove("t.sqlite")
