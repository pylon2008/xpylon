#coding=GBK
import chardet

def str2unicode(string):
    if string == None:
        return None

    uniStr = u""
    if isinstance(string, unicode):
        uniStr = string
    elif isinstance(string, str):
        if len(string) > 0:
            result = chardet.detect(string)
            uniStr = string.decode(result["encoding"])
    else:
        raise TypeError, "str2unicode input type error"
    return uniStr
