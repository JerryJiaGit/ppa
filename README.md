# ppa
Introduction:

  ppa (Piano Practice Assistant) is a simple sound detection tool, which is based on raspberrypi 2B for my daughter piano practice and task duration report. It's using aubio pitch detect and have some machine state to check pitch count and calculate moving average value for music play detect or task done checks.

HW Installation:

  Raspberrypi 2 Model B - https://www.raspberrypi.org/
  
  16G MicroSD Card for raspberrypi OS (8G is good enough) - https://www.amazon.com/Sandisk-Ultra-Micro-UHS-I-Adapter/dp/B073K14CVB/ref=sr_1_3?ie=UTF8&qid=1537542690&sr=8-3&keywords=micro+sd+raspberry+pi 
  
  USB MIC - https://alexnld.com/product/usb-microphone-for-raspberry-pi/
  
  USB WIFI (optional) - https://www.amazon.com/Official-Raspberry-Pi-WiFi-dongle/dp/B014HTNO52/ref=sr_1_3?ie=UTF8&qid=1537542560&sr=8-3&keywords=raspberry+pi+usb+wifi


SW Installation:

1. Preparing Raspberry OS

  https://www.raspberrypi.org/documentation/installation/installing-images/
  
  after boot into raspbian, setup wifi 
  
  sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
  

  check USB MIC sound card
  
  sudo alsamixer

2. Preparing before running

  sudo apt-get install python3-pip
  
  sudo apt-get install python3-pyaudio
  
  sudo apt-get install libatlas-base-dev
  
  pip3 install numpy
  
  pip3 install aubio
  

3. Running ppa,py at background

  sudo nohup python3 ppa.py &
