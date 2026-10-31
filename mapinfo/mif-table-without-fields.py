import os, tempfile
from osgeo import gdal, ogr

# Work inside a fresh directory so the messages carry a short relative path.
os.chdir(tempfile.mkdtemp())
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource("nofields.mif")
lyr = ds.CreateLayer("nofields", geom_type=ogr.wkbPoint)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
print("create feature returns:", lyr.CreateFeature(f))
ds = lyr = f = None
print("files:", sorted(os.listdir(".")))
src = ogr.Open("nofields.mif")
print("open:", "None" if src is None else src.GetLayerCount())
