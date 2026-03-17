####=================####
#Author: Alex Leith, Duri Bradshaw
#Date: 2026-03-17
#Version: 0.0.3
#Purpose: Gets methods out of the main body. There is a custom 'processTriggers' method that needs to be removed for most people.
####=================####

import ftplib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE
from email import encoders
import globals
import zipfile
import glob

#Check for trigger files and if found, set up trigger. #CUSTOMISE THIS#
def processTriggers(downloadedFiles):

    unzipList = ['TasNetworks_LGAs.zip']

    #email message text.
    messageText = ''  
    
    if(len(downloadedFiles) == 0):
        globals.logging.info("No files downloaded, so no script triggers checked.")
        return ''
        
    for j in downloadedFiles:
        print('downloaded: ', j)
        #unzip list
        for o in unzipList:
            if(o == j):
                fullLocalFile = os.path.join(globals.localPath, j)
                unzipTo = fullLocalFile[0:-4]
                if not os.path.exists(unzipTo):
                    # Create the directory
                    os.makedirs(unzipTo)
                unzip(fullLocalFile, unzipTo)

    return messageText
    
#OTHER METHODS
##METHODS##

#sends an email with one subject, message and attachment
def sendEmail(emailFrom, emailTo, subject, message, attachment):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = emailFrom
    
    if(type(emailTo) == list):
        msg['To'] = COMMASPACE.join(emailTo)
    else:
        msg['To'] = emailTo
        emailTo = [emailTo]
    
    msg.attach(MIMEText(message))
    
    if(attachment != "0"):
        #attach the log file
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(globals.logFile,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(globals.logFile))
        msg.attach(part)
    
    s = smtplib.SMTP(globals.mailServer)
    s.sendmail(emailFrom, emailTo, msg.as_string())
    s.quit()
    
#takes input from the file listing from the ftp site and returns a list of file names (fn) and file sizes (fs)
def getAttributes(line):
    lineSplit = line.split(' ')
    lineSplit = [x for x in lineSplit if x != ""]
    
    #file size
    fs = lineSplit[4]
    fnList = lineSplit[8:]
    
    #file name
    fn = ""
    for i in fnList:
        fn = fn + i + " "
    fn = fn.strip()
    
    return fn,fs

def downloadFile(localFile, remoteFile, ftp):
    f = open(localFile,"wb")

    print("INFO: Downloading: "+remoteFile)
    try:
        ftp.retrbinary("RETR " + remoteFile, f.write)
        f.close()

        globals.downloadedFiles.append(remoteFile)
        globals.logging.info("Retrieved: " + remoteFile + " to: " + localFile)
        #globals.logging.info("Unzipping...")
        #unzip(localFile, globals.localPath)
    except Exception as e:
        globals.logging.error("Failed to retrieve: " + remoteFile + " to: " + localFile + " error was: " + str(e))
        f.close()

#unzip files
def unzip(zipFilePath, destDir):
    zfile = zipfile.ZipFile(zipFilePath)
    for name in zfile.namelist():
        (dirName, fileName) = os.path.split(name)
        if fileName == '':
            # directory
            newDir = destDir + '/' + dirName
            if not os.path.exists(newDir):
                os.mkdir(newDir)
        else:
            # file
            fd = open(destDir + '/' + name, 'wb')
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()
