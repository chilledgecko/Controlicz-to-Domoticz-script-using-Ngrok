# Controlicz to Domoticz script using Ngrok
Script to update Controlicz with current local Ngrok URL to allow access to the Domoticz web service without opening a web port on the local firewall.

This script package is specific for a Domoticz (domoticz.com) home automation system 
that is using Amazon Alexa or Google Home via controlicz.com for voice control.

It is using ngrok (ngrok.com) to run a tunnel from the Domoticz web service on the local machine 
to a named url from ngrok which controlicz then uses for access to Domoticz.

Using ngrok prevents the requirement for a port to be opened inbound at the local firewall, enhancing security.
However using the free use tier from ngrok the ngrok url changes each restart preventing a static address being used.


Steps required

1. Install ngrok
2. Run ngrok as a service
3. Configure controliczUpdate.py
4. Configure cron to run controliczUpdate.py

Assumptions
 - ngrok is installed to  /opt/ngrok
 - contrtoliczUpdate.py is installed to /opt/controlicz
 - local account is your standard user account, sudo is not required 



1.  ***** Install ngrok *****

Go to https://ngrok.com/ create an account and sign in

Go to https://ngrok.com/download and download the ngrok client for your target machine

unzip ngrok client to /opt/ngrok

Go to https://dashboard.ngrok.com/auth and copy your Tunnel Authtoken

On your local machine return to /opt/ngrok and run ./ngrok authtoken <YOUR_AUTH_TOKEN>

Copy the created ngrok.yml to /opt/ngrok cp ~/.ngrok2/ngrok.yml /opt/ngrok

Edit /opt/ngrok/ngrok.yml (nano /opt/ngrok/ngrok.yml) and add the following lines below the authtoken: xxxx line

keep the indenting;

	web_addr: 0.0.0.0:4040
	tunnels:
  		domoticz-http:
    	addr: 8080
    	proto: http



2. ***** Run ngrok as a service *****

Download the ngrok.service file and copy to /etc/systemd/system

If ngrok is installed in /opt/ngrok no changes are required, if ngrok is installed elsewhere edit the path in ExecStart=

Start the service  by running sudo systemctl start ngrok

Check it is running ok by running sudo systemctl status ngrok

Enable ngrok service for automatic startup by running sudo systemctl enable ngrok

ngrok will now always be running unless there is an issue.

You can web browse to localhost:4040 to view the local ngrok web page to further confirm ngrok is running

You can also browse to https://dashboard.ngrok.com/status to view your active tunnels



3. ***** Configure controliczUpdate.py *****

Download the controliczUpdate.py file and copy to /opt/controlicz

There are a number of configurable options, only the Controlicz user details need to be changed for the script to work.

If you wish to make changes this is a list of what is available;

logdirectory =          "/opt/controlicz/"						        # location of this script
logfile =               logdirectory + "controlicz.log"     	# all updates / issues will be seen here
statusfile =            logdirectory + "status.log"         	# holds the current value of the ngrok url

#Email Details
emailOK =               "false"                              	# set false if no email notification required, 
                                                              # and true if notification is required
mailServer =            "smtp.gmail.com"						          # Mail server address
mailServerPort =        "587"									                # Mail Server Port
fromEmail =             "someValidEmail@gmail.com"				    # Sending email address
fromEmailPwd =          "someValidEmailPassword"				      # Sending email password
toEmail =               "LetMeKnow@gmail.com"					        # Recipient email address

#Controlicz Details
Controlicz_username =   "ControliczUserName"					        # Controlicz Username  			*** Needs valid user name
Controlicz_pwd =        "ControliczPassword"					        # Controlicz Password  			*** Needs valid password
ControliczURL =         "https://controlicz.com/hostname"		  # Only change if required by Controlicz

#ngrok local URL
localURL =              'http://localhost:4040/api/tunnels'		# Local ngrok webpage, used to check availability

If you wish to have email notification of issues change emailOK = "true" and add the email details, gmail is preconfigured.

You must make the script executable before it can run so execute chmod +x /opt/controlicz/controliczUpdate.py



4. ***** Configure cron to run controliczUpdate.py *****

Configure cron to run the script every 5 minutes (or whatever you require) 

Run crontab -e

At the bottom of the cron file add the following;

*/5 * * * * /opt/controlicz/controliczUpdate.py

hit 'control o' to write out the updated file

hit 'control x' to exit crontab -e


Either let cron run the script or manually run /opt/controlicz/controliczUpdate.py

You should see two new files in the /opt/controlicz directory controlicz.log and status.log

View the files using nano controlicz.log and nano status.log respectively.

controlicz.log should indicate that there was a new ngrok url and an update to controlicz has taken place.

status.log should hold the latest ngrok url as well as the last state

You can confirm the named ngrok url matches what is indicated on the local and ngrok web sites.


