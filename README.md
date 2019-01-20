# bunny-bike
This project began life as a copy of the "bike barometer" found here: https://www.youtube.com/watch?v=GP6LIhDopQk
At the time my wife (then fiance, aka bunny) was living in Boston and could either commute via the MBTA or ride her bike.
She now lives in Durham where we ride the GoTriangle buses and biking isn't really an option. So right now the code is designed to display the following on a 16x2 character LCD screen:
Current time, time until next bus arrival, current temperature and the forecast for the day.
There is still code present for controlling a servo motor that you can also put in your circuit.
Please note that all my code is hard-coded, meaning it only works for the three buses we use and only for the two stops right outside our apartment. You'll have to do a lot of digging around in API's to adapt anything.

Install guide:
## Setup Raspberry Pi
I used a Raspberry Pi Zero with the latest Raspbian OS. I don't think any atypical setup was involved. It needs internet access.
## Get Adafruit_Python_CharLCD:
NOTE: Installing this may also install Adafruit_Python_GPIO (below) automatically. This library will run both the LCD and the servo.
````
$ sudo apt-get update
$ sudo apt-get install build-essential python-pip python-dev python-smbus git
$ sudo pip install RPi.GPIO
$ git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
$ cd Adafruit_Python_CharLCD
$ sudo python setup.py install
````
## Get Adafruit_Python_GPIO:
````
$ sudo apt-get update
$ git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
$ cd Adafruit_Python_GPIO
$ sudo python setup.py install
````
## Get your API keys
Go to Weather Underground and your local transit agency and obtain private API keys. GoTriangle uses Mashape: https://market.mashape.com/transloc/openapi-1-2
Insert the keys in the appropriate locations within the code.
## Setup the circuit
![alt text](https://github.com/JohannesKepler/bunny-bike/blob/master/Bike%20Clock%20Schematic_bb.png)
## To-do:
Clean up code! Also implement the following features:
- [x] Scrolling text to display messages longer than 16 characters.
- [ ] A physical button that switches bus lookups.
- [ ] Instructions on how to keep the code running indefinitely (right now it doesn't run for more than 1-3 hours).
- [ ] Instructions on how to run the code on boot.
