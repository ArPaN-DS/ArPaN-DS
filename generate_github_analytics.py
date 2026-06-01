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
DAYS_BACK = 60  # Change to 30, 60, or 120
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
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def get_bold_font(size):
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/consolab.ttf",
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


def generate_github_analytics(username, days_back=60, token=None):
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
    
    # Image dimensions (Spacious 1200 x 800 layout)
    W, H = 1200, 800
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_title = get_bold_font(32)
    font_metric = get_bold_font(120)
    font_metric_sm = get_bold_font(80)
    font_label = get_bold_font(26)
    font_sm = get_font(14)
    font_xs = get_font(12)
    
    # Top title "GitHub Analytics"
    draw.text((W // 2, 55), "GitHub Analytics", fill=WHITE, font=font_title, anchor="mm")
    
    # Horizontal rule separator under title
    draw.line([(100, 100), (W - 100, 100)], fill=DIM, width=1)
    
    # Metrics Row Positions (naked layout, floating text)
    cx1, cx2, cx3 = 270, 600, 930
    cy = 200
    
    # Vertical separators between metrics
    draw.line([(440, 135), (440, 265)], fill=DIM, width=1)
    draw.line([(760, 135), (760, 265)], fill=DIM, width=1)
    
    # ── Left Metric: Total Contributions (Blue value, white label) ──
    draw.text((cx1, cy - 15), str(total_contributions), fill=BLUE, font=font_metric, anchor="mm")
    draw.text((cx1, cy + 32), "Total Contributions", fill=WHITE, font=font_label, anchor="mm")
    draw.text((cx1, cy + 58), "Dec 7, 2024 - Present", fill=GRAY, font=font_xs, anchor="mm")
    
    # ── Middle Metric: Current Streak (Circular progress ring with flame outline) ──
    r = 38
    circle_y = cy - 20
    # Ring
    draw.ellipse([(cx2 - r, circle_y - r), (cx2 + r, circle_y + r)], outline=DIM, width=4)
    draw.arc([(cx2 - r, circle_y - r), (cx2 + r, circle_y + r)], start=-90, end=270 if streaks["current"] > 0 else -90, fill=PURPLE, width=4)
    
    # Purple flame shape outline on top of ring
    flame_y = circle_y - r - 5
    flame_points = [
        (cx2, flame_y - 12),
        (cx2 + 6, flame_y - 5),
        (cx2 + 4, flame_y - 1),
        (cx2 + 7, flame_y + 4),
        (cx2, flame_y + 8),
        (cx2 - 7, flame_y + 4),
        (cx2 - 4, flame_y - 1),
        (cx2 - 6, flame_y - 5),
    ]
    draw.polygon(flame_points, outline=PURPLE, fill=BG, width=2)
    
    # Texts
    draw.text((cx2, circle_y + 2), str(streaks["current"]), fill=WHITE, font=font_metric_sm, anchor="mm")
    draw.text((cx2, cy + 46), "Current Streak", fill=BLUE, font=font_label, anchor="mm")
    draw.text((cx2, cy + 72), streaks["current_range"] if streaks["current_range"] else "None", fill=GRAY, font=font_xs, anchor="mm")
    
    # ── Right Metric: Longest Streak (Blue value, white label) ──
    draw.text((cx3, cy - 15), str(streaks["longest"]), fill=BLUE, font=font_metric, anchor="mm")
    draw.text((cx3, cy + 32), "Longest Streak", fill=WHITE, font=font_label, anchor="mm")
    draw.text((cx3, cy + 58), streaks["longest_range"] if streaks["longest_range"] else "None", fill=GRAY, font=font_xs, anchor="mm")
    
    # ── Line Graph Section ──
    graph_y0 = 400
    graph_y1 = 710
    graph_x0 = 100
    graph_x1 = 1100
    graph_w = graph_x1 - graph_x0
    graph_h = graph_y1 - graph_y0
    
    # Graph Title (Light blue "Arpan Majumdar's Contribution Graph")
    draw.text((W // 2, graph_y0 - 40), "Arpan Majumdar's Contribution Graph", fill=BLUE, font=font_label, anchor="mm")
    
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
    
    # 1. Draw horizontal dotted grid lines
    num_grid_lines = 5
    for i in range(num_grid_lines):
        val = int(i * y_max / (num_grid_lines - 1))
        y = graph_y1 - (val / y_max) * graph_h
        for x in range(graph_x0, graph_x1, 8):
            draw.line([(x, y), (x + 4, y)], fill=DIM, width=1)
        # Y label
        draw.text((graph_x0 - 20, y), str(val), fill=GRAY, font=font_xs, anchor="rm")
        
    # Map points to screen coordinates
    points = []
    x_spacing = graph_w / (days_back - 1)
    for i, count in enumerate(contributions_list):
        x = graph_x0 + i * x_spacing
        y = graph_y1 - (count / y_max) * graph_h
        points.append((x, y))
        
    # 2. Draw vertical dotted grid lines at label steps
    label_step = 1
    if days_back > 30:
        label_step = 2
    if days_back > 60:
        label_step = 5
        
    for i in range(len(points)):
        if i % label_step == 0 or i == len(points) - 1:
            x = points[i][0]
            for y in range(graph_y0, graph_y1, 8):
                draw.line([(x, y), (x, y + 4)], fill=DIM, width=1)
                
    # Generate smooth spline points (Catmull-Rom spline)
    spline_points = []
    if len(points) >= 3:
        control_points = [points[0]] + points + [points[-1]]
        num_segments = 8
        for i in range(1, len(control_points) - 2):
            p0, p1, p2, p3 = control_points[i-1], control_points[i], control_points[i+1], control_points[i+2]
            for step in range(num_segments):
                t = step / float(num_segments)
                t2 = t * t
                t3 = t2 * t
                sx = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                sy = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                sy = max(graph_y0, min(graph_y1, sy))
                spline_points.append((sx, sy))
        spline_points.append(points[-1])
    else:
        spline_points = points
        
    # 3. Translucent purple fill under the curve
    gradient_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient_overlay)
    polygon_points = [(graph_x0, graph_y1)] + spline_points + [(graph_x1, graph_y1)]
    gradient_draw.polygon(polygon_points, fill=(124, 58, 237, 40))
    img.paste(gradient_overlay, (0, 0), gradient_overlay)
    
    # 4. Solid purple curve line
    draw.line(spline_points, fill=PURPLE, width=3)
    
    # 5. Data markers (white dots with purple borders)
    for x, y in points:
        draw.ellipse([(x - 3, y - 3), (x + 3, y + 3)], fill=WHITE, outline=PURPLE, width=1)
        
    # X-axis base line
    draw.line([(graph_x0, graph_y1), (graph_x1, graph_y1)], fill=DIM, width=2)
    
    # X-axis day numbers under ticks
    for i, date in enumerate(dates_list):
        if i % label_step == 0 or i == len(dates_list) - 1:
            day_str = str(date.day)
            x = points[i][0]
            # Draw tick
            draw.line([(x, graph_y1), (x, graph_y1 + 4)], fill=DIM, width=1)
            # Draw day number
            draw.text((x, graph_y1 + 10), day_str, fill=GRAY, font=font_xs, anchor="mt")
            
    # X-axis month labels (drawn below day numbers)
    last_month = None
    for i, date in enumerate(dates_list):
        month_str = date.strftime("%b")
        if month_str != last_month:
            x = points[i][0]
            draw.text((x, graph_y1 + 28), month_str, fill=WHITE, font=font_sm, anchor="mt")
            last_month = month_str
            
    # X-axis title
    draw.text((W // 2, graph_y1 + 50), "Days", fill=GRAY, font=font_sm, anchor="mm")
    
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
