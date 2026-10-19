import os, tempfile
from osgeo import gdal, ogr

def attempt(label, field_type, name, values):
    p = os.path.join(tempfile.mkdtemp(), "t.gpkg")
    ds = ogr.GetDriverByName("GPKG").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn(name, field_type))
    ok = 0
    for v in values:
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField(name, v)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        if lyr.CreateFeature(f) == 0:
            ok += 1
    ds = lyr = f = None
    src = ogr.Open(p)
    back = src.GetLayer(0)
    idx = back.GetLayerDefn().GetFieldIndex(name)
    read = [r.GetField(idx) if idx >= 0 else None for r in back]
    print(label)
    print("   written:", values, "| CreateFeature succeeded:", ok, "of", len(values))
    print("   read back:", read, "| field", name, "present:", idx >= 0)

attempt("text field named fid", ogr.OFTString, "fid", ["a", "b", "c"])
attempt("integer field fid, value 1 twice", ogr.OFTInteger, "fid", [1, 1, 2])
attempt("text field named geom", ogr.OFTString, "geom", ["a", "b", "c"])
