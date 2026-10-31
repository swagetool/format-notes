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
