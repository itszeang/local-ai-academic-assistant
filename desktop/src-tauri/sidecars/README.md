Backend sidecar placement
=========================

Development runs the FastAPI backend from `backend/` with Uvicorn.

During `tauri dev`, `desktop/scripts/dev-before-dev.ps1` starts the FastAPI backend if port `8765` is not
already open, then starts the Vite frontend.

Packaged desktop builds should place a platform-specific backend launcher in this directory and add it to
`bundle.externalBin` once the packaging target is chosen. The Tauri shell already exposes the
`backend_ready` command so the UI can check whether the local API is reachable at `127.0.0.1:8765`.
