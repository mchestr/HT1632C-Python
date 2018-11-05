# HT1632C Python Library

A library used to interface with the RaspberryPi and a set of HT1632c Sure Electronic LED Boards.

This library strives to achieve a sane, and well documented implementation of the HT1632C LED driver.
This library depends on [WiringPy-Python](https://pypi.org/project/wiringpi/).


## Connection

Using a Raspberry PI model B2, you need to connect some GPIO pins to the
LED BR1 port, the input port, like this:


| RPI Label      | Pin | SURE Label | Pin |
|----------------|-----|------------|-----|
| 5V             | 4   | 5V         | 16   |
| GND            | 6   | GND        | 8  |
| GPIO 10 (MOSI) | 19  | DATA       | 7   |
| GPIO 11 (SCLK) | 23  | WR         | 5   |
| GPIO 8  (CE0)  | 24  | CLK        | 2   |
| GPIO 7  (CE1)  | 26  | CS         | 1   |


## Installation

On your Raspberry PI open a shell, or connect to it by ssh. First you
need to install the python development package and the wiringPi library


### Prerequisites

Execute the following commands to have an updated package database, and
to install python-dev and git-core:

```
sudo apt-get update
sudo apt-get install python-dev git-core
```

Install the wiringPi library. You may have a look
at http://wiringpi.com/ for further information and documentation.
Inside the shell execute these commands, to download the source code with
git, build and install the library.

```
git clone git://git.drogon.net/wiringPi
cd wiringPi
./build
```

### Enable SPI on Board

`gpio load spi`

or

`sudo raspi-config`: `Interfacing Options --> SPI --> Yes`


### Install

`sudo python setup.py install`


## Examples

Once you have done the above, try out one of the examples.
