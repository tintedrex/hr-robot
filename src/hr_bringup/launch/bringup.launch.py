"""Minimal HR bringup launch (placeholder for Jetson-side nodes)."""

from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            LogInfo(msg="HR bringup scaffold — add Jetson nodes here (see docs/HR-SRS-SW-v0.1.md)."),
        ]
    )
