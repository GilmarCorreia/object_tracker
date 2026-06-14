#!/usr/bin/env python3

# ROS2 Imports
# Developer Imports
import cv2
import rclpy
from challenge_interfaces.msg import ObjectState
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class ObjectTracker(Node):
    # Constructor
    def __init__(self):
        super().__init__("object_tracker")

        # Declare parameters
        self.declare_parameter("camera_name", "camera")
        self.declare_parameter("camera_topic", "/image_raw")
        self.declare_parameter("debug_topic", "/tracker/debug_image")
        self.declare_parameter("state_topic", "/tracker/object_state")
        self.declare_parameter("min_area", 500)
        self.declare_parameter("color", "yellow")

        # Set attributes from parameters
        self.__set_camera_name(
            self.get_parameter("camera_name").get_parameter_value().string_value
        )

        self.__set_camera_topic(
            self.get_camera_name()
            + self.get_parameter("camera_topic").get_parameter_value().string_value
        )

        self.__set_debug_topic(
            self.get_parameter("debug_topic").get_parameter_value().string_value
        )

        self.__set_state_topic(
            self.get_parameter("state_topic").get_parameter_value().string_value
        )

        self.__set_min_area(
            self.get_parameter("min_area").get_parameter_value().integer_value
        )

        self.__set_color(self.get_parameter("color").get_parameter_value().string_value)

        # Attributes
        self.__set_cv_bridge(CvBridge())

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            self.get_camera_topic(),
            self.image_callback,
            qos_profile=qos_profile_sensor_data,
        )
        self.set_is_reading(True)

        # Publishers
        self.state_pub = self.create_publisher(ObjectState, self.get_state_topic(), 10)

        self.debug_pub = self.create_publisher(Image, self.get_debug_topic(), 10)

        self.get_logger().info(
            f"Tracking objects with {self.__color} color from {self.get_camera_topic()}"
        )

    # Setters
    def __set_camera_name(self, name: str):
        self.__camera_name = name

    def __set_camera_topic(self, topic: str):
        self.__camera_topic = topic

    def __set_debug_topic(self, topic: str):
        self.__debug_topic = topic

    def __set_state_topic(self, topic: str):
        self.__state_topic = topic

    def __set_min_area(self, area: int):
        self.__min_area = area

    def __set_cv_bridge(self, bridge: CvBridge):
        self.__bridge = bridge

    def __set_color(self, color: str):
        self.__color = color

    def set_is_reading(self, reading: bool):
        self.__is_reading = reading

    # Getters
    def get_camera_name(self):
        return self.__camera_name

    def get_camera_topic(self):
        return self.__camera_topic

    def get_debug_topic(self):
        return self.__debug_topic

    def get_state_topic(self):
        return self.__state_topic

    def get_min_area(self):
        return self.__min_area

    def get_cv_bridge(self):
        return self.__bridge

    def get_color(self):
        lower_ref = (0, 0, 0)
        upper_ref = (0, 0, 0)

        # HSV Boundaries for each color
        # https://www.youtube.com/watch?v=G3PW5ysKDxc as example

        if self.__color.lower() == "red_lower":
            lower_ref = (0, 50, 50)
            upper_ref = (10, 255, 255)
        elif self.__color.lower() == "red_upper":
            lower_ref = (170, 50, 50)
            upper_ref = (180, 255, 255)
        elif self.__color.lower() == "orange":
            lower_ref = (10, 100, 20)
            upper_ref = (25, 255, 255)
        elif self.__color.lower() == "green":
            lower_ref = (36, 50, 50)
            upper_ref = (86, 255, 255)
        elif self.__color.lower() == "blue":
            lower_ref = (100, 150, 0)
            upper_ref = (140, 255, 255)
        elif self.__color.lower() == "yellow":
            lower_ref = (25, 100, 100)
            upper_ref = (35, 255, 255)
        else:
            self.get_logger().warn(
                f"Color '{self.__color}' not recognized. Defaulting to yellow."
            )
            lower_ref = (25, 100, 100)
            upper_ref = (35, 255, 255)

        ref = (lower_ref, upper_ref)

        return ref

    def is_reading(self):
        return self.__is_reading

    # Callbacks
    def image_callback(self, msg: Image):
        if self.is_reading():
            try:
                frame = self.get_cv_bridge().imgmsg_to_cv2(msg, desired_encoding="bgr8")

                debug_frame = frame.copy()
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # color mask
                color_ref = self.get_color()

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

                # initialize the object state msg
                state = ObjectState()

                state.header.stamp = self.get_clock().now().to_msg()
                state.visible = False
                state.x = -1.0
                state.y = -1.0
                state.confidence = 0.0

                # if any contours exists
                if contours:
                    # take the largest contour (focus on one object)
                    largest = max(contours, key=cv2.contourArea)
                    # compute the area size
                    area = cv2.contourArea(largest)

                    # if the area is bigger than 500 px^2 | avoid noises
                    if area > self.get_min_area():
                        # compute the small rectangle that fits the object
                        x, y, w, h = cv2.boundingRect(largest)

                        center_x = x + (w / 2.0)
                        center_y = y + (h / 2.0)

                        # update the object state msg
                        state.visible = True
                        state.x = float(center_x)
                        state.y = float(center_y)

                        # create the confidence equation
                        confidence = min(area / (w * h), 1.0)
                        state.confidence = float(confidence)

                        # draw the rectangle
                        cv2.rectangle(
                            debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2
                        )

                        # draw the center point
                        cv2.circle(
                            debug_frame,
                            (int(center_x), int(center_y)),
                            5,
                            (255, 0, 0),
                            -1,
                        )

                        # draw the text
                        cv2.putText(
                            debug_frame,
                            f"({int(center_x)}, {int(center_y)})",
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2,
                        )

                self.state_pub.publish(state)

                # convert and publish the image
                debug_msg = self.get_cv_bridge().cv2_to_imgmsg(
                    debug_frame, encoding="bgr8"
                )
                debug_msg.header = msg.header
                self.debug_pub.publish(debug_msg)

            except Exception as ex:
                self.get_logger().error(f"Tracking failed: {ex}")
                self.set_is_reading(False)
        else:
            self.get_logger().info("Closing the node.")


def main(args=None):
    rclpy.init(args=args)
    node = ObjectTracker()

    try:
        while rclpy.ok() and node.is_reading():
            rclpy.spin_once(node)
    except KeyboardInterrupt:
        node.set_is_reading(False)
    finally:
        node.destroy_node()
        # rclpy.shutdown()
