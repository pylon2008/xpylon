#coding=GBK
import urllib2, random
import win32api, win32inet, datetime, logging
import win32con, win32file, random, traceback

def getRandomIntSet(maxVal):
    randomSet = []
    for i in range(maxVal):
        isIn = False
        while isIn==False:
            ii = random.randint(0, maxVal-1)
            if ii not in randomSet:
                randomSet.append(ii)
                isIn = True
    return randomSet

##g_OutDataTime.year = 2013
##g_OutDataTime.month = 5
##g_OutDataTime.day = 30
def isOutOfData():
    g_IsOutOfData = False
    g_OutDataTime = datetime.datetime(2013,7,7, 0, 0)
    if g_IsOutOfData==False:
        timeNow = datetime.datetime.now()
        if timeNow > g_OutDataTime:
            g_IsOutOfData = True
##    print "g_IsOutOfData: ", g_IsOutOfData
    return g_IsOutOfData

##datetime.datetime.utcnow()
##attrs = [("year","年"),('month',"月"),("day","日"),
##         ('hour',"小时"),( 'minute',"分"),( 'second',"秒"),
##         ( 'microsecond',"毫秒"),('min',"最小"),( 'max',"最大"),]
##for k,v in attrs:
##    "now.%s = %s #%s" % (k,getattr(now, k),v)

##    # 使用自己的代理地址，注意ProxyHandler()的参数必须是字典类型
##    # build_opener()创建一个实例句柄
##    # 使用这个句柄通过open方法访问目标网址
##    # 为了便于知道哪些代理地址不能用，这里我抛出了两个已知异常，并输出异常代理地址
##    # 最后打印出发生异常的个数
def isProxyValid(proxy):
    isOk = True
    try:
        proxy_handler = urllib2.ProxyHandler({'http':'http://'+proxy})
        opener = urllib2.build_opener(proxy_handler)
        opener.open('http://www.ip138.com/')
    except urllib2.URLError:
       # print 'URLError! The bad proxy is %s' % proxy      
        isOk = False
    except urllib2.HTTPError:
        #print 'HTTPError! The bad proxy is %s' % proxy
        isOk = False
    except:
        #print 'Unknown Errors! The bad proxy is %s' % proxy
        isOk = False
    return isOk

def setIERefresh():
    INTERNET_OPTION_REFRESH = 0x000025
    INTERNET_OPTION_SETTINGS_CHANGED = 0x000027
    cc = win32inet.InternetSetOption(None, INTERNET_OPTION_SETTINGS_CHANGED, None)
    cc = win32inet.InternetSetOption(None, INTERNET_OPTION_REFRESH, None)

def setProxy(proxy):
    pathInReg='Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'
    key=win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,pathInReg,0,win32con.KEY_ALL_ACCESS)

    value,enableType = win32api.RegQueryValueEx(key,'ProxyEnable')
    if value==0:
        win32api.RegSetValueEx(key,'ProxyEnable',0,win32con.REG_DWORD,1)

    d = win32api.RegSetValueEx(key,'ProxyServer',0,win32con.REG_SZ,proxy)
    c = win32api.RegQueryValueEx(key,'ProxyServer')
    win32api.RegCloseKey(key)
    setIERefresh()

def clearProxy():
    pathInReg='Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'
    key=win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,pathInReg,0,win32con.KEY_ALL_ACCESS)
    value,enableType = win32api.RegQueryValueEx(key,'ProxyEnable')
    if value==1:
        win32api.RegSetValueEx(key,'ProxyEnable',0,win32con.REG_DWORD,0)
    d = win32api.RegSetValueEx(key,'ProxyServer',0,win32con.REG_SZ,"")
    win32api.RegCloseKey(key)
    setIERefresh()

class IEProxy(object):
    def __init__(self, proxyFile):
        self.proxyFile = proxyFile
        self.proxySet = []
        f=file(proxyFile,'r')
        while True:
            line=f.readline()
            if len(line)==0:
                break
            rr = line.split(" ")
            self.proxySet.append( [rr[0], int(rr[1])] )
        f.close()
        self.curProxyIdx = -1
        self.errorSet = []

    def changeProxy(self):
        if isOutOfData()==True:
            self.clearProxy()
            return None
        
        PROXY_VALID_FLAG = 567
        while True:
            self.curProxyIdx += 1
            if self.curProxyIdx >= len(self.proxySet):
                self.curProxyIdx = 0
            if self.proxySet[self.curProxyIdx][1]==PROXY_VALID_FLAG:
                isOk = isProxyValid(self.proxySet[self.curProxyIdx][0])
                value = PROXY_VALID_FLAG
                if isOk == True:
                    value = PROXY_VALID_FLAG
                else:
                    value = random.randint(0, 1)
                    if value==0:
                        value = random.randint(0, PROXY_VALID_FLAG-1)
                    else:
                        value = random.randint(PROXY_VALID_FLAG+1, 1000)
                self.proxySet[self.curProxyIdx][1] = value
                if isOk==True:
                    break
                else:
                    if self.curProxyIdx not in self.errorSet:
                        self.errorSet.append(self.curProxyIdx)

        setProxy(self.proxySet[self.curProxyIdx][0])
        self.writeProxy()

    def clearProxy(self):
        try:
            clearProxy()
        except:
            logging.error("clearProxy exception")
            traceStr = traceback.format_exc()
            logging.error(traceStr)
        

    def writeProxy(self):
        tmpFile = file("ptmp.txt", "w+")
        numP = len(self.proxySet)
        randomInt = getRandomIntSet( numP )
        for idx in randomInt:
            if idx>=0 and idx<numP:
                proxy = self.proxySet[idx]
                line = proxy[0] + " " + str(proxy[1]) + "\r\n"
                tmpFile.write(line)
            else:
                logging.error("proxy random error: " + str(idx))
        tmpFile.close()
        uFile = self.proxyFile
        win32file.DeleteFile(uFile)
        win32file.CopyFile(u"ptmp.txt", uFile, False)
        #win32file.MoveFile(u"ptmp.txt", uFile)

    

def scan_proxy():
    proxy = IEProxy('proxy.txt')
    for i in range(30):
        proxy.changeProxy()

if __name__=='__main__':
    scan_proxy()
