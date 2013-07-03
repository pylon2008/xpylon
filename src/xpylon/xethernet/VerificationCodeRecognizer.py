from ctypes import *

class VerificationCodeRecognizer(object):
    def __init__(self, userName, password):
        self.UUY = windll.LoadLibrary('UUWiseHelper')
        self.userName = userName
        self.password = password
        self.softInfoResult = 0
        self.userID = 0
        self.codeID = 0

    def getScore(self):
        getScore = self.UUY.uu_getScoreW
        user = c_wchar_p(self.userName)
        passwd = c_wchar_p(self.password)
        return getScore(user, passwd)

    def login(self):
        setSoftInfo = self.UUY.uu_setSoftInfoW
        login = self.UUY.uu_loginW
        
        s_id = c_int(91219)
        s_key = c_wchar_p('b6ef521449e2456fae07be997572f6b6')
        self.softInfoResult = setSoftInfo(s_id, s_key)
        print "softInfoResult: ", self.softInfoResult

        user = c_wchar_p(self.userName)
        passwd = c_wchar_p(self.password)
        self.userID = login(user, passwd)
        print "userID: ", self.userID
        print "getScore: ", self.getScore()

    def getCodeFromImagePath(self, imgPath, codeType):
        recognizeByCodeTypeAndPath = self.UUY.uu_recognizeByCodeTypeAndPathW
        result=c_wchar_p("")
        self.codeID = recognizeByCodeTypeAndPath(c_wchar_p(imgPath),c_int(codeType),result)
        if self.codeID<=0:
            #self.UUY.uu_reportError(self.codeID)
            return ""
        
        codeStr = result.value.decode('ascii')
        return codeStr

    def reportError(self):
        return self.UUY.uu_reportError(self.codeID)

    
