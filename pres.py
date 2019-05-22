# Libraries to intract with raspberry pi 
import sys
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
from RPLCD import CharLCD

# libraries to be imported for sending email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


GPIO.setwarnings(False)  	# Doesn't generate warnings
GPIO.setmode(GPIO.BOARD)	# Setting raspi GPIO to BOARD numbering

living_room_HT_PIN              = 2			# connected to GPIO 2 pin
room_1_HT_PIN                   = 3			# connected to GPIO 3 pin
room_2_HT_PIN                   = 4			# connected to GPIO 4 pin
PIR_sensor_PIN                  = 10		# connected to BOARD 10 pin
servo_room1_PIN                 = 29		# connected to BOARD 29 pin

GPIO.setup(servo_room1_PIN, GPIO.OUT)                   # setting Servo motor pin as output pin
GPIO.setup(PIR_sensor_PIN, GPIO.IN)                     # Read output from PIR motion sensor

# creating LCD function to display 
lcd = CharLCD(numbering_mode=GPIO.BOARD, cols=16, rows=2, pin_rs=40, pin_e=38, pins_data=[37, 35, 33, 31])

file = "/home/pi/Documents/codes/"  		# file location to a variable
prev_ext = "Empty"							

# checks PIR status
def pir_reading():
    time.sleep(2)
    PIR_Value = GPIO.input(PIR_sensor_PIN)
    if PIR_Value == 1:
        print('Turning ON Living Room')
        lcd.clear()
        lcd.cursor_pos = (0,0)
        lcd.write_string("Turning ON L R")
    else:
        print('Turning off LR')
        lcd.clear()
        lcd.cursor_pos = (0,0)
        lcd.write_string("Turning OFF L R")

# Turn the servo to desired position during ON condition
def servo_ON(PIN):
        p = GPIO.PWM(PIN, 50)
        print("Servo ON")
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string("Servo_room 1 ON")
        p.start(2.5)                        
        time.sleep(3)
        p.ChangeDutyCycle(12.5)
        p.stop()
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Window Open")
        print('Window Open')

# Turn the servo to desied position during OFF condition
def servo_OFF(PIN):
        p = GPIO.PWM(PIN, 50)
        print("Servo ON")
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string("Servo_room 1 ON")
        p.start(12.5)                     
        time.sleep(3)
        p.ChangeDutyCycle(2.5)
        p.stop()
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Window Close")
        print("Window Close")

# Main functionality starts
while True:

    print('________________')
    
    # Displays Welcoming title on LCD
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("HOME AUTOMATION & MONITORING SYS")
    time.sleep(5)


    pir_reading()			# reads PIR status

    # Humidity and Temperature Values
    humidity_LR, temperature_LR = Adafruit_DHT.read_retry(11,living_room_HT_PIN )
    humidity_R1, temperature_R1 = Adafruit_DHT.read_retry(11,room_1_HT_PIN )
    humidity_R2, temperature_R2 = Adafruit_DHT.read_retry(11,room_2_HT_PIN )

    # printing on to the terminal
    print("Living room \tHumidity: %d Temperature: %d "%(humidity_LR,temperature_LR))
    print("Room 1 \t\tHumidity: %d Temperature: %d "%(humidity_R1,temperature_R1))
    print("Room 2 \t\tHumidity: %d Temperature: %d "%(humidity_R2,temperature_R2))


    # Displays temp and humidity values on the LCD
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp_LR: %d C" % temperature_LR)
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Humidity_LR: %d%%" % humidity_LR)
    time.sleep(3)

    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp_R1: %d C" % temperature_R1)
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Humidity_R1: %d%%" % humidity_R1)
    time.sleep(3)

    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp_R2: %d C" % temperature_R2)
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Humidity_R2: %d%%" % humidity_R2)
    time.sleep(3)

    # Condition to actuate servo 
    if humidity_R1 >80:
        servo_ON(servo_room1_PIN)
    else:
        servo_OFF(servo_room1_PIN)


    # Code snippet for generating dynamic file names
    ext = 'Data'+time.strftime("%Y%m%d%H")
    file_name = file + ext+'.csv'

    # code to send email
    if prev_ext != ext:
        fromaddr = "from address"
        toaddr = "to address"

        # instance of MIMEMultipart
        msg = MIMEMultipart()

        # storing the senders email addres
        msg['From'] = fromaddr

        # storing the receivers email address
        msg['To'] = toaddr

        # storing the subject
        msg['Subject'] = "Home data"

        # string to store the body of the mail
        body = "Data"

        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # open the file to be sent
        filename = prev_ext + '.csv'
        attachment = open(file +filename, "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login(fromaddr, "password")

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, toaddr, text)

        # terminating the session
        s.quit()

    prev_ext = ext

    # saving data to file in csv file.
    print(file_name)
    with open(file_name, "a") as log:
        log.write("{0},{1},{2},{3}\n".format('Date','Area','Temperature C','Humidity %'))
        log.write("{0},{1},{2},{3}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),'L R',temperature_LR,humidity_LR))
        log.write("{0},{1},{2},{3}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),'R 1',temperature_R1,humidity_R1))
        log.write("{0},{1},{2},{3}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),'R 2',temperature_R2,humidity_R2))
        if humidity_R1>80:
            log.write("{0},{1},{2}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),'R 1 Servo','Window Open'))
        else:
            log.write("{0},{1},{2}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),'R 1 Servo','Window Close'))

        log.write("------------------------")

