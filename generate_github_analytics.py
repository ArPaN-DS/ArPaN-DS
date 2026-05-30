"""
Generate GitHub Analytics Dashboard
- Total Contributions (with accurate count from GitHub since account creation)
- Current Streak (with correct active-day calculation)
- Longest Streak (with correct active-day calculation)
- Contribution Graph (configurable timeline: 30, 60, 120 days)
"""

import requests
import json
from datetime import datetime, timedelta
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# ── Configuration ──────────────────────────────────────────────
GITHUB_USERNAME = "ArPaN-DS"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)  # Set via environment variable or repository secret
DAYS_BACK = 90  # Change to 30, 60, or 120
OUTPUT_PATH = "assets/github_analytics.png"

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


def get_font(size):
    """Try to load a decent font, fall back to default."""
    font_paths = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def get_bold_font(size):
    font_paths = [
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return get_font(size)


def fetch_github_contributions(username, token=None):
    """
    Fetch GitHub contribution data using GraphQL API.
    Iterates through all years since account creation (2024) to get all-time contributions.
    """
    url = "https://api.github.com/graphql"
    
    start_year = 2024
    current_year = datetime.now().year
    
    contributions_by_date = {}
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    for year in range(start_year, current_year + 1):
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"
        
        query = """query ($userName: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $userName) {
            contributionsCollection(from: $from, to: $to) {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }"""
        
        variables = {"userName": username, "from": from_date, "to": to_date}
        payload = {"query": query, "variables": variables}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"⚠️ GraphQL Error for {year}: {data['errors']}")
                    continue
                
                user_data = data.get("data", {}).get("user", {})
                if not user_data:
                    continue
                    
                contrib_coll = user_data.get("contributionsCollection", {})
                cal = contrib_coll.get("contributionCalendar", {})
                
                weeks = cal.get("weeks", [])
                for week in weeks:
                    for day in week.get("contributionDays", []):
                        date_str = day["date"]
                        # Filter to only keep dates since account creation (Dec 7, 2024)
                        if date_str >= "2024-12-07":
                            contributions_by_date[date_str] = day["contributionCount"]
            else:
                print(f"⚠️ API Error for {year}: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error fetching data for {year}: {e}")
            
    if not contributions_by_date:
        return None
        
    total_contributions = sum(contributions_by_date.values())
    
    return {
        "by_date": contributions_by_date,
        "total": total_contributions
    }


def calculate_streaks(contributions_by_date):
    """Calculate current and longest streaks based on active days (>0 contributions)."""
    # Filter dates with contributions > 0
    active_dates = sorted([
        datetime.strptime(d, "%Y-%m-%d").date()
        for d, count in contributions_by_date.items()
        if count > 0
    ])
    
    if not active_dates:
        return {"current": 0, "longest": 0, "current_range": None, "longest_range": None}
    
    # Calculate longest streak
    longest_streak = 1
    longest_start = active_dates[0]
    longest_end = active_dates[0]
    
    current_longest = 1
    current_longest_start = active_dates[0]
    
    for i in range(1, len(active_dates)):
        prev_date = active_dates[i - 1]
        curr_date = active_dates[i]
        
        if (curr_date - prev_date).days == 1:
            current_longest += 1
            if current_longest > longest_streak:
                longest_streak = current_longest
                longest_start = current_longest_start
                longest_end = curr_date
        elif (curr_date - prev_date).days > 1:
            current_longest = 1
            current_longest_start = curr_date
            
    # Calculate current streak
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    current_streak = 0
    current_start = None
    current_end = None
    
    # Check if there is a contribution today or yesterday to start the current streak
    if active_dates[-1] == today or active_dates[-1] == yesterday:
        current_streak = 1
        current_end = active_dates[-1]
        current_start = active_dates[-1]
        
        # Go backwards from the end of the list
        for i in range(len(active_dates) - 2, -1, -1):
            curr_date = active_dates[i]
            prev_date = active_dates[i + 1]
            
            if (prev_date - curr_date).days == 1:
                current_streak += 1
                current_start = curr_date
            else:
                break
                
    # Format ranges
    current_range = f"{current_start.strftime('%b %d')} - {current_end.strftime('%b %d')}" if current_streak > 0 else "None"
    longest_range = f"{longest_start.strftime('%b %d')} - {longest_end.strftime('%b %d')}" if longest_streak > 0 else "None"
    
    # If the streak is 1 day, just show that day
    if current_streak == 1:
        current_range = current_start.strftime('%b %d')
    if longest_streak == 1:
        longest_range = longest_start.strftime('%b %d')
        
    return {
        "current": current_streak,
        "longest": longest_streak,
        "current_range": current_range,
        "longest_range": longest_range
    }


def draw_vertical_text(draw, img, text, pos, fill, font):
    """Draw text rotated 90 degrees counter-clockwise."""
    txt_img = Image.new("RGBA", (200, 40), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((100, 20), text, fill=fill, font=font, anchor="mm")
    rotated = txt_img.rotate(90, expand=True)
    px = pos[0] - rotated.width // 2
    py = pos[1] - rotated.height // 2
    img.paste(rotated, (px, py), rotated)


def generate_github_analytics(username, days_back=90, token=None):
    """Generate GitHub Analytics dashboard image."""
    print(f"📊 Generating GitHub Analytics for {username}...")
    print(f"   Timeline: Last {days_back} days")
    print(f"   Token present: {bool(token)}")
    
    # Fetch contributions
    contrib_data = fetch_github_contributions(username, token)
    
    if contrib_data is None or not contrib_data.get("by_date"):
        print("⚠️  Could not fetch GitHub data. Using demo data.")
        contrib_data = generate_demo_data(days_back)
    
    contributions_by_date = contrib_data["by_date"]
    total_contributions = contrib_data["total"]
    
    # Calculate streaks
    streaks = calculate_streaks(contributions_by_date)
    
    # Image dimensions (Cropped height for compact layout, removing duplicate title)
    W, H = 1200, 680
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_metric = get_bold_font(60)
    font_metric_sm = get_bold_font(38)
    font_label = get_bold_font(16)
    font_sm = get_font(14)
    font_xs = get_font(12)
    
    # Top metrics row (shifted up to y = 40)
    metrics_y = 40
    metric_width = 280
    metric_height = 150
    metrics_x_positions = [120, 460, 800]
    
    # ── Card 1: Total Contributions ──
    x1 = metrics_x_positions[0]
    draw.rounded_rectangle(
        [(x1, metrics_y), (x1 + metric_width, metrics_y + metric_height)],
        radius=15,
        fill=CARD_BG,
        outline=DIM,
        width=2
    )
    draw.text((x1 + metric_width // 2, metrics_y + 50), str(total_contributions), fill=WHITE, font=font_metric, anchor="mm")
    draw.text((x1 + metric_width // 2, metrics_y + 98), "Total Contributions", fill=WHITE, font=font_label, anchor="mm")
    draw.text((x1 + metric_width // 2, metrics_y + 122), "Dec 7, 2024 - Present", fill=GRAY, font=font_xs, anchor="mm")
    
    # ── Card 2: Current Streak (Circular progress design) ──
    x2 = metrics_x_positions[1]
    draw.rounded_rectangle(
        [(x2, metrics_y), (x2 + metric_width, metrics_y + metric_height)],
        radius=15,
        fill=CARD_BG,
        outline=DIM,
        width=2
    )
    cx, cy = x2 + metric_width // 2, metrics_y + metric_height // 2
    r = 34
    circle_y = cy - 18
    # Inactive track
    draw.ellipse([(cx - r, circle_y - r), (cx + r, circle_y + r)], outline=DIM, width=4)
    # Active arc (glowing purple to blue gradient feel)
    draw.arc([(cx - r, circle_y - r), (cx + r, circle_y + r)], start=-90, end=90 if streaks["current"] > 0 else -90, fill=PURPLE, width=4)
    draw.arc([(cx - r, circle_y - r), (cx + r, circle_y + r)], start=90, end=270 if streaks["current"] > 0 else 90, fill=BLUE, width=4)
    
    # Custom double-layered flame shape (Orange-500 outer, Yellow-500 inner)
    flame_y = circle_y - r - 6
    outer_points = [
        (cx, flame_y - 12),
        (cx + 6, flame_y - 5),
        (cx + 4, flame_y - 1),
        (cx + 7, flame_y + 4),
        (cx, flame_y + 8),
        (cx - 7, flame_y + 4),
        (cx - 4, flame_y - 1),
        (cx - 6, flame_y - 5),
    ]
    inner_points = [
        (cx, flame_y - 6),
        (cx + 3, flame_y - 2),
        (cx + 2, flame_y + 1),
        (cx + 4, flame_y + 3),
        (cx, flame_y + 6),
        (cx - 4, flame_y + 3),
        (cx - 2, flame_y + 1),
        (cx - 3, flame_y - 2),
    ]
    draw.polygon(outer_points, fill=(249, 115, 22))  # Orange
    draw.polygon(inner_points, fill=(234, 179, 8))   # Yellow
    
    # Text inside the circle
    draw.text((cx, circle_y + 2), str(streaks["current"]), fill=WHITE, font=font_metric_sm, anchor="mm")
    # Text below circle
    draw.text((cx, cy + 40), "Current Streak", fill=BLUE, font=font_label, anchor="mm")
    draw.text((cx, cy + 60), streaks["current_range"] if streaks["current_range"] else "None", fill=GRAY, font=font_xs, anchor="mm")
    
    # ── Card 3: Longest Streak ──
    x3 = metrics_x_positions[2]
    draw.rounded_rectangle(
        [(x3, metrics_y), (x3 + metric_width, metrics_y + metric_height)],
        radius=15,
        fill=CARD_BG,
        outline=DIM,
        width=2
    )
    draw.text((x3 + metric_width // 2, metrics_y + 50), str(streaks["longest"]), fill=BLUE, font=font_metric, anchor="mm")
    draw.text((x3 + metric_width // 2, metrics_y + 98), "Longest Streak", fill=WHITE, font=font_label, anchor="mm")
    draw.text((x3 + metric_width // 2, metrics_y + 122), streaks["longest_range"] if streaks["longest_range"] else "None", fill=GRAY, font=font_xs, anchor="mm")
    
    # ── Line Graph Section (Shifted up to y0 = 240, y1 = 580) ──
    graph_y0 = 240
    graph_y1 = 580
    graph_x0 = 120
    graph_x1 = 1080
    graph_w = graph_x1 - graph_x0
    graph_h = graph_y1 - graph_y0
    
    # Graph Title
    draw.text((W // 2, graph_y0 - 25), f"{username}'s Contribution Graph", fill=WHITE, font=font_label, anchor="mm")
    
    # Gather contribution data list for the last days_back days
    today = datetime.now().date()
    contributions_list = []
    dates_list = []
    for i in range(days_back):
        date = today - timedelta(days=days_back - 1 - i)
        date_str = date.strftime("%Y-%m-%d")
        count = contributions_by_date.get(date_str, 0)
        contributions_list.append(count)
        dates_list.append(date)
        
    max_val = max(contributions_list) if contributions_list else 0
    if max_val == 0:
        max_val = 1
    y_max = ((max_val // 10) + 1) * 10 if max_val > 10 else 10
    
    # Draw horizontal dotted grid lines
    num_grid_lines = 5
    for i in range(num_grid_lines):
        val = int(i * y_max / (num_grid_lines - 1))
        y = graph_y1 - (val / y_max) * graph_h
        # Dotted line
        for x in range(graph_x0, graph_x1, 8):
            draw.line([(x, y), (x + 4, y)], fill=DIM, width=1)
        # Y label
        draw.text((graph_x0 - 20, y), str(val), fill=GRAY, font=font_xs, anchor="rm")
        
    # Vertical "Contributions" text on the left
    draw_vertical_text(draw, img, "Contributions", (graph_x0 - 60, graph_y0 + graph_h // 2), fill=GRAY, font=font_xs)
    
    # Map points to screen coordinates
    points = []
    x_spacing = graph_w / (days_back - 1)
    for i, count in enumerate(contributions_list):
        x = graph_x0 + i * x_spacing
        y = graph_y1 - (count / y_max) * graph_h
        points.append((x, y))
        
    # 1. Layered Fading Gradient under the curve
    gradient_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient_overlay)
    for k in range(6):
        factor = (k + 1) / 6.0  # opacity layer heights from 1/6 to 6/6
        layer_points = []
        for x, y in points:
            h = graph_y1 - y
            y_layer = graph_y1 - h * factor
            layer_points.append((x, y_layer))
        
        layer_polygon = [(graph_x0, graph_y1)] + layer_points + [(graph_x1, graph_y1)]
        gradient_draw.polygon(layer_polygon, fill=(124, 58, 237, 6))
    img.paste(gradient_overlay, (0, 0), gradient_overlay)
    
    # 2. Dual-Pass Glowing Line Chart (Pass 1: wide glow overlay)
    glow_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_overlay)
    glow_draw.line(points, fill=(124, 58, 237, 45), width=7)
    img.paste(glow_overlay, (0, 0), glow_overlay)
    
    # 3. Dual-Pass Glowing Line Chart (Pass 2: sharp electric violet line)
    draw.line(points, fill=(168, 85, 247), width=3)
    
    # 4. Glowing dual-circle data markers
    point_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    point_draw = ImageDraw.Draw(point_overlay)
    for x, y in points:
        # Outer glow
        point_draw.ellipse([(x - 4.5, y - 4.5), (x + 4.5, y + 4.5)], fill=(168, 85, 247, 100))
    img.paste(point_overlay, (0, 0), point_overlay)
    
    for x, y in points:
        # Inner white core with purple outline
        draw.ellipse([(x - 2.5, y - 2.5), (x + 2.5, y + 2.5)], fill=WHITE, outline=(168, 85, 247), width=1)
        
    # X-axis base line
    draw.line([(graph_x0, graph_y1), (graph_x1, graph_y1)], fill=DIM, width=2)
    
    # X-axis month labels and tick marks
    last_month = None
    last_label_idx = -99
    for i, date in enumerate(dates_list):
        month_str = date.strftime("%b")
        if month_str != last_month:
            # Check if this new month label is too close to the last one (e.g. less than 10 days)
            if i - last_label_idx >= 10:
                x = points[i][0]
                # Draw tick
                draw.line([(x, graph_y1), (x, graph_y1 + 5)], fill=GRAY, width=1)
                # Draw month text
                draw.text((x, graph_y1 + 15), month_str, fill=GRAY, font=font_xs, anchor="mt")
                last_month = month_str
                last_label_idx = i
            
    # Sublabels on X-axis sides
    draw.text((graph_x0, graph_y1 + 35), f"{days_back} Days Ago", fill=GRAY, font=font_xs, anchor="lt")
    draw.text((graph_x1, graph_y1 + 35), "Today", fill=GRAY, font=font_xs, anchor="rt")
    
    # X-axis title
    draw.text((W // 2, graph_y1 + 45), "Days", fill=GRAY, font=font_sm, anchor="mm")
    
    # Footer
    footer_y = H - 25
    draw.text((W // 2, footer_y), f"Generated on {datetime.now().strftime('%B %d, %Y')}", fill=DIM, font=font_xs, anchor="mm")
    
    # Save image
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img.save(OUTPUT_PATH)
    print(f"✅ GitHub Analytics generated: {OUTPUT_PATH}")
    print(f"   Total Contributions: {total_contributions}")
    print(f"   Current Streak: {streaks['current']} days")
    print(f"   Longest Streak: {streaks['longest']} days")


def generate_demo_data(days_back):
    """Generate demo contribution data for testing."""
    contributions_by_date = {}
    today = datetime.now().date()
    
    start_date = datetime.strptime("2024-12-07", "%Y-%m-%d").date()
    total_days = (today - start_date).days + 1
    
    # Simulate a lower density of contributions overall (e.g., ~350 contributions over 540 days)
    np.random.seed(42)
    for i in range(total_days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 15% chance of contribution on any day, with 1 to 5 contributions
        if np.random.random() < 0.15:
            contributions_by_date[date_str] = int(np.random.randint(1, 6))
        else:
            contributions_by_date[date_str] = 0
            
    return {
        "by_date": contributions_by_date,
        "total": sum(contributions_by_date.values())
    }


if __name__ == "__main__":
    generate_github_analytics(GITHUB_USERNAME, days_back=DAYS_BACK, token=GITHUB_TOKEN)
