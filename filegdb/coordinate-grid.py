import os, tempfile
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
for epsg, (x, y) in ((32633, (512345.1234567891, 5612345.987654321)),
                     (4326, (30.123456789012345, 50.987654321098765))):
    for options in ([], ["XYSCALE=1000000000"]):
        p = os.path.join(tempfile.mkdtemp(), "t.gdb")
        ds = ogr.GetDriverByName("OpenFileGDB").CreateDataSource(p)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        lyr = ds.CreateLayer("t", srs, ogr.wkbPoint, options=options)
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt(f"POINT ({x!r} {y!r})"))
        lyr.CreateFeature(f)
        ds = lyr = f = None
        src = ogr.Open(p)
        layer = src.GetLayer(0)
        step = layer.GetLayerDefn().GetGeomFieldDefn(0).GetCoordinatePrecision().GetXYResolution()
        feat = next(iter(layer))
        g = feat.GetGeometryRef()
        print(f"EPSG:{epsg} {(options or ['default'])[0]:<20} step {step:g} "
              f"moved {max(abs(g.GetX() - x), abs(g.GetY() - y)):.3g}")
