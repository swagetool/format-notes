# File names inside a ZIP can be in a code page Python does not know about

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Older tools write names in the local code page and do not set the UTF-8 flag. Python's `zipfile` decodes them as cp437. A Japanese archive entry shows up as `Éⁿî` followed by a backtick and an extension. The original is recoverable by encoding back to cp437 and decoding with the right code page. Here that is cp932 (Shift-JIS).

The snippet makes such an archive by writing a placeholder name and replacing its bytes with the Shift-JIS ones.

## Reproduce

```python
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
```

Output, as printed (standard output first, then standard error):

```
zipfile gives: 'Éⁿî`.dwg'
repaired:      線形.dwg
```

## What to do

If a name has non-ASCII letters and the UTF-8 flag is not set, try the code pages that are plausible for the source and take the one that decodes without error. Tell the user that the name was recovered by guess.
