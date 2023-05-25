import sounddevice, sys
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

def bpm_to_samples(bpm):
    return int(sample_rate / (bpm / 60.0))

def note(f, bpm):
    saw = Saw(f)
    nsamples = bpm_to_samples(bpm)
    samples = saw.samples(0, n = nsamples)
    assert nsamples == len(samples)
    return samples

def rest(bpm):
    nsamples = bpm_to_samples(bpm)
    return np.zeros(nsamples, dtype=np.float32)

anote = note(440, 120)
space = rest(120)
np.append(anote, space)
track = np.repeat(anote, 2)

args = sys.argv
nargs = len(args)
if nargs > 1:
    io.wavfile.write(args[1], sample_rate, track)
else:
    sounddevice.play(track, samplerate=sample_rate, blocking=True)
