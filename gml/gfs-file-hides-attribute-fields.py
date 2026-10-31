import os, tempfile
from osgeo import gdal, ogr

gdal.UseExceptions()
d = tempfile.mkdtemp()
p = os.path.join(d, "t.gml")
with open(p, "w") as fh:
    fh.write("""<?xml version="1.0" encoding="UTF-8"?>
<ogr:FeatureCollection xmlns:ogr="http://ogr.maptools.org/" xmlns:gml="http://www.opengis.net/gml">
 <gml:featureMember>
  <ogr:t fid="a">
   <ogr:name lang="en" source="survey">Main</ogr:name>
   <ogr:geom><gml:Point><gml:coordinates>1,2</gml:coordinates></gml:Point></ogr:geom>
  </ogr:t>
 </gml:featureMember>
</ogr:FeatureCollection>
""")

def fields(**opts):
    src = gdal.OpenEx(p, gdal.OF_VECTOR, open_options=["%s=%s" % kv for kv in opts.items()])
    defn = src.GetLayer(0).GetLayerDefn()
    return [defn.GetFieldDefn(i).GetName() for i in range(defn.GetFieldCount())]

gfs = os.path.join(d, "t.gfs")
print("files:", sorted(os.listdir(d)))
print("default open:                 ", fields())
print("files:", sorted(os.listdir(d)))
print("option on, .gfs exists:       ", fields(GML_ATTRIBUTES_TO_OGR_FIELDS="YES"))
os.remove(gfs)
print("option on, no .gfs yet:       ", fields(GML_ATTRIBUTES_TO_OGR_FIELDS="YES"))
os.remove(gfs)
print("option on and WRITE_GFS=NO:   ", fields(GML_ATTRIBUTES_TO_OGR_FIELDS="YES", WRITE_GFS="NO"))
print("files:", sorted(os.listdir(d)))
