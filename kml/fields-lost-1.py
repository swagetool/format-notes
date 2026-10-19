import os, tempfile
from osgeo import ogr

def run(set_one_value):
    p = os.path.join(tempfile.mkdtemp(), "t.kml")
    ds = ogr.GetDriverByName("LIBKML").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("height", ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn("note", ogr.OFTString))
    for i in range(3):
        f = ogr.Feature(lyr.GetLayerDefn())
        if set_one_value and i == 0:
            f.SetField("note", "x")
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
        lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    d = src.GetLayer(0).GetLayerDefn()
    return [d.GetFieldDefn(i).GetName() for i in range(d.GetFieldCount())
            if d.GetFieldDefn(i).GetName() in ("height", "note")]

print("every value empty:      fields read back =", run(False))
print("one value on one point: fields read back =", run(True))
