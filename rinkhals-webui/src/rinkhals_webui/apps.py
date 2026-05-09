from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any, Dict, List

# Paths mirror the variables in tools.sh and get-entities-apps.sh
_RINKHALS_ROOT = "/useremain/rinkhals/.current"
_RINKHALS_HOME = "/useremain/rinkhals"
_BUILTIN_APPS_DIR = os.path.join(_RINKHALS_ROOT, "home", "rinkhals", "apps")
_USER_APPS_DIR = os.path.join(_RINKHALS_HOME, "apps")

_SKIP_APPS: frozenset[str] = frozenset({"example"})


class AppsController:
    """Mirrors the logic of get-entities-apps.sh and toggle-app.sh."""

    # ------------------------------------------------------------------
    # Discovery helpers
    # ------------------------------------------------------------------

    def _discover_apps(self) -> List[tuple[str, str, bool]]:
        """Return a deduplicated list of (app_name, app_root, is_builtin) tuples."""
        seen: set[str] = set()
        apps: List[tuple[str, str, bool]] = []

        for base_dir, is_builtin in [
            (_BUILTIN_APPS_DIR, True),
            (_USER_APPS_DIR, False),
        ]:
            if not os.path.isdir(base_dir):
                continue
            try:
                entries = sorted(os.listdir(base_dir))
            except OSError:
                continue

            for entry in entries:
                if entry in _SKIP_APPS or entry.startswith("."):
                    continue
                app_root = os.path.join(base_dir, entry)
                if not os.path.isdir(app_root):
                    continue
                if not (
                    os.path.isfile(os.path.join(app_root, "app.json"))
                    and os.path.isfile(os.path.join(app_root, "app.sh"))
                ):
                    continue
                if entry not in seen:
                    seen.add(entry)
                    apps.append((entry, app_root, is_builtin))

        return apps

    def _read_metadata(self, app_root: str) -> Dict[str, Any]:
        path = os.path.join(app_root, "app.json")
        try:
            with open(path) as f:
                raw = f.read()
            # Strip JS-style single-line comments before JSON parsing
            raw = re.sub(r"//[^\n]*", "", raw)
            data = json.loads(raw)
            # Validate schema version (matches get-entities-apps.sh guard)
            if str(data.get("$version", "")) != "1":
                return {}
            return data
        except Exception:
            return {}

    def _is_enabled(self, app_name: str, app_root: str) -> bool:
        """Matches the enabled-check from get-entities-apps.sh:
        enabled = (.enabled in app_root OR $RINKHALS_HOME/apps/$app.enabled) AND
                  NOT (.disabled in app_root OR $RINKHALS_HOME/apps/$app.disabled)
        """
        has_enabled = os.path.isfile(os.path.join(app_root, ".enabled")) or os.path.isfile(
            os.path.join(_USER_APPS_DIR, f"{app_name}.enabled")
        )
        has_disabled = os.path.isfile(os.path.join(app_root, ".disabled")) or os.path.isfile(
            os.path.join(_USER_APPS_DIR, f"{app_name}.disabled")
        )
        return has_enabled and not has_disabled

    def _get_status(self, app_root: str) -> str:
        """Run app.sh status and extract the status word."""
        app_sh = os.path.join(app_root, "app.sh")
        try:
            result = subprocess.run(
                [app_sh, "status"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=app_root,
            )
            for line in result.stdout.splitlines():
                if "Status" in line:
                    parts = line.split()
                    return parts[1] if len(parts) >= 2 else "unknown"
        except Exception:
            pass
        return "unknown"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_apps(self) -> List[Dict[str, Any]]:
        result = []
        for app_name, app_root, _is_builtin in self._discover_apps():
            meta = self._read_metadata(app_root)
            if not meta:
                continue
            result.append(
                {
                    "app": app_name,
                    "name": meta.get("name", app_name),
                    "description": meta.get("description", ""),
                    "version": meta.get("version", ""),
                    "enabled": self._is_enabled(app_name, app_root),
                    "status": self._get_status(app_root),
                }
            )
        return result

    def toggle_app(self, app_name: str) -> bool:
        """Toggle an app's enabled state; returns the new enabled state."""
        for name, app_root, is_builtin in self._discover_apps():
            if name == app_name:
                return self._do_toggle(app_name, app_root, is_builtin)
        raise ValueError(f"App not found: {app_name!r}")

    # ------------------------------------------------------------------
    # Toggle implementation (mirrors toggle-app.sh)
    # ------------------------------------------------------------------

    def _do_toggle(self, app_name: str, app_root: str, is_builtin: bool) -> bool:
        currently_enabled = self._is_enabled(app_name, app_root)
        os.makedirs(_USER_APPS_DIR, exist_ok=True)

        home_enabled = os.path.join(_USER_APPS_DIR, f"{app_name}.enabled")
        home_disabled = os.path.join(_USER_APPS_DIR, f"{app_name}.disabled")

        if is_builtin:
            # Builtin: use $RINKHALS_HOME/apps/$app.enabled / $app.disabled
            if currently_enabled:
                _rm(home_enabled)
                _touch(home_disabled)
            else:
                _rm(home_disabled)
                # Only create .enabled flag if the app root has no .enabled already
                if not os.path.isfile(os.path.join(app_root, ".enabled")):
                    _touch(home_enabled)
        else:
            # User app: use $RINKHALS_HOME/apps/$app/.enabled / .disabled
            app_enabled = os.path.join(_USER_APPS_DIR, app_name, ".enabled")
            app_disabled = os.path.join(_USER_APPS_DIR, app_name, ".disabled")
            _rm(home_enabled)
            _rm(home_disabled)
            if currently_enabled:
                _rm(app_enabled)
                _touch(app_disabled)
            else:
                _rm(app_disabled)
                _touch(app_enabled)

        self._run_lifecycle(app_root, "stop" if currently_enabled else "start")
        return not currently_enabled

    def _run_lifecycle(self, app_root: str, command: str) -> None:
        app_sh = os.path.join(app_root, "app.sh")
        if not os.path.isfile(app_sh):
            return
        try:
            subprocess.run(
                [app_sh, command],
                capture_output=True,
                timeout=10,
                cwd=app_root,
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def _rm(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def _touch(path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, "a").close()
