
### Info

Python script to read sound from the computers output and process it for a variety of visualization effects.

### Demonstration
http://www.youtube.com/watch?v=6z6rRS_tOmw

### Steps to get going on Linux machine 
Note: specifically debian, but can be used as a guide for other distros

##### Install useful tools and dependencies
`sudo apt-get install python-pip python-dev portaudio19-dev`
`sudo pip install -r requirements.txt`

##### Try to run script
`python audioprocessing.py`
This should open a little dialog window with a couple controls on it. The important one to fill out is Serial Port.
I have this in here as I was using the application to send color values to an arduino, but you may just be able to enter
null (to pipe it to /dev/null).

##### Linux Sound Configuration
Now the difficulty I encountered during this implementation is attempting to capture the sound output from the sound card. The purpose of the application is to process all sound data coming out of the machine. The solution I have currently involves performing a configuration in pavucontrol to redirect the audio out to the microphone. It is super simple to do, and is pretty well covered in this article https://www.kirsle.net/blog/entry/redirect-audio-out-to-mic-in--linux-. 
