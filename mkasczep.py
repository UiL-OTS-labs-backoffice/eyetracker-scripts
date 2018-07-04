#!/usr/bin/env python3
'''A small program to convert Eyelink edf files to Eyelink asc files'''

import sys
import re
import shutil
import os
import os.path
import pathlib
import edfinfo

_EDF2ASC = 'edf2asc'
_EDFINFO = 'edfinfo'
EDF2ASC = shutil.which(_EDF2ASC)
EDFINFO = shutil.which(_EDFINFO)

# regular expressions to handle file type
FTYPE1 = re.compile(r'^((\w+)(-\w+)?)\.(\w+)\.(\d+)\.(\d+)\.edf$')
FTYPE2 = re.compile(r'/^(\d+)\_(\d+)\_(\d+)\.edf$')

def die(msg):
    '''print error message and die unsuccessfully.'''
    print(msg, file=sys.stderr)
    exit(1)

def print_usage():
    '''Prints how to use the mkasczep function'''
    print("USAGE:")
    print("    mkasczep <edf-file> ...")
    exit(0)

def process_filetype1(filename):
    '''Process filetype1

    DEPRECATED
    Because these days The reading experiment boilerplate creates the
    directories.
    '''
    mobj = FTYPE1.match(filename)
    fullexpname = mobj.group(1)
    expname = mobj.group(2)
    listname = mobj.group(4)
    blocknum = mobj.group(5)
    subjectnum = mobj.group(6)

    fnout = "{}_{}{}__{}.edf".format(
        fullexpname, listname, blocknum, subjectnum
        )

    exppath = pathlib.Path(expname)

    try:
        if not os.path.isdir(exppath):
            os.makedirs(expname)
        datadir = exppath / "dat"
        if not os.path.isdir(datadir):
            os.makedirs(datadir)
        obtdir = expdir / "obt"
        if not os.path.isdir(obtdir):
            os.makedirs(datadir)
        pladir = expdir / "pla"
        if not os.path.isdir(pladir):
            os.makedirs(pladir)
        resultdir = expdir / "results"
        if not os.path.isdir(resultdir):
            os.makedirs(resultdir)
    except Exception as error:
        die(str(error))

    newname = exppath / "dat" / fnout
    os.rename(filename. newname)

    os.system("edf2asc {}".format(newname))

def process_filetype2(filename):
    '''Processes filetype2'''
    raw_asc_fn = os.path.splitext(filename)[0] + ".asc"

    info = edfinfo.EyeFileInfo()
    info.parse_file(filename)
    os.system("edf2asc {}".format(filename))
    fnbase = pathlib.Path(
        "{}_{}{}_{}".format(
            info.experiment,
            "000" if info.participant == "dummy" else info.participant,
            info.list,
            info.recording
            )
        )
    fnasc = fnbase + ".asc"

    print('renaming "{}" to "{}".'.format(raw_asc_fn, fnasc))
    os.rename(raw_asc_fn, fnasc)


def process_files(fnlist):
    '''Converts all relevant edf files to there matching ascii versions'''
    for filename in fnlist:
        if FTYPE1.match(filename):
            process_filetype1(filename)
        elif FTYPE2.match(filename):
            process_filetype2(filename)
        else:
            print('Skipping "{}".'.format(filename))

def main():
    '''runs the program'''
    if not EDF2ASC:
        die("Unable to find {}".format(_EDF2ASC))
    if not EDFINFO:
        die("Unable to find {}".format(_EDFINFO))

    if len(sys.argv) < 2:
        print_usage()

    process_files(sys.argv[1:])

if __name__ == "__main__":
    main()
