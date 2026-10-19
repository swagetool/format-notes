# Reprojecting from a feet-based 2D CRS leaves Z in feet

Kind: PROJ behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

PROJ moves X and Y between two 2D coordinate systems and does not touch Z. If the source CRS is in US survey feet and the target is EPSG:4326, a height of 1000 comes out as 1000. A reader that assumes metres now sees a height 3.28 times too big. Nothing warns you, the call succeeds, and a before/after comparison of Z says "unchanged".

PROJ does convert Z when the source CRS is a compound CRS that includes a vertical part, for example EPSG:3734+6360 (Ohio North in feet plus NAVD88 height in feet). The same 1000 then becomes 304.8006 metres.

## Reproduce

Snippet file: `z-not-converted-by-reprojection.py`

```python
from osgeo import osr

def make(user_input):
    s = osr.SpatialReference()
    s.SetFromUserInput(user_input)
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return s

x, y, z = 1800000.0, 600000.0, 1000.0      # Ohio North, US survey feet
wgs84 = make("EPSG:4326")
wgs84_3d = make("EPSG:4979")
flat = osr.CoordinateTransformation(make("EPSG:3734"), wgs84)
compound = osr.CoordinateTransformation(make("EPSG:3734+6360"), wgs84_3d)

print("2D CRS in feet to 4326:           Z 1000 ->", flat.TransformPoint(x, y, z)[2])
print("compound CRS (3734+6360) to 4979: Z 1000 ->", compound.TransformPoint(x, y, z)[2])
```

Output, as printed (standard output first, then standard error):

```
2D CRS in feet to 4326:           Z 1000 -> 1000.0
compound CRS (3734+6360) to 4979: Z 1000 -> 304.8006096012192
```

## What to do

Do not infer the Z unit from the horizontal CRS. If the vertical unit matters, build the transform from a compound CRS and check the result on one real point. If you cannot know the vertical unit, say so in the output instead of converting by guess.

## Sources

- [PROJ mailing list, "ESRI:102655 - z-axis in meter insted of us-ft"](https://lists.osgeo.org/pipermail/proj/2020-June/009660.html): a PROJ maintainer answers that a projected 2D CRS has no Z axis, that the Z value PROJ returns is undefined and may or may not be changed, and that a compound CRS is needed when Z is an elevation tied to a vertical CRS.
- We did not find a GDAL issue about this.
