import wave
import struct
import math
import os

SAMPLE_RATE = 44100

def write_wav(filename, samples):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        # Convert float (-1.0 to 1.0) to 16-bit int
        raw_data = bytearray()
        for s in samples:
            s_clamped = max(-1.0, min(1.0, s))
            val = int(s_clamped * 32767.0)
            raw_data.extend(struct.pack('<h', val))
        wav_file.writeframes(raw_data)
    print(f"Generated {filepath} ({len(samples)} samples)")

def generate_jump():
    # Springy pitch sweep 250Hz -> 650Hz, 0.18s
    duration = 0.18
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = t / duration
        freq = 240.0 + 460.0 * (progress ** 1.5)
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        # Envelope: fast attack, smooth decay
        env = (1.0 - progress) * min(1.0, t * 80.0)
        # Mix sine + mild triangle harmonic
        val = (math.sin(phase) * 0.75 + math.sin(phase * 2.0) * 0.25) * env * 0.7
        samples.append(val)
    write_wav("jump.wav", samples)

def generate_land():
    # Thud + soft metal clink, 0.15s
    duration = 0.15
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase1 = 0.0
    phase2 = 0.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = t / duration
        # Low thud: 120Hz -> 50Hz
        freq1 = 120.0 * math.exp(-progress * 5.0)
        phase1 += 2.0 * math.pi * freq1 / SAMPLE_RATE
        # Metallic high clink: 1800Hz decay
        phase2 += 2.0 * math.pi * 1800.0 / SAMPLE_RATE
        env_thud = math.exp(-progress * 18.0)
        env_metal = math.exp(-progress * 35.0) * 0.3
        val = (math.sin(phase1) * env_thud + math.sin(phase2) * env_metal) * 0.8
        samples.append(val)
    write_wav("land.wav", samples)

def generate_collect():
    # Sparkling major arpeggio: C6 (1046.5), E6 (1318.5), G6 (1567.9), C7 (2093)
    notes = [1046.5, 1318.5, 1567.9, 2093.0]
    note_dur = 0.065
    samples = []
    for note_idx, freq in enumerate(notes):
        num_s = int(note_dur * SAMPLE_RATE)
        phase = 0.0
        for i in range(num_s):
            t = i / SAMPLE_RATE
            p = t / note_dur
            phase += 2.0 * math.pi * freq / SAMPLE_RATE
            env = math.exp(-p * 6.0)
            # Pure bell-like tone: sine + soft 3rd harmonic
            val = (math.sin(phase) * 0.8 + math.sin(phase * 3.0) * 0.2) * env * 0.65
            samples.append(val)
    # Ringing tail on final note
    tail_samples = int(0.25 * SAMPLE_RATE)
    phase = 0.0
    final_freq = notes[-1]
    for i in range(tail_samples):
        t = i / SAMPLE_RATE
        p = t / 0.25
        phase += 2.0 * math.pi * final_freq / SAMPLE_RATE
        env = math.exp(-p * 12.0) * 0.65
        val = math.sin(phase) * env
        samples.append(val)
    write_wav("collect.wav", samples)

def generate_switch():
    # Mechanical whirr + power click: 0.35s
    duration = 0.35
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = t / duration
        if progress < 0.3:
            # Servo spin: 300 -> 700Hz
            freq = 300.0 + 1300.0 * progress
            env = progress / 0.3
        else:
            # Power pulse: 880Hz -> 440Hz with shimmer
            p2 = (progress - 0.3) / 0.7
            freq = 880.0 * math.exp(-p2 * 2.0)
            env = math.exp(-p2 * 5.0)
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        val = math.sin(phase) * env * 0.6
        samples.append(val)
    write_wav("switch.wav", samples)

def generate_bridge():
    # Ethereal rising hum with power beam resonance: 0.8s
    duration = 0.8
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase1 = 0.0
    phase2 = 0.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = t / duration
        freq1 = 150.0 + 350.0 * (progress ** 2.0)
        freq2 = freq1 * 1.5  # perfect fifth
        phase1 += 2.0 * math.pi * freq1 / SAMPLE_RATE
        phase2 += 2.0 * math.pi * freq2 / SAMPLE_RATE
        env = math.sin(progress * math.pi) * 0.7
        val = (math.sin(phase1) * 0.6 + math.sin(phase2) * 0.4) * env
        samples.append(val)
    write_wav("bridge.wav", samples)

def generate_portal():
    # Cosmic resonant hum: 1.0s
    duration = 1.0
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = t / duration
        # Vibrato
        lfo = math.sin(2.0 * math.pi * 5.0 * t) * 20.0
        freq = 520.0 + lfo
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        env = math.sin(progress * math.pi) * 0.7
        val = (math.sin(phase) * 0.7 + math.sin(phase * 2.0) * 0.3) * env
        samples.append(val)
    write_wav("portal.wav", samples)

def generate_victory():
    # Joyous fanfare: G5, C6, E6, G6 (held)
    melody = [
        (783.99, 0.12),
        (1046.50, 0.12),
        (1318.51, 0.14),
        (1567.98, 0.55),
    ]
    samples = []
    for freq, dur in melody:
        n_samples = int(dur * SAMPLE_RATE)
        phase = 0.0
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            p = t / dur
            phase += 2.0 * math.pi * freq / SAMPLE_RATE
            env = (1.0 - p * 0.7) * min(1.0, t * 150.0)
            val = (math.sin(phase) * 0.7 + math.sin(phase * 2.0) * 0.25) * env * 0.7
            samples.append(val)
    write_wav("victory.wav", samples)

def generate_ambient():
    # Warm peaceful looping ambient soundscape (4.0s seamless loop)
    duration = 4.0
    num_samples = int(duration * SAMPLE_RATE)
    samples = []
    chords = [261.63, 329.63, 392.00, 523.25]  # C Major chord pad
    phases = [0.0] * len(chords)
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        # Gentle slow modulation
        lfo = 0.8 + 0.2 * math.sin(2.0 * math.pi * 0.5 * t)
        for idx, freq in enumerate(chords):
            phases[idx] += 2.0 * math.pi * freq / SAMPLE_RATE
            val += math.sin(phases[idx]) * (0.25 / len(chords))
        samples.append(val * lfo * 0.4)
    write_wav("ambient.wav", samples)

if __name__ == "__main__":
    generate_jump()
    generate_land()
    generate_collect()
    generate_switch()
    generate_bridge()
    generate_portal()
    generate_victory()
    generate_ambient()
    print("All audio assets generated successfully!")
