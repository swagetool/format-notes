import os, tempfile
from osgeo import gdal, ogr

gdal.PushErrorHandler(lambda c, n, m: print("[gdal]", m))

def run(options):
    p = os.path.join(tempfile.mkdtemp(), "t.gdb")
    ds = ogr.GetDriverByName("OpenFileGDB").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=options)
    for name, kind in (("big", ogr.OFTInteger64), ("day", ogr.OFTDate),
                       ("clock", ogr.OFTTime), ("zoned", ogr.OFTDateTime),
                       ("fine", ogr.OFTDateTime)):
        lyr.CreateField(ogr.FieldDefn(name, kind))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("big", 2 ** 53 + 1)
    f.SetField("day", "2024/01/05")
    f.SetField("clock", "10:20:30")
    f.SetField("zoned", "2024/01/05 10:20:30+03")
    f.SetField("fine", "2024/01/05 10:20:30.123")
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    g = next(iter(src.GetLayer(0)))
    print(options or "default layout")
    for name in ("big", "day", "clock", "zoned", "fine"):
        print("  ", name.ljust(6), g.GetFieldAsString(name))

print("written: big 9007199254740993, day 2024/01/05, clock 10:20:30,")
print("         zoned 2024/01/05 10:20:30+03, fine 2024/01/05 10:20:30.123")
run([])
run(["TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER"])
