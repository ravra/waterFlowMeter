#!/usr/bin/env python

# Simple script to monitor a cheap water flow sensor attached to gpio 4. The script counts pulses over an interval and then
# checks if the count exceeds a limit. If it does, it sends an email.
# This script uses some of the pigpio code for doing the counts.
# ravraid 1/31/19

import time, datetime
from smtplib import SMTP_SSL as SMTP
from email.MIMEText import MIMEText
import pigpio

intervalTime  = 15  # in seconds
triggerMin    = 50  # limit in pulse counts - adjust to detect small leaks

SMTPserver    = 'smtp.gmail.com'

sender        = 'FOO@BLAH.COM'
destination   = ['FOO@BLAH.COM']
USERNAME      = "FOO@BLAH.COM"
PASSWORD      = "MYPASSWORD"

subject       = ""
waterFlow     = 0
flowGpio      = 4

text_subtype = 'plain'

def sendMail(content):
    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject']=       subject
        msg['From']   = sender # some SMTP servers will do this automatically, not all

        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.close()

    except Exception, exc:
        sys.exit( "mail failed; %s" % str(exc) ) # give a error message

pi = pigpio.pi()

pi.set_mode(flowGpio, pigpio.INPUT)
pi.set_pull_up_down(flowGpio, pigpio.PUD_DOWN)

flowCallback = pi.callback(flowGpio, pigpio.FALLING_EDGE)

old_count   = 0
triggerTime = datetime.datetime.today() - datetime.timedelta(weeks=1)  # Initialize it to more than a day ago

while True:

   time.sleep(intervalTime)

   count = flowCallback.tally()
   waterFlow = count - old_count
   #print("counted {} pulses".format(waterFlow))
   yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
   # Only send at most one message per day so check if the last trigger was more than 24hours ago
   if ( (waterFlow > triggerMin) & (triggerTime < yesterday) ):
       triggerTime = datetime.datetime.today()
       print "Note: Sending mail.."
       subject= "Waterflow over limit: " + str(waterFlow)
       message= "Limit is: " + str(triggerMin) + " and water flow is: " + str(waterFlow) + '\n'
       message = message + '\n\n' + "Sent from rpiZero1 waterFlowMeter.py" + '\n'
       sendMail(message)
   old_count = count

pi.stop()
