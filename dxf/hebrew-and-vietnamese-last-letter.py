import os, tempfile
from osgeo import ogr

def read_text(page, codec, text):
    pairs = ["0", "SECTION", "2", "HEADER", "9", "$DWGCODEPAGE", "3", page, "0", "ENDSEC",
             "0", "SECTION", "2", "ENTITIES",
             "0", "TEXT", "8", "t", "10", "1", "20", "2", "30", "0", "40", "1", "1", text,
             "0", "ENDSEC", "0", "EOF"]
    raw = "\n".join(pairs).encode(codec) + b"\n"
    p = os.path.join(tempfile.mkdtemp(), "t.dxf")
    open(p, "wb").write(raw)
    for lyr in ogr.Open(p):
        for f in lyr:
            return f.GetField("Text")

for page, codec, text in [("ANSI_1255", "cp1255", "רחוב ראשי"),
                          ("ANSI_1258", "cp1258", "Ha Noi"),
                          ("ANSI_1252", "cp1252", "Hanoi")]:
    got = read_text(page, codec, text)
    print(page, "written:", repr(text), "read:", repr(got))

# Does forcing the encoding help? Same file, same last-letter loss?
from osgeo import gdal
gdal.SetConfigOption("DXF_ENCODING", "CP1255")
print("DXF_ENCODING=CP1255:", repr(read_text("ANSI_1255", "cp1255", "רחוב ראשי")))
gdal.SetConfigOption("DXF_ENCODING", "CP1258")
print("DXF_ENCODING=CP1258:", repr(read_text("ANSI_1258", "cp1258", "Ha Noi")))
