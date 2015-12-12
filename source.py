import time
import smtplib
import MySQLdb
import picamera
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import base64

DS18B20_1="/sys/bus/w1/devices/28-031462453fff/w1_slave"
DS18B20_2="/sys/bus/w1/devices/28-04146467c8ff/w1_slave"

print("Welcome to Wireless Temperature Monitoring System\n")
i=0
while i<3:
    first=open(DS18B20_1,"r")
    data1=first.read()
    first.close()

    second=open(DS18B20_2,"r")
    data2=second.read()
    second.close()

    (discard,sep,reading1)=data1.partition('t=')
    (discard,sep,reading2)=data2.partition('t=')

    t1=float(reading1)/1000
    t2=float(reading2)/1000

    r1=int(t1)
    r2=int(t2)

    print(" Inside Room Temp="+str(r1)+" *c")
    print(" Outside Room Temp="+str(r2)+" *c\n")

    if(r2>25):
        print 'capturing...'
        with picamera.PiCamera() as camera:
            camera.start_preview()
            time.sleep(3)
            camera.capture('image.jpg')
            camera.stop_preview()
        print "Done"   
        strFrom = 'reloadp52@gmail.com'
        strTo = 'vigneshp8080@gmail.com'
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'test message'
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText('This is the alternative plain text message.')
        msgAlternative.attach(msgText)
        msgText = MIMEText('<b>Inside room temperature is high</b>Check image<br><img src="cid:image1"><br>', 'html')
        msgAlternative.attach(msgText)
        fp = open('image.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
        u='reloadp52@gmail.com'
        p='mynameisvigneshP'
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        smtp.login(u,p)
        smtp.sendmail(strFrom, strTo, msgRoot.as_string())
        smtp.quit()
        time.sleep(2)
    i=i+1
db=MySQLdb.connect("localhost","monitor","pi","temps")
curs=db.cursor()
with db:
    curs.execute("Insert into tempdat values(CURRENT_DATE(),NOW(),'home',\""+str(r1)+"\",'28-031462453fff')")
    curs.execute("Insert into tempdat values(CURRENT_DATE(),NOW(),'home',\""+str(r2)+"\",'28-04146467c8ff')")
    
    print "Data committed"
    curs.execute("select *from tempdat");
    print"Wireless Temperature Monitoring Database System"
    print"\nDate            Time            Location            Temperature             SensorId"
    print"*******************************************************************************************"
    for reading in curs.fetchall():
        print str(reading[0])+"         "+str(reading[1])+"        "+str(reading[2])+"                  "+str(reading[3])+"              "+str(reading[4])
    print"*******************************************************************************************"
db.close()
