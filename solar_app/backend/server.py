"""Backend entry point for the PV dashboard skeleton."""

from solar_app.frontend.dashboard import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
