import random, sounddevice, sys
import numpy as np
from scipy import io

sample_rate = 44100

def make_times(t, tv, n):
    """Return a sequence of n time points for wave sampling."""
    times = np.linspace(
        t,
        t + n,
        num = n,
        endpoint = False,
        dtype = np.float32,
    )
    if tv is not None:
        times += tv
    return times

class Saw(object):
    """Sawtooth VCO."""
    def __init__(self, f):
        """Make a new sawtooth generator."""
        self.tmul = f / sample_rate

    def samples(self, t, tv = None, n = 1):
        """Return the next n samples from this generator."""
        times = make_times(t, tv, n)
        # https://en.wikipedia.org/wiki/Sawtooth_wave
        a = self.tmul * times
        return 2.0 * (a - np.floor(0.5 + a))

bpm = 120
bpm_nsamples = int(sample_rate / (bpm / 60.0))

def quarter_note(f):
    saw = Saw(f)
    samples = saw.samples(0, n = int(0.9 * bpm_nsamples))
    release = np.zeros(int(0.1 * bpm_nsamples), dtype=np.float32)
    return np.append(samples, release)

def quarter_rest():
    return np.zeros(bpm_nsamples)

def key_to_freq(midi_key):
    return 440 * 2**((midi_key - 69) / 12)

def major_scale(midi_key):
    offsets = [0, 2, 4, 5, 7, 9, 11]
    return [midi_key + q for q in offsets]

trial_scale = major_scale(60)

def measure(n):
    freqs = [key_to_freq(random.choice(trial_scale)) for _ in range(n)]
    return np.concatenate(tuple(quarter_note(f) for f in freqs))

riff = measure(4)

track = np.tile(riff, 8)

args = sys.argv
nargs = len(args)
if nargs > 1:
    io.wavfile.write(args[1], sample_rate, track)
else:
    sounddevice.play(track, samplerate=sample_rate, blocking=True)
