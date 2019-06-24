from injectargs import *
import pdb

class tailfitresult(object):
    @injectArguments
    def __init__(self,tailfit, filename, path, startpoint,FPS, numframes, direction, shahash, tailfitversion):
        pass

    def __str__(self,):
        strings = self.__dict__.keys()
        strings.pop(strings.index('tailfit'))
        strings = [string +': '+str(self.__dict__[string])+'  ' for string in strings]
        strings.insert(0,"Tailfit from video: "+str(self.filename)+' with length ' +str(len(self.tailfit)) +'\n')
        return ''.join(strings)
