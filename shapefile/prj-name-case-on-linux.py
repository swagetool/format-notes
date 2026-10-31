import os, tempfile
from osgeo import ogr, osr

d = tempfile.mkdtemp()
p = os.path.join(d, "Road.shp")
srs = osr.SpatialReference()
srs.ImportFromEPSG(32633)
ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(p)
lyr = ds.CreateLayer("Road", srs=srs, geom_type=ogr.wkbPoint)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (500000 5000000)"))
lyr.CreateFeature(f)
ds = lyr = f = None

def crs():
    src = ogr.Open(p)
    s = src.GetLayer(0).GetSpatialRef()
    return s.GetAuthorityCode(None) if s else None

print("Road.prj:", crs())
os.rename(os.path.join(d, "Road.prj"), os.path.join(d, "road.prj"))
print("road.prj:", crs())
