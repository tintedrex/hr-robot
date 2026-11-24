"""Jetson outer balance loop stub — publishes BalanceReference at >= 50 Hz (SW-BAL-002)."""

import math

import rclpy
from geometry_msgs.msg import Vector3
from rclpy.node import Node

from hr_msgs.msg import BalanceMode, BalanceReference


class BalanceOuterNode(Node):
    def __init__(self) -> None:
        super().__init__("balance_outer")
        self._pub = self.create_publisher(BalanceReference, "hr/balance/reference", 10)
        self._mode_pub = self.create_publisher(BalanceMode, "hr/balance/mode", 10)
        # 50 Hz minimum per SW-BAL-002
        self._timer = self.create_timer(0.02, self._on_timer)
        self._t0 = self.get_clock().now()
        self.get_logger().info("balance_outer started (stub, 50 Hz)")

    def _on_timer(self) -> None:
        now = self.get_clock().now().to_msg()
        elapsed = (self.get_clock().now() - self._t0).nanoseconds * 1e-9

        ref = BalanceReference()
        ref.stamp = now
        ref.com_target_m = Vector3(x=0.0, y=0.0, z=0.9)
        # Tiny idle sway so the topic is visibly alive in tools
        ref.torso_rpy_rad = Vector3(
            x=0.0,
            y=0.01 * math.sin(elapsed),
            z=0.0,
        )
        ref.yaw_rate_cmd_rad_s = 0.0
        ref.mode = BalanceMode.STAND
        self._pub.publish(ref)

        mode = BalanceMode()
        mode.stamp = now
        mode.mode = BalanceMode.STAND
        self._mode_pub.publish(mode)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = BalanceOuterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
