# An ISO 19139 metadata file opens as GML with no layers

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

An XML file that is not GML can still be opened by the GML driver if it uses the GML namespace. ISO 19139 metadata does, for time periods and extents. In the snippet a small metadata document with a `gml/3.2` element opens without error as driver `GML` and has 0 layers. Code that checks only that the open call returned a dataset takes it for an empty GML file.

A real GML file whose features GDAL cannot find looks the same.

## Reproduce

Snippet file: `iso-19139-metadata-opens-as-gml.py`

```python
import os, tempfile
from osgeo import gdal

p = os.path.join(tempfile.mkdtemp(), "meta.xml")
with open(p, "w") as fh:
    fh.write("""<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd"
                 xmlns:gco="http://www.isotc211.org/2005/gco"
                 xmlns:gml="http://www.opengis.net/gml/3.2">
  <gmd:fileIdentifier><gco:CharacterString>x</gco:CharacterString></gmd:fileIdentifier>
  <gmd:identificationInfo>
    <gml:TimePeriod gml:id="t1">
      <gml:beginPosition>2020-01-01</gml:beginPosition>
      <gml:endPosition>2020-12-31</gml:endPosition>
    </gml:TimePeriod>
  </gmd:identificationInfo>
</gmd:MD_Metadata>
""")

ds = gdal.OpenEx(p, gdal.OF_VECTOR)
print("opened:", ds is not None)
print("driver:", ds.GetDriver().ShortName)
print("layers:", ds.GetLayerCount())
```

Output, as printed (standard output first, then standard error):

```
opened: True
driver: GML
layers: 0
```

## What to do

Treat a dataset with 0 layers as "nothing readable", and say which driver opened it and how many layers it had. If the file is metadata, report that instead of an empty result.

## Sources

- The [GDAL GML driver page](https://gdal.org/en/stable/drivers/vector/gml.html) says only that the driver scans the file "looking for known gml objects in the gml namespace" when no `.xsd` is usable. It does not say what happens to a file that has the namespace and no features, so this note records what the snippet shows. The label "driver bug" is ours for an undocumented limitation.
- We did not find a GDAL issue about this.
