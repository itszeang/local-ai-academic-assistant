from fastapi.testclient import TestClient

from app.common.config import Settings
from app.main import create_app


def test_health_contract_has_local_readiness_shape(tmp_path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ready", "degraded"}
    assert isinstance(payload["offline_ready"], bool)
    assert isinstance(payload["missing_local_resources"], list)
