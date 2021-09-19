#!/usr/bin/env python3

import sys
import math
import osmosdr
import time
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import secplus_decode
import secplus_v2_decode

class secplus_rx(gr.top_block):
    def __init__(self, freq):
        gr.top_block.__init__(self)

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 0.05
        self.samp_rate = samp_rate = 2000000
        self.freq = freq
        self.decim2 = decim2 = 50
        self.decim1 = decim1 = 2

        ##################################################
        # Blocks
        ##################################################

        self.secplus_v2_decode = secplus_v2_decode.blk(samp_rate=samp_rate // decim1 // decim2, threshold=threshold)
        self.secplus_decode = secplus_decode.blk(samp_rate=samp_rate // decim1 // decim2, threshold=threshold)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=decim2,
                taps=[1.0/decim2]*decim2,
                fractional_bw=None)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=decim1,
                taps=None,
                fractional_bw=None)

        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq - 300e3, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_gain(30, 0)
        self.osmosdr_source_0.set_if_gain(32, 0)
        self.osmosdr_source_0.set_bb_gain(32, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(1e6, 0)
        self.blocks_rotator_cc_0 = blocks.rotator_cc(2 * math.pi * -300e3 / samp_rate)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.blocks_rotator_cc_0, 0))
        self.connect((self.blocks_rotator_cc_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.secplus_decode, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.secplus_v2_decode, 0))

if __name__ == '__main__':
    #freq = 310150000
    #freq = 315150000
    #freq = 315010000
    freq = 390150000


    tb = secplus_rx(freq)
    tb.start()
    while True:
        try:
            time.sleep(1)
        except:
            tb.stop()
            tb.wait()
            sys.exit(0)

