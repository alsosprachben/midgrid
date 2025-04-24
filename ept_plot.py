import numpy as np
import matplotlib.pyplot as plt

def project_temperament(ratios):
    log_heights = np.log2(ratios)
    angles = [2 * np.pi * (h % 1) for h in log_heights]
    radii = [1 + h for h in log_heights]
    return angles, radii

# Constants
num_fifths = 12
s = (3**12 / 2**19)**(1.0 / 7)  # 7th root of Pythagorean comma
log_fifth = np.log2(3 / 2)

# Build ET and EPT pitch tables
et_table = [2**(n / 12) for n in range(12)]                 # ET: 2^(n/12)
ept_table = [(2 * s)**(n / 12) for n in range(12)]          # EPT: (2s)^(n/12)

# Pythagorean spiral: 12 steps modulo-wrapped, final step shows comma
pyth_ratios = [((3/2)**i) / (2 ** np.floor(np.log2((3/2)**i))) for i in range(12)]
pyth_ratios.append((3/2)**12 / (2**7) * 2)  # Raise final C one octave
angles_pyth, pyth_radii_mod1 = project_temperament(pyth_ratios)

# Fifth-walk permutation (circle of fifths)
fifth_order = [(7 * i) % 12 for i in range(12)] + [12]

#
import matplotlib
# ET ratios from permuted indices
et_ratios = [et_table[i] for i in [(7 * i) % 12 for i in range(12)]] + [et_table[0] * 2]
angles_et, et_radii_mod1 = project_temperament(et_ratios)

ept_ratios = [ept_table[i] for i in [(7 * i) % 12 for i in range(12)]] + [ept_table[0] * 2 * s]
angles_ept, ept_radii_mod1 = project_temperament(ept_ratios)

# --- Highlight intervals where ET/EPT differ by more than perceptual JND (e.g., 5 cents ~ 0.003 log2) ---
# Define perceptual JND threshold in log2 (5 cents ≈ 0.003)
jnd_threshold = 0.003
highlight_color = 'purple'
wedge_alpha = 0.35
wedge_span = np.pi * 0.0039 * 2  # approx. 5 cents in log2 each side, so 10 cents total
wedge_inner = 0.95
wedge_outer = 1.3


# Normalize all radii to lie within 1 octave
# et_radii_mod1 and ept_radii_mod1 already defined
# pyth_radii_mod1 already defined

# Just Intonation (JI): 12-note scale using low-integer harmonic ratios
just_ratios = [1/1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8]
just_table = just_ratios  # Already 12 notes, no need to extend
# Apply fifth-walk ordering
just_ratios = [just_table[i] for i in [(7 * i) % 12 for i in range(12)]] + [just_table[0] * 2]
angles_just, just_radii_mod1 = project_temperament(just_ratios)

# Plot
fig = plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)

alpha = 0.25
ax.plot(angles_et, et_radii_mod1, 'o-', label='Equal Temperament (ET)', color='red', linewidth=2, markersize=6, alpha=alpha)
ax.plot(angles_ept, ept_radii_mod1, 's--', label='Equal Pythagorean Temperament (EPT)', color='darkgreen', linewidth=2, markersize=6, alpha=alpha)
ax.plot(angles_pyth, pyth_radii_mod1, 'd-', label='Pythagorean', color='blue', linewidth=2, markersize=6, alpha=alpha)
ax.plot(angles_just, just_radii_mod1, 'x-', label='Just Intonation (JI)', color='orange', linewidth=2, markersize=6, alpha=alpha)

 # Meantone temperament (quarter-comma), symbolic: (5/4)^(1/4)
meantone_fifth = (5/4)**(1/4)

# Walk 12 meantone fifths in circle-of-fifths order, normalize into 1 octave
meantone_notes = []
for i in fifth_order:
    step = meantone_fifth ** i
    normalized = step / (2 ** np.floor(np.log2(step)))
    meantone_notes.append(normalized)

angles_meantone, radii_meantone = project_temperament(meantone_notes)

ax.plot(angles_meantone, radii_meantone, '^--', label='Meantone Temperament', color='magenta', linewidth=2, markersize=6, alpha=alpha)

 # Annotate ET curve points with note names (circle of fifths)
note_names = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
for angle, radius, name in zip(angles_et[:-1], et_radii_mod1[:-1], note_names):
    ax.text(angle, radius + 0.15, name, fontsize=11, ha='center', va='center', color='red', weight='bold')

# Draw faint wedges on the plot background for JND-exceeding intervals
for i in range(12):  # only use the 12-note comparison
    angle = angles_et[i]
    theta = np.linspace(angle - wedge_span, angle + wedge_span, 100)
    # Wedge starts at base of octave and ends at top of octave
    r_inner = np.ones_like(theta) * 1.0  # start at base of octave
    r_outer = np.ones_like(theta) * 2.0  # end at top of octave
    theta_full = np.concatenate([theta, theta[::-1]])
    r_full = np.concatenate([r_outer, r_inner[::-1]])
    ax.fill(theta_full, r_full, color=highlight_color, alpha=wedge_alpha, linewidth=0, zorder=20)

ax.set_title('Spiral of Fifths (Within 1 Octave, Enhanced Visibility)', va='bottom')
ax.set_rticks(et_table, labels=[])
ax.set_rlabel_position(0)
ax.grid(True)
# ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.1))
# Add manual legend entry for JND wedges
from matplotlib.patches import Patch
jnd_patch = Patch(color=highlight_color, alpha=wedge_alpha, label='ET JND Wedge')
ax.legend(handles=ax.get_legend_handles_labels()[0] + [jnd_patch], loc='upper right', bbox_to_anchor=(1.45, 1.1))

plt.tight_layout()
# Add more margin to ensure labels are not clipped
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
plt.savefig("spiral_fifths_within_one_octave_visible.png")
plt.show()