#coding=GBK
import win32gui, win32api, win32process, win32con
import win32com.client, os
import time, datetime, traceback, logging, pywintypes
from win32com.shell import shell, shellcon
from xpylon.xutil.Process import *

# 获取屏幕的宽、高
##width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
##height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
##import ctypes
##ctypes.windll.user32.GetWindowTextLengthW

IE_INTERVAL_TIME_CLOSE = 1
IE_INTERVAL_TIME_SACROLL = 0.08
IE_TIME_OUT_SCROLL = 4
IE_TIME_OUT_NEW_PAGE = 15

def getScrollDelta():
    baseScrollDelta = [20,30,40,50,60,70]
    zoom = 3.0
    scrollDelta = []
    for i in baseScrollDelta:
        value = i * zoom
        value = (int)(value)
        scrollDelta.append(value)
    return scrollDelta

def deleteFileFolder(src):
    '''delete files and folders'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            deleteFileFolder(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass

def getSpecialFolderPath(csid):
    try:
        path = shell.SHGetSpecialFolderPath(0, csid, False)
    except:
        path = None
    return path

def clearIECookie():
    cookiePath = getSpecialFolderPath(shellcon.CSIDL_COOKIES)
    if cookiePath!=None:
        deleteFileFolder(cookiePath)

def getAllRunningIE():
    ShellWindowsCLSID = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'  
    ies = win32com.client.DispatchEx(ShellWindowsCLSID)
    copyIes = []
    for ie in ies:
        copyIes.append(ie)
    return copyIes

def closeAllRunningIE():
    try:
        ies = getAllRunningIE()
        logging.debug("len(ies): %d", len(ies))
        for ie in ies:
            url = ie.LocationURL
            logging.debug("ie.LocationURL: %s", url)
            if (u"http://" in url) or (u"about:blank" in url):
                logging.debug("closeAllRunningIE: %s", url)
                while ie.Busy==True:
                    ie.stop()
                    time.sleep(0.1)
                ie.quit()
                time.sleep(IE_INTERVAL_TIME_CLOSE)
            else:
                a = 0
    except:
        logging.error("closeAllRunningIE exception")
        traceStr = traceback.format_exc()
        logging.error(traceStr)

    try:
        killProcess(u"iexplore.exe")
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)

def existIE(url):
    ies = getAllRunningIE()
    if len(ies)==0:  
        return None
    for ie in ies:
        ieURL = ie.LocationURL
        if type(ie.LocationURL) == unicode:
            ieURL = ieURL.encode('GBK')
        newURL = url
        if newURL[-1]=='\n':
            newURL = newURL[0:-1]
        if type(newURL) == str:
            newURL = newURL.encode('GBK')            
        if ieURL==newURL:
            return ie
    return None

# 模拟人工输入文本
def enumHumanInput(node, value):
    thisValue = ''
    for c in value:
        thisValue = thisValue + c
        node.value = thisValue
        time.sleep(0.2)
    return thisValue

# 根据tag名称获取父节点的所有子节点
def getSubNodesByTag(parentNode, tag):
    childNodes=[]
    if parentNode != None:
        for childNode in parentNode.getElementsByTagName(tag):  
            childNodes.append(childNode)  
    return childNodes

# 在节点集合nodes中查找属性attr为值val的节点
def getNodeByAttr(nodes, attr, val):
    for node in nodes:  
        if str(node.getAttribute(attr))==val:  
            return node  
    return None

# 判断节点是否在屏幕范围内
def isNodeInScreen(node, ie):
    client = node.getBoundingClientRect()
    nodeHeight = client.bottom - client.top
    nodeMiddle = (client.bottom + client.top)/2
    clientHeight = ie.getClientHeight()
    ieMiddle = clientHeight/2
    isIn = True
    if clientHeight<=nodeHeight:
        if client.top>0 and client.top<70:
            isIn = True
        else:
            isIn = False
    else:
        dis = ieMiddle-nodeMiddle
        if dis<=50 and dis>=-50:
            isIn = True
        else:
            isIn = False
    return isIn

def getScrollDirection(node, ie):
    scrollDirection = 1
    client = node.getBoundingClientRect()
    nodeHeight = client.bottom - client.top
    nodeMiddle = (client.bottom + client.top) / 2
    clientHeight = ie.getClientHeight()
    ieMiddle = clientHeight/2
    if nodeMiddle > ieMiddle:
        scrollDirection = 1
    else:
        scrollDirection = -1
    return scrollDirection


class IEExplorer(object):
    def __init__(self):
        self.ie = None
        self.oldURL = ""
        self.timeBegOp = None                   # 开始操作宝贝的起点时间，从开始滚动开始
        self.IEHandle = None

    def newIE(self, url):  
        self.ie = win32com.client.Dispatch("InternetExplorer.Application")
        self.navigate(url)

    def openURL(self, url):
        self.ie = existIE(url)
        if self.ie == None:
            self.newIE(url)
        self.IEHandle = self.getIEHandle()
        #self.setForeground()

    def navigate(self, url):
        self.ie.Navigate(url)

    def waitReadyState(self, totalTimeout):
        isBusy = False
        timeout = 0.0
        while True:
            if self.ie.ReadyState==4:
                break
            else:
                deltaTime = 0.5
                time.sleep(deltaTime)
                timeout += deltaTime
            if timeout>=totalTimeout:
                isBusy = True
                break
        if isBusy==True:
            logging.debug("waitReadyState: "+str(isBusy))
        return isBusy
        
    def waitNavigate(self, oldURL, totalTimeout):
        self.waitReadyState()
        timeout = 0.0
        isBusy = False
        while True:
            if self.ie.LocationURL!=oldURL:
                break
            else:
                deltaTime = 0.5
                time.sleep(deltaTime)
                timeout += deltaTime
            if timeout>=totalTimeout:
                isBusy = True
                break
        if isBusy==True:
            logging.debug("waitNavigate: "+str(isBusy))
        return isBusy
                
    def waitBusy(self, totalTimeout):
        isBusy = False
        timeout = 0.0
        while True:
            if self.isBusy():
                deltaTime = 0.5
                time.sleep(deltaTime)
                timeout += deltaTime
            else:
                break
            if timeout>=totalTimeout:
                isBusy = True
                break
        if isBusy==True:
            logging.debug("waitBusy: "+str(isBusy))
        return isBusy

    def setVisible(self, visible):
        self.ie.Visible = visible

    def getIE(self):
        return self.ie

    def getIEHandle(self):
        if self.IEHandle == None:
            debugInfo = "type(self.ie.hwnd): " + str(type(self.ie.hwnd)) \
                        + ", self.ie.hwnd: " + str(self.ie.hwnd)
            logging.debug(debugInfo)
            self.IEHandle = pywintypes.HANDLE(self.ie.hwnd)
        return self.IEHandle

    def setForeground(self):
        #preshell = win32com.client.Dispatch("WScript.Shell")        
        #preshell.SendKeys(u'%')
        #ieHandle = self.getIEHandle()
        #win32gui.SetForegroundWindow(ieHandle)
        
        forcegroundWindow = win32gui.GetForegroundWindow()
        forcegroundThreadId, forcegroundProcessId = win32process.GetWindowThreadProcessId(forcegroundWindow)
        appThreadId = win32api.GetCurrentThreadId()
        if appThreadId != forcegroundThreadId:
            win32process.AttachThreadInput(forcegroundThreadId, appThreadId, True)
            ieHandle = self.getIEHandle()
            win32gui.BringWindowToTop(ieHandle)
            win32gui.ShowWindow(ieHandle, win32con.SW_SHOW)
            win32process.AttachThreadInput(forcegroundThreadId, appThreadId, False)
        else:
            ieHandle = self.getIEHandle()
            win32gui.BringWindowToTop(ieHandle)
            win32gui.ShowWindow(ieHandle, win32con.SW_SHOW)
            

    def resizeMax(self):
        WM_SYSCOMMAND = int('112', 16)
        SC_MINIMIZE = int('F020', 16)
        SC_MAXIMIZE = int('F030', 16)
        ieHandle = self.getIEHandle()
        win32api.SendMessage(ieHandle, WM_SYSCOMMAND, SC_MAXIMIZE, 0)
    
    def getBody(self):
        return self.ie.Document.body

    # window.screenLeft
    # window.screenTop
    def getWindow(self):
        return self.ie.Document.parentWindow

    def quit(self):
        while self.waitBusy(IE_TIME_OUT_SCROLL)==True:
            self.stop()
            time.sleep(0.1)
        self.ie.quit()

    def stop(self):
        self.ie.stop()

    def isBusy(self):
        return self.ie.Busy

    def locationURL(self):
        return self.ie.LocationURL

    # 获取屏幕的可视高度
    def getClientHeight(self):
        return self.ie.Document.documentElement.clientHeight

    def scrollToNode(self, node):
        scrollDirection = getScrollDirection(node, self)
        scrollDelta = getScrollDelta()
        isIn = False
        timeBeg = datetime.datetime.now()

        oldClient = node.getBoundingClientRect()
        while isIn==False:
            for delta in scrollDelta:
                while self.waitBusy(IE_TIME_OUT_SCROLL)==True:
                    self.stop()
                    time.sleep(0.1)
                self.waitReadyState(IE_TIME_OUT_SCROLL)
                self.getWindow().scrollBy(0,delta*scrollDirection)
                if isNodeInScreen(node, self)==True:
                    isIn = True
                    break
            time.sleep(IE_INTERVAL_TIME_SACROLL)
            timeEnd = datetime.datetime.now()
            deltaTime = (timeEnd-timeBeg).seconds
            newClient = node.getBoundingClientRect()
            deltaMove = newClient.top-oldClient.top
            if deltaMove<0:
                deltaMove = -deltaMove
            if (deltaTime >= 30) or (deltaMove<10):
                isIn = True
                break
            logging.debug("deltaMove: " + str(deltaMove))
            logging.debug("deltaTime: " + str(deltaTime))
            oldClient = newClient

    def stayInSubPage(self, timeOut):
        scrollDelta = getScrollDelta()
        a = datetime.datetime.now()
        self.timeBegOp = a
        while True:
            for delta in scrollDelta:
                while self.waitBusy(IE_TIME_OUT_SCROLL)==True:
                    self.stop()
                    time.sleep(0.1)
                isBusy = self.waitReadyState(IE_TIME_OUT_SCROLL)
                if isBusy==True:
                    logging.debug("stayInSubPage::waitReadyState: "+str(isBusy))
                self.getWindow().scrollBy(0,delta)
            time.sleep(IE_INTERVAL_TIME_SACROLL)
            b = datetime.datetime.now()
            deltaTime = (b-a).seconds
            if deltaTime >= timeOut:
                break










def test_special_path():
    cachePath = getSpecialFolderPath(shellcon.CSIDL_INTERNET_CACHE)
    print "CSIDL_INTERNET_CACHE: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COOKIES)
    print "CSIDL_COOKIES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_DESKTOP)
    print "CSIDL_DESKTOP: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_INTERNET)
    print "CSIDL_INTERNET: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PROGRAMS)
    print "CSIDL_PROGRAMS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_CONTROLS)
    print "CSIDL_CONTROLS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PRINTERS)
    print "CSIDL_PRINTERS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PERSONAL)
    print "CSIDL_PERSONAL: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_FAVORITES)
    print "CSIDL_FAVORITES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_STARTUP)
    print "CSIDL_STARTUP: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_RECENT)
    print "CSIDL_RECENT: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_SENDTO)
    print "CSIDL_SENDTO: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_BITBUCKET)
    print "CSIDL_BITBUCKET: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_STARTMENU)
    print "CSIDL_STARTMENU: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_MYDOCUMENTS)
    print "CSIDL_MYDOCUMENTS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_MYMUSIC)
    print "CSIDL_MYMUSIC: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_MYVIDEO)
    print "CSIDL_MYVIDEO: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_DESKTOPDIRECTORY)
    print "CSIDL_DESKTOPDIRECTORY: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_DRIVES)
    print "CSIDL_DRIVES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_NETWORK)
    print "CSIDL_NETWORK: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_NETHOOD)
    print "CSIDL_NETHOOD: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_FONTS)
    print "CSIDL_FONTS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_TEMPLATES)
    print "CSIDL_TEMPLATES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_STARTMENU)
    print "CSIDL_COMMON_STARTMENU: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_PROGRAMS)
    print "CSIDL_COMMON_PROGRAMS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_STARTUP)
    print "CSIDL_COMMON_STARTUP: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_DESKTOPDIRECTORY)
    print "CSIDL_COMMON_DESKTOPDIRECTORY: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_APPDATA)
    print "CSIDL_APPDATA: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PRINTHOOD)
    print "CSIDL_PRINTHOOD: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_LOCAL_APPDATA)
    print "CSIDL_LOCAL_APPDATA: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_ALTSTARTUP)
    print "CSIDL_ALTSTARTUP: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_ALTSTARTUP)
    print "CSIDL_COMMON_ALTSTARTUP: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_FAVORITES)
    print "CSIDL_COMMON_FAVORITES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_INTERNET_CACHE)
    print "CSIDL_INTERNET_CACHE: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COOKIES)
    print "CSIDL_COOKIES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_HISTORY)
    print "CSIDL_HISTORY: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_APPDATA)
    print "CSIDL_COMMON_APPDATA: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_WINDOWS)
    print "CSIDL_WINDOWS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_SYSTEM)
    print "CSIDL_SYSTEM: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PROGRAM_FILES)
    print "CSIDL_PROGRAM_FILES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_MYPICTURES)
    print "CSIDL_MYPICTURES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PROFILE)
    print "CSIDL_PROFILE: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_SYSTEMX86)
    print "CSIDL_SYSTEMX86: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PROGRAM_FILESX86)
    print "CSIDL_PROGRAM_FILESX86: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PROGRAM_FILES_COMMON)
    print "CSIDL_PROGRAM_FILES_COMMON: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_PROGRAM_FILES_COMMONX86)
    print "CSIDL_PROGRAM_FILES_COMMONX86: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_TEMPLATES)
    print "CSIDL_COMMON_TEMPLATES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_DOCUMENTS)
    print "CSIDL_COMMON_DOCUMENTS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_ADMINTOOLS)
    print "CSIDL_COMMON_ADMINTOOLS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_ADMINTOOLS)
    print "CSIDL_ADMINTOOLS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_CONNECTIONS)
    print "CSIDL_CONNECTIONS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_MUSIC)
    print "CSIDL_COMMON_MUSIC: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_PICTURES)
    print "CSIDL_COMMON_PICTURES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_VIDEO)
    print "CSIDL_COMMON_VIDEO: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_RESOURCES)
    print "CSIDL_RESOURCES: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_RESOURCES_LOCALIZED)
    print "CSIDL_RESOURCES_LOCALIZED: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMMON_OEM_LINKS)
    print "CSIDL_COMMON_OEM_LINKS: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_CDBURN_AREA)
    print "CSIDL_CDBURN_AREA: ", cachePath
    cachePath = getSpecialFolderPath(shellcon.CSIDL_COMPUTERSNEARME)
    print "CSIDL_COMPUTERSNEARME: ", cachePath

##清除IE临时文件的另外一个途径是直接调用Wininet函数，请看下面用于清除IE临时文件的函数
##BOOL DelTempFiles()
##    { BOOL bResult = FALSE;
##      BOOL bDone = FALSE;
##      LPINTERNET_CACHE_ENTRY_INFO lpCacheEntry = NULL;
##      DWORD dwTrySize, dwEntrySize = 4096; // start buffer size
##      HANDLE hCacheDir = NULL;
##      DWORD dwError = ERROR_INSUFFICIENT_BUFFER;
##      do
##      { switch (dwError)
##        { // need a bigger buffer
##          case ERROR_INSUFFICIENT_BUFFER:
##          delete [] lpCacheEntry;
##          lpCacheEntry = (LPINTERNET_CACHE_ENTRY_INFO)
##          new char[dwEntrySize];
##          lpCacheEntry->dwStructSize = dwEntrySize;
##          dwTrySize = dwEntrySize;
##          BOOL bSuccess;
##          if (hCacheDir == NULL)
##          bSuccess = (hCacheDir = FindFirstUrlCacheEntry(NULL, lpCacheEntry, &dwTrySize)) != NULL;
##          else bSuccess = FindNextUrlCacheEntry(hCacheDir, lpCacheEntry, &dwTrySize);
##          if (bSuccess) dwError = ERROR_SUCCESS;
##          else { dwError = GetLastError(); dwEntrySize = dwTrySize; // use new size returned } break;
##          // we are done
##          case ERROR_NO_MORE_ITEMS:
##          bDone = TRUE; bResult = TRUE;
##          break; // we have got an entry case ERROR_SUCCESS:
##          // donot delete cookie entry
##if (!(lpCacheEntry->CacheEntryType & COOKIE_CACHE_ENTRY))
##DeleteUrlCacheEntry(lpCacheEntry->lpszSourceUrlName);
##// get ready for next entry dwTrySize = dwEntrySize;
##if (FindNextUrlCacheEntry(hCacheDir, lpCacheEntry, &dwTrySize))
##dwError = ERROR_SUCCESS; else { dwError = GetLastError(); dwEntrySize = dwTrySize; // use new size returned } break; // unknown error default: bDone = TRUE; break; } if (bDone) { delete [] lpCacheEntry; if (hCacheDir) FindCloseUrlCache(hCacheDir); } } while (!bDone); return bResult;}

##4、清除表单自动完成历史记录
##CString sKey;DWORD dwRet;
##    if (IsWindows2k() || IsWindowsNT())//先判断系统
##    {CString sBaseKey;
##     SECURITY_DESCRIPTOR NewSD;
##     BYTE* pOldSD;
##     PACL pDacl = NULL;
##     PSID pSid = NULL;
##     TCHAR szSid[256];
##     if (GetUserSid(&pSid))
##     {//get the hiden key name
##      GetSidString(pSid, szSid);
##      sKey = _T("Software\\Microsoft\\Protected Storage System Provider\\");
##      sKey += szSid;//get old SDsBaseKey = sKey;
##      GetOldSD(HKEY_CURRENT_USER, sBaseKey, &pOldSD);//set new SD and then clear
##      if (CreateNewSD(pSid, &NewSD, &pDacl))
##      {RegSetPrivilege(HKEY_CURRENT_USER, sKey, &NewSD, FALSE);
##       sKey += _T("\\Data");
##       RegSetPrivilege(HKEY_CURRENT_USER, sKey, &NewSD, FALSE);
##       sKey += _T("\\e161255a-37c3-11d2-bcaa-00c04fd929db");
##       RegSetPrivilege(HKEY_CURRENT_USER, sKey, &NewSD, TRUE);
##       dwRet = SHDeleteKey(HKEY_CURRENT_USER, sKey);}
##      if (pDacl != NULL)HeapFree(GetProcessHeap(), 0, pDacl);//restore old SD
##      if (pOldSD)
##      {RegSetPrivilege(HKEY_CURRENT_USER, sBaseKey, (SECURITY_DESCRIPTOR*)pOldSD, FALSE);delete pOldSD;}}
##     if (pSid)HeapFree(GetProcessHeap(), 0, pSid);}//win9x
##    DWORD dwSize = MAX_PATH;
##    TCHAR szUserName[MAX_PATH];GetUserName(szUserName, &dwSize);
##    sKey = _T("Software\\Microsoft\\Protected Storage System Provider\\");
##    sKey += szUserName;sKey += _T("\\Data\\e161255a-37c3-11d2-bcaa-00c04fd929db");
##    dwRet = SHDeleteKey(HKEY_LOCAL_MACHINE, sKey);


    # 浏览器地址栏历史地址的清除
    # SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Internet Explorer\\TypedURLs"))

    # 清除自动密码历史记录
    # SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Internet Explorer\\IntelliForms"));

    # 清收藏夹中的内容
    # SHGetSpecialFolderPath(NULL, szPath, CSIDL_FAVORITES, FALSE)

    # 清RAS自动拨号历史记录
    # SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\RAS Autodial\\Addresses"))

    # 清系统临时文件夹
    # GetTempPath(MAX_PATH, szPath)

    # 清空回收站
    # SHEmptyRecycleBin(NULL, NULL, SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND);

    # 清除"运行"中的自动匹配历史记录
    # SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU"));

    # 清"文档"中的历史记录
    # TCHAR szPath[MAX_PATH];if (SHGetSpecialFolderPath(NULL, szPath, CSIDL_RECENT, FALSE)){ EmptyDirectory(szPath);}
    # SHDeleteKey(HKEY_CURRENT_USER,_T("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs"));
    

##12、清除上次登陆用户记录
##
##SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"), _T("DefaultUserName"));SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"), _T("AltDefaultUserName"));SHDeleteValue(HKEY_LOCAL_MACHINE, _T("Software\\Microsoft\\Windows\\CurrentVersion\\Winlogon"), _T("DefaultUserName"));
##13、清除"查找文件"自动匹配历史记录
##
##SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Doc Find Spec MRU"));SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Internet Explorer\\Explorer Bars\\{C4EE31F3-4768-11D2-BE5C-00A0C9A83DA1}\\ContainingTextMRU"));SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Internet Explorer\\Explorer Bars\\{C4EE31F3-4768-11D2-BE5C-00A0C9A83DA1}\\FilesNamedMRU"));
##14、清除"查找计算机"自动匹配历史记录
##SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FindComputerMRU"));SHDeleteKey(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Internet Explorer\\Explorer Bars\\{C4EE31F3-4768-11D2-BE5C-00A0C9A83DA1}\\ComputerNameMRU"));
##15、清除网络联接历史记录
##TCHAR szPath[MAX_PATH];if (SHGetSpecialFolderPath(NULL, szPath, CSIDL_NETHOOD, FALSE)){ //得到目录，并清空 EmptyDirectory(szPath);}
##16、清远程登录历史记录
##CString sKey;for (int i=1; i<=8; i++){ sKey.Format(_T("Machine%d"), i); SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Telnet"), sKey); sKey.Format(_T("Service%d"), i); SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Telnet"), sKey); sKey.Format(_T("TermType%d"), i); SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Telnet"), sKey);}SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Telnet"), _T("LastMachine"));SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Telnet"), _T("LastService"));SHDeleteValue(HKEY_CURRENT_USER, _T("Software\\Microsoft\\Telnet"), _T("LastTermType"));
##17、清浏览网址历史记录
##下面这个函数可以用于清除网址历史记录
##
###include "SHLGUID.H"HRESULT ClearHistory() {HRESULT hr;CoInitialize(NULL);{ IUrlHistoryStg2* pUrlHistoryStg2 = NULL; hr= CoCreateInstance(CLSID_CUrlHistory,NULL,1, IID_IUrlHistoryStg2,(void**)&pUrlHistoryStg2); if (SUCCEEDED(hr)) { hr = pUrlHistoryStg2->ClearHistory(); pUrlHistoryStg2->Release(); }}CoUninitialize(); return hr;}
##
##// 如果上面代码不能清
##// 则有下面的，不完美，但能工作.
##TCHAR szPath[MAX_PATH];GetWindowsDirectory(szPath, MAX_PATH);_tcscat(szPath, _T("\\History"));EmptyDirectory(szPath, FALSE, TRUE); if (SHGetSpecialFolderPath(NULL, szPath, CSIDL_HISTORY, FALSE)){ EmptyDirectory(szPath, FALSE, TRUE);}


##    test_special_path()
##    import win32api
##    pathInReg='Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
##    key=win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,pathInReg,0,win32con.KEY_ALL_ACCESS)
##
##    value,enableType = win32api.RegQueryValueEx(key,'Cookies')
##    print "value: ", value
##    print "enableType: ", enableType
##    value,enableType = win32api.RegQueryValueEx(key,'Cache')
##    print "value: ", value
##    print "enableType: ", enableType
##
##    win32api.RegCloseKey(key)

