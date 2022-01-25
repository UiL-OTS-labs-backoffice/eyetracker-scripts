#!/usr/bin/env python3

"""edfinfo provides some basic information about edf files"""

import re
import os.path
import shutil
import subprocess
import tempfile
import pathlib

from typing import List

_PROGRAM_NAME = 'edfinfo'
_DESCRIPTION = """edfinfo provides some helpfull information about SR-Reseach/Eyelink
edf files (.edf)"""

_EDF2ASC = 'edf2asc'
_HAVE_EDF2ASC = shutil.which(_EDF2ASC) != None
MSG = "MSG"


def is_edf(fn:str):
    """Returns whether or not the file is a edf file"""
    return os.path.splitext(fn)[1] == ".edf"

def is_asc(fn:str):
    """Returns whether or not the file is a asc file"""
    return os.path.splitext(fn)[1] == ".asc"

def is_eytracker_fn(fn:str):
    """Returns True if edfinfo should think the file is a valid eyetracker
    file False otherwise.
    """
    return is_asc(fn) or is_edf(fn)

class NotAnEyetrackerFile(Exception):
    """ Raised by EdfInfo when it thinks it is parsing an invalid file """

class EyeFileInfo:
    """
    Obtains general info about a eyelink data file (.edf file).
    """

    RE_START        = r'^(\*\* )?'
    RE_MSG_START    = r'^(MSG\s+\d+\s+)'

    RE_DATE         = re.compile(RE_START + r'DATE: (.*)')
    RE_TYPE         = re.compile(RE_START + r'TYPE: (.*)')
    RE_VERSION      = re.compile(RE_START + r'VERSION: (.*)')
    RE_SOURCE       = re.compile(RE_START + r'SOURCE: (.*)')
    RE_EYELINK      = re.compile(RE_START + r'(EYELINK .*)')
    RE_CAMERA       = re.compile(RE_START + r'CAMERA: (.*)')
    RE_SERIAL       = re.compile(RE_START + r'SERIAL NUMBER: (.*)')
    RE_CAMERA_CONF  = re.compile(RE_START + r'CAMERA_CONFIG: (.*)')
    RE_RECORDED_BY  = re.compile(RE_START + r'RECORDED BY: (.*)')
    RE_EXPERIMENT   = re.compile(RE_START + r'EXPERIMENT: (.*)')
    RE_RESEARCHER   = re.compile(RE_START + r'RESEARCHER: (.*)')
    RE_PARTICIPANT  = re.compile(RE_START + r'PARTICIPANT: (.*)')
    RE_SESSION      = re.compile(RE_START + r'SESSION: (.*)')
    RE_LIST         = re.compile(RE_START + r'LIST: (.*)')
    RE_RECORDING    = re.compile(RE_START + r'RECORDING: (.*)')

    # These are added because Zep-2 output this info in messages instead of preamble
    RE_M_RECORDED_BY  = re.compile(RE_MSG_START + r'RECORDED BY:(.*)')
    RE_M_EXPERIMENT   = re.compile(RE_MSG_START + r'EXPERIMENT:(.*)')
    RE_M_RESEARCHER   = re.compile(RE_MSG_START + r'RESEARCHER:(.*)')
    RE_M_PARTICIPANT  = re.compile(RE_MSG_START + r'PARTICIPANT:(.*)')
    RE_M_SESSION      = re.compile(RE_MSG_START + r'SESSION:(.*)')
    RE_M_LIST         = re.compile(RE_MSG_START + r'LIST:(.*)')
    RE_M_RECORDING    = re.compile(RE_MSG_START + r'RECORDING:(.*)')

    # If the next two regexes match we've parsing of eyefileinfo
    # should be completed.
    RE_MSG          = re.compile(r'^MSG')
    RE_ENDP         = re.compile(r'^ENDP:.*')

    def __init__(self):
        self.date           = ""
        self.type           = ""
        self.version        = ""
        self.source         = ""
        self.eyelink        = ""
        self.camera         = ""
        self.serial         = ""
        self.camera_conf    = ""
        self.recorded_by    = ""
        self.experiment     = ""
        self.researcher     = ""
        self.participant    = ""
        self.session        = ""
        self.list           = ""
        self.recording      = ""

    def is_complete(self):
        """Determines whether all attributes are set to there final
        value"""
        for key, value in self.__dict__.items():
            if not value:
                return False
        return True

    def _parse_preamble(self, lines:List[str]):
        """Parses the preable of and edf file and fills out
        The required attributes on self

        Note in Zep-2 some of these variables have been moved
        from the preable to the MSG's in the actual data.
        hence, some deeper parsing is neccessary. Used
        EdfInfo.is_complete() to check whether additional info
        should be obtained from the file.
        """
        for line in lines:
            if obj:= self.RE_DATE.match(line):
                self.date = obj.group(2)
                continue
            
            if obj:= self.RE_TYPE.match(line):
                self.type= obj.group(2)
                continue
            
            if obj:= self.RE_VERSION.match(line):
                self.version= obj.group(2)
                continue
            
            if obj:= self.RE_SOURCE.match(line):
                self.source= obj.group(2)
                continue
            
            if obj:= self.RE_EYELINK.match(line):
                self.eyelink= obj.group(2)
                continue
            
            if obj:= self.RE_CAMERA.match(line):
                self.camera= obj.group(2)
                continue
            
            if obj:= self.RE_SERIAL.match(line):
                self.serial= obj.group(2)
                continue
            
            if obj:= self.RE_CAMERA_CONF.match(line):
                self.camera_conf = obj.group(2)
                continue
            
            if obj:= self.RE_RECORDED_BY.match(line):
                self.recorded_by = obj.group(2)
                continue
            
            if obj:= self.RE_EXPERIMENT.match(line):
                self.experiment = obj.group(2)
                continue
            
            if obj:= self.RE_RESEARCHER.match(line):
                self.researcher = obj.group(2)
                continue
            
            if obj:= self.RE_PARTICIPANT.match(line):
                self.participant = obj.group(2)
                continue
            
            if obj:= self.RE_SESSION.match(line):
                self.session = obj.group(2)
                continue
            
            if obj:= self.RE_LIST.match(line):
                self.list = obj.group(2)
                continue
            
            if obj:= self.RE_RECORDING.match(line):
                self.recording = obj.group(2)
                continue
    
    def _parse_msg_lines(self, lines:List[str]):
        """Parses the messages to collect info
        about the experiment, researcher, participant,
        session, list and recording info.

        If information was already found in the preamble
        it's overwritten, hence the messages are treated
        as leading.
        """
        for line in lines:
            if obj := self.RE_M_RECORDED_BY.match(line):
                self.recording = obj.group(2)

            if obj := self.RE_M_EXPERIMENT.match(line):
                self.experiment = obj.group(2)

            if obj := self.RE_M_RESEARCHER.match(line):
                self.researcher = obj.group(2)

            if obj := self.RE_M_PARTICIPANT.match(line):
                self.participant = obj.group(2)

            if obj := self.RE_M_SESSION.match(line):
                self.session = obj.group(2)

            if obj := self.RE_M_LIST.match(line):
                self.list= obj.group(2)

            if obj := self.RE_M_RECORDING.match(line):
                self.recording = obj.group(2)
    
    
    def parse_file(self, fn:str):
        """Parses the file fn
        @fn a valid eyetracker file

        Raises NotAnEyetrackerFile when we think it is not an eyetracker
        file.
        """
        if not is_eytracker_fn(fn):
            raise NotAnEyetrackerFile()

        lines = []

        with open(fn, 'rb') as f:
            # If these match, than we should have everything we need.
            for l in f:
                line = l.decode('utf8')
                obj = self.RE_MSG.match(line)
                if obj:
                    break
                obj = self.RE_ENDP.match(line)
                if obj:
                    break
                lines.append(line)

        self._parse_preamble(lines)

        if not self.is_complete():
            if _HAVE_EDF2ASC:
                self.deep_parse(fn)

    def deep_parse(self, fn:str):
        """Extracts the .edf file to .asc and inspects whether the eyelink MSG
        can fill out the missing values"""

        if not is_eytracker_fn(fn):
            raise ValueError(f"Not a valid filename: \"${fn}\"")

        tempname = os.path.join(
            tempfile.gettempdir(),
            os.path.splitext(os.path.basename(fn))[0] + '.asc'
        )
        
        if is_edf(fn):
            if not _HAVE_EDF2ASC:
                raise RunTimeError('the SR research edf2asc program wasn\'t found')

            # Create a temporary output file in .asc format
            # edf2asc The SR research edf -> asc converter
            #   -y  : overwrite .asc if exists
            #   -ns : no samples
            subprocess.run([_EDF2ASC, "-y", "-ns", fn, tempname], stdout=subprocess.DEVNULL)
        else:
            shutil.copy(fn, tempname)

        msg_lines = []
        with open(tempname) as myfile:
            msg_lines = [line.strip() for line in myfile if line[:len(MSG)] == MSG]
        self._parse_msg_lines(msg_lines)

        # Cleanup after use
        temppath = pathlib.Path(tempname)
        temppath.unlink()
    
    def __str__(self):
        """Return a string representation of self compatible with the
        older edfinfo perl script.
        """
        s = ""
        if self.date:
            s += "  date:\t\t\t{}".format(self.date) + os.linesep
        if self.type:
            s += "  type:\t\t\t{}".format(self.type) + os.linesep
        if self.version:
            s += "  version:\t\t{}".format(self.version) + os.linesep
        if self.source:
            s += "  source:\t\t{}".format(self.source) + os.linesep
        if self.eyelink:
            s += "  eyelink:\t\t{}".format(self.eyelink) + os.linesep
        if self.camera:
            s += "  camera:\t\t{}".format(self.camera) + os.linesep
        if self.serial:
            s += "  serial number:\t{}".format(self.serial) + os.linesep
        if self.camera_conf:
            s += "  camera config:\t{}".format(self.camera_conf) + os.linesep
        if self.recorded_by:
            s += "  recorded by:\t\t{}".format(self.recorded_by) + os.linesep
        if self.experiment:
            s += "  experiment:\t\t{}".format(self.experiment) + os.linesep
        if self.researcher:
            s += "  researcher:\t\t{}".format(self.researcher) + os.linesep
        if self.participant:
            s += "  participant:\t\t{}".format(self.participant) + os.linesep
        if self.session:
            s += "  session:\t\t{}".format(self.session) + os.linesep
        if self.list:
            s += "  list:\t\t\t{}".format(self.list) + os.linesep
        if self.recording:
            s += "  recording:\t\t{}".format(self.recording)
        return s

if __name__ == "__main__":
    import sys
    import argparse as ap
    
    parser = ap.ArgumentParser(_PROGRAM_NAME, description=_DESCRIPTION)
    parser.add_argument('input_files', nargs='+', help="The input .edf file's")
    args = parser.parse_args()

    for fn in args.input_files:
        if is_eytracker_fn(fn) and os.path.exists(fn):
            info = EyeFileInfo()
            info.parse_file(fn)
            print("{}:".format(fn))
            print(str(info))
        else:
            print(
                "Skipping \"{}\" (not an edf or asc file).".format(fn),
                file=sys.stderr
                )

