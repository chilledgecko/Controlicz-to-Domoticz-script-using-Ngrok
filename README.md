# Controlicz to Domoticz script using Ngrok

Definitions

Domoticz - a home automation software application (www.domoticz.com)

Controlicz - a cloud based service to connect Amazon Alexa or Google Home to Domoticz (www.controlicz.com)

Ngrok - a cloud based tunneling service that connects a local PC with a named URL. (www.ngrok.com)


In order for Controlicz to connect to the user local instance of Domoticz a port needs to be opened at the local firewall to allow a connection from Conrtolicz to the Domoticz web front end.
This requires both the open port as well as a DDNS type url to be configured to map the local IP address to a named URL that Controlicz can use.
The use of ngrok negates both the port opening and the requirement for a dynamic DNS service, enhancing security by reducing the public IP footprint and so reducing the risk from random port scans.
However, if the ngrok url is guessed then the access is again available. Don't be too complacent.
The random ngrok url is in the format of **{four octets}.ngrok.io** e.g. https://86017ff7.ngrok.io 

This script and associated ngrok local service automates the monitoring of ngrok for availability and updating of the current ngrok tunnel url as and when it changes.


## Operation
Ngrok is run as a continually running system service which is monitored each time the Python script is run.
The ngrok service is configured to restart on failure so should be stable.

Cron is used to run the Python script at preset intervals. Five minutes is the default but can be changed.

The script is very low in resource requirements so will not have much impact. 

The script will monitor the availability of ngrok and obtain the current ngrok url. 
If the ngrok url has changed the script will log on to the controlicz.com web site using your controlicz details and update the registered ngrok url to allow controlicz to continue to connect to your Domoticz instance and continue service between your Alexa/Google voice commands and Domoticz.

The ngrok url only changes if the service fails/stops so the url should not change that often. Only a local machine reboot or a ngrok cloud services reset are expected to cause a change of url. So once the ngrok url has been updated the script should just be running as a monitor.

There is a configurable option to send an email if an error situation is encountered to allow you to investigate ASAP.

![Basic operation](https://github.com/chilledgecko/Controlicz-to-Domoticz-script-using-Ngrok/blob/master/controliczDomoticz.png)

## Steps required

1. Install ngrok
2. Run ngrok as a service
3. Configure controliczUpdate.py
4. Configure cron to run controliczUpdate.py

## Assumptions
 - ngrok is installed to  **/opt/ngrok**
 - controliczUpdate.py is installed to **/opt/controlicz**
 - local installation account is your standard user account, elevated privileges are not required except when setting up the ngrok service, at which point sudo is used.  
 
---
---

## Install ngrok
 
Go to https://ngrok.com/ create a free account and sign in

Go to https://ngrok.com/download and download the ngrok client for your target machine

unzip ngrok client to /opt/ngrok

Go to https://dashboard.ngrok.com/auth and copy your Tunnel Authtoken

On your local machine return to /opt/ngrok and run   **./ngrok authtoken <YOUR_AUTH_TOKEN>**

Copy the created ngrok.yml to /opt/ngrok   **cp ~/.ngrok2/ngrok.yml /opt/ngrok**

Edit /opt/ngrok/ngrok.yml   **nano /opt/ngrok/ngrok.yml** and add the following lines below the   **authtoken: xxxx** line

keep the indenting;
```
region: eu
web_addr: 0.0.0.0:4040
  tunnels:
    domoticz-http:
      addr: 8080
      proto: http
```

---
## Run ngrok as a service 

Download the ngrok.service file and copy to /etc/systemd/system

If ngrok is installed in /opt/ngrok no changes are required, if ngrok is installed elsewhere edit the path in **ExecStart=**

Start the service  by running   **sudo systemctl start ngrok**

Check it is running ok by running   **sudo systemctl status ngrok**

Enable ngrok service for automatic startup by running   **sudo systemctl enable ngrok**

ngrok will now always be running unless there is an issue.

You can web browse to http://localhost:4040 to view the local ngrok web page to further confirm ngrok is running

You can also browse to https://dashboard.ngrok.com/status to view your active tunnels


---
## Configure controliczUpdate.py 

Download the controliczUpdate.py file and copy to /opt/controlicz

There are a number of configurable options, only the Controlicz user details need to be changed for the script to work.

If you wish to make changes this is a list of what is available;


```
logdirectory =        "/opt/controlicz/"		  # location of this script
logfile =             logdirectory + "controlicz.log"     # all updates / issues will be seen here
statusfile =          logdirectory + "status.log"         # holds the current value of the ngrok url

#Email Details
emailOK =             "false"                             # set false if no email notification required, 
                                                          # and true if notification is required
mailServer =          "smtp.gmail.com"			  # Mail server address
mailServerPort =      "587"				  # Mail Server Port
fromEmail =           "someValidEmail@gmail.com"	  # Sending email address
fromEmailPwd =        "someValidEmailPassword"		  # Sending email password
toEmail =             "LetMeKnow@gmail.com"		  # Recipient email address

#Controlicz Details
Controlicz_username = "ControliczUserName"		  # Controlicz Username	*** Needs valid user name
Controlicz_pwd =      "ControliczPassword"		  # Controlicz Password	*** Needs valid password
ControliczURL =       "https://controlicz.com/hostname"	  # Only change if required by Controlicz

#ngrok local URL
localURL =            "http://localhost:4040/api/tunnels" # Local ngrok webpage, used to check availability
```
If you wish to have email notification of issues change **emailOK = "true"** and add the email details, gmail is preconfigured.

You must make the script executable before it can run so execute   **chmod +x /opt/controlicz/controliczUpdate.py**


---
## Configure cron to run controliczUpdate.py

Configure cron to run the script every 5 minutes (or whatever you require) 

Run   **crontab -e**

At the bottom of the cron file add the following;

***/5 * * * * /opt/controlicz/controliczUpdate.py**

hit 'control o' to write out the updated file

hit 'control x' to exit crontab -e




Either let cron run the script or manually run   **/opt/controlicz/controliczUpdate.py**

You should see two new files in the /opt/controlicz directory controlicz.log and status.log

View the files using   **nano controlicz.log** and   **nano status.log** respectively.

controlicz.log should indicate that there was a new ngrok url and an update to controlicz has taken place.

status.log should hold the latest ngrok url as well as the last state

You can confirm the named ngrok url matches what is indicated on the local and ngrok web sites.


