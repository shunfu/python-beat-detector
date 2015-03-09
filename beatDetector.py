"""
Sources

http://www.swharden.com/blog/2013-05-09-realtime-fft-audio-visualization-with-python/
http://julip.co/2012/05/arduino-python-soundlight-spectrum/
"""

import ui_plot
import sys
import numpy
from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as Qwt
from recorder import *
from time import perf_counter

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

colors_list = ["red", "blue", "green"]
colors_idx = 0;

bpm_list = []
prev_beat = perf_counter()
low_freq_avg_list = []

def plot_audio_and_detect_beats():
    if not input_recorder.has_new_audio: 
        return

    # get x and y values from FFT
    xs, ys = input_recorder.fft()
    
    # calculate average for all frequency ranges
    y_avg = numpy.mean(ys)

    # calculate low frequency average
    low_freq = [ys[i] for i in range(len(xs)) if xs[i] < 1000]
    low_freq_avg = numpy.mean(low_freq)
    
    global low_freq_avg_list
    low_freq_avg_list.append(low_freq_avg)
    cumulative_avg = numpy.mean(low_freq_avg_list)
    
    bass = low_freq[:int(len(low_freq)/2)]
    bass_avg = numpy.mean(bass)
    # print("bass: {:.2f} vs cumulative: {:.2f}".format(bass_avg, cumulative_avg))
    
    # check if there is a beat
    # song is pretty uniform across all frequencies
    if (y_avg > 10 and (bass_avg > cumulative_avg * 1.5 or
            (low_freq_avg < y_avg * 1.2 and bass_avg > cumulative_avg))):
        global prev_beat
        curr_time = perf_counter()
        # print(curr_time - prev_beat)
        if curr_time - prev_beat > 60/180: # 180 BPM max
            # print("beat")
            # change the button color
            global colors_idx
            colors_idx += 1;
            uiplot.btnD.setStyleSheet("background-color: {:s}".format(colors_list[colors_idx % len(colors_list)]))
            
            # change the button text
            global bpm_list
            bpm = int(60 / (curr_time - prev_beat))
            if len(bpm_list) < 4:
                if bpm > 60:
                    bpm_list.append(bpm)
            else:
                bpm_avg = int(numpy.mean(bpm_list))
                if abs(bpm_avg - bpm) < 35:
                    bpm_list.append(bpm)
                uiplot.btnD.setText(_fromUtf8("BPM: {:d}".format(bpm_avg)))
            
            # reset the timer
            prev_beat = curr_time
    
    # shorten the cumulative list to account for changes in dynamics
    if len(low_freq_avg_list) > 50:
        low_freq_avg_list = low_freq_avg_list[25:]
        # print("REFRESH!!")

    # keep two 8-counts of BPMs so we can maybe catch tempo changes
    if len(bpm_list) > 24:
        bpm_list = bpm_list[8:]

    # reset song data if the song has stopped
    if y_avg < 10:
        bpm_list = []
        low_freq_avg_list = []
        uiplot.btnD.setText(_fromUtf8("BPM"))
        # print("new song")

    # plot the data
    c.setData(xs, ys)
    uiplot.qwtPlot.replot()
    input_recorder.newAudio = False

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    
    win_plot = ui_plot.QtGui.QMainWindow()
    uiplot = ui_plot.Ui_win_plot()
    uiplot.setupUi(win_plot)
    # uiplot.btnA.clicked.connect(plot_audio_and_detect_beats)
    # uiplot.btnB.clicked.connect(lambda: uiplot.timer.setInterval(100.0))
    # uiplot.btnC.clicked.connect(lambda: uiplot.timer.setInterval(10.0))
    # uiplot.btnD.clicked.connect(lambda: uiplot.timer.setInterval(1.0))
    c = Qwt.QwtPlotCurve()  
    c.attach(uiplot.qwtPlot)
    
    uiplot.qwtPlot.setAxisScale(uiplot.qwtPlot.yLeft, 0, 100000)
    
    uiplot.timer = QtCore.QTimer()
    uiplot.timer.start(1.0)
    
    win_plot.connect(uiplot.timer, QtCore.SIGNAL('timeout()'), plot_audio_and_detect_beats) 
    
    input_recorder = InputRecorder()
    input_recorder.start()

    ### DISPLAY WINDOWS
    win_plot.show()
    code = app.exec_()

    # clean up
    input_recorder.close()
    sys.exit(code)