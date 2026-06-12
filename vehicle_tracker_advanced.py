import cv2
import numpy as np

cap = cv2.VideoCapture("traffic.mp4")

vehicle_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

next_id = 0
tracks = {}          # id -> {cx, cy, box, lost, speed_px, direction, trail}
vehicle_count = 0
counted_ids = set()

OFFSET = 10
LINE_Y = 550
MAX_LOST = 15        # frames before dropping a track
TRAIL_LEN = 20       # how many past positions to draw
PIXELS_PER_METER = 8.0   # tune this for real video (pixels that equal 1 metre)
FPS = 30


def match_detections(tracks, detections, max_dist=80):
    if not tracks or not detections:
        return {}, list(range(len(detections))), list(tracks.keys())

    track_ids = list(tracks.keys())
    tc = np.array([[tracks[tid]['cx'], tracks[tid]['cy']] for tid in track_ids], dtype=float)
    dc = np.array([[d['cx'], d['cy']] for d in detections], dtype=float)

    # Pairwise distances: shape (n_tracks, n_detections)
    D = np.linalg.norm(tc[:, None] - dc[None, :], axis=2)

    matched, used_dets, used_tracks = {}, set(), set()
    for idx in np.argsort(D.ravel()):
        r, c = divmod(int(idx), len(detections))
        if r in used_tracks or c in used_dets:
            continue
        if D[r, c] > max_dist:
            break
        matched[track_ids[r]] = c
        used_tracks.add(r)
        used_dets.add(c)

    unmatched_dets = [i for i in range(len(detections)) if i not in used_dets]
    unmatched_tracks = [track_ids[r] for r in range(len(track_ids)) if r not in used_tracks]
    return matched, unmatched_dets, unmatched_tracks


while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.line(frame, (25, LINE_Y), (1200, LINE_Y), (255, 0, 0), 3)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 5)
    mask = vehicle_detector.apply(blur)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for contour in contours:
        if cv2.contourArea(contour) < 1500:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        detections.append({'cx': x + w // 2, 'cy': y + h // 2, 'box': (x, y, w, h)})

    matched, unmatched_dets, unmatched_tracks = match_detections(tracks, detections)

    # Update matched tracks
    for tid, det_idx in matched.items():
        d = detections[det_idx]
        t = tracks[tid]
        dx = d['cx'] - t['cx']
        t['trail'].append((d['cx'], d['cy']))
        if len(t['trail']) > TRAIL_LEN:
            t['trail'].pop(0)
        t.update({
            'cx': d['cx'], 'cy': d['cy'],
            'box': d['box'],
            'lost': 0,
            'speed_px': np.hypot(dx, d['cy'] - t['cy']),
            'direction': 'R->' if dx >= 0 else '<-L',
        })

    # Register new tracks
    for det_idx in unmatched_dets:
        d = detections[det_idx]
        tracks[next_id] = {
            'cx': d['cx'], 'cy': d['cy'],
            'box': d['box'],
            'lost': 0,
            'speed_px': 0.0,
            'direction': 'R->',
            'trail': [(d['cx'], d['cy'])],
        }
        next_id += 1

    # Age unmatched tracks
    for tid in unmatched_tracks:
        tracks[tid]['lost'] += 1

    # Drop stale tracks
    tracks = {tid: t for tid, t in tracks.items() if t['lost'] <= MAX_LOST}

    # Draw all active tracks
    for tid, t in tracks.items():
        if t['lost'] > 0:
            continue

        x, y, w, h = t['box']
        speed_kmh = (t['speed_px'] * FPS / PIXELS_PER_METER) * 3.6

        # Bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # ID / direction / speed label
        label = f"ID:{tid}  {t['direction']}  {speed_kmh:.0f} km/h"
        cv2.putText(frame, label, (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # Centre dot
        cv2.circle(frame, (t['cx'], t['cy']), 4, (0, 0, 255), -1)

        # Motion trail
        for i in range(1, len(t['trail'])):
            cv2.line(frame, t['trail'][i - 1], t['trail'][i], (0, 165, 255), 2)

        # Count vehicle when it crosses the line
        if tid not in counted_ids and LINE_Y - OFFSET < t['cy'] < LINE_Y + OFFSET:
            vehicle_count += 1
            counted_ids.add(tid)
            cv2.line(frame, (25, LINE_Y), (1200, LINE_Y), (0, 255, 0), 3)

    cv2.putText(frame, f"Vehicle Count: {vehicle_count}",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Vehicle Tracking", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()