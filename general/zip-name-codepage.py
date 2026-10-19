import io, zipfile

placeholder = b"XXXX.dwg"                    # same length as the Shift-JIS name
sjis_name = "線形.dwg".encode("cp932")
assert len(sjis_name) == len(placeholder)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr(placeholder.decode(), b"data")
raw = buf.getvalue().replace(placeholder, sjis_name)   # no UTF-8 flag, as old tools write it

name = zipfile.ZipFile(io.BytesIO(raw)).namelist()[0]
print("zipfile gives:", repr(name))
print("repaired:     ", name.encode("cp437").decode("cp932"))
