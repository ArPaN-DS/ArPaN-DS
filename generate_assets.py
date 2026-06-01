"""
Generate all custom animated assets for GitHub profile.
Assets:
  1. architecture_flow.png  — Animated system pipeline diagram
  2. metrics_dashboard.png  — Impact metrics strip
  3. deepfake_viz.png       — Spectrogram real vs synthetic comparison
  4. conv_viz.png           — Animated chat interface
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import os

# ── Color Palette (matching profile theme) ──────────────────────
BG       = (13, 17, 23)       # #0D1117
CARD_BG  = (22, 27, 34)       # #161B22
BLUE     = (88, 166, 255)     # #58A6FF
PURPLE   = (124, 58, 237)     # #7c3aed
GREEN    = (35, 134, 54)      # #238636
NAVY     = (15, 76, 129)      # #0f4c81
RED      = (220, 38, 38)      # #dc2626
AMBER    = (180, 83, 9)       # #b45309
WHITE    = (255, 255, 255)
GRAY     = (139, 148, 158)    # #8b949e
DIM      = (48, 54, 61)       # #30363D


def get_font(size, bold=False):
    """Load a high-quality TTF font, downloading it if necessary, or falling back to system fonts."""
    import requests
    font_dir = "assets/fonts"
    os.makedirs(font_dir, exist_ok=True)
    
    font_name = "Inter-Bold.ttf" if bold else "Inter-Regular.ttf"
    font_path = os.path.join(font_dir, font_name)
    
    if not os.path.exists(font_path):
        url = f"https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/{'latin-700-normal.ttf' if bold else 'latin-400-normal.ttf'}"
        try:
            print(f"Downloading {font_name} from Google Fonts (via Fontsource)...")
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(font_path, "wb") as f:
                    f.write(r.content)
            else:
                print(f"Failed to download {font_name}: {r.status_code}")
        except Exception as e:
            print(f"Warning: Could not download {font_name}: {e}")
            
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Warning: Failed to load downloaded font {font_name}: {e}")
        
    # Fallback to system fonts
    system_paths = []
    if os.name == 'nt':  # Windows
        system_paths = [
            f"C:/Windows/Fonts/{'segoeuib' if bold else 'segoeui'}.ttf",
            f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
            f"C:/Windows/Fonts/{'consolab' if bold else 'consola'}.ttf",
        ]
    else:  # Linux (Ubuntu runner)
        system_paths = [
            f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
            f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        ]
        
    for path in system_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
                
    # Ultimate fallback
    return ImageFont.load_default()


def get_bold_font(size):
    return get_font(size, bold=True)


def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ════════════════════════════════════════════════════════════════
# 1. ARCHITECTURE FLOW DIAGRAM
# ════════════════════════════════════════════════════════════════
def generate_architecture_flow():
    W, H = 800, 340
    frames = []
    num_frames = 40
    
    stages = [
        ("🎙️", "Raw Audio", "Wiretap Input", NAVY),
        ("🔊", "VAD +\nDiarize", "Silero + pyannote", PURPLE),
        ("🧠", "Speaker\nEmbedding", "ECAPA-TDNN", BLUE),
        ("🔍", "Deepfake\nDetector", "WavLM 94M", RED),
        ("📋", "Forensic\nReport", "Court-Ready", GREEN),
    ]
    
    box_w, box_h = 120, 80
    gap = 30
    total_w = len(stages) * box_w + (len(stages) - 1) * gap
    start_x = (W - total_w) // 2
    y_center = H // 2
    
    font_sm = get_font(11)
    font_md = get_font(13)
    font_lg = get_bold_font(16)
    font_title = get_bold_font(14)
    
    for frame_i in range(num_frames):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        
        # Title
        draw.text((W // 2, 22), "System Pipeline — Voice Forensics", fill=WHITE, font=font_title, anchor="mm")
        draw.text((W // 2, 40), "How raw audio becomes court-admissible evidence", fill=GRAY, font=font_sm, anchor="mm")
        
        # Draw connections first (behind boxes)
        for i in range(len(stages) - 1):
            x1 = start_x + i * (box_w + gap) + box_w
            x2 = start_x + (i + 1) * (box_w + gap)
            y = y_center
            
            # Arrow line
            draw.line([(x1, y), (x2, y)], fill=DIM, width=2)
            # Arrowhead
            draw.polygon([(x2 - 6, y - 5), (x2, y), (x2 - 6, y + 5)], fill=DIM)
        
        # Animate "data packet" flowing through pipeline
        progress = (frame_i / num_frames) * (len(stages))
        packet_stage = int(progress)
        packet_frac = progress - packet_stage
        
        # Draw glowing connection for active stage
        if packet_stage < len(stages) - 1:
            x1 = start_x + packet_stage * (box_w + gap) + box_w
            x2 = start_x + (packet_stage + 1) * (box_w + gap)
            y = y_center
            
            # Glow line
            glow_x = x1 + (x2 - x1) * packet_frac
            for r in range(8, 0, -1):
                alpha_color = lerp_color(BG, BLUE, (8 - r) / 8 * 0.6)
                draw.ellipse([(glow_x - r, y - r), (glow_x + r, y + r)], fill=alpha_color)
            draw.ellipse([(glow_x - 4, y - 4), (glow_x + 4, y + 4)], fill=BLUE)
        
        # Draw boxes
        for i, (emoji, title, sub, color) in enumerate(stages):
            x = start_x + i * (box_w + gap)
            y = y_center - box_h // 2
            
            # Determine if this stage is "active"
            is_active = i <= packet_stage
            is_current = i == packet_stage
            
            box_color = CARD_BG if not is_active else lerp_color(CARD_BG, color, 0.3)
            border_color = DIM if not is_active else color
            
            # Draw box
            draw_rounded_rect(draw, [x, y, x + box_w, y + box_h], radius=10, fill=box_color, outline=border_color)
            
            # Glow effect for current stage
            if is_current:
                pulse = 0.5 + 0.5 * np.sin(frame_i * 0.5)
                glow_color = lerp_color(CARD_BG, color, 0.15 * pulse)
                draw_rounded_rect(draw, [x - 2, y - 2, x + box_w + 2, y + box_h + 2], radius=12, fill=None, outline=lerp_color(DIM, color, pulse))
            
            # Text
            text_color = WHITE if is_active else GRAY
            draw.text((x + box_w // 2, y + 18), emoji, fill=text_color, font=font_md, anchor="mm")
            
            # Draw title (handle multiline)
            lines = title.split("\n")
            for li, line in enumerate(lines):
                draw.text((x + box_w // 2, y + 35 + li * 14), line, fill=text_color, font=font_md, anchor="mm")
            
            draw.text((x + box_w // 2, y + box_h - 10), sub, fill=GRAY if not is_active else lerp_color(GRAY, color, 0.5), font=font_sm, anchor="mm")
        
        # Bottom note
        draw.text((W // 2, H - 18), "Dual-pass scanning  •  Zero false positives  •  Multi-hour scalable", fill=DIM, font=font_sm, anchor="mm")
        
        frames.append(img)
    
    frames[0].save(
        "assets/architecture_flow.png",
        save_all=True,
        append_images=frames[1:],
        duration=120,
        loop=0,
        optimize=True
    )
    print("✅ architecture_flow.png generated")


# ════════════════════════════════════════════════════════════════
# 2. IMPACT METRICS DASHBOARD
# ════════════════════════════════════════════════════════════════
def generate_metrics_dashboard():
    W, H = 800, 110
    frames = []
    num_frames = 30
    
    metrics = [
        ("⚡", "10+", "Production\nSystems", BLUE),
        ("🧠", "100M+", "Total Model\nParameters", PURPLE),
        ("📊", "134K+", "Training\nSamples", GREEN),
        ("🏆", "ACL+CLEF", "Research\nVenues", NAVY),
        ("⏱️", "<200ms", "Voice AI\nLatency", AMBER),
        ("🌐", "6", "Languages\nSupported", RED),
    ]
    
    card_w = 115
    card_h = 75
    total_w = len(metrics) * card_w + (len(metrics) - 1) * 10
    start_x = (W - total_w) // 2
    y = (H - card_h) // 2
    
    font_sm = get_font(10)
    font_val = get_bold_font(18)
    font_label = get_font(10)
    font_title = get_bold_font(12)
    
    for frame_i in range(num_frames):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        
        for i, (icon, value, label, color) in enumerate(metrics):
            x = start_x + i * (card_w + 10)
            
            # Staggered reveal animation
            reveal_progress = min(1.0, max(0.0, (frame_i - i * 2) / 8.0))
            
            if reveal_progress <= 0:
                continue
            
            # Card background with subtle gradient feel
            card_color = lerp_color(BG, CARD_BG, reveal_progress)
            border = lerp_color(BG, DIM, reveal_progress)
            draw_rounded_rect(draw, [x, y, x + card_w, y + card_h], radius=8, fill=card_color, outline=border)
            
            # Top accent line
            accent = lerp_color(BG, color, reveal_progress)
            draw.line([(x + 10, y + 1), (x + card_w - 10, y + 1)], fill=accent, width=2)
            
            # Icon + Value
            text_alpha = lerp_color(BG, WHITE, reveal_progress)
            dim_alpha = lerp_color(BG, GRAY, reveal_progress)
            
            draw.text((x + card_w // 2, y + 20), f"{icon} {value}", fill=text_alpha, font=font_val, anchor="mm")
            
            # Label (multiline)
            lines = label.split("\n")
            for li, line in enumerate(lines):
                draw.text((x + card_w // 2, y + 42 + li * 12), line, fill=dim_alpha, font=font_label, anchor="mm")
        
        frames.append(img)
    
    # Hold last frame longer
    for _ in range(15):
        frames.append(frames[-1])
    
    frames[0].save(
        "assets/metrics_dashboard.png",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True
    )
    print("✅ metrics_dashboard.png generated")


# ════════════════════════════════════════════════════════════════
# 3. DEEPFAKE VISUALIZATION — Spectrogram Comparison
# ════════════════════════════════════════════════════════════════
def generate_deepfake_viz():
    W, H = 360, 280
    frames = []
    num_frames = 40
    
    font_sm = get_font(10)
    font_md = get_font(12)
    font_title = get_bold_font(13)
    
    np.random.seed(42)
    
    # Generate fake "spectrogram" data
    t = np.linspace(0, 4 * np.pi, 180)
    freqs = np.linspace(0, 1, 60)
    
    for frame_i in range(num_frames):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        
        draw.text((W // 2, 14), "Real vs Synthetic Voice Analysis", fill=WHITE, font=font_title, anchor="mm")
        
        phase = frame_i * 0.2
        
        # ── Real voice spectrogram (top) ──
        draw.text((10, 32), "✅ Authentic Voice", fill=GREEN, font=font_md)
        spec_y = 48
        spec_h = 90
        spec_w = W - 20
        draw_rounded_rect(draw, [10, spec_y, 10 + spec_w, spec_y + spec_h], radius=4, fill=CARD_BG)
        
        for fi in range(50):
            for ti in range(150):
                # Natural harmonic pattern
                f_norm = fi / 50
                t_norm = ti / 150
                val = 0.5 * np.sin(3 * np.pi * f_norm + phase) * np.exp(-2 * f_norm)
                val += 0.3 * np.sin(6 * np.pi * f_norm + phase * 0.7) * np.exp(-3 * f_norm)
                val += 0.15 * np.random.random()
                val = max(0, min(1, val))
                
                # Green-tinted heatmap
                r = int(val * 35)
                g = int(val * 134 + (1 - val) * 17)
                b = int(val * 54 + (1 - val) * 23)
                
                px = 15 + int(ti * (spec_w - 10) / 150)
                py = spec_y + 5 + int(fi * (spec_h - 10) / 50)
                if 15 <= px < W - 10 and spec_y + 3 <= py < spec_y + spec_h - 3:
                    img.putpixel((px, py), (r, g, b))
        
        # ── Synthetic voice spectrogram (bottom) ──
        draw.text((10, spec_y + spec_h + 10), "🚨 Synthetic (TTS Deepfake)", fill=RED, font=font_md)
        spec_y2 = spec_y + spec_h + 26
        draw_rounded_rect(draw, [10, spec_y2, 10 + spec_w, spec_y2 + spec_h], radius=4, fill=CARD_BG)
        
        for fi in range(50):
            for ti in range(150):
                # Unnatural repeating pattern (deepfake signature)
                f_norm = fi / 50
                t_norm = ti / 150
                val = 0.6 * np.sin(4 * np.pi * f_norm) * np.sin(2 * np.pi * t_norm + phase)
                val += 0.4 * np.sin(8 * np.pi * f_norm) * 0.5  # Too-perfect harmonics
                val += 0.05 * np.random.random()  # Less noise than real
                val = max(0, min(1, abs(val)))
                
                # Red-tinted heatmap
                r = int(val * 220 + (1 - val) * 17)
                g = int(val * 38 + (1 - val) * 17)
                b = int(val * 38 + (1 - val) * 23)
                
                px = 15 + int(ti * (spec_w - 10) / 150)
                py = spec_y2 + 5 + int(fi * (spec_h - 10) / 50)
                if 15 <= px < W - 10 and spec_y2 + 3 <= py < spec_y2 + spec_h - 3:
                    img.putpixel((px, py), (r, g, b))
        
        # Scanning line animation
        scan_x = 15 + int((frame_i / num_frames) * (spec_w - 10))
        draw.line([(scan_x, spec_y + 3), (scan_x, spec_y + spec_h - 3)], fill=(*BLUE, 200), width=2)
        draw.line([(scan_x, spec_y2 + 3), (scan_x, spec_y2 + spec_h - 3)], fill=(*BLUE, 200), width=2)
        
        # Bottom verdict
        verdict_y = spec_y2 + spec_h + 8
        pulse = 0.5 + 0.5 * np.sin(frame_i * 0.3)
        verdict_color = lerp_color(GRAY, RED, pulse)
        draw.text((W // 2, verdict_y), "⚠️ Codec artifacts + unnatural harmonics detected", fill=verdict_color, font=font_sm, anchor="mm")
        
        frames.append(img)
    
    frames[0].save(
        "assets/deepfake_viz.png",
        save_all=True,
        append_images=frames[1:],
        duration=120,
        loop=0,
        optimize=True
    )
    print("✅ deepfake_viz.png generated")


# ════════════════════════════════════════════════════════════════
# 4. CONVERSATIONAL AI — Chat Interface
# ════════════════════════════════════════════════════════════════
def generate_conv_viz():
    W, H = 360, 280
    frames = []
    num_frames = 50

    font_sm = get_font(10)
    font_md = get_font(11)
    font_title = get_bold_font(12)
    
    messages = [
        ("user",  "Is this voice recording authentic?"),
        ("ai",    "Analyzing audio... Running ECAPA-TDNN speaker verification."),
        ("ai",    "🔍 Cosine similarity: 0.34 (below threshold)"),
        ("ai",    "🛡️ Deepfake probability: 91.2% — TTS synthesis detected."),
        ("ai",    "📋 Forensic report generated with evidence clips."),
    ]
    
    for frame_i in range(num_frames):
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        
        # Header bar
        draw_rounded_rect(draw, [0, 0, W, 30], radius=0, fill=CARD_BG)
        draw.text((W // 2, 15), "🤖 AI Forensic Assistant — Live Session", fill=WHITE, font=font_title, anchor="mm")
        
        # Green dot (online status) - pulsing
        pulse = 0.5 + 0.5 * np.sin(frame_i * 0.3)
        online_color = lerp_color((20, 80, 20), GREEN, pulse)
        draw.ellipse([(12, 10), (20, 18)], fill=online_color)
        
        # Determine how many messages to show based on frame
        progress = frame_i / num_frames * len(messages)
        visible_msgs = int(progress) + 1
        typing_progress = progress - int(progress)
        
        y_offset = 40
        for i in range(min(visible_msgs, len(messages))):
            role, text = messages[i]
            is_current = (i == visible_msgs - 1) and (i < len(messages))
            
            if is_current and i > 0:
                # Show partial text (typing effect)
                chars_to_show = int(len(text) * typing_progress)
                display_text = text[:chars_to_show]
                if chars_to_show < len(text):
                    cursor_blink = "█" if frame_i % 6 < 3 else " "
                    display_text += cursor_blink
            else:
                display_text = text
            
            if not display_text.strip():
                continue
            
            if role == "user":
                # User message (right-aligned, blue)
                bubble_color = NAVY
                text_x = W - 20
                anchor = "rm"
                
                # Calculate text width for bubble
                bbox = draw.textbbox((0, 0), display_text, font=font_md)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                bx = W - 25 - tw - 10
                
                draw_rounded_rect(draw, [bx, y_offset, W - 10, y_offset + th + 14], radius=10, fill=bubble_color)
                draw.text((W - 18, y_offset + th // 2 + 7), display_text, fill=WHITE, font=font_md, anchor="rm")
                y_offset += th + 22
            else:
                # AI message (left-aligned, card bg)
                bubble_color = CARD_BG
                
                # Wrap text
                max_chars = 42
                words = display_text.split()
                lines = []
                current = ""
                for w in words:
                    if len(current + " " + w) > max_chars:
                        lines.append(current)
                        current = w
                    else:
                        current = (current + " " + w).strip()
                if current:
                    lines.append(current)
                
                line_h = 14
                total_h = len(lines) * line_h + 10
                
                draw_rounded_rect(draw, [10, y_offset, W - 60, y_offset + total_h], radius=10, fill=bubble_color, outline=DIM)
                for li, line in enumerate(lines):
                    draw.text((18, y_offset + 5 + li * line_h), line, fill=WHITE, font=font_md)
                
                y_offset += total_h + 8
        
        # Typing indicator when between messages
        if visible_msgs < len(messages):
            dot_phase = frame_i % 12
            dots = "." * (dot_phase // 4 + 1)
            draw.text((18, y_offset + 5), f"AI is analyzing{dots}", fill=GRAY, font=font_sm)
        
        # Bottom status bar
        draw_rounded_rect(draw, [0, H - 22, W, H], radius=0, fill=CARD_BG)
        draw.text((W // 2, H - 11), "⚡ Sub-200ms latency  •  Gemini Live API  •  Tri-modal fusion", fill=DIM, font=font_sm, anchor="mm")
        
        frames.append(img)
    
    # Hold final frame
    for _ in range(15):
        frames.append(frames[-1])
    
    frames[0].save(
        "assets/conv_viz.png",
        save_all=True,
        append_images=frames[1:],
        duration=140,
        loop=0,
        optimize=True
    )
    print("✅ conv_viz.png generated")


# ════════════════════════════════════════════════════════════════
# RUN ALL
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    generate_architecture_flow()
    generate_metrics_dashboard()
    generate_deepfake_viz()
    generate_conv_viz()
    print("\n🎉 All assets generated!")
