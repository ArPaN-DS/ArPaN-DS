import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots(figsize=(6, 4))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')
ax.axis('off')

# Data for the waveform
x = np.linspace(0, 4 * np.pi, 250)
lines = []
colors = ['#0f4c81', '#7c3aed', '#238636', '#58A6FF', '#4285F4']
for i in range(5):
    line, = ax.plot(x, np.sin(x), color=colors[i], lw=2.5, alpha=0.8)
    lines.append(line)

ax.set_ylim(-2.5, 2.5)
ax.set_xlim(0, 4 * np.pi)

# Animation function
def update(frame):
    for i, line in enumerate(lines):
        phase_shift = frame * 0.15 * (i + 1)
        # Creating a dynamic voice-like waveform with Gaussian envelope
        freq_mod = 1.0 + 0.3 * np.sin(frame * 0.1 + i)
        envelope = np.exp(-0.15 * (x - 2 * np.pi)**2)
        y = np.sin(freq_mod * 3 * x + phase_shift) * envelope
        y += 0.5 * np.sin(5 * freq_mod * x - phase_shift * 0.5) * envelope
        y *= (1.5 - 0.2 * i)
        line.set_ydata(y)
    return lines

ani = animation.FuncAnimation(fig, update, frames=60, interval=50, blit=True)
ani.save('assets/voice.gif', writer='pillow', fps=20)
plt.close(fig)
