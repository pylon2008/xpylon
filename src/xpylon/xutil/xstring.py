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

def clearDuplicateSpace(value):
    tvalue = value.replace(u"\t", u" ")
    print u"\t" in tvalue
    values = tvalue.split(u" ")
    newValue = u""
    for i in values:
        if u"" != i:
            newValue = newValue + i + u" "
    newValue = newValue[0:-1]
    return newValue
            
def test_clearDuplicateSpace():
    url = u"peng ying liang    is a good   boy,\t really a \t\t good boy"
    newUrl = clearDuplicateSpace(url)
    print url
    print newUrl
