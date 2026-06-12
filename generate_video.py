import cv2
import numpy as np
import random

width, height = 1280, 720
fps = 30
duration = 20  # seconds
out = cv2.VideoWriter(
    "traffic.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

vehicles = []

def spawn_vehicle():
    # Lanes chosen so vehicle centers (y + h/2) pass through counting line at y=550
    lane = random.choice([150, 250, 350, 450, 520])
    w = random.randint(80, 140)
    h = random.randint(40, 70)
    speed = random.randint(6, 14)
    color = (
        random.randint(50, 220),
        random.randint(50, 220),
        random.randint(50, 220),
    )
    return {"x": -w, "y": lane, "w": w, "h": h, "speed": speed, "color": color}

# Write 90 empty frames first so background subtractor can establish background
empty = np.zeros((height, width, 3), dtype=np.uint8)
empty[:] = (40, 40, 40)
for lane_y in [230, 330, 430, 530]:
    for x in range(0, width, 80):
        cv2.rectangle(empty, (x, lane_y - 2), (x + 40, lane_y + 2), (200, 200, 100), -1)
cv2.line(empty, (25, 550), (1200, 550), (255, 0, 0), 3)
for _ in range(90):
    out.write(empty)

for frame_num in range(fps * duration):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (40, 40, 40)  # dark road

    # Road markings
    for lane_y in [230, 330, 430, 530]:
        for x in range(0, width, 80):
            cv2.rectangle(frame, (x, lane_y - 2), (x + 40, lane_y + 2), (200, 200, 100), -1)

    # Spawn vehicles randomly
    if frame_num % 18 == 0:
        vehicles.append(spawn_vehicle())

    # Move and draw vehicles
    for v in vehicles:
        v["x"] += v["speed"]
        x, y, w, h = v["x"], v["y"], v["w"], v["h"]
        cv2.rectangle(frame, (x, y), (x + w, y + h), v["color"], -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
        # windshield
        cv2.rectangle(frame, (x + w - 30, y + 8), (x + w - 6, y + h - 8), (180, 220, 255), -1)

    # Remove off-screen vehicles
    vehicles[:] = [v for v in vehicles if v["x"] < width + 160]

    # Counting line
    cv2.line(frame, (25, 550), (1200, 550), (255, 0, 0), 3)

    out.write(frame)

out.release()
print("traffic.mp4 generated successfully")
