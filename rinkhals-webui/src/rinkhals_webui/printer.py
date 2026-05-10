from __future__ import annotations

import fcntl
import struct
from typing import Optional

from .klippy import KlippyClient

_VIDEO_DEVICE = "/dev/video10"
_VIDIOC_G_CTRL = 0xC008561B
_VIDIOC_S_CTRL = 0xC008561C
_V4L2_CID_GAIN = 0x00980913


class PrinterController:
    """Controller for printer-level commands."""

    def __init__(self, client: Optional[KlippyClient] = None) -> None:
        self._client = client or KlippyClient()

    def set_led(self, on: bool) -> None:
        """Turn the print head LED on (True) or off (False)."""
        self._client.call("led/set_led", params={"S": 1 if on else 0})

    def get_camera_led(self) -> bool:
        """Read the camera LED state directly from the V4L2 device."""
        buf = struct.pack("Ii", _V4L2_CID_GAIN, 0)
        with open(_VIDEO_DEVICE, "rb") as fd:
            result = fcntl.ioctl(fd, _VIDIOC_G_CTRL, buf)
        _, value = struct.unpack("Ii", result)
        return value != 0

    def set_camera_led(self, on: bool) -> None:
        """Set the camera LED state directly via the V4L2 device."""
        buf = struct.pack("Ii", _V4L2_CID_GAIN, 1 if on else 0)
        with open(_VIDEO_DEVICE, "rb") as fd:
            fcntl.ioctl(fd, _VIDIOC_S_CTRL, buf)
