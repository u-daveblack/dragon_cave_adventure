import numpy as np
from scipy.io.wavfile import write

# Common parameters
sample_rate = 44100  # Hz

def save_wav(filename, signal):
    # Normalize to 16-bit PCM
    signal = np.int16(signal / np.max(np.abs(signal)) * 32767)
    write(filename, sample_rate, signal)

# 1. Jump sound: Short, rising chirp (like a game jump)
def generate_jump():
    duration = 0.2  # seconds
    freq_start = 400  # Hz
    freq_end = 800    # Hz
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = np.linspace(freq_start, freq_end, len(t))
    signal = 0.5 * np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-4 * t / duration)  # Quick attack, decay
    return signal * envelope

# 2. Coin sound: High-pitched, metallic ding
def generate_coin():
    duration = 0.3  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freqs = [1200, 1800, 2400]  # Multiple high frequencies for sparkle
    signal = sum(0.3 * np.sin(2 * np.pi * f * t) for f in freqs)
    envelope = np.exp(-6 * t / duration)  # Sharp decay for chime effect
    return signal * envelope

# 3. Roar sound: Deep, guttural dragon roar
def generate_roar():
    duration = 2.0  # seconds for a longer, epic roar
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Base low-frequency tone (fundamental growl)
    freq_base = 80  # Hz (deep rumble)
    signal = 0.4 * np.sin(2 * np.pi * freq_base * t)
    
    # Add harmonic overtones for richness
    signal += 0.3 * np.sin(2 * np.pi * freq_base * 2 * t)  # First harmonic
    signal += 0.2 * np.sin(2 * np.pi * freq_base * 3 * t)  # Second harmonic
    
    # Frequency modulation for dynamic, animalistic quality
    mod_freq = 5  # Hz (slow oscillation)
    signal += 0.3 * np.sin(2 * np.pi * (freq_base + 20 * np.sin(2 * np.pi * mod_freq * t)) * t)
    
    # Add filtered noise for throaty texture
    noise = np.random.normal(0, 0.15, len(t))
    # Simple low-pass filter effect: smooth noise with moving average
    noise_filtered = np.convolve(noise, np.ones(100)/100, mode='same')
    signal += noise_filtered
    
    # Envelope: Slow attack, sustained, then decay
    envelope = (1 - np.exp(-5 * t / duration)) * np.exp(-2 * t / duration)
    return signal * envelope

# 4. Hit sound: Short, harsh noise burst
def generate_hit():
    duration = 0.1  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # White noise base
    signal = np.random.normal(0, 0.5, len(t))
    # Add low tone for impact
    signal += 0.3 * np.sin(2 * np.pi * 200 * t)
    envelope = np.exp(-10 * t / duration)  # Very sharp decay
    return signal * envelope

# Generate and save all sounds
save_wav('jump.wav', generate_jump())
save_wav('coin.wav', generate_coin())
save_wav('roar.wav', generate_roar())
save_wav('hit.wav', generate_hit())