import os, tempfile
from osgeo import gdal, ogr

values = {"carriage return": "a\rb", "control char 0x01": "a\x01b", "U+FFFE": "a\ufffeb"}
formats = [("GML", "t.gml"), ("LIBKML", "t.kml"), ("CSV", "t.csv"),
           ("GeoJSON", "t.geojson"), ("GPKG", "t.gpkg")]

gdal.PushErrorHandler("CPLQuietErrorHandler")
for drv, name in formats:
    out = []
    for label, v in values.items():
        p = os.path.join(tempfile.mkdtemp(), name)
        ds = ogr.GetDriverByName(drv).CreateDataSource(p)
        lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
        lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField("v", v)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        lyr.CreateFeature(f)
        ds = lyr = f = None
        gdal.ErrorReset()
        src = ogr.Open(p)
        if src is None:
            out.append("%s: FILE WILL NOT OPEN" % label)
            continue
        got = [r.GetField("v") for r in src.GetLayer(0)]
        why = " (" + gdal.GetLastErrorMsg()[:40] + ")" if not got else ""
        out.append("%s: %s%s" % (label, "kept" if got == [v] else repr(got), why))
    print(drv.ljust(8), " | ".join(out))
