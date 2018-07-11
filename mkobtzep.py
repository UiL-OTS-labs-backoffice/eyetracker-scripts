#!/usr/bin/env python3
'''Creates the object files suitable for the Fixation program and transforms
the png files created by zep to png's
'''
import shutil
import sys
import argparse
from pathlib import Path
from PIL import Image

PROG_NAME = 'mkobtzep'
PROG_DESCRIPTION = (
    "Convert png's to bmp's because that the only thing "
    "Fixation understands. Additionally it generates the object files necessary "
    "for analysis with fixation."
    )

DATADIR = "dat"
OBTDIR = "obt"
IMGDIR = "img"

OBJ_COLS = 14

PNG = ".png"
BMP = ".bmp"
OBT = ".obt"

INVALID_DIR = 'The folder "{}" doesn\'t exist or is not a folder'
OUT_LINE_FMT = (
    '{:<23}'
    '{:>3}'
    '{:>4}{:>4}'
    '{:>5}{:>5}'
    '{:>4}{:>4}{:>4}'
    '{:>5}{:>5}{:>5}{:>5}'
    '{:>4}{:>4}'
    '\r\n'
    )

def die(msg):
    '''Prints message to stderr and exit unsuccessfully.'''
    print(msg, file=sys.stderr)
    exit(1)

def parse_arguments():
    '''
    Parses the provided arguments and returns (experiment name, number of
    lists)
    '''
    parser = argparse.ArgumentParser(PROG_NAME, description=PROG_DESCRIPTION)
    parser.add_argument("expname", help="The name of the experiment")
    parser.add_argument(
        "listnum",
        type=int,
        help="The number of the list to generate the objects for"
        )
    args = parser.parse_args()
    return args.expname, args.listnum

def convert_image_to(infile, outfile):
    '''Converts image infile to the output image outfile'''
    print('Converting "{}" into "{}".'.format(infile, outfile))
    loadedim = Image.open(infile)
    loadedim.save(outfile)

def convert_planame(expname, planame):
    '''
    Converts planame to a bmp for fixation.

    It makes sure the data is written to the /exp/img/ folder relative to the
    current working directory.

    @param expname (three letter) experiment name
    @param planame basename of the picture
    '''
    imgdir = Path("./{}".format(expname)) / IMGDIR
    if not imgdir.exists() or not imgdir.is_dir():
        die(INVALID_DIR.format(str(imgdir)))
    fnin = str(imgdir / (planame + PNG))
    fnout = str(imgdir / (planame + BMP))
    if Path(fnout).exists():
        print(
            'skipping "{}" since its output "{}" already exists.'.format(
                fnin,
                fnout
                )
            )
        return
    convert_image_to(fnin, fnout)

def create_obt(expname, obtname, words):
    '''Creates a new obt file for one stimulus
    The new obt file will be created in the exp/obt/ directory
    relative to the current working directory.
    '''
    obtdir = Path("./{}".format(expname)) / OBTDIR
    if not obtdir.exists() or not obtdir.is_dir():
        die(INVALID_DIR.format(str(obtdir)))
    fnout = str(obtdir / ("python_" + obtname + OBT))
    with open(fnout, 'wb') as obtfile:
        for fields in words:
            stimnum, condition, nl, ln, wnt, nwl, wnl, \
            wx, wy, ww, wh, ll, wl, word = tuple(fields)
            line = OUT_LINE_FMT.format(
                word,       # object
                wl,         # object length
                wnl+1,      # object number in line
                nwl,        # number of objects in line
                ll,         # line length
                wnt+1,      # object number in line
                ln+1,       # line number
                nl,         # number of lines in text
                stimnum,    # stimulus number
                wx,         # object x
                wy,         # object y
                wx + ww,    # object x + object width
                wy + wh,    # object y + object height
                0,          # object code
                0           # object position code
                )
            obtfile.write(line.encode('utf8'))


def process_lines(llist, expname):
    '''Processes the lines in the line list llist'''
    trials = {}
    for line in llist:
        #split line and strip (leading and) trailing white space
        try:
            fields = line.split(';')
            fields = [int(fields[0]), fields[1]] +\
                [int(i) for i in fields[2:-1]] +\
                [fields[-1].strip()]
        except ValueError:
            #skip line
            continue

        # Put the fields that belong to one trial in the trials dict as a list.
        if len(fields) == OBJ_COLS:
            trialnum = fields[0]
            if trialnum in trials:
                trials[trialnum].append(fields)
            else:
                trials[trialnum] = [fields]

    for key, trial in trials.items():
        condition = trial[0][1]
        planame = '{}{:03}'.format(condition, key)
        convert_planame(expname, planame)
        create_obt(expname, planame, trial)


def process_file(expname, listnum):
    '''
    Processes the list number
    '''
    pathin1 = Path("./" + expname) / "obt" / "objects{}.csv".format(listnum)
    lines = []
    try:
        with open(str(pathin1)) as infile:
            lines = infile.readlines()
    except IOError:
        die("Unable to open: '{}'".format(str(pathin1)))

    process_lines(lines, expname)

def main():
    '''The main function'''
    expname, listnumber = parse_arguments()
    process_file(expname, listnumber)

if __name__ == "__main__":
    main()
