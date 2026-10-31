import os, tempfile
from osgeo import ogr

for options in ([], ["TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER"]):
    p = os.path.join(tempfile.mkdtemp(), "t.gdb")
    ds = ogr.GetDriverByName("OpenFileGDB").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=options)
    lyr.CreateField(ogr.FieldDefn("when", ogr.OFTDateTime))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("when", "2024/01/05 10:20:30")     # no time zone
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    g = next(iter(src.GetLayer(0)))
    print((options or ["default layout"])[0].ljust(46), g.GetFieldAsString("when"))
