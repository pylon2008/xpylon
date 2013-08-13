#coding=GBK

import wmi, datetime, os, platform, chardet, socket, logging, traceback, time
from xpylon.xutil import xstring
from xpylon.xutil import SysInfo
from email.mime.text import MIMEText
from email.header import Header   
import smtplib, poplib, email

def getActiveKey():
    element = u"@@@"
    hostname = SysInfo.getHostName()
    platformStr = SysInfo.getPlatform()
    macs = SysInfo.getEnableMacs()
    cpu = SysInfo.getCpuName()
    strSelfInfo = element + hostname + element + platformStr + element + macs + element + cpu + element
    return strSelfInfo

def doActive(items):
    try:
        emailaddr = u"@sina.cn"
        emailpwd = u""
        sender =  emailaddr
        receiver = emailaddr
        subject = u"[tbsearch-active]"
        smtpserver = u"smtp.sina.com"
        username = emailaddr
        password = emailpwd

        emailcontent = items

        msg = MIMEText(emailcontent,'plain','utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = receiver
         
        smtp = smtplib.SMTP() 
        smtp.connect('smtp.sina.com') 
        smtp.login(username, password) 
        smtp.sendmail(sender, receiver, msg.as_string()) 
        smtp.quit()
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
    
def requestActive(key):
    try:
        emailaddr = u"@sina.cn"
        emailpwd = u""
        thistime = datetime.datetime.now()
        sender =  emailaddr
        receiver = emailaddr
        subject = xstring.str2unicode(str(thistime)) + u"[" + xstring.str2unicode(SysInfo.getHostName()) + u"]"
        smtpserver = u"smtp.sina.com"
        username = emailaddr
        password = emailpwd

        emailcontent = key
        emailcontent += u"\r\n\r\n"
        emailcontent = emailcontent + u"\r\n" \
                       + u"time：" + xstring.str2unicode(str(thistime)) + u"\r\n" \
                       + u"hostname：" + xstring.str2unicode(SysInfo.getHostName()) + u"\r\n" \
                       + u"platform：" + xstring.str2unicode(SysInfo.getPlatform()) + u"\r\n" \
                       + u"mac：" + xstring.str2unicode(SysInfo.getEnableMacs()) + u"\r\n" \
                       + u"cpu：" + xstring.str2unicode(SysInfo.getCpuInfo()) + u"\r\n" \
                       + u"mem：" + xstring.str2unicode(SysInfo.getMemInfo()) + u"\r\n" \
                       + u"disk：" + xstring.str2unicode(SysInfo.getDiskInfo()) + u"\r\n" \

        msg = MIMEText(emailcontent,'plain','utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = receiver
         
        smtp = smtplib.SMTP() 
        smtp.connect('smtp.sina.com') 
        smtp.login(username, password) 
        smtp.sendmail(sender, receiver, msg.as_string()) 
        smtp.quit()
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)

def getActiveMailContent(mail):
    content = u""
    try:
        if mail.is_multipart():
            content = u""
            raise TypeError, u"The active is edit by human"
        else:
            contenttype = mail.get_content_charset()
            contentencoding = email.Header.decode_header(mail['Content-Transfer-Encoding'])[0][0]
            contentencoding = xstring.str2unicode(contentencoding)
            payload = mail.get_payload(decode = contentencoding)
            if contenttype==None:
                content = xstring.str2unicode(payload) 
            else:
                try:
                    content = unicode(payload,contenttype)
                except UnicodeDecodeError:
                    content = u""
                    raise TypeError, u"The content type error"
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        content = u""
    return content

def getActiveValue(key, softname):
    value = None
    try:
        host = 'pop.sina.com'  
        username = u"@sina.cn"  
        password = u""  
          
        pop_conn = poplib.POP3(host)   
        pop_conn.user(username)   
        pop_conn.pass_(password)   

        mailCount,size = pop_conn.stat()
        realsubject = u"[" + softname + u"-active" +u"]"
        #Get messages from server:
        activemail = None
        for i in range(mailCount, 0, -1):
            msg = pop_conn.retr(i)
            msgstr = '\n'.join(msg[1])
            mail = email.message_from_string(msgstr)
            subject = email.Header.decode_header(mail['subject'])[0][0]
            if xstring.str2unicode(subject) == realsubject:
                activemail = mail
                break
        pop_conn.quit()

        if activemail != None:
            content = getActiveMailContent(activemail)
            items = content.split(u"\r\n")
            dic = {}
            for item in items:
                if item!=u"":
                    keyvalue = item.split(u"===>")
                    if len(keyvalue) == 2:
                        dic[keyvalue[0]] = keyvalue[1]
            value = dic[key]       
    except:
        value = None
        traceStr = traceback.format_exc()
        logging.error(traceStr)
    return value

def isActive(softname):
    isactive = False
    try:
        key = getActiveKey()
        value = getActiveValue(key, softname)
        if value != None:
            t = time.strptime(value, "%Y-%m-%d %X")
            d = datetime.datetime(* t[:6]) 
            dnow = datetime.datetime.now()
            deltaSec = (dnow-d).days
            if d >= dnow:
                isactive = True
    except:
        isactive = False
        traceStr = traceback.format_exc()
        logging.error(traceStr)
    if isactive==False:
        key = getActiveKey()
        requestActive(key)
    return isactive
   
def main_test():
##    key = getActiveKey()
##    requestActive(key)
##    items = key + u"===>2013-08-04 21:40:15\r\n"
##    doActive(items)
    print isActive(u"tbsearch")
    

if __name__ == '__main__': 
    main_test() 


