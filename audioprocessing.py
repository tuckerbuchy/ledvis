import pyaudio
import wave
import numpy
import array
import matplotlib.pyplot as plt
import serial
from Tkinter import *
#   import tkMessageBox
import math
import colorsys
import matplotlib
import struct

class IIR:
    def __init__(self, alpha):
        self.alpha = alpha
        self.prev = 0
    def update(self, value):
        self.prev = (1-self.alpha)*value + self.alpha*self.prev
        return self.prev

class SoundToColorProcessor:
    def __init__(self):
        self.serial_port = None
        self.HSV_VALUE = 0.7

        self.PEAK_THRESHOLD = 3e6
        self.BAND_LOWER = 40
        self.BAND_UPPER = 500

        self.SATURATION_FIR_DEQUE_SIZE = 20
        self.HUE_IIR_ALPHA = 0.9

        self.CHUNK = 2048
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100

        self.PROCESSING = False
        self.OCTAVES = 1
    '''
    calculate the magnitude of the fourier tranform parts
    '''
    def calculateMagnitude(self, real, imaginary):
        magnitudes = [] #where we wills store mags
        x = 0
        while x < len(real) and x < len(imaginary):
            magnitudes.append(numpy.sqrt(real[x]*real[x] + imaginary[x]*imaginary[x]))
            x += 1
        return magnitudes

    def getFrequencyIndex(self, freq):
        return freq/(self.RATE/self.CHUNK)

    def convertPercentToColorValue(self, percent):
        return int(round(percent*255))

    def convertColorVectorToString(self, color_vector):
        result = ""
        for color in color_vector:
            result += (format(color, '02x'))
        return result

    def mapFrequencyToHue(self, freq):
        if freq < self.BAND_LOWER:
            freq = self.BAND_LOWER
        elif freq > self.BAND_UPPER:
            freq = self.BAND_UPPER
            
        freq_log = numpy.log(freq)/numpy.log(2**self.OCTAVES)
        lower_log = numpy.log(self.BAND_LOWER)/numpy.log(2**self.OCTAVES)
        upper_log = numpy.log(self.BAND_UPPER)/numpy.log(2**self.OCTAVES)
        hue = (freq_log - lower_log) / (1.0*upper_log - 1.0*lower_log)
        return hue

    def startProcessing(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        try:
            ser = serial.Serial(self.serial_port, timeout=1)
        except serial.SerialException:
            print "Couldn't connect to serial port"
            return

        ###Plots and canvas initialization########
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot(numpy.random.randn(100))
        plt.axis([20, 5000, 0, 1.1e7])
        plt.show(block=False)
        tk_canvas = Tk()
        tk_canvas.geometry("500x500")

        hue_iir = IIR(self.HUE_IIR_ALPHA)
        saturation_fir_deque = []

        while(self.PROCESSING is True):
            data = stream.read(self.CHUNK)
            nums = array.array('h', data)
            results = numpy.fft.fft(nums)
            freq_bins = numpy.fft.fftfreq(len(nums), 1.0/self.RATE)
                
            results = results[0:(len(results)/2 - 1)]
            freq_bins = 2 * freq_bins[0:(len(freq_bins)/2 - 1)]
            
            mags = self.calculateMagnitude(results.real, results.imag)
            
            lower_band_index = self.getFrequencyIndex(self.BAND_LOWER)
            upper_band_index = self.getFrequencyIndex(self.BAND_UPPER)
            
            max_mag  = max(mags[lower_band_index:upper_band_index])
            max_freq_index = mags.index(max_mag)
            max_freq = freq_bins[max_freq_index]
            
            new_frequency = self.BAND_LOWER
            #if max_freq >= BAND_LOWER and max_freq < BAND_UPPER:
            if max_mag > self.PEAK_THRESHOLD:
                new_frequency = max_freq
            
            averaged_frequency = hue_iir.update(new_frequency)
            hue = self.mapFrequencyToHue(averaged_frequency)
            
            mag_sum = numpy.sum(mags)
            saturation_fir_deque.append(mag_sum)
            if len(saturation_fir_deque) > self.SATURATION_FIR_DEQUE_SIZE:
                #print("Popped!")
                saturation_fir_deque.pop(0)
            
            average_sum = numpy.mean(saturation_fir_deque)
            max_sum = max(saturation_fir_deque)
            if max_sum == 0:
                max_sum = 1
            saturation = 0.85 + (0.15)*average_sum/max_sum
            
            rgb = colorsys.hsv_to_rgb(hue, saturation, self.HSV_VALUE)
            rgb = map(self.convertPercentToColorValue, rgb)
            rgb_string = "#" + self.convertColorVectorToString(rgb)
            packet = [0,0,0]
            packet = []

            for color in rgb:
                packet.append(color)
            
            ser.write(bytearray(packet))
            
            #print("Frequency: " + str(max_freq) + " " + "Color: " + rgb_string)
            tk_canvas.configure(background=rgb_string)
            
            ##graph the fourier stuff
            line.set_data(freq_bins, mags)
            fig.canvas.draw()
            fig.canvas.flush_events()

        ser.close()
        plt.close()
        tk_canvas.destroy()
        stream.stop_stream()
        stream.close()
        p.terminate()

    def startStopCallback(self):
        if (self.PROCESSING is True):
            self.PROCESSING = False
        else:
            self.PROCESSING = True
            self.startProcessing()
    def setUpperBand(self, val):
        high = int(val)
        if high <= self.BAND_LOWER:
            print("Cannot set upper band this low")
        else:
            self.BAND_UPPER = int(val)

    def setLowerBand(self, val):
        low = int(val)
        if low >= self.BAND_UPPER:
            print("Error", "Cannot set lower bound this high")
        else:
            self.BAND_LOWER = int(val)

    def setFirQueue(self, val):
        self.SATURATION_FIR_DEQUE_SIZE = int(val)

    def setHueAlpha(self, val):
        self.HUE_IIR_ALPHA = float(val)

    def setNumberOfOctaves(self, val):
        self.OCTAVES = int(val)

    def setSerial(self, val):
        self.serial_port = val

    def start(self):
        main_window = Tk()

        lower_band_entry = Entry(main_window)
        lower_button = Button(main_window, text="Set Lower Band (Hz)", command=lambda:self.setLowerBand(lower_band_entry.get()))
        lower_band_entry.pack()
        lower_button.pack()
        
        upper_band_entry = Entry(main_window)
        upper_button = Button(main_window, text="Set Upper Band (Hz)", command= lambda:self.setUpperBand(upper_band_entry.get()))
        upper_band_entry.pack()
        upper_button.pack()

        num_octaves_slide = Scale(main_window, from_=1, to_=5, label="Number of Octaves", command=self.setFirQueue)
        num_octaves_slide.pack()

        fir_queue_slide = Scale(main_window, from_=1, to_=40, label="FIR Saturation Queue", command=self.setFirQueue)
        fir_queue_slide.pack()

        ser_entry = Entry(main_window)
        ser_button = Button(main_window, text="Set Serial Port", command=lambda:self.setSerial(ser_entry.get()))
        ser_entry.pack()
        ser_button.pack()
        
        control_button = Button(main_window, text="Start/Pause", command=self.startStopCallback)
        control_button.pack()
        main_window.mainloop()

proc = SoundToColorProcessor()
proc.start();
