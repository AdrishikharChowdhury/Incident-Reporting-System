import uvicorn


def main() -> None:
    print("Hello from incident-api!")
    uvicorn.run(
        "incident_api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="debug",
    )
