import cv2

# Load video
cap = cv2.VideoCapture("traffic.mp4")

# Background Subtractor
vehicle_detector = cv2.createBackgroundSubtractorMOG2(
    history=100,
    varThreshold=40
)

vehicle_count = 0
detections = []

offset = 10
line_position = 550

while True:
    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape

    # Draw counting line
    cv2.line(frame, (25, line_position),
             (1200, line_position),
             (255, 0, 0), 3)

    # Convert frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur image
    blur = cv2.GaussianBlur(gray, (5, 5), 5)

    # Detect moving vehicles
    mask = vehicle_detector.apply(blur)

    _, mask = cv2.threshold(mask, 254, 255,
                            cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < 1500:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        center_x = int(x + w/2)
        center_y = int(y + h/2)

        detections.append((center_x, center_y))

        # Draw rectangle around vehicle
        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

        cv2.circle(
            frame,
            (center_x, center_y),
            4,
            (0, 0, 255),
            -1
        )

    for (cx, cy) in detections:

        if line_position - offset < cy < line_position + offset:

            vehicle_count += 1

            cv2.line(
                frame,
                (25, line_position),
                (1200, line_position),
                (0, 255, 0),
                3
            )

            detections.remove((cx, cy))

    cv2.putText(
        frame,
        f"Vehicle Count: {vehicle_count}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    cv2.imshow("Vehicle Tracking", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()