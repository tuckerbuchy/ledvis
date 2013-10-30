import pyaudio
import wave
import numpy
import array
import matplotlib.pyplot as plt
import serial

def calculateMagnitude(real, imaginary):
    magnitudes = [] #where we wills store mags
    x = 0
    while x < len(real) and x < len(imaginary):
        magnitudes.append(numpy.sqrt(real[x]*real[x] + imaginary[x]*imaginary[x]))
        x += 1
    
    return magnitudes
         

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1000

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
ser = serial.Serial('/dev/ttyACM0')
print "SERIAL NAME: " + ser.name

print("* recording")

frames = []

#plt.ion()

#fig = plt.figure()
#ax = fig.add_subplot(111)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    nums = array.array('h', data)
    results = numpy.fft.fft(nums)
    freq_bins = numpy.fft.fftfreq(len(nums))
    
    #This 
    mags = calculateMagnitude(results.real, results.imag)
    big_freq_index =  mags.index(max(mags))
    freq = (big_freq_index * 44100) / (CHUNK)
    #if i % 1000 == 0:
    ser.write(str(freq))
    print (freq)
    #plt.clf()
    #plt.plot(freq, results.real, freq, results.imag)
    #fig.canvas.draw()
    frames.append(data)
print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()


# if we need to write it to a wav file (for testing)

#WAVE_OUTPUT_FILENAME = "output.wav"
#wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#wf.setnchannels(CHANNELS)
#wf.setsampwidth(p.get_sample_size(FORMAT))
#wf.setframerate(RATE)
#wf.writeframes(b''.join(frames))
#wf.close()
