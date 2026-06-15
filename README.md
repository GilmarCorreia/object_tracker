# object_tracker

ROS 2 Python package that performs color-based object tracking on webcam images.

Main behavior:
- Subscribes to `/camera/image_raw` to receive RGB images.
- Detects the configured color object and computes its center.
- Publishes state to `/tracker/object_state` as `challenge_interfaces/ObjectState`.
- Publishes debug images to `/tracker/debug_image` with a bounding box overlay.

Common parameters:
- `camera_name`, `camera_topic`, `debug_topic`, `state_topic`, `min_area`, `color`.
