import cv2


def detect_object(frame, color_ref, min_area=500):

    if frame is None:
        raise ValueError('frame is None')

    if frame.size == 0:
        raise ValueError('empty frame')

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # creates a mask based on the hsv boundary
    mask = cv2.inRange(hsv, color_ref[0], color_ref[1])

    # create a kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    # erode + dilate
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # dilate + erode
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # try to find the connected regions
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    result = {
        'visible': False,
        'x': -1,
        'y': -1,
        'confidence': 0.0
    }

    canvas_infos = {
        'x': -1,
        'y': -1,
        'w': -1,
        'h': -1
    }

    # if any contours exists
    if contours:

        # take the largest contour (focus on one object)
        largest = max(contours, key=cv2.contourArea)
        # compute the area size
        area = cv2.contourArea(largest)

        # if the area is bigger than 500 px^2 | avoid noises
        if area > min_area:
            # compute the small rectangle that fits the object
            x, y, w, h = cv2.boundingRect(largest)

            center_x = x + (w / 2.0)
            center_y = y + (h / 2.0)

            # create the confidence equation
            confidence = min(area / (w * h), 1.0)

            result = {
                'visible': True,
                'x': center_x,
                'y': center_y,
                'confidence': confidence
            }

            canvas_infos = {
                'x': x,
                'y': y,
                'w': w,
                'h': h
            }

    return result, canvas_infos
