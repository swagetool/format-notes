import os, tempfile
from osgeo import ogr

cases = [("ESRI Shapefile", "t.shp"), ("GML", "t.gml"), ("CSV", "t.csv"),
         ("MapInfo File", "t"), ("GPKG", "t.gpkg"), ("GeoJSON", "t.geojson"),
         ("FlatGeobuf", "t.fgb")]
print("written: row 1 s='' n=0, row 2 s=NULL n=NULL")
for drv, name in cases:
    p = os.path.join(tempfile.mkdtemp(), name)
    ds = ogr.GetDriverByName(drv).CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("s", ogr.OFTString))
    lyr.CreateField(ogr.FieldDefn("n", ogr.OFTInteger))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("s", "")
    f.SetField("n", 0)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    g = ogr.Feature(lyr.GetLayerDefn())
    g.SetFieldNull("s")
    g.SetFieldNull("n")
    g.SetGeometry(ogr.CreateGeometryFromWkt("POINT (3 4)"))
    lyr.CreateFeature(g)
    ds = lyr = f = g = None
    if drv == "MapInfo File":
        p = os.path.join(p, "t.tab")
    src = ogr.Open(p)
    back = [(r.GetField("s"), r.GetField("n")) for r in src.GetLayer(0)]
    print(drv.ljust(15), back)
