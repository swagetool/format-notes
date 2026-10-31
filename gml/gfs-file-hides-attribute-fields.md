# GDAL ignores the GML attribute-fields option once it has written a .gfs file

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The open option `GML_ATTRIBUTES_TO_OGR_FIELDS=YES` makes GDAL create fields from XML attributes of property elements. The driver page says it "has only an effect the first time a GML file is opened". On the first open GDAL also writes a `.gfs` file next to the GML file (the default, `WRITE_GFS=AUTO`), and that file fixes the field list.

In the snippet the file has `<ogr:name lang="en" source="survey">`. A default open writes `t.gfs` with 2 fields. Opening again with the option on still gives 2 fields. With no `.gfs` the same option gives 4. With `WRITE_GFS=NO` no file is written and the option works on every open.

Anyone who opens the file once without the option, for instance a viewer, changes what a later open with the option returns. The folder must be writable for that to happen.

## Reproduce

Snippet file: `gfs-file-hides-attribute-fields.py`

```python
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
```

Output, as printed (standard output first, then standard error):

```
files: ['t.gml']
default open:                  ['fid', 'name']
files: ['t.gfs', 't.gml']
option on, .gfs exists:        ['fid', 'name']
option on, no .gfs yet:        ['fid', 'name_lang', 'name_source', 'name']
option on and WRITE_GFS=NO:    ['fid', 'name_lang', 'name_source', 'name']
files: ['t.gml']
```

## What to do

If you need the attribute fields, open with `GML_ATTRIBUTES_TO_OGR_FIELDS=YES` and `WRITE_GFS=NO` every time, or delete a stale `.gfs` before opening. Compare the field count with what the file contains.

## Sources

- [GDAL GML driver page](https://gdal.org/en/stable/drivers/vector/gml.html): the open option `GML_ATTRIBUTES_TO_OGR_FIELDS` "has only an effect the first time a GML file is opened". `WRITE_GFS` in AUTO mode writes the `.gfs` when there is no recognised `.xsd`, no existing `.gfs`, and the file system is not a network one.
- [QGIS issue 65888](https://github.com/qgis/QGIS/issues/65888): attribute fields missing when the GML open option is set in QGIS. The reporter's guess is that QGIS does not pass the option when it first creates the `.gfs`. Open when we looked.
- We did not find a GDAL issue about this.
