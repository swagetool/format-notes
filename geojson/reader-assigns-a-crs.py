import os, tempfile
from osgeo import ogr

def crs_of(coords):
    p = os.path.join(tempfile.mkdtemp(), "t.geojson")
    open(p, "w").write('{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},'
                       '"geometry":{"type":"Point","coordinates":%s}}]}' % coords)
    src = ogr.Open(p)
    srs = src.GetLayer(0).GetSpatialRef()
    return srs.GetAuthorityName(None) + ":" + srs.GetAuthorityCode(None)

print("no CRS written, 2D point:      reader says", crs_of("[30, 50]"))
print("no CRS written, Z = 100:       reader says", crs_of("[30, 50, 100]"))
print("no CRS written, Z = 0:         reader says", crs_of("[30, 50, 0]"))
