import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!
import numpy
import scipy
import pyaudio
import threading
import pylab

class InputRecorder:
    """Simple, cross-platform class to record from the default input device."""
    
    def __init__(self):
        self.RATE = 44100
        self.BUFFERSIZE = 2**12
        self.secToRecord = .1
        self.kill_threads = False
        self.has_new_audio = False
        self.setup()
        
    def setup(self):
        self.buffers_to_record = int(self.RATE * self.secToRecord / self.BUFFERSIZE)
        if self.buffers_to_record == 0:
            self.buffers_to_record = 1
        self.samples_to_record = int(self.BUFFERSIZE * self.buffers_to_record)
        self.chunks_to_record = int(self.samples_to_record / self.BUFFERSIZE)
        self.sec_per_point = 1. / self.RATE
        
        self.p = pyaudio.PyAudio()
        # make sure the default input device is broadcasting the speaker output
        # there are a few ways to do this
        # e.g., stereo mix, VB audio cable for windows, soundflower for mac
        print("Using default input device: {:s}".format(self.p.get_default_input_device_info()['name']))
        self.in_stream = self.p.open(format=pyaudio.paInt16,
                                     channels=1,
                                     rate=self.RATE,
                                     input=True,
                                     frames_per_buffer=self.BUFFERSIZE)
        
        self.audio = numpy.empty((self.chunks_to_record * self.BUFFERSIZE), dtype=numpy.int16)               
    
    def close(self):
        self.kill_threads = True
        self.p.close(self.in_stream)
    
    ### RECORDING AUDIO ###  
    
    def get_audio(self):
        """get a single buffer size worth of audio."""
        audio_string = self.in_stream.read(self.BUFFERSIZE)
        return numpy.fromstring(audio_string, dtype=numpy.int16)
        
    def record(self):
        while not self.kill_threads:
            for i in range(self.chunks_to_record):
                self.audio[i*self.BUFFERSIZE:(i+1)*self.BUFFERSIZE] = self.get_audio()
            self.has_new_audio = True
    
    def start(self):
        self.t = threading.Thread(target=self.record)
        self.t.start()

    ### MATH ###
            
    def downsample(self, data, mult):
        """Given 1D data, return the binned average."""
        overhang = len(data) % mult
        if overhang:
            data = data[:-overhang]
        data = numpy.reshape(data, (len(data) / mult, mult))
        data = numpy.average(data, 1)
        return data    
        
    def fft(self, data=None, trim_by=10, log_scale=False, div_by=100):
        if not data: 
            data = self.audio.flatten()
        left, right = numpy.split(numpy.abs(numpy.fft.fft(data)), 2)
        ys = numpy.add(left, right[::-1])
        if log_scale:
            ys = numpy.multiply(20, numpy.log10(ys))
        xs = numpy.arange(self.BUFFERSIZE/2, dtype=float)
        if trim_by:
            i = int((self.BUFFERSIZE/2) / trim_by)
            ys = ys[:i]
            xs = xs[:i] * self.RATE / self.BUFFERSIZE
        if div_by:
            ys = ys / float(div_by)
        return xs, ys
    
    ### VISUALIZATION ###
    
    def plot_sound_wave(self):
        """open a matplotlib popup window showing audio data."""
        pylab.plot(self.audio.flatten())
        pylab.show()