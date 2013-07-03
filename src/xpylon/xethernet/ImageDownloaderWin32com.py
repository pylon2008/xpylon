# coding=GBK
import win32com.client,time,win32inet,win32file,os
import win32com.client,pythoncom
class ImgDownloader:
    def __init__(self,urls,dir):
        self.__dir=dir
        self.__urls = urls
        self.__ie=win32com.client.Dispatch('InternetExplorer.Application')
        print self.__ie
        self.__ie.Visible = 1   

    def __wait__(self):
        while self.__ie.Busy:
            time.sleep(1)

    def start(self):
        for url in self.__urls:
            try:
                self.__ie.Navigate(url)
                self.__wait__()  
                cachInfo=win32inet.GetUrlCacheEntryInfo(url)
                if cachInfo:
                    pathSrc=cachInfo['LocalFileName']
                    srcPathInfo = pathSrc.split('\\')
                    srcName = srcPathInfo[-1]
                    pathinfo=url.split('/')
                    filename=pathinfo[-1]
                    if filename[-4:-1] != srcName[-4:-1]:
                        filename = srcName
                    win32file.CopyFile(pathSrc,os.path.join(self.__dir,filename),True)
            except:
                print 'Get Image Error: ', url
                a = 0

    def close(self):
        self.__ie.Quit()

if __name__=='__main__':
##    urls = ['http://images.sohu.com/bill/s2013/MKT/wuxian/0129/14280-3.jpg',\
##            'http://imgstatic.baidu.com/img/image/wantu/detail/mopai195x100.jpg',\
##            'http://imgstatic.baidu.com/img/image/zhuanti/ad_model2.jpg'\
##            'http://captcha.qq.com/getimage?aid=1007901&amp;r=0.02795622928603747']
    urls = ['http://captcha.qq.com/getimage?aid=1007901&amp;r=0.02795622928603747']
    d=ImgDownloader(urls,'c:\\temp\\')
    d.start()
    d.close()
