HT1632C Python Library
======

A library used to interface with the RaspberryPi and a set of HT1632c Sure Electronic LED Boards.


Connection
----------

Using a Raspberry PI model B2, you need to connect some GPIO pins to the
LED BR1 port, the input port, like this:


| RPI                | SURE    |
|--------------------|---------|
| GND             6  | GND  8  |
| 5V              4  | 5V   16 |
| GPIO 10 (MOSI) 19  | DATA 7  |
| GPIO 11 (SCLK) 23  | WR   5  |
| GPIO 8  (CE0)  24  | CLK  2  |
| GPIO 7  (CE1)  26  | CS   1  |


INSTALL
=======

On your Raspberry PI open a shell, or connect to it by ssh. First you
need to install the python development package and the wiringPi library


Requirements
------------

Execute the following commands to have an updated package database, and
to install python-dev and git-core:

```
sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install git-core
```

You are now ready to install the wiringPi library. You may have a look
at http://wiringpi.com/ for further information and documentation.
Inside the shell execute these commands, to download the source code with
git, build and install the library, in the end remove the source, which is
no longer needed:

```
git clone git://git.drogon.net/wiringPi
cd wiringPi
git pull origin
./build
cd ..
rm -rf wiringPi
```

wiringPi installs the command gpio, you may use it right now to check that
all went well with:

`gpio -v`

and execute the following to get an overview about your GPIO connector:

`gpio readall`


ht1632 clib
-----------

Still inside a shell, change to the ht1632 clib directory, like:

`cd ht1632clib`

Have a look at the file panelconfig.h, if you own a SURE electronics
32-16 Bicolor LED matrix display, no need to change anything. Else
you need to adapt some constants here, to match your display type and
chip selection pins.

NOTE: the compiled ht1632 clib will match and work for that configured
      board only.

Execute the following command to compile the library:

`make`

The library is now ready to be used, before being able to actually
talk to the LED matrix, you need to load the wiringPi spi extension like:

`gpio load spi`


Examples
---------------

Once you have done the above, try out one of the examples in the src directory. Depending on where 
the ht1632clib-py.so file is located you may need to adjust the `PATH_TO_SO` variable in ht1632c.py file.
