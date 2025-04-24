import numpy as np
import matplotlib.pyplot as plt

def project_temperament(ratios):
    log_heights = np.log2(ratios)
    angles = [2 * np.pi * (h % 1) for h in log_heights]
    radii = [1 + h for h in log_heights]
    return angles, radii

# Constants (shared)
num_fifths = 12
s = (3**12 / 2**19)**(1.0 / 7)  # 7th root of Pythagorean comma
log_fifth = np.log2(3 / 2)
# Fifth-walk permutation (circle of fifths)
fifth_order = [(7 * i) % 12 for i in range(12)] + [12]

def plot_temperament_spiral(tuning_defs, filename="spiral_fifths.png", title="Spiral of Fifths"):
    import matplotlib
    from matplotlib.patches import Patch
    # --- Highlight intervals where ET/EPT differ by more than perceptual JND (e.g., 5 cents ~ 0.003 log2) ---
    # Define perceptual JND threshold in log2 (5 cents ≈ 0.003)
    jnd_threshold = 0.003
    highlight_color = 'gray'
    wedge_alpha = 0.15
    wedge_span = np.pi * 0.0039 * 2  # approx. 5 cents in log2 each side, so 10 cents total
    wedge_inner = 0.95
    wedge_outer = 1.3
    alpha = 0.25

    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    et_table = [2**(n / 12) for n in range(12)]
    # Note names for ET (circle of fifths order)
    note_names = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

    # Plot all tunings in the list
    for label, color, marker, line_style, ratios in tuning_defs:
        angles, radii = project_temperament(ratios)
        # Compose marker/line_style string
        plot_style = marker + line_style
        ax.plot(angles, radii, plot_style, label=label, color=color, linewidth=2, markersize=6, alpha=alpha)

    # Always compute ET angles for wedges and labels
    et_base_table = [2**(n / 12) for n in range(12)]
    et_ratios_for_wedges = [et_base_table[i] for i in [(7 * i) % 12 for i in range(12)]]
    et_angles, et_radii = project_temperament(et_ratios_for_wedges)

    for i in range(12):
        angle = et_angles[i]
        theta = np.linspace(angle - wedge_span, angle + wedge_span, 100)
        r_inner = np.ones_like(theta) * 1.0
        r_outer = np.ones_like(theta) * 2.0
        theta_full = np.concatenate([theta, theta[::-1]])
        r_full = np.concatenate([r_outer, r_inner[::-1]])
        ax.fill(theta_full, r_full, color=highlight_color, alpha=wedge_alpha, linewidth=0, zorder=20)

    # Draw ET note labels once, outside the wedges
    for i in range(12):
        angle = et_angles[i]
        outer_radius = 2.10
        ax.text(angle, outer_radius, note_names[i], fontsize=11, ha='center', va='center', color='black', weight='bold')


    ax.set_title(title + ' (Within 1 Octave)', va='bottom')

    # Draw custom radial guide rings at log2 positions of the 12 ET notes
    for r in [1 + np.log2(v) for v in et_table]:
        ax.plot(np.linspace(0, 2*np.pi, 500), [r]*500, linestyle=':', color='gray', linewidth=0.5, zorder=0)

    ax.set_rlabel_position(0)
    ax.set_xticks([])
    ax.set_yticklabels([])
    ax.grid(True)
    # Add manual legend entry for JND wedges
    jnd_patch = Patch(color=highlight_color, alpha=wedge_alpha, label='ET JND Wedge')
    ax.legend(handles=ax.get_legend_handles_labels()[0] + [jnd_patch], loc='upper right', bbox_to_anchor=(1.45, 1.1))
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.savefig(filename)
    plt.show()


# --- Prepare tuning systems and call the plot function ---

# ET and EPT pitch tables
et_table = [2**(n / 12) for n in range(12)]                 # ET: 2^(n/12)
ept_table = [(2 * s)**(n / 12) for n in range(12)]          # EPT: (2s)^(n/12)

# ET ratios from permuted indices
et_ratios = [et_table[i] for i in [(7 * i) % 12 for i in range(12)]] + [et_table[0] * 2]

# EPT ratios from permuted indices
ept_ratios = [ept_table[i] for i in [(7 * i) % 12 for i in range(12)]] + [ept_table[0] * 2 * s]

# Pythagorean spiral: 12 steps modulo-wrapped, final step shows comma
pyth_ratios = [((3/2)**i) / (2 ** np.floor(np.log2((3/2)**i))) for i in range(12)]
pyth_ratios.append((3/2)**12 / (2**7) * 2)  # Raise final C one octave

# Just Intonation (JI): 12-note scale using low-integer harmonic ratios
just_table = [1/1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8]
just_ratios = [just_table[i] for i in [(7 * i) % 12 for i in range(12)]] + [just_table[0] * 2]

# Meantone temperament (quarter-comma), symbolic: (5/4)^(1/4)
meantone_fifth = (5/4)**(1/4)
meantone_notes = []
for i in fifth_order:
    step = meantone_fifth ** i
    normalized = step / (2 ** np.floor(np.log2(step)))
    meantone_notes.append(normalized)


if __name__ == "__main__":
    plot_temperament_spiral([
        ("Equal Temperament (ET)", "red", "o", "-", et_ratios),
        ("Equal Pythagorean Temperament (EPT)", "darkgreen", "s", "--", ept_ratios),
        ("Pythagorean", "blue", "d", "-", pyth_ratios),
        ("Just Intonation (JI)", "orange", "x", "-", just_ratios),
        ("Meantone Temperament", "magenta", "^", "--", meantone_notes),
    ], filename="spiral_fifths_within_one_octave_visible.png")