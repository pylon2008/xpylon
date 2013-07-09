#coding=GBK

import os, logging
from xpylon.xutil.xstring import *

def killProcess(name):
    cmd = u"taskkill /F /T /IM " + str2unicode(name)
    result = os.popen(cmd).read()
    result = str2unicode(result)
    result = u"killProcess result: " + result
    logging.debug(result)

if __name__=='__main__':
    killProcess(u"iexplore.exe")
