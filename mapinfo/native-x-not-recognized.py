import os, tempfile
from osgeo import gdal, ogr

os.chdir(tempfile.mkdtemp())
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource("t.tab")
lyr = ds.CreateLayer("t")
lyr.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField(0, 1)
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

# The same four files under a second name, the only change is the table type in the .tab.
for ext in ("tab", "dat", "map", "id"):
    data = open("t." + ext, "rb").read()
    if ext == "tab":
        data = data.replace(b"Type NATIVE", b"Type NativeX")
    open("n." + ext, "wb").write(data)

gdal.UseExceptions()
for name in ("t.tab", "n.tab"):
    for line in open(name):
        if "Type" in line:
            print(name, "header:", line.strip())
    try:
        ds = ogr.Open(name)
        print(name, "opened, features:", ds.GetLayer(0).GetFeatureCount())
    except Exception as e:
        print(name, "error:", e)
