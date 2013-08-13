#coding=GBK
import chardet

def str2unicode(string):
    if string == None:
        return None

    uniStr = u""
    if isinstance(string, unicode):
        uniStr = string
    else:
        result = chardet.detect(string)
        uniStr = string.decode(result["encoding"])
    return uniStr
