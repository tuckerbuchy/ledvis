import pyaudio
import wave
import numpy
import array
import matplotlib.pyplot as plt
import serial
import Tkinter

def getColorFromWaveLength(wavelength):
    gamma = 1.00
    max_intensity = 255

    if wavelength >= 350 and wavelength < 440:
        red = -(wavelength - 440) / (440 - 350);
        green = 0.0
        blue    = 1.0
    elif wavelength >= 440 and wavelength < 490:
        red = 0.0
        green = (wavelength - 440) / (490 - 440)
        blue    = 1.0
    elif wavelength >= 490 and wavelength < 510:
        red = 0.0
        green = 1.0
        blue = -(wavelength - 510) / (510 - 490)
    elif wavelength >= 510 and wavelength < 580: 
        red = (wavelength - 510) / (580 - 510)
        green = 1.0
        blue = 0.0
    elif wavelength >= 580 and wavelength < 645:
        red = 1.0
        green = -(wavelength - 645) / (645 - 580)
        blue = 0.0
    elif wavelength >= 645 and wavelength <= 780:
        red = 1.0
        green = 0.0
        blue = 0.0
    else:
        red = 0.0
        green = 0.0
        blue = 0.0

    #Intensity factorAdjust goes through the range:
    #0.1 (350-420 nm) 1.0 (420-645 nm) 1.0 (645-780 nm) 0.2
 
    if wavelength >= 350 and wavelength < 420:
        factor = 0.1 + 0.9*(wavelength - 350) / (420 - 350)
        
    elif wavelength >= 420 and wavelength < 645:
        factor = 1.0
        
    elif wavelength >= 645 and wavelength <= 780:
        factor = 0.2 + 0.8*(780 - wavelength) / (780 - 645)
        
    else:
        factor = 0.0

    R = int(round(factorAdjust (red, factor, max_intensity, gamma)));
    G = int(round(factorAdjust (green, factor, max_intensity, gamma)));
    B = int(round(factorAdjust (blue, factor, max_intensity, gamma)));

    #return Color.FromArgb(R, G, B);
    #eturn "R:" + R + ", G:" + G + ", B:" + B
    
    return "#" + (format((R), '02x')) + (format(int(G), '02x')) + (format(int(B), '02x')) #format(R,'x') + format(G, 'x') + format(B, 'x')
    #return "#" + hex(R) + hex(G) + hex(B)
    
def factorAdjust (color, factor, intensityMax, gamma):
    
    if (color == 0.0):
        return 0
    else:
        return numpy.round (intensityMax * (color * factor ** gamma))

def getSoundRatio(freq):
    highest_freq = 2000
    lowest_freq = 50
    return (freq - lowest_freq) / (highest_freq - lowest_freq)

def getVisualWavelengthFromRatio(ratio):
    #really it should be the inverse, because wavelength is 
    #inversely proportional to frequency.
    longest_wavelength = 780
    shortest_wavelength = 350
    mapped_wavelength = (longest_wavelength - shortest_wavelength) * ratio + shortest_wavelength
    return mapped_wavelength

def calculateMagnitude(real, imaginary):
    magnitudes = [] #where we wills store mags
    x = 0
    while x < len(real) and x < len(imaginary):
        magnitudes.append(numpy.sqrt(real[x]*real[x] + imaginary[x]*imaginary[x]))
        x += 1
    
    return magnitudes
         
CHUNK = 2056
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
#ser = serial.Serial('/dev/ttyACM0')
#print "SERIAL NAME: " + ser.name

print("* recording")

frames = []

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(numpy.random.randn(100))
plt.axis([20, 5000, 0, 1.1e7])
#ax.set_xscale('log', basex=2)
plt.show(block=False)

canvas = Tkinter.Tk()
canvas.geometry("500x500")
i = 0
while(1):
    data = stream.read(CHUNK)
    nums = array.array('h', data)
    results = numpy.fft.fft(nums)
    freq_bins = numpy.fft.fftfreq(len(nums), 1.0/RATE)
    
    results = results[0:(len(results)/2 - 1)]
    freq_bins = 2 * freq_bins[0:(len(freq_bins)/2 - 1)]
    
    mags = calculateMagnitude(results.real, results.imag)
 
    max_freq_index = mags.index(max(mags))
    max_freq = freq_bins[max_freq_index]

    #mags_normalized = mags/freq_max
    
    #Algorithm
    ##########
    #-Take ratio of max freq over reasonable auditory range (50-10000hz) 
    #-Times this ratio by the reasonable visual range (X-Ynm)
    #-convert visual wave length to rgb value
    #-send it over wire
    if max_freq < 10000:
        sound_ratio = getSoundRatio(max_freq)
        wave_length = getVisualWavelengthFromRatio(sound_ratio)
        color = getColorFromWaveLength(wave_length)
        print("Frequency: " + str(max_freq) + " " + "Color: " + str(color))
        canvas.configure(background=color)
    line.set_data(freq_bins, mags)
    fig.canvas.draw()
    fig.canvas.flush_events()

    i += 1
print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()
