# eyetracker-scripts
Helper scripts that are part of the chain to analyze Reading and VWP experiments
These scripts are generally started from the data directory of your zep
experiment.

## Purpose of the scripts
The scripts in this repository are ment to support researchers at the UiL OTS
labs that are doing eytracking and want to analyze the data with Fixation.

These scripts are meant to become a replacement for the older perl scripts

## dependencies
- python3.5 or greater
- PILLOW in order to convert .png's to bitmaps.
- edf2asc from SR-Research (necessary to convert edf to ascii files)

## note
Previously the eyetracker scripts depended on the presence of the
Image Magic utilities in order to convert the png's to bmp's. Than the
perlscripts started an external program (convert) to convert the .png's
to bitmaps.

That dependency is now changed to Pillow, since that is a python library
that avoids the dependency on external programs, however, it is still
a dependency so it must be installed.
