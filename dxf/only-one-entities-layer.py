import os, tempfile
from osgeo import gdal, ogr

p = os.path.join(tempfile.mkdtemp(), "two.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
a = ds.CreateLayer("roads", geom_type=ogr.wkbLineString)
print("first layer:", a is not None)
b = ds.CreateLayer("buildings", geom_type=ogr.wkbPolygon)
print("second layer:", b)
print("GDAL says:", gdal.GetLastErrorMsg())
