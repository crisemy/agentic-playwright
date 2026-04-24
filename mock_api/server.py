# mock_api/server.py
"""Entry point to run the mock API server."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "mock_api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
