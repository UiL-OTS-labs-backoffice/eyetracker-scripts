#!/usr/bin/env python3
"""A small program to convert Eyelink edf files to Eyelink asc files"""

import sys
import re
import shutil
import os
import os.path
import pathlib
import argparse as ap
import edfinfo

_EDF2ASC = "edf2asc"
_EDFINFO = "edfinfo"
EDF2ASC = shutil.which(_EDF2ASC)

# regular expressions to handle file type
FTYPE1 = re.compile(r"^((\w+)(-\w+)?)\.(\w+)\.(\d+)\.(\d+)\.edf$")
FTYPE2 = re.compile(r"^(\d+)\_(\d+)\_(\d+)\.edf$")

SKIPFILE_MSG = 'Skipping "{}", because it\'s output "{}" exists.'

PROGNAME = os.path.basename(sys.argv[0])
PROGDESC = "translate .edf files to their ascii counterpart."

VERBOSE = False


def die(msg):
    """print error message and die unsuccessfully."""
    print(msg, file=sys.stderr)
    exit(1)


def process_filetype1(filename):
    """Process filetype1

    DEPRECATED
    Because these days The reading experiment boilerplate creates the
    directories.
    """
    mobj = FTYPE1.match(filename)
    fullexpname = mobj.group(1)
    expname = mobj.group(2)
    listname = mobj.group(4)
    blocknum = mobj.group(5)
    subjectnum = mobj.group(6)

    fnout = "{}_{}{}__{}.edf".format(fullexpname, listname, blocknum, subjectnum)

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
    os.rename(filename.newname)

    os.system("edf2asc {}".format(newname))


def process_filetype2(filename):
    """Processes filetype2"""
    raw_asc_fn = os.path.splitext(filename)[0] + ".asc"

    info = edfinfo.EyeFileInfo()
    info.parse_file(filename)

    # handle case that participant is dummy or pp123 like
    pp_id = "000" if info.participant == "dummy" else info.participant
    pp_id = pp_id[2:] if pp_id[:2].lower() == "pp" else pp_id

    try:
        if not (0 <= int(pp_id) <= 999):
            raise ValueError("Participant not in range 0 <= x <= 999")
    except ValueError as e:
        exit(f"{filename} hasn't got a valid participant id: {str(e)}")

    fnbase = pathlib.Path(
        "{}_{}{}_{}".format(info.experiment, info.list, info.recording, pp_id)
    )
    fnasc = fnbase.with_suffix(".asc")
    if fnasc.exists():
        if VERBOSE:
            print(SKIPFILE_MSG.format(filename, fnasc))
        return

    os.system("edf2asc {}".format(filename))

    print('renaming "{}" to "{}".'.format(raw_asc_fn, fnasc))
    os.rename(str(raw_asc_fn), str(fnasc))


def process_files(fnlist):
    """Converts all relevant edf files to there matching ascii versions"""
    for filename in fnlist:
        if FTYPE2.match(filename):
            process_filetype2(filename)
        elif FTYPE1.match(filename):  # Probably not longer used.
            process_filetype1(filename)
        else:
            print('Skipping "{}": unknown filetype.'.format(filename))


def parse_cmd_arguments():
    """Parses the command line arguments"""
    aparser = ap.ArgumentParser(PROGNAME, description=PROGDESC)
    aparser.add_argument(
        "edffiles",
        nargs="*",
        help=(
            "edf-files to process these are overwritten when -g or "
            "--glob is also specified"
        ),
    )
    aparser.add_argument(
        "-g",
        "--glob",
        help="glob (scan) working directory for .edf files",
        action="store_true",
    )
    aparser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Makes the output a bit more verbose.",
    )
    args = aparser.parse_args()
    files = args.edffiles if args.edffiles else []
    if args.glob:
        files = [str(i) for i in pathlib.Path(".").glob("*.edf")]
    if args.verbose:
        global VERBOSE
        VERBOSE = True
    return files


def main():
    """runs the program"""
    if not EDF2ASC:
        die("Unable to find {}".format(_EDF2ASC))

    files = parse_cmd_arguments()
    if files:
        process_files(files)
    else:
        print("No input exiting")


if __name__ == "__main__":
    main()
