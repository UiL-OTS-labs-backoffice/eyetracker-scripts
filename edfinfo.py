#!/usr/bin/env python3

'''edfinfo provides some basic information about edf files'''

import re
import os.path

_PROGRAM_NAME = 'edfinfo'
_DESCRIPTION = '''edfinfo provides some helpfull information about SR-Reseach/Eyelink
edf files (.edf)'''


def is_edf(fn):
    '''Returns whether or not the file is a edf file'''
    return os.path.splitext(fn)[1] == ".edf"

def is_asc(fn):
    '''Returns whether or not the file is a asc file'''
    return os.path.splitext(fn)[1] == ".asc"

def is_eytracker_fn(fn):
    '''Returns True if edfinfo should think the file is a valid eyetracker
    file False otherwise.
    '''
    return is_asc(fn) or is_edf(fn)

class NotAnEyetrackerFile(Exception):
    ''' Raised by EdfInfo when it thinks it is parsing an invalid file '''

class EyeFileInfo:
    '''
    Obtains general info about a eyelink data file (.edf file).
    '''

    RE_START        = r'^(\*\* )?'

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
    
    def parse_file(self, fn):
        '''Parses the file fn
        Raises NotAnEyetrackerFile when we think it is not an eyetracker
        file.
        '''
        if not is_eytracker_fn(fn):
            raise NotAnEyetrackerFile()
        with open(fn, 'rb') as f:
            for l in f:
                line = l.decode('utf8')
                obj = self.RE_DATE.match(line)
                if obj:
                    self.date = obj.group(2)
                    continue
                obj = self.RE_TYPE.match(line)
                if obj:
                    self.type= obj.group(2)
                    continue
                obj = self.RE_VERSION.match(line)
                if obj:
                    self.version= obj.group(2)
                    continue
                obj = self.RE_SOURCE.match(line)
                if obj:
                    self.source= obj.group(2)
                    continue
                obj = self.RE_EYELINK.match(line)
                if obj:
                    self.eyelink= obj.group(2)
                    continue
                obj = self.RE_CAMERA.match(line)
                if obj:
                    self.camera= obj.group(2)
                    continue
                obj = self.RE_SERIAL.match(line)
                if obj:
                    self.serial= obj.group(2)
                    continue
                obj = self.RE_CAMERA_CONF.match(line)
                if obj:
                    self.camera_conf = obj.group(2)
                    continue
                obj = self.RE_RECORDED_BY.match(line)
                if obj:
                    self.recorded_by = obj.group(2)
                    continue
                obj = self.RE_EXPERIMENT.match(line)
                if obj:
                    self.experiment = obj.group(2)
                    continue
                obj = self.RE_RESEARCHER.match(line)
                if obj:
                    self.researcher = obj.group(2)
                    continue
                obj = self.RE_PARTICIPANT.match(line)
                if obj:
                    self.participant = obj.group(2)
                    continue
                obj = selsys.argv[1:]f.RE_SESSION.match(line)
                if obj:
                    self.session = obj.group(2)
                    continue
                obj = self.RE_LIST.match(line)
                if obj:
                    self.list = obj.group(2)
                    continue
                obj = self.RE_RECORDING.match(line)
                if obj:
                    self.recording = obj.group(2)
                    continue

                # If these match, than we should have everything we need.
                obj = self.RE_MSG.match(line)
                if obj:
                    break
                obj = self.RE_ENDP.match(line)
                if obj:
                    break
    
    def __str__(self):
        '''Return a string representation of self compatible with the
        older edfinfo perl script.
        '''
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
        if is_eytracker_fn(fn):
            info = EyeFileInfo()
            info.parse_file(fn)
            print("{}:".format(fn))
            print(str(info))
        else:
            print(
                "Skipping \"{}\" (not an edf or asc file).".format(fn),
                file=sys.stderr
                )

