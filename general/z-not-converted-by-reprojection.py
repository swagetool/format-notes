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
