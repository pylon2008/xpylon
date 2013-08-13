#coding=GBK

import wmi 
import os 
import sys 
import platform 
import time 
import chardet
import socket
from xpylon.xutil import xstring

   
#sys.getdefaultencoding()
def getDiskInfo():
    diskstr = u""
    try:
        c = wmi.WMI()    
        #��ȡӲ�̷��� 
        for physical_disk in c.Win32_DiskDrive (): 
            for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"): 
                for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"):
                    diskstr = diskstr \
                           + xstring.str2unicode(physical_disk.Caption) + u"��" \
                           + xstring.str2unicode(partition.Caption) + u"��" \
                           + xstring.str2unicode(logical_disk.Caption) + u"\r\n"
        #��ȡӲ��ʹ�ðٷ���� 
        for disk in c.Win32_LogicalDisk (DriveType=3):
            freeper = "%0.2f%% free" % (100.0 * long (disk.FreeSpace) / long (disk.Size))
            diskstr = diskstr \
                   + xstring.str2unicode(disk.Caption) \
                   + xstring.str2unicode(str(long (disk.FreeSpace))) + u"��" \
                   + xstring.str2unicode(str(long (disk.Size))) \
                   + u"(" + xstring.str2unicode(freeper) + u")" + u"\r\n"
            
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        diskstr = u""
    return diskstr

def getPlatform():
    platformStr = u""
    try:
        platformStr = platform.platform()
        platformStr = xstring.str2unicode(platformStr)
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        platformStr = u""
    return platformStr

def getEnableMacs():
    Macs = u""
    try:
        c = wmi.WMI()    
        #��ȡMAC��IP��ַ 
        for interface in c.Win32_NetworkAdapterConfiguration (IPEnabled=1): 
            mac = interface.MACAddress
            mac = xstring.str2unicode(mac)
            Macs = Macs + mac + u"-"
        Macs = Macs[0:-1]
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        Macs = u""
    return Macs

def getCpuName():
    cpu = u""
    try:
        c = wmi.WMI()        
        #CPU���ͺ��ڴ� 
        for processor in c.Win32_Processor(): 
            mac = xstring.str2unicode(processor.Name)
            cpu = cpu + mac + u"-"
        cpu = cpu[0:-1]
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        cpu = u""
    return cpu

def getCpuInfo():
    cpu = u""
    try:
        c = wmi.WMI()        
        #CPU���ͺ��ڴ� 
        for processor in c.Win32_Processor(): 
            mac = xstring.str2unicode(processor.Name)
            cpu = cpu + mac + u"-"
        cpu = cpu[0:-1]
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        cpu = u""
    return cpu

def getMemInfo():
    mem = u""
    try:
        c = wmi.WMI()        
        #CPU���ͺ��ڴ� 
        for Memory in c.Win32_PhysicalMemory():
            meminfo = "%.fMB" %(int(Memory.Capacity)/1048576)
            meminfo = xstring.str2unicode(meminfo)
            mem = mem + meminfo + u"-"
        mem = mem[0:-1]
    except:
        traceStr = traceback.format_exc()
        logging.error(traceStr)
        mem = u""
    return mem

def getHostName():
    return socket.gethostname()

def main(): 
    #sys_version() 
    #cpu_mem() 
    #disk() 
    #network() 
    #cpu_use()
    #getSelfInfo()
    #print getDiskInfo()
    #print getCpuInfo()

    aa = "������"
    bb = xstring.str2unicode(aa)
 
if __name__ == '__main__': 
    main() 
##    print "platform.system(): ", platform.system() 
##    print "platform.release(): ", platform.release() 
##    print "platform.version(): ", platform.version() 
##    print "platform.platform(): ", platform.platform() 
##    print "platform.machine(): ", platform.machine()












###############################################################################################################
##def disk(): 
##    c = wmi.WMI()    
##    #��ȡӲ�̷��� 
##    for physical_disk in c.Win32_DiskDrive (): 
##        for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"): 
##            for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"): 
##                print physical_disk.Caption.encode("GBK"), partition.Caption.encode("GBK"), logical_disk.Caption 
##    
##    #��ȡӲ��ʹ�ðٷ���� 
##    for disk in c.Win32_LogicalDisk (DriveType=3): 
##        print disk.Caption, "%0.2f%% free" % (100.0 * long (disk.FreeSpace) / long (disk.Size)) 
##
##
##def cpu_mem(): 
##    c = wmi.WMI()        
##    #CPU���ͺ��ڴ� 
##    for processor in c.Win32_Processor(): 
##        print "Processor ID: %s" % processor.DeviceID
##        print "Processor Manufacturer: %s" % processor.Manufacturer
##        print "Processor PNPDeviceID: %s" % processor.PNPDeviceID 
##        print "processor.InstallDate: ", processor.InstallDate
##        print "Process Name: %s" % processor.Name.strip() 
##    for Memory in c.Win32_PhysicalMemory(): 
##        print "Memory Capacity: %.fMB" %(int(Memory.Capacity)/1048576)
##        print "Memory.Caption: ", Memory.Caption
##        print "Memory.CreationClassName: ", Memory.CreationClassName
##        print "Memory.Description: ", Memory.Description
##        print "Memory.DeviceLocator: ", Memory.DeviceLocator
##        print "Memory.Manufacturer: ", Memory.Manufacturer
##        print "Memory.MemoryType: ", Memory.MemoryType
##        print "Memory.OtherIdentifyingInfo: ", Memory.OtherIdentifyingInfo
##        print "Memory.PartNumber: ", Memory.PartNumber
##        print "Memory.SerialNumber: ", Memory.SerialNumber
##        print "Memory.SKU: ", Memory.SKU
##        print "Memory.Version: ", Memory.Version
##
##def sys_version():  
##    c = wmi.WMI() 
##    #��ȡ����ϵͳ�汾 
##    for mysys in c.Win32_OperatingSystem():
##        print "Version:%s" % mysys.Caption.encode("GBK"),"Vernum:%s" % mysys.BuildNumber
##        print mysys.keys
##        #print  mysys.OSArchitecture
##        print mysys.NumberOfProcesses #��ǰϵͳ���еĽ�������
## 
##def cpu_use(): 
##    #5sȡһ��CPU��ʹ���� 
##    c = wmi.WMI() 
##    while True: 
##        for cpu in c.Win32_Processor(): 
##            timestamp = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime()) 
##            print '%s | Utilization: %s: %d %%' % (timestamp, cpu.DeviceID, cpu.LoadPercentage) 
##            time.sleep(5)    
##              
## 
##def network(): 
##    c = wmi.WMI()    
##    #��ȡMAC��IP��ַ 
##    for interface in c.Win32_NetworkAdapterConfiguration (IPEnabled=1): 
##        print "MAC: %s" % interface.MACAddress 
##    for ip_address in interface.IPAddress: 
##        print "ip_add: %s" % ip_address 
##    print 
##    
##    #��ȡ�����������λ�� 
##    for s in c.Win32_StartupCommand (): 
##        print "[%s] %s <%s>" % (s.Location.encode("GBK"), s.Caption.encode("GBK"), s.Command.encode("UTF8"))  
##    
##    
##    #��ȡ��ǰ���еĽ��� 
##    for process in c.Win32_Process (): 
##        print process.ProcessId, process.Name 

