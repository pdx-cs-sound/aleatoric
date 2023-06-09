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

def note(f, frac):
    nsamples = bpm_nsamples * 4 // frac
    release = int(0.05 * bpm_nsamples)
    saw = Saw(f)
    samples = saw.samples(0, n = nsamples - release)
    release = np.zeros(release, dtype=np.float32)
    return np.append(samples, release)

def rest(frac):
    return np.zeros(bpm_nsamples * 4 // frac)

def key_to_freq(midi_key):
    return 440 * 2**((midi_key - 69) / 12)

major_offsets = [0, 2, 4, 5, 7, 9, 11]
minor_offsets = [0, 2, 3, 5, 7, 8, 10]

def scale(midi_key, offsets):
    return [midi_key + q for q in offsets]

def beats(n):
    nb = 16
    b = nb * [1/16]
    njoins = random.randrange(1, 8)
    for _ in range(njoins):
        join_point = random.randrange(nb - 1)
        new_beat = b[join_point] + b[join_point - 1]
        b[join_point] = new_beat
        del b[join_point - 1]
        nb -= 1
    return [1 / d for d in b]

trial_beat = beats(4)

# A Minor scale.
root = 57
trial_scale = scale(root, minor_offsets)

chord_weights = [0.8, 0.2, 0.8, 0.1, 0.8, 0.1, 0.05]

nsnare = int(sample_rate * 0.005)
snare_sample = 40 * np.random.rand(nsnare) - 1

def snare(n, frac):
    return np.append(snare_sample, np.zeros(int(bpm_nsamples * n // frac - nsnare)))

def measure(n, d):
    freqs = [key_to_freq(random.choices(trial_scale, weights=chord_weights)[0])
             for _ in range(n)]
    levels = [0.5] * n
    levels[0] = 1.0
    notes = np.concatenate(tuple(
        l * note(f, n) for l, f in zip(levels, freqs)
    ))
    drum = np.concatenate(tuple(
        snare(n, b) for b in trial_beat
    ))
    # XXX This is terrible. Should actually compute
    # the right number of samples for the drum track
    # rather than this kludge.
    drum = np.append(drum, np.zeros(sample_rate))
    drum = drum[:len(notes)]
    drone = note(d - 24, 1)
    return 0.3 * (notes + drone + drum)

def bars(n, m):
    choices = [trial_scale[i] for i in (0, 3, 4)]
    basses = [random.choice(choices) for _ in range(n)]
    basses[-1] = trial_scale[0]
    return np.concatenate(tuple(measure(m, d) for d in basses))

stanza = bars(4, 4)

track = 0.5 * np.tile(stanza, 2)

args = sys.argv
nargs = len(args)
if nargs > 1:
    io.wavfile.write(args[1], sample_rate, track)
else:
    sounddevice.play(track, samplerate=sample_rate, blocking=True)
