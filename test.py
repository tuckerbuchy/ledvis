import pyaudio
import wave
import numpy
import array
import matplotlib.pyplot as plt
import serial
import Tkinter
import math
import colorsys
import matplotlib
import struct

#this is a class to implement the IIR filtering described by logan
class IIR:
    def __init__(self, alpha):
        self.alpha = alpha
        self.prev = 0
    def update(self, value):
        self.prev = (1-self.alpha)*value + self.alpha*self.prev
        return self.prev
        

def getSoundRatio(freq):
    freq_log = numpy.log(freq)/numpy.log(2**OCTAVES)
    freq_log_next_octave = numpy.ceil(freq_log)
    freq_log_prev_octave = numpy.floor(freq_log)
    print("freq_log: " + str(freq_log) + " next octave: " + str(freq_log_next_octave))  
    ratio = (freq_log - freq_log_prev_octave)
    print("RATIO: " + str(ratio))
    return ratio

def calculateMagnitude(real, imaginary):
    magnitudes = [] #where we wills store mags
    x = 0
    while x < len(real) and x < len(imaginary):
        magnitudes.append(numpy.sqrt(real[x]*real[x] + imaginary[x]*imaginary[x]))
        x += 1
    
    return magnitudes

def getFrequencyIndex(freq):
    return freq/(RATE/CHUNK)

def convertPercentToColorValue(percent):
    return int(round(percent*255))

def convertColorVectorToString(color_vector):
    result = ""
    for color in color_vector:
        result += (format(color, '02x'))
    return result

def mapFrequencyToHue(freq):
    if freq < BAND_LOWER:
        freq = BAND_LOWER
    elif freq > BAND_UPPER:
        freq = BAND_UPPER
        
    freq_log = numpy.log(freq)/numpy.log(2**OCTAVES)
    lower_log = numpy.log(BAND_LOWER)/numpy.log(2**OCTAVES)
    upper_log = numpy.log(BAND_UPPER)/numpy.log(2**OCTAVES)
    hue = (freq_log - lower_log) / (1.0*upper_log - 1.0*lower_log)
    return hue    

##################CONSTANTS####################
HSV_VALUE = 0.7

PEAK_THRESHOLD = 4e6
BAND_LOWER = 100
BAND_UPPER = 1000

SATURATION_FIR_DEQUE_SIZE = 30
HUE_IIR_ALPHA = 0.90

CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1000

OCTAVES = 2
###############################################
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

ser = serial.Serial('/dev/ttyACM1')
#print "SERIAL NAME: " + ser.name

print("* recording")

###Plots and canvas initialization########
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(numpy.random.randn(100))
plt.axis([20, 5000, 0, 1.1e7])
plt.show(block=False)
tk_canvas = Tkinter.Tk()
tk_canvas.geometry("500x500")
##########################################

hue_iir = IIR(HUE_IIR_ALPHA)
saturation_fir_deque = []

while(1):
    data = stream.read(CHUNK)
    nums = array.array('h', data)
    results = numpy.fft.fft(nums)
    freq_bins = numpy.fft.fftfreq(len(nums), 1.0/RATE)
        
    results = results[0:(len(results)/2 - 1)]
    freq_bins = 2 * freq_bins[0:(len(freq_bins)/2 - 1)]
    
    mags = calculateMagnitude(results.real, results.imag)
    
    lower_band_index = getFrequencyIndex(BAND_LOWER)
    upper_band_index = getFrequencyIndex(BAND_UPPER)
    
    max_mag  = max(mags[lower_band_index:upper_band_index])
    max_freq_index = mags.index(max_mag)
    max_freq = freq_bins[max_freq_index]
    
    new_frequency = BAND_LOWER
    #if max_freq >= BAND_LOWER and max_freq < BAND_UPPER:
    if max_mag > PEAK_THRESHOLD:
        new_frequency = max_freq
    
    averaged_frequency = hue_iir.update(new_frequency)
    hue = mapFrequencyToHue(averaged_frequency)
    
    mag_sum = numpy.sum(mags)
    saturation_fir_deque.append(mag_sum)
    if len(saturation_fir_deque) > SATURATION_FIR_DEQUE_SIZE:
        print("Popped!")
        saturation_fir_deque.pop(0)
    
    average_sum = numpy.mean(saturation_fir_deque)
    max_sum = max(saturation_fir_deque)
    if max_sum == 0:
        max_sum = 1
    saturation = 0.5 + (0.5)*average_sum/max_sum
    
    rgb = colorsys.hsv_to_rgb(hue, saturation, HSV_VALUE)
    rgb = map(convertPercentToColorValue, rgb)
    rgb_string = "#" + convertColorVectorToString(rgb)
    #packet = [0,0,0]
    packet = []

    for color in rgb:
        packet.append(color)
    
    ser.write(bytearray(packet))
    
    print("Frequency: " + str(max_freq) + " " + "Color: " + rgb_string)
    tk_canvas.configure(background=rgb_string)
    
    ##graph the fourier stuff
    #line.set_data(freq_bins, mags)
    fig.canvas.draw()
    fig.canvas.flush_events()
print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()
