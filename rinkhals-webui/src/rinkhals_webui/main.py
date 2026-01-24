"""Minimal MicroPython bootstrap for the Rinkhals WebUI port."""

try:
    import machine  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    machine = None

try:
    import utime as _time  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    import time as _time


def _sleep_ms(duration_ms: int) -> None:
    """Sleep helper that works on both CPython and MicroPython."""
    if hasattr(_time, "sleep_ms"):
        _time.sleep_ms(duration_ms)
    else:
        _time.sleep(duration_ms / 1000)


class _MockPin:
    """Lightweight stand-in when `machine.Pin` is unavailable during simulation."""

    OUT = 0

    def __init__(self, pin_id: int, mode: int, value: int = 0) -> None:
        self.pin_id = pin_id
        self.mode = mode
        self._value = value

    def value(self, new_value: int | None = None) -> int:
        if new_value is None:
            return self._value
        self._value = new_value
        print(f"[mock-pin] pin={self.pin_id} -> {self._value}")
        return self._value


class StatusLED:
    """Basic status indicator abstraction to verify event flow end-to-end."""

    def __init__(self, pin_id: int = 2, active_high: bool = True) -> None:
        pin_cls = machine.Pin if machine and hasattr(machine, "Pin") else _MockPin
        initial = 1 if not active_high else 0
        self._pin = pin_cls(pin_id, pin_cls.OUT, value=initial)
        self._active_high = active_high

    def on(self) -> None:
        self._pin.value(1 if self._active_high else 0)

    def off(self) -> None:
        self._pin.value(0 if self._active_high else 1)

    def blink(self, count: int = 3, period_ms: int = 200) -> None:
        for _ in range(count):
            self.on()
            _sleep_ms(period_ms // 2)
            self.off()
            _sleep_ms(period_ms // 2)


def main() -> None:
    led = StatusLED()
    led.blink(count=5, period_ms=300)


if __name__ == "__main__":  # pragma: no cover
    main()
