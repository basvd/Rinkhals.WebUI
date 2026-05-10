import os
from os import path

from microdot import Response, send_file


STATIC_DIR = os.environ.get("STATIC_DIR")


def frontend_missing_response() -> Response:
    """Return a helpful message when the static bundle is unavailable."""

    message = (
        "Static frontend bundle not found. Run `hatch run build-frontend` from the project root."
    )

    return Response(message, status_code=503, headers={"Content-Type": "text/plain; charset=UTF-8"})


def serve_static(asset_path: str):
    """Return a file under the static directory if it exists."""

    if not STATIC_DIR or not path.isdir(STATIC_DIR):
        return None

    relative_path = asset_path.lstrip("/")
    candidate = path.normpath(path.join(STATIC_DIR, relative_path))
    dist_prefix = STATIC_DIR if STATIC_DIR.endswith("/") else STATIC_DIR + "/"

    # Ensure requested file stays within dist_root (prefix match on normalized
    # paths works because both are absolute and canonicalized).
    if candidate != STATIC_DIR and not candidate.startswith(dist_prefix):
        return None

    if path.isfile(candidate):
        return send_file(candidate)

    return None
