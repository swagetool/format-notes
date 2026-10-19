# Reporting a different result

A note is a claim about one set of versions. If you get a different result, that is useful, so please report it.

Open a GitHub issue and include:

1. The note (its path, for example `kml/fields-lost.md`).
2. Your GDAL version (`gdalinfo --version`), PROJ version if the note is about reprojection, Python version and operating system. If you used a container image, its exact tag.
3. How you ran the snippet. Say whether it was the file from this repository, unchanged.
4. The output you got, pasted as text, with standard error included.
5. What you expected instead.

The monthly run of the workflow in `.github/workflows/notes.yml` already shows differences on three GDAL versions. Download its report from the run page before you file an issue, because your case may be listed there.

Corrections to wording, a link that does not say what the note claims, and new traps are welcome as pull requests. A new note needs a snippet that builds its own data, the output as printed, and the version it ran on. Please do not attach files from real projects.
