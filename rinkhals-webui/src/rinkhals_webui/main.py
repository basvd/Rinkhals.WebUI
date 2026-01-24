from microdot import Microdot, Response

app = Microdot()
Response.default_content_type = "text/plain"


@app.route("/")
def index(_request):
    """Return a static greeting so we can verify the Microdot stack."""

    return "Hello from Rinkhals WebUI!"


def main() -> None:
    """Start the Microdot development server."""

    app.run(host="0.0.0.0", port=1414, debug=False)


if __name__ == "__main__":
    main()
