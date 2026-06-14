import cv2
import numpy as np
from object_tracker.detector import detect_object
import pytest


def test_detect_yellow_circle():

    img = np.zeros(
        (480, 640, 3),
        dtype=np.uint8
    )

    cv2.circle(
        img,
        (320, 240),
        50,
        (0, 255, 255),
        -1
    )

    result = detect_object(
        img,
        ((25, 100, 100), (35, 255, 255))
    )

    assert result['visible'] is True
    assert abs(result['x'] - 320) < 5
    assert abs(result['y'] - 240) < 5


def test_no_object():

    img = np.zeros(
        (480, 640, 3),
        dtype=np.uint8
    )

    result = detect_object(
        img,
        ((25, 100, 100), (35, 255, 255))
    )

    assert result['visible'] is False


def test_invalid_image():

    with pytest.raises(ValueError):
        detect_object(
            None,
            ((25, 100, 100), (35, 255, 255))
        )
