# Oneday project from Jerry Jia for his daughter Hannah piano practice 
# v0.1 21/9/2018 - init with pitch detection and email function 
# v0.2 24/9/2018 - add print to file as record.csv, will add weekly summary later

import pyaudio
import wave
import numpy as np
from aubio import pitch
from aubio import source, notes
import time
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

CHUNK = 256
FORMAT = pyaudio.paInt16 #some other sound card may need pyaudio.paFloat32
DEVICE = 0 
CHANNELS = 1
RATE = 44100

# no need record sound, just for debug if need
#RECORD_SECONDS = 5
#WAVE_OUTPUT_FILENAME = "output.wav"

class Queue:
    def __init__(self):
        self.queue = []
        self.i = 0
    def enqueue(self,val):
        self.queue.insert(0,val)
    def dequeue(self):
        if self.is_empty():
            return None
        else:
            return self.queue.pop()
    def size(self):
        return len(self.queue)
    def is_empty(self):
        return self.size() == 0
    def avg(self,lon):
        return sum(self.queue)/lon
    def __str__(self):
        return str(self.queue)

def sendmail():
        host_server = 'smtp.qq.com'
        sender_qq = '18***' # change to your qq mail
        pwd = 'pwd***' # mail password
        sender_qq_mail = '18***@qq.com' # sending mail box
        toEmails = ["jia***@gmail.com"] # email reciver list
        mail_content = "One task done and sending summary: " + time.asctime(time.localtime(task_starttime)) + ", task=" + str(int(task_duration/60) + " min, " + "realplay=" + str(int(realplay_duration/60)) + " min."
        mail_title = 'Piano Practice Report'
        smtp = SMTP_SSL(host_server)
        smtp.set_debuglevel(0)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)
        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = ",".join(toEmails)
        smtp.sendmail(sender_qq_mail, toEmails, msg.as_string())
        smtp.quit()

confidence_TH = 0.30 # pitch confidence
insqueue_TH = 0.01 # one second th, sound detection
count_onesecond = 120 # count per second

musiconset_TH = 0.2
play_TH = 0.1
task_TH = 0.1
s_instance = Queue()
s_short=Queue()
s_short_time = 7
s_mid=Queue()
s_mid_time = 90
s_long=Queue()
s_long_time = 360

p = pyaudio.PyAudio()

# To dump soundcard list
for i in range(p.get_device_count()):
  dev = p.get_device_info_by_index(i)
  print((i,dev['name'],dev['maxInputChannels']))

# Stream define
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=DEVICE,
                frames_per_buffer=CHUNK)

print("* recording")


# no need record sound, only for debug
#frames = []

# open record file as 'a'
f = open("record.csv", "a") 

# Pitch define
tolerance = 0.8
downsample = 1
win_s = 512 // downsample # fft size DLCLOUD 2048
hop_s = 256  // downsample # hop size DLCLOUD 1024
pitch_o = pitch("yin", win_s, hop_s, RATE)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

# Notes
#notes_o = notes("default", win_s, hop_s, RATE)
task_status = 0
segment_status = 0

task_starttime = time.time()
task_endtime = time.time()
task_duration = 0.01

segment_endtime = time.time()
segment_starttime = time.time()
realplay_duration = 0.01

starttime = time.time()
pitchlasttime = starttime
pitchstarttime = starttime
lasttime = starttime

# main loop
while True:
# no need record sound for RECORD_SECONDS
#for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    buffer = stream.read(CHUNK, exception_on_overflow = False)
    # no need record sound, only for debug
    #frames.append(buffer)

    signal = np.fromstring(buffer, dtype=np.int16) # related to FORMAT
    signal = signal.astype(np.float32, order='C') # have to convert to float32 for aubio pitch function

    #Pitch
    pitch = pitch_o(signal)[0]
    confidence = pitch_o.get_confidence()

    # VOLUME
    #volume = np.sum(signal**2)/len(signal)
    # Format the volume output so that at most
    # it has six decimal numbers.
    #volume = "{:.6f}".format(volume)
    
    # Energy
    #energy = vec_local_energy(signal)
    #print ("Energy: ", energy)
    
    # Notes
    #new_note = notes_o(signal)
    #print(new_note)


    pitchtime = time.time()
    if int(pitchtime-starttime)-int(lasttime)>0: # run per second
        #print(s_instance.avg(count_onesecond))

        # Update short, mid and long queue for count
        if s_instance.avg(count_onesecond)> insqueue_TH:
            s_short.enqueue(1)
            s_mid.enqueue(1)
            s_long.enqueue(1)
        else:
            s_short.enqueue(0)
            s_mid.enqueue(0)
            s_long.enqueue(0)
        if s_short.size() > s_short_time: s_short.dequeue()
        if s_mid.size() > s_mid_time: s_mid.dequeue()
        if s_long.size() > s_long_time: s_long.dequeue()
        #print("Pitch: {} / {} / {} / {} / {}".format(pitch,confidence,pitchtime-starttime,"0","0"))

        # It is moving avg values for different time duration
        shortavg=s_short.avg(s_short_time)
        midavg=s_mid.avg(s_mid_time)
        longavg=s_long.avg(s_long_time)
        #print ("Queue avg: {} / {} / {}".format(shortavg,midavg,longavg))

        # State machine and checks
        if shortavg > musiconset_TH and midavg > (play_TH+0.1) and longavg < task_TH and task_status == 0:
            task_starttime = time.time()
            print ("Task started ", time.asctime(time.localtime(task_starttime)))
            segment_starttime = task_starttime
            segment_status = 1
            task_status=1
            midsize=s_mid.size()
            lonsize=s_long.size()
            for m in range(0,midsize):s_mid.dequeue()
            for m in range(0,lonsize):s_long.dequeue()
            
            for m in range(0,s_mid_time):s_mid.enqueue(1)
            for m in range(0,s_long_time):s_long.enqueue(1)
        elif shortavg > musiconset_TH and midavg > (play_TH+0.05) and longavg > task_TH and task_status == 1 and segment_status == 0:
            segment_starttime = time.time()
            segment_status = 1
            #print("event segment start", time.asctime(time.localtime(segment_starttime)))
        elif shortavg < musiconset_TH and midavg < play_TH and longavg > task_TH and task_status == 1 and segment_status == 1:
            segment_endtime = time.time()
            realplay_duration = realplay_duration + segment_endtime - segment_starttime
            segment_status = 0
            lonsize=s_long.size()
            for m in range(0,lonsize): s_long.dequeue()
            for m in range(0,s_long_time):s_long.enqueue(1)
            #print("event segment end", time.asctime(time.localtime(segment_endtime)), "realplay duration",realplay_duration)
            print("segment,",time.asctime(time.localtime(segment_starttime)),",",time.asctime(time.localtime(segment_endtime)),","+str(segment_endtime-segment_starttime),file=f)
        elif shortavg < musiconset_TH and midavg < play_TH and longavg < task_TH and task_status == 1:
            task_endtime = time.time()
            task_duration = task_endtime-task_starttime
            print ("Task done and sending mail:", time.asctime(time.localtime(task_starttime)),time.asctime(time.localtime(task_endtime)),task_duration,realplay_duration)
            print("task,",time.asctime(time.localtime(task_starttime)),",",time.asctime(time.localtime(task_endtime)),","+str(task_duration),file=f)
            task_status = 0
            sendmail()
            task_duration = 0
            realplay_duration = 0
        else:
            do_nothing_no_print_per_second = 0
            #if shortavg > musiconset_TH:print ("music on")
            #else: print ("music off")
            #if midavg < play_TH:print ("rest")
    
    lasttime = pitchtime-starttime
    
    if confidence>confidence_TH:
        #Timestamp for each pitch
        #pitchstarttime = time.time()
        #print("Pitch: {} / {} / {} / {} / {}".format(pitch,confidence,pitchstarttime-starttime,pitchstarttime-pitchlasttime,"1"))
        #pitchlasttime = pitchstarttime
        
        # sound queue update
        s_instance.enqueue(1)
        if s_instance.size() > count_onesecond: s_instance.dequeue()
        #print ("Instance avg: {}".format(s_instance.avg()))
        
        # Volume
        #print ("Vol: ", volume)

        # Note
        #if (new_note[0] != 0):
        #    note_str = ' '.join(["%.2f" % i for i in new_note])
        #    print("Notes: ", new_note)

    else:
        #print("Pitch: {} / {} / {} / {} / {}".format(pitch,confidence,pitchstarttime-starttime,0,"0"))

        # If no detect sound, update queue
        s_instance.enqueue(0)
        if s_instance.size() > count_onesecond: s_instance.dequeue()
        #print ("Instance avg: {}".format(s_instance.avg()))
stream.stop_stream()
stream.close()
p.terminate()


# no need record, just for debug
#print("* done recording")
#wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#wf.setnchannels(CHANNELS)
#wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
#wf.setframerate(RATE)
#wf.writeframes(b''.join(frames))
#wf.close()