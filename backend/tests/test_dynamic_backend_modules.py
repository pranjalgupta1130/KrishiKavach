import io
import pytest
from PIL import Image

def create_test_image(color=(30, 180, 40), size=(100, 100), fmt="JPEG") -> bytes:
    """Helper to generate in-memory test images of given RGB color."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_crop_health_endpoint_success(client):
    """Verify GET /api/v1/crop-health/{plot_id} returns structured dynamic response."""
    response = client.get("/api/v1/crop-health/tukaram_beed_01")
    assert response.status_code == 200
    data = response.json()

    assert data["plot_id"] == "tukaram_beed_01"
    assert "crop" in data
    assert "crop_stage" in data
    assert isinstance(data["days_after_sowing"], int)
    assert "accumulated_gdd" in data
    assert "threshold_gdd" in data
    assert isinstance(data["pest_risk_high"], bool)
    assert "GDD" in data["model_version"]


def test_crop_health_nonexistent_plot(client):
    """Verify non-existent plot returns 404."""
    response = client.get("/api/v1/crop-health/nonexistent_plot_xyz")
    assert response.status_code == 404


def test_market_endpoint_success(client):
    """Verify GET /api/v1/market/{plot_id} returns valid market intelligence."""
    response = client.get("/api/v1/market/tukaram_beed_01")
    assert response.status_code == 200
    data = response.json()

    assert data["plot_id"] == "tukaram_beed_01"
    assert data["currency"] == "INR"
    assert data["unit"] == "quintal"
    assert data["current_price"] > 0
    assert data["moving_average"] > 0
    assert data["trend"] in {"UP", "DOWN", "STABLE"}
    assert data["data_status"] in {"LIVE", "CACHED", "FALLBACK"}


def test_scan_crop_valid_image(client):
    """Verify POST /api/v1/scan accepts valid image and returns deterministic ScanResponse."""
    img_bytes = create_test_image(color=(40, 190, 50))  # Green healthy foliage
    files = {"file": ("test_healthy.jpg", img_bytes, "image/jpeg")}

    response = client.post("/api/v1/scan", files=files)
    assert response.status_code == 200
    data = response.json()

    assert "observation" in data
    assert data["defect_type"] == "healthy_foliage"
    assert data["severity"] == "NOMINAL"
    assert data["confidence"] > 0.0
    assert isinstance(data["observations"], list)
    assert data["needs_field_scouting"] is False


def test_scan_crop_determinism(client):
    """Verify uploading identical image bytes twice produces identical analysis results."""
    img_bytes = create_test_image(color=(200, 160, 20))  # Chlorosis image
    files1 = {"file": ("chlorosis1.jpg", img_bytes, "image/jpeg")}
    files2 = {"file": ("chlorosis2.jpg", img_bytes, "image/jpeg")}

    res1 = client.post("/api/v1/scan", files=files1).json()
    res2 = client.post("/api/v1/scan", files=files2).json()

    assert res1["defect_type"] == res2["defect_type"]
    assert res1["severity"] == res2["severity"]
    assert res1["confidence"] == res2["confidence"]
    assert res1["affected_area_pct"] == res2["affected_area_pct"]


def test_scan_crop_image_differentiation(client):
    """Verify materially different images yield different observations and severities."""
    healthy_bytes = create_test_image(color=(30, 180, 40))
    chlorosis_bytes = create_test_image(color=(220, 180, 20))

    res_healthy = client.post("/api/v1/scan", files={"file": ("healthy.jpg", healthy_bytes, "image/jpeg")}).json()
    res_chlorosis = client.post("/api/v1/scan", files={"file": ("chlorosis.jpg", chlorosis_bytes, "image/jpeg")}).json()

    assert res_healthy["defect_type"] != res_chlorosis["defect_type"]
    assert res_healthy["severity"] != res_chlorosis["severity"]


def test_scan_crop_unsupported_format(client):
    """Verify unsupported text file is rejected with 400 Bad Request."""
    files = {"file": ("document.txt", b"Hello text", "text/plain")}
    response = client.post("/api/v1/scan", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_scan_crop_empty_file(client):
    """Verify empty 0-byte upload is rejected with 400 Bad Request."""
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/v1/scan", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_seed_history_and_readonly_get_history(client):
    """
    Verify GET /decision/history is strictly read-only and POST /decision/seed-history
    creates 3 distinct historical records tagged with DEMO/SEEDED metadata.
    """
    # 1. Read-only check: GET history before seeding returns empty list
    get_res = client.get("/api/v1/decision/history/test_history_plot_01")
    assert get_res.status_code == 200
    assert get_res.json() == []

    # 2. Seed history explicitly
    seed_res = client.post("/api/v1/decision/seed-history/tukaram_beed_01")
    assert seed_res.status_code == 201
    seeded_data = seed_res.json()
    assert len(seeded_data) >= 3

    # Verify DEMO/SEEDED metadata tag
    for item in seeded_data:
        assert "DEMO/SEEDED" in item["confidence_indicator"]

    # Verify rule boundary crossing in seeded historical records
    actions = [item["primary_action"] for item in seeded_data]
    prohibitions = [item["critical_prohibition"] for item in seeded_data]

    # Must contain different actions & prohibitions across dates
    assert len(set(actions)) >= 2
    assert len(set(prohibitions)) >= 2

