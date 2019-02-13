#!/usr/bin/python3

#
#
# Run this script as a cron job (example is every 5 mins)
# crontab -e 
# */5 * * * * /opt/controlicz/controliczUpdate.py
#
# Note update.py must be exacutable 
# chmod +x /opt/controlicz/controliczUpdate.py
#
#
# Script assumes the working directory is /opt/controlicz 
# change variable 'logdirectory' if different 
#
#


#System Variables

logdirectory =          "/opt/controlicz/"						# location of this script
logfile =               logdirectory + "controlicz.log"     	# all updates / issues will be seen here
statusfile =            logdirectory + "status.log"         	# holds the current value of the ngrok url
#Email Details
emailOK =               "false"                              	# set false if no email notification required, true if notification is required
mailServer =            "smtp.gmail.com"						# Mail server address
mailServerPort =        "587"									# Mail Server Port
fromEmail =             "someValidEmail@gmail.com"				# Sending email address
fromEmailPwd =          "someValidEmailPassword"				# Sending email password
toEmail =               "LetMeKnow@gmail.com"					# Recipient email address
#Controlicz Details
Controlicz_username =   "ControliczUserName"					# Controlicz Username  			*** Needs valid user name
Controlicz_pwd =        "ControliczPassword"					# Controlicz Password  			*** Needs valid password
ControliczURL =         "https://controlicz.com/hostname"		# Only change if required by Controlicz
#ngrok local URL
localURL =              'http://localhost:4040/api/tunnels'		# Local ngrok webpage, used to check availability


##### ---- No changes beyond here ---- #####

import requests 
import json
import time
import smtplib



# My functions
def getTime(): #returns current time in day-month-year hour:minute:second format
    ts = time.gmtime()
    currentTime = time.strftime("%d-%b-%Y %H:%M:%S", ts)
    return currentTime

def writeLog(logdata): #appends input [logdata] to a local file [logfile] complete with timestamp
    f = open(logfile, "a")
    f.write(getTime() + "   " + logdata + "\n")
    f.close() 
    return

def storeData(url, status): #overwrites input [url,status] to a local file [statusfile]
    f = open(statusfile, "w")
    f.write(url + "\n" + status)
    f.close() 
    return

def readData(): #reads [url,status] from a local file [statusfile]
    try:
        f = open(statusfile, "r")
        url = (f.readline().rstrip())
        status = f.readline()
        f.close() 
    except FileNotFoundError: #first time run - no previous file writes
        url = "dummy.url"
        status = "true"
        f = open(statusfile, "w")
        f.write(url + "\n" + status)
        f.close() 
    return url, status

def sendEmail(message):
    if emailOK == "true":
        server = smtplib.SMTP(mailServer, mailServerPort)
        server.starttls()
        server.login(fromEmail, fromEmailPwd)
        server.sendmail(fromEmail, toEmail, message)
        server.quit()
        writeLog ("Sent email with message - " + message)
    else:
        writeLog("Email not selected. No email sent.")

    exit()
    return # script stopped

def getNgrokUrl(): # Gets the ngrok url from the local api
    res = requests.get(localURL)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    rawURL = res_json["tunnels"][1]["public_url"] # note - can be either http or https as ngrok json data changes sequence randomly
    if "https" not in rawURL: # returned the http: address - not what we want
        finalURL = rawURL[:4] + 's' + rawURL[4:] # stick an 's' in the string after 'http'
    else:
        finalURL = rawURL
    return finalURL

def checkNgrokWeb(): # Checks if ngrok is running using the local api
    alive = "false"
    try:
        r = requests.get(localURL,timeout=3) # connect to local wabpage, set time limit for response
        r.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # timeout or unexpected response
        #print ("Down")
        writeLog("ngrok web page is DOWN at " + localURL + "  Run 'sudo systemctl start ngrok.service' to start")
        alive = "down"
    except requests.exceptions.HTTPError: # internal web error response (4xx, 5xx), it's up but not responding correctly
        writeLog("ngrok web page returned an exception when accessing " + localURL)
        alive = "unsure"
    else:
        alive = "true"
    return alive

def updateControlicz(newURL): # send new ngrok url to Controlicz
    writeLog ("Attempting to update controlicz URL to " + newURL)
    newURL = newURL.strip('https://')   # remove leading https:// before uploading as controlicz adds it
    postData = {'host': newURL}         # data to send
    headers = {'Content-Type': 'application/json'}
    try:
        r= requests.post(ControliczURL, data=json.dumps(postData), headers=headers, auth=(Controlicz_username, Controlicz_pwd))
        r.raise_for_status()
        writeLog("Controlicz status response = Code[" + str(r.status_code) + "] Text - '" + r.text + "'")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout): # timeout or unexpected response
        writeLog("Controlicz web page API is DOWN.")
    except requests.exceptions.HTTPError: # internal web error response, it's up but not responding correctly (4xx, 5xx errors)
        writeLog("Controlicz web page returned an exception when accessing " + ControliczURL)
    else:
        writeLog("URL " + ngrokurl + " has been updated at Controlicz.")
    return

## Here we go - Main code ##
ngrokExists = "false"
ngrokExists = checkNgrokWeb() # is ngrok running?
oldURL, oldstatus = readData() # read in the previous url and status from file

if ngrokExists == "unsure": #ngrok is up but gave an unexpected response
    i = 0
    while i < 5: 
        i += 1  
        time.sleep(5) # wait 5 seconds for things to settle
        if ngrokExists != "unsure": # something has changed
            continue 
        else: # still not responding correctly
            if i == 5:        
                writeLog("ngrok is not responding correctly, quiting ")
                sendEmail("ngrok is up but the local web page is not responding correctly")            

if ngrokExists == "down": #ngrok is down, no response from web server
    writeLog("ngrok service is not running, quiting ")
    sendEmail("WARNING - ngrok service is not running. Please restart it. [sudo systemctl start ngrok.service]")
        
if ngrokExists == "true": #ngrok is up
    ngrokurl = getNgrokUrl() # get the ngrok working URL
    if ngrokurl != oldURL: # different url to what we had, we need to update controlicz
        writeLog("Old URL " + oldURL + " does not match latest URL " + ngrokurl + " an update is needed")
        updateControlicz(ngrokurl)
        storeData(ngrokurl, ngrokExists) # write out to local file for later reference


    



