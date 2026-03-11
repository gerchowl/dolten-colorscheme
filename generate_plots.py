#!/usr/bin/env python3
"""Generate high-quality palette visualization PNGs for Dalton Dark."""

import colorsys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ---------- palette ----------
PALETTE = {
    "background":  "#1b1b1b",
    "black":       "#282828",
    "selection":   "#333333",
    "red":         "#d85050",
    "green":       "#5b914e",
    "yellow":      "#c4c40c",
    "blue":        "#7aa2f7",
    "magenta":     "#a050d0",
    "cyan":        "#56717f",
    "white":       "#b8b8b8",
    "br-black":    "#3c3c3c",
    "br-red":      "#f07068",
    "br-green":    "#88b97d",
    "br-yellow":   "#eded02",
    "br-blue":     "#97b1f1",
    "br-magenta":  "#c070f0",
    "br-cyan":     "#6691a7",
    "br-white":    "#d8d8d8",
    "foreground":  "#c8c9cc",
}

# Friendly names
NAMES = {
    "background": "background", "black": "black", "selection": "selection",
    "red": "punch red", "green": "dark grass", "yellow": "vivid gold",
    "blue": "clear blue", "magenta": "vivid violet", "cyan": "steel teal",
    "white": "pale silver", "br-black": "ash", "br-red": "hot cherry",
    "br-green": "soft lime", "br-yellow": "neon gold", "br-blue": "soft periwinkle",
    "br-magenta": "hot violet", "br-cyan": "slate blue", "br-white": "bright mist",
    "foreground": "foreground",
}

BG = "#1b1b1b"
FG = "#c8c9cc"

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def relative_luminance(r, g, b):
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def contrast_ratio(l1, l2):
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)

# Foreground colors (skip bg-like colors)
FG_KEYS = [
    "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "br-red", "br-green", "br-yellow", "br-blue", "br-magenta", "br-cyan", "br-white",
    "foreground",
]

# All colors for matrix (including bg-like)
MATRIX_KEYS = [
    "background", "black", "selection", "br-black",
    "cyan", "magenta", "red", "green", "br-cyan", "br-magenta", "br-red",
    "blue", "br-blue", "br-green", "white", "yellow", "foreground", "br-white", "br-yellow",
]

def setup_fig(w, h):
    fig = plt.figure(figsize=(w, h), facecolor=BG)
    return fig


# ==================== 1. SWATCHES ====================
def gen_swatches():
    keys = list(PALETTE.keys())
    n = len(keys)
    fig, ax = plt.subplots(figsize=(14, 2.8), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.5, 1.5)
    ax.axis("off")

    for i, k in enumerate(keys):
        color = PALETTE[k]
        rect = FancyBboxPatch((i - 0.4, 0.2), 0.8, 0.9, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor="#555555", linewidth=0.8)
        ax.add_patch(rect)
        ax.text(i, 0.05, PALETTE[k], ha="center", va="top", fontsize=6.5,
                color=FG, family="monospace")
        ax.text(i, -0.15, k, ha="center", va="top", fontsize=6, color="#888888",
                family="monospace")

    fig.tight_layout(pad=0.5)
    fig.savefig("img/swatches.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  swatches.png")


# ==================== 2. LUMINANCE ====================
def gen_luminance():
    lum_data = []
    for k in FG_KEYS:
        rgb = hex_to_rgb(PALETTE[k])
        lum = relative_luminance(*rgb)
        lum_data.append((k, lum, PALETTE[k]))

    lum_data.sort(key=lambda x: x[1])

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG)
    ax.set_facecolor(BG)

    for i, (name, lum, color) in enumerate(lum_data):
        ax.barh(i, lum, height=0.7, color=color, edgecolor="#444444", linewidth=0.5)
        label = f"{name} ({NAMES[name]})  L={lum:.3f}"
        text_x = lum + 0.01 if lum < 0.6 else lum - 0.01
        ha = "left" if lum < 0.6 else "right"
        text_color = FG if lum < 0.6 else BG
        ax.text(text_x, i, label, va="center", ha=ha, fontsize=7,
                color=text_color, family="monospace")

    ax.set_xlim(0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("Relative Luminance", color="#888888", fontsize=9)
    ax.tick_params(colors="#666666")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#444444")

    fig.tight_layout(pad=1)
    fig.savefig("img/luminance.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  luminance.png")


# ==================== 3. STRIPS ====================
def gen_strips():
    normal = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    bright = ["br-black", "br-red", "br-green", "br-yellow", "br-blue", "br-magenta", "br-cyan", "br-white"]

    fig, axes = plt.subplots(2, 1, figsize=(10, 2), facecolor=BG)

    for ax, keys, title in [(axes[0], normal, "Normal"), (axes[1], bright, "Bright")]:
        ax.set_facecolor(BG)
        ax.set_xlim(0, len(keys))
        ax.set_ylim(0, 1)
        ax.axis("off")

        for i, k in enumerate(keys):
            color = PALETTE[k]
            rect = plt.Rectangle((i, 0), 1, 1, facecolor=color)
            ax.add_patch(rect)
            # Label
            rgb = hex_to_rgb(color)
            lum = relative_luminance(*rgb)
            text_color = "#000000" if lum > 0.3 else "#ffffff"
            label = k.replace("br-", "")
            ax.text(i + 0.5, 0.6, label, ha="center", va="center", fontsize=7,
                    color=text_color, family="monospace", weight="bold")
            ax.text(i + 0.5, 0.35, PALETTE[k], ha="center", va="center", fontsize=6,
                    color=text_color, family="monospace")

        ax.text(-0.1, 0.5, title, ha="right", va="center", fontsize=8,
                color="#888888", family="monospace")

    fig.tight_layout(pad=0.5)
    fig.savefig("img/strips.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  strips.png")


# ==================== 4. COLOR WHEEL ====================
def gen_wheel():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG, subplot_kw={"projection": "polar"})
    ax.set_facecolor(BG)

    # Draw HSL hue ring as background
    theta_bg = np.linspace(0, 2 * np.pi, 360)
    r_inner, r_outer = 0.85, 1.05
    for t in theta_bg:
        hue = (np.degrees(t) % 360) / 360.0
        rgb = colorsys.hls_to_rgb(hue, 0.5, 0.7)
        ax.bar(t, r_outer - r_inner, bottom=r_inner, width=2 * np.pi / 360,
               color=rgb, edgecolor="none", alpha=0.3)

    # Plot palette colors
    for k in FG_KEYS:
        rgb = hex_to_rgb(PALETTE[k])
        h, l, s = colorsys.rgb_to_hls(*rgb)
        theta = h * 2 * np.pi
        r = s
        size = 80 + 300 * l  # size proportional to lightness
        ax.scatter(theta, r, c=[PALETTE[k]], s=size, edgecolors="#ffffff55",
                   linewidths=1.5, zorder=5)
        # Label offset
        label_r = r + 0.08
        ax.text(theta, label_r, k, ha="center", va="center", fontsize=6,
                color=FG, family="monospace")

    ax.set_ylim(0, 1.1)
    ax.set_rticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=6, color="#666666")
    ax.set_rlabel_position(45)
    ax.grid(color="#333333", linewidth=0.5)
    ax.tick_params(colors="#666666", labelsize=7)
    ax.spines["polar"].set_color("#444444")

    fig.tight_layout(pad=1)
    fig.savefig("img/wheel.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  wheel.png")


# ==================== 5. HUE × SATURATION ====================
def gen_hs():
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG)
    ax.set_facecolor(BG)

    # HSL gradient background (L=50%)
    grad = np.zeros((100, 360, 3))
    for x in range(360):
        for y in range(100):
            s = y / 100.0
            rgb = colorsys.hls_to_rgb(x / 360.0, 0.5, s)
            grad[y, x] = rgb
    ax.imshow(grad, origin="lower", extent=[0, 360, 0, 100], aspect="auto", alpha=0.25)

    # Plot colors
    for k in FG_KEYS:
        rgb = hex_to_rgb(PALETTE[k])
        h, l, s = colorsys.rgb_to_hls(*rgb)
        hue_deg = h * 360
        sat_pct = s * 100
        ax.scatter(hue_deg, sat_pct, c=[PALETTE[k]], s=200, edgecolors="#ffffff55",
                   linewidths=1.5, zorder=5)
        ax.annotate(k, (hue_deg, sat_pct), textcoords="offset points",
                    xytext=(8, -4), fontsize=7, color=FG, family="monospace")

    ax.set_xlim(0, 360)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Hue (°)", color="#888888", fontsize=9)
    ax.set_ylabel("Saturation (%)", color="#888888", fontsize=9)
    ax.set_xticks(range(0, 361, 30))
    ax.tick_params(colors="#666666", labelsize=7)
    ax.grid(color="#333333", linewidth=0.5, alpha=0.5)
    for spine in ax.spines.values():
        spine.set_color("#444444")

    fig.tight_layout(pad=1)
    fig.savefig("img/hue-saturation.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  hue-saturation.png")


# ==================== 6. HUE × LIGHTNESS ====================
def gen_hl():
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG)
    ax.set_facecolor(BG)

    # HSL gradient background (S=70%)
    grad = np.zeros((100, 360, 3))
    for x in range(360):
        for y in range(100):
            l = y / 100.0
            rgb = colorsys.hls_to_rgb(x / 360.0, l, 0.7)
            grad[y, x] = rgb
    ax.imshow(grad, origin="lower", extent=[0, 360, 0, 100], aspect="auto", alpha=0.25)

    # Plot colors
    for k in FG_KEYS:
        rgb = hex_to_rgb(PALETTE[k])
        h, l, s = colorsys.rgb_to_hls(*rgb)
        hue_deg = h * 360
        light_pct = l * 100
        ax.scatter(hue_deg, light_pct, c=[PALETTE[k]], s=200, edgecolors="#ffffff55",
                   linewidths=1.5, zorder=5)
        ax.annotate(k, (hue_deg, light_pct), textcoords="offset points",
                    xytext=(8, -4), fontsize=7, color=FG, family="monospace")

    ax.set_xlim(0, 360)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Hue (°)", color="#888888", fontsize=9)
    ax.set_ylabel("Lightness (%)", color="#888888", fontsize=9)
    ax.set_xticks(range(0, 361, 30))
    ax.tick_params(colors="#666666", labelsize=7)
    ax.grid(color="#333333", linewidth=0.5, alpha=0.5)
    for spine in ax.spines.values():
        spine.set_color("#444444")

    fig.tight_layout(pad=1)
    fig.savefig("img/hue-lightness.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  hue-lightness.png")


# ==================== 7. CONTRAST MATRIX ====================
def gen_matrix():
    keys = MATRIX_KEYS
    n = len(keys)

    fig, ax = plt.subplots(figsize=(14, 14), facecolor=BG)
    ax.set_facecolor(BG)

    # Compute luminances
    lums = {}
    for k in keys:
        lums[k] = relative_luminance(*hex_to_rgb(PALETTE[k]))

    # Sort by luminance for matrix ordering
    sorted_keys = sorted(keys, key=lambda k: lums[k])

    for i, bg_key in enumerate(sorted_keys):
        for j, fg_key in enumerate(sorted_keys):
            bg_color = PALETTE[bg_key]
            fg_color = PALETTE[fg_key]
            ratio = contrast_ratio(lums[bg_key], lums[fg_key])

            # Cell background
            rect = plt.Rectangle((j, n - 1 - i), 1, 1, facecolor=bg_color,
                                 edgecolor="#333333", linewidth=0.5)
            ax.add_patch(rect)

            # Ratio text
            if ratio >= 4.5:
                weight = "bold"
                alpha = 1.0
            elif ratio >= 3.0:
                weight = "normal"
                alpha = 0.8
            else:
                weight = "normal"
                alpha = 0.4

            ax.text(j + 0.5, n - 1 - i + 0.5, f"{ratio:.1f}",
                    ha="center", va="center", fontsize=6, family="monospace",
                    color=fg_color, weight=weight, alpha=alpha)

    # Labels
    for i, k in enumerate(sorted_keys):
        # Row labels (left - background color)
        ax.text(-0.1, n - 1 - i + 0.5, k, ha="right", va="center",
                fontsize=7, color=PALETTE[k], family="monospace")
        # Column labels (top - foreground color)
        ax.text(i + 0.5, n + 0.1, k, ha="center", va="bottom",
                fontsize=7, color=PALETTE[k], family="monospace",
                rotation=45, rotation_mode="anchor")

    ax.set_xlim(-2, n)
    ax.set_ylim(-1.5, n + 2)
    ax.axis("off")

    # Legend
    ax.text(0, -0.5, "BOLD = WCAG AA (≥4.5:1)    normal = weak (≥3.0:1)    dim = fail (<3.0:1)",
            fontsize=7, color="#888888", family="monospace")
    ax.text(0, -1.0, "Rows = background color    Columns = foreground (text) color",
            fontsize=7, color="#888888", family="monospace")

    fig.tight_layout(pad=1)
    fig.savefig("img/matrix.png", dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("  matrix.png")


# ==================== RUN ALL ====================
if __name__ == "__main__":
    import os
    os.makedirs("img", exist_ok=True)
    print("Generating plots...")
    gen_swatches()
    gen_luminance()
    gen_strips()
    gen_wheel()
    gen_hs()
    gen_hl()
    gen_matrix()
    print("Done.")
