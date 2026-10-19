import os, random, tempfile
from osgeo import ogr, osr

random.seed(1)
pts = [(500000 + random.random() * 100000, 5400000 + random.random() * 100000)
       for _ in range(2000)]

def roundtrip(srs):
    d = tempfile.mkdtemp()
    ds = ogr.GetDriverByName("MapInfo File").CreateDataSource(d)
    lyr = ds.CreateLayer("t", srs, ogr.wkbPoint)
    for x, y in pts:
        f = ogr.Feature(lyr.GetLayerDefn())
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.AddPoint_2D(x, y)
        f.SetGeometry(pt)
        lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(os.path.join(d, "t.tab"))
    back = src.GetLayer(0)
    worst = 0.0
    for (x, y), f in zip(pts, back):
        g = f.GetGeometryRef()
        worst = max(worst, abs(g.GetX() - x), abs(g.GetY() - y))
    return worst

utm = osr.SpatialReference()
utm.ImportFromEPSG(32610)
print("with EPSG:32610, worst shift: %.4f" % roundtrip(utm))
print("without a CRS,   worst shift: %.4f" % roundtrip(None))
