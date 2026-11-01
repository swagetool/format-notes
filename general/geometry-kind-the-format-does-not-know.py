import os, tempfile
from osgeo import gdal, ogr

WKT = "POLYHEDRALSURFACE Z (((0 0 0,1 0 0,1 1 0,0 0 0)),((0 0 0,1 0 0,1 0 1,0 0 0)))"
os.chdir(tempfile.mkdtemp())
for driver, ext in (("ESRI Shapefile", "shp"), ("MapInfo File", "tab"), ("KML", "kml"), ("LIBKML", "kml"),
                    ("DXF", "dxf"), ("GeoJSON", "geojson"), ("GPKG", "gpkg"), ("GML", "gml"),
                    ("FlatGeobuf", "fgb"), ("CSV", "csv")):
    msgs = []
    gdal.PushErrorHandler(lambda c, n, m: msgs.append(" ".join(m.split())))
    name = "t." + ext
    ds = ogr.GetDriverByName(driver).CreateDataSource(name)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbUnknown if driver == "DXF" else ogr.wkbPolyhedralSurfaceZ,
                         options=["GEOMETRY=AS_WKT"] if driver == "CSV" else [])
    if driver != "DXF":
        lyr.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(WKT))
    written = lyr.CreateFeature(f)
    ds = lyr = f = None
    back = ogr.Open(name)
    lyr = back.GetLayer(0)
    kinds = []
    for g in (x.GetGeometryRef() for x in lyr):
        kinds.append("no geometry" if g is None else "%s with %d parts" % (g.GetGeometryName(), g.GetGeometryCount()))
    gdal.PopErrorHandler()
    print("%s: write returned %d, read back %d feature(s): %s" % (driver, written, lyr.GetFeatureCount(), kinds))
    for m in msgs:
        print("    message:", m)
    back = lyr = None
