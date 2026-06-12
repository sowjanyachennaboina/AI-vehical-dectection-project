# Advanced Vehicle Tracking with ID, Speed & Direction

An enhanced vehicle tracker built on top of the basic counter. Each vehicle gets a unique ID, a motion trail, speed estimate, and direction label.

---

## Project Structure

```
AI project/
├── generate_video.py           # Generates synthetic traffic.mp4
├── vehicle_tracker.py          # Basic: detects and counts vehicles
├── vehicle_tracker_advanced.py # Advanced: ID + speed + direction tracking
├── requirements.txt            # Python dependencies
└── traffic.mp4                 # Generated video (created by generate_video.py)
```

---

## Features

| Feature | Description |
|---------|-------------|
| Unique ID | Every vehicle is assigned an ID (ID:0, ID:1 …) that persists across frames |
| Motion Trail | Orange line showing the last 20 positions of each vehicle |
| Speed Estimate | Speed displayed in km/h next to each vehicle |
| Direction | Shows `R->` (moving right) or `<-L` (moving left) |
| Line Counting | Counts each unique vehicle ID crossing the line once — no double-counting |

---

## Prerequisites

- Python 3.8+
- pip

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
opencv-python
numpy
```

---

## Step 2: Generate the Traffic Video

If you haven't already created `traffic.mp4`:

```bash
python generate_video.py
```

---

## Step 3: Run the Advanced Tracker

```bash
python vehicle_tracker_advanced.py
```

Two windows will appear:
- **Vehicle Tracking** — video with bounding boxes, ID labels, speed, direction, and trail
- **Mask** — binary foreground mask

Press **ESC** to stop.

---

## How It Works

```
Detect contours (background subtraction)
        │
        ▼
Get centroid of each detection
        │
        ▼
Match to existing tracks by nearest centroid (max 80 px distance)
        │
   ┌────┴────┐
Matched    Unmatched detection
   │              │
Update track   Create new track with new ID
   │
   ▼
Compute speed (pixels/frame → km/h)
Compute direction (dx > 0 → R->, else <-L)
Append to trail
        │
        ▼
Draw bounding box + label + trail + centre dot
        │
        ▼
If centre crosses LINE_Y (±OFFSET) and ID not yet counted → increment count
```

---

## Configuration

| Parameter | Line | Default | Description |
|-----------|------|---------|-------------|
| `LINE_Y` | 11 | `550` | Y-coordinate of the counting line |
| `OFFSET` | 10 | `10` | Tolerance around line (±px) |
| `MAX_LOST` | 13 | `15` | Frames of no detection before a track is dropped |
| `TRAIL_LEN` | 14 | `20` | Number of past positions drawn as trail |
| `PIXELS_PER_METER` | 15 | `8.0` | Scale factor — tune for real video |
| `FPS` | 16 | `30` | Frames per second of the video |

---

## Tuning for a Real Video

### Set the correct scale (PIXELS_PER_METER)

Measure a known real-world distance in your video (e.g. a lane width ≈ 3.5 m) and count how many pixels it spans. Then:

```python
PIXELS_PER_METER = pixel_width_of_lane / 3.5
```

### Adjust the counting line

Change `LINE_Y` to the row where you want to count crossings:

```python
LINE_Y = 400   # example for a different video
```

### Reduce false detections

Raise the contour area threshold:

```python
if cv2.contourArea(contour) < 3000:   # was 1500
    continue
```

### Reduce ID fragmentation (same vehicle gets two IDs)

Increase `max_dist` in the `match_detections` call:

```python
matched, unmatched_dets, unmatched_tracks = match_detections(tracks, detections, max_dist=120)
```

---

## Difference vs Basic Tracker

| | `vehicle_tracker.py` | `vehicle_tracker_advanced.py` |
|---|---|---|
| Vehicle IDs | No | Yes |
| Motion trail | No | Yes (20 frames) |
| Speed | No | Yes (km/h estimate) |
| Direction | No | Yes (R-> / <-L) |
| Double-count guard | No | Yes (per ID) |