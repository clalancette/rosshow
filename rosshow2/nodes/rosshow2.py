#!/usr/bin/env python3

import os
import random
import sys
import threading
import time

import rclpy

from librosshow.getch import Getch
import librosshow.termgraphics as termgraphics

VIEWER_MAPPING = {
  "std_msgs/Bool": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/Float32": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/Float64": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/Int8": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/Int16": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/Int32": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/Int64": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/UInt8": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/UInt16": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/UInt32": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "std_msgs/UInt64": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {}),
  "sensor_msgs/CompressedImage": ("librosshow.viewers.sensor_msgs.CompressedImageViewer", "CompressedImageViewer", {}),
  "sensor_msgs/FluidPressure": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {"data_field": "fluid_pressure"}),
  "sensor_msgs/RelativeHumidity": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {"data_field": "relative_humidity"}),
  "sensor_msgs/Illuminance": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {"data_field": "illuminance"}),
  "sensor_msgs/Image": ("librosshow.viewers.sensor_msgs.ImageViewer", "ImageViewer", {}),
  "sensor_msgs/Imu": ("librosshow.viewers.sensor_msgs.ImuViewer", "ImuViewer", {}),
  "sensor_msgs/LaserScan": ("librosshow.viewers.sensor_msgs.LaserScanViewer", "LaserScanViewer", {}),
  "sensor_msgs/NavSatFix": ("librosshow.viewers.sensor_msgs.NavSatFixViewer", "NavSatFixViewer", {}),
  "sensor_msgs/PointCloud2": ("librosshow.viewers.sensor_msgs.PointCloud2Viewer", "PointCloud2Viewer", {}),
  "sensor_msgs/Range": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {"data_field": "range"}),
  "sensor_msgs/Temperature": ("librosshow.viewers.generic.SinglePlotViewer", "SinglePlotViewer", {"data_field": "temperature"}),
}

def capture_key_loop(viewer):
    getch = Getch()

    while True:
        c = getch()
        if c == '\x03': # Ctrl+C
            sys.exit()

        if "keypress" not in dir(viewer):
            continue

        if c == '\x1B': # ANSI escape
            c = getch()
            if c == '\x5B':
                c = getch()
                if c == '\x41':
                    viewer.keypress("up")
                if c == '\x42':
                    viewer.keypress("down")
                if c == '\x43':
                    viewer.keypress("left")
                if c == '\x44':
                    viewer.keypress("right")
        else:
            viewer.keypress(c)

def main():
    # Parse arguments
    # TODO: proper argument parsing
    TOPIC = "-"
    argi = 1
    while TOPIC.startswith("-"):
        if argi >= len(sys.argv):
            print("Usage: rosshow2 [-a] <topic>")
            print("   -a:   Use ASCII only (no Unicode)")
            print("   -c1:  Force monochrome")
            print("   -c4:  Force 4-bit color (16 colors)")
            print("   -c24: Force 24-bit color")
            sys.exit(0)
        TOPIC = sys.argv[argi]
        argi+= 1

    if ("-a" in sys.argv) or ("--ascii" in sys.argv):
        USE_ASCII = True
    else:
        USE_ASCII = False

    if "-c1" in sys.argv:
        color_support = termgraphics.COLOR_SUPPORT_1
    elif "-c4" in sys.argv:
        color_support = termgraphics.COLOR_SUPPORT_16
    elif "-c24" in sys.argv:
        color_support = termgraphics.COLOR_SUPPORT_24BIT
    else:
        color_support = None # TermGraphics class will autodetect

    args = {}
    rclpy.init(args=args)

    node = rclpy.create_node('rosshow2')

    # We have to sleep a bit here to make sure we get the topics
    time.sleep(1)

    # Get information on all topic types

    topic_types = dict(node.get_topic_names_and_types())
    if TOPIC not in topic_types:
        print("Topic {0} does not appear to be published yet.".format(TOPIC))
        sys.exit(1)

    # TODO(clalancette): Handle topics with multiple types

    # The topic_types is a list of types; if there is more than one type for
    # a particular topic, then we have to ask the user to be more specific
    if len(topic_types[TOPIC]) > 1:
        print("Topic {0} has multiple types, this is currently not supported".format(TOPIC))
        sys.exit(1)

    topic_type = topic_types[TOPIC][0]
    if topic_type not in VIEWER_MAPPING:
        print("Unsupported message type.")
        sys.exit(1)

    # Create the canvas and viewer accordingly

    canvas = termgraphics.TermGraphics( \
            mode = (termgraphics.MODE_EASCII if USE_ASCII else termgraphics.MODE_UNICODE),
            color_support = color_support)

    module_name, class_name, viewer_kwargs = VIEWER_MAPPING[topic_type]
    viewer_class = getattr(__import__(module_name, fromlist=(class_name)), class_name)
    viewer = viewer_class(canvas, title = TOPIC, **viewer_kwargs)

    message_package, message_name = topic_type.split("/", 2)
    message_class = getattr(__import__(message_package + ".msg", fromlist=(message_name)), message_name)

    # Subscribe to the topic so the viewer actually gets the data

    node.create_subscription(message_class, TOPIC, viewer.update)

    # Listen for keypresses

    thread = threading.Thread(target = capture_key_loop, args = (viewer,))
    thread.daemon = True
    thread.start()

    # Drawing loop

    while rclpy.ok():
        time.sleep(1.0 / 15.0)
        rclpy.spin_once(node)
        viewer.draw()


if __name__ == "__main__":
    main()
