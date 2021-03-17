# Open Assistant

Open source voice assistant development. Make your own minds!

Open Assistant is a private open source personal assistant prototype able to complete operating system tasks using vocal commands.

## Installation

### Windows

#### _Click & Run_

* Download [http://openassistant.org/download/oa_0.21_windows.zip](http://openassistant.org/download/oa_0.21_windows.zip)
* Unzip package
* Launch `oa.exe` in "Open Assistant" folder

#### _Source_

* Install [common list of Python packages](https://www.python.org/downloads/windows/)
* Install Windows-specific dependencies: ``pip install pywin32``
* Install Python dependencies: `pip install -r requirements.txt`

### macOS

* Install [brew](https://brew.sh/) if you have not already.
* Install pocketsphinx dependencies: `brew install swig openal-soft`
* Link the openal-soft libraries to the include path: `ln -s /usr/local/Cellar/openal-soft/1.20.1/include/AL/* /usr/local/include`
* Install Python dependencies: `pip3 install -r requirements.txt`

### Ubuntu Linux

* Install system requirements ``sudo apt-get install -y python3 python3-dev python3-pip build-essential swig git libpulse-dev espeak libasound2-dev``
* Install Python dependencies: `pip3 install -r requirements.txt`

### Arch Linux

* Install system requirements ``sudo pacman -S swig espeak``
* Install Python dependencies: `pip install -r requirements.txt`

## Using Open Assistant

* [Download Open Assistant](https://github.com/openassistant/oa-core/archive/master.zip)
* Run Open Assistant from within the unzipped directory: ``python -m oa`` or ``python3 -m oa``
* Make sure your microphone is working and levels are set properly.
* Say "Boot Mind!" as a listening test. If you hear R2D2, boot mind is listening.
* Say "Open Assistant!" to launch root mind. Say "Root Mind!" to see if you can get the reply, "Hello World!"
* Say "List commands!" to get a list of available voice commands.
* Add your own!
