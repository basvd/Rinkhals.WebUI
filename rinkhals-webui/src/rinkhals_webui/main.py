import glob
import json
import os
import subprocess

from microdot import Microdot, Response

from .ace import ACEController
from .apps import AppsController
from .klippy import KlippyError
from .printer import PrinterController
from .static import serve_static, frontend_missing_response

app = Microdot()
Response.default_content_type = "text/html"


JSON_HEADERS = {"Content-Type": "application/json; charset=UTF-8"}
TEXT_HEADERS = {"Content-Type": "text/plain; charset=UTF-8"}

ace_controller = ACEController()
apps_controller = AppsController()
printer_controller = PrinterController()

_SCRIPTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
_LOG_DIR = "/useremain/rinkhals"


def json_response(payload, status_code=200):
    return Response(json.dumps(payload), status_code=status_code, headers=JSON_HEADERS)


def error_response(message, status_code=500):
    return json_response({"error": message}, status_code=status_code)


def get_json_body(request):
    data = request.json
    if data is None or not isinstance(data, dict):
        raise ValueError("Expected JSON object body")
    return data


@app.route("/api/health")
async def health(request):
    return json_response({"status": "ok"})


@app.route("/api/ace", methods=["GET"])
async def ace_status(request):
    try:
        hubs = ace_controller.list_hubs()
    except KlippyError as exc:
        return error_response(str(exc), status_code=502)
    return json_response({"filament_hubs": hubs})


@app.route("/api/ace/config", methods=["GET"])
async def ace_config(request):
    try:
        config = ace_controller.fetch_config()
    except KlippyError as exc:
        return error_response(str(exc), status_code=502)
    return json_response(config)


@app.route("/api/ace/config", methods=["POST"])
async def update_ace_config(request):
    try:
        body = get_json_body(request)
        ace_controller.update_config(body)
    except ValueError as exc:
        return error_response(str(exc), status_code=400)
    except KlippyError as exc:
        return error_response(str(exc), status_code=502)
    return json_response({"status": "ok"})


@app.route("/api/ace/<int:ace_id>/filament", methods=["POST"])
async def set_filament(request, ace_id):
    try:
        body = get_json_body(request)
    except ValueError as exc:
        return error_response(str(exc), status_code=400)

    missing = [field for field in ("slot", "material", "color") if field not in body]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", status_code=400)

    try:
        slot = int(body["slot"])
        material = str(body["material"])
        color = str(body["color"])
        ace_controller.set_filament(ace_id, slot, material, color)
    except (ValueError, KlippyError) as exc:
        return error_response(str(exc), status_code=400 if isinstance(exc, ValueError) else 502)

    return json_response({"status": "ok"})


@app.route("/api/ace/<int:ace_id>/drying", methods=["POST"])
async def start_drying(request, ace_id):
    try:
        body = get_json_body(request)
    except ValueError as exc:
        return error_response(str(exc), status_code=400)

    missing = [field for field in ("duration", "temp") if field not in body]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", status_code=400)

    try:
        duration = int(body["duration"])
        temp = int(body["temp"])
        fan_speed = body.get("fan_speed")
        ace_controller.start_drying(ace_id, duration, temp, None if fan_speed is None else int(fan_speed))
    except (ValueError, KlippyError) as exc:
        return error_response(str(exc), status_code=400 if isinstance(exc, ValueError) else 502)

    return json_response({"status": "ok"})


@app.route("/api/ace/<int:ace_id>/drying", methods=["DELETE"])
async def stop_drying(request, ace_id):
    try:
        ace_controller.stop_drying(ace_id)
    except KlippyError as exc:
        return error_response(str(exc), status_code=502)
    return json_response({"status": "ok"})


# ---------------------------------------------------------------------------
# LED API
# ---------------------------------------------------------------------------


@app.route("/api/led", methods=["POST"])
async def set_led(request):
    try:
        body = get_json_body(request)
    except ValueError as exc:
        return error_response(str(exc), status_code=400)
    if "on" not in body:
        return error_response("Missing field: on", status_code=400)
    try:
        printer_controller.set_led(bool(body["on"]))
    except KlippyError as exc:
        return error_response(str(exc), status_code=502)
    return json_response({"on": bool(body["on"])})


@app.route("/api/camera-led", methods=["GET"])
async def get_camera_led(request):
    try:
        on = printer_controller.get_camera_led()
    except Exception as exc:
        return error_response(str(exc))
    return json_response({"on": on})


@app.route("/api/camera-led", methods=["POST"])
async def set_camera_led(request):
    try:
        body = get_json_body(request)
    except ValueError as exc:
        return error_response(str(exc), status_code=400)
    if "on" not in body:
        return error_response("Missing field: on", status_code=400)
    try:
        printer_controller.set_camera_led(bool(body["on"]))
    except Exception as exc:
        return error_response(str(exc))
    return json_response({"on": bool(body["on"])})


# ---------------------------------------------------------------------------
# Apps API
# ---------------------------------------------------------------------------


@app.route("/api/apps", methods=["GET"])
async def list_apps(request):
    try:
        apps = apps_controller.list_apps()
    except Exception as exc:
        return error_response(str(exc))
    return json_response({"apps": apps})


@app.route("/api/apps/<name>/toggle", methods=["POST"])
async def toggle_app(request, name):
    try:
        enabled = apps_controller.toggle_app(name)
    except ValueError as exc:
        return error_response(str(exc), status_code=404)
    except Exception as exc:
        return error_response(str(exc))
    return json_response({"app": name, "enabled": enabled})


# ---------------------------------------------------------------------------
# System API
# ---------------------------------------------------------------------------


@app.route("/api/system/sync", methods=["POST"])
async def system_sync(request):
    try:
        subprocess.run(["sync"], timeout=10, check=True)
    except Exception as exc:
        return error_response(str(exc))
    return json_response({"status": "ok"})


@app.route("/api/system/reboot", methods=["POST"])
async def system_reboot(request):
    # Popen is non-blocking; the response is delivered before the OS reboots.
    subprocess.Popen(["reboot"])
    return json_response({"status": "rebooting"})


@app.route("/api/system/logs", methods=["GET"])
async def system_logs(request):
    parts = []
    for path in sorted(glob.glob(os.path.join(_LOG_DIR, "*.log"))):
        try:
            with open(path) as f:
                content = f.read()
            parts.append(f"=== {path} ===\n{content}")
        except OSError:
            pass
    body = "\n\n".join(parts) if parts else "(no log files found)"
    return Response(body, status_code=200, headers=TEXT_HEADERS)


@app.route("/api/system/update", methods=["GET"])
async def system_update(request):
    script = os.path.join(_SCRIPTS_DIR, "ota-update-info.py")
    try:
        result = subprocess.run(
            ["python3", script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Script exited with non-zero status")
        data = json.loads(result.stdout)
        return json_response(data)
    except Exception as exc:
        return json_response({"status": "error", "message": str(exc)})


# ---------------------------------------------------------------------------
# Static / index
# ---------------------------------------------------------------------------


@app.route("/")
async def index(request):
    index = serve_static("index.html")
    if index is None:
        return frontend_missing_response()
    return index


@app.route("/<path:path>")
async def static(request, path):
    asset = serve_static(path)
    if asset is not None:
        return asset
    return Response("Not Found", status_code=404, headers=TEXT_HEADERS)


def main() -> None:
    """Start the Microdot development server."""

    app.run(host="0.0.0.0", port=1414, debug=True)


if __name__ == "__main__":
    main()
