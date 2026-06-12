# Vehicle Tracking & Counting with OpenCV

A Python project that generates a synthetic traffic video and counts vehicles crossing a line using background subtraction.

---

## Project Structure

```
AI project/
├── generate_video.py   # Generates synthetic traffic.mp4
├── vehicle_tracker.py  # Detects and counts vehicles
├── requirements.txt    # Python dependencies
└── traffic.mp4         # Generated video (created by generate_video.py)
```

---

## Prerequisites

- Python 3.8+
- pip

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` should contain:

```
opencv-python
numpy
```

---

## Step 2: Generate the Traffic Video

Run the video generator to create `traffic.mp4`:

```bash
python generate_video.py
```

This will:
- Create a 1280×720, 20-second synthetic traffic video at 30 fps
- Simulate vehicles of random sizes, colors, and speeds moving across 5 lanes
- Draw dashed lane markings and a red counting line at y=550
- Write 90 blank warm-up frames at the start so the background subtractor works correctly

Output: `traffic.mp4` in the same folder.

---

## Step 3: Run the Vehicle Tracker

```bash
python vehicle_tracker.py
```

This will:
- Open `traffic.mp4` using OpenCV
- Use `BackgroundSubtractorMOG2` to detect moving vehicles
- Draw green bounding boxes around detected vehicles
- Count each vehicle that crosses the blue line at y=550
- Display the running count on screen

Two windows will appear:
- **Vehicle Tracking** — the video with bounding boxes and count overlay
- **Mask** — the binary foreground mask used for detection

Press **ESC** to stop.

---

## How It Works

```
Video Frame
    │
    ▼
Grayscale → Gaussian Blur → Background Subtraction → Binary Mask
    │
    ▼
Find Contours → Filter by area (≥ 1500 px²)
    │
    ▼
Draw bounding box + center point
    │
    ▼
Check if center crosses line (y = 550 ± 10 px)
    │
    ▼
Increment vehicle count
```

---

## Configuration

| Parameter | File | Default | Description |
|-----------|------|---------|-------------|
| `line_position` | `vehicle_tracker.py:16` | `550` | Y-coordinate of counting line |
| `offset` | `vehicle_tracker.py:15` | `10` | Tolerance around counting line (±px) |
| `duration` | `generate_video.py:7` | `20` | Video length in seconds |
| `fps` | `generate_video.py:6` | `30` | Frames per second |

---

## Using a Real Video

Replace the generated video with your own traffic footage:

```python
# vehicle_tracker.py
cap = cv2.VideoCapture("your_video.mp4")
```

Adjust `line_position` to match where you want to count vehicles in your video.

---

## Troubleshooting

**Video won't open:**
```python
cap = cv2.VideoCapture("traffic.mp4")
if not cap.isOpened():
    print("Error: Cannot open video file")
    exit()
```

**Too many false detections:** Increase the area filter threshold in `vehicle_tracker.py`:
```python
if area < 1500:  # raise this value, e.g. 3000
    continue
```

**Count is too high / double-counting:** Increase `history` in the background subtractor or reduce `offset`:
```python
vehicle_detector = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=40)
offset = 5
```
