import json

from microdot import Microdot, Response, send_file
from .static import serve_static, frontend_missing_response

app = Microdot()
Response.default_content_type = "text/html"


JSON_HEADERS = {"Content-Type": "application/json; charset=UTF-8"}
TEXT_HEADERS = {"Content-Type": "text/plain; charset=UTF-8"},


@app.route("/api/health")
async def health(request):
    return Response(json.dumps({"status": "ok"}), headers=JSON_HEADERS)


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
