import io


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_matches_requires_user_header(client):
    response = client.get("/matches")
    assert response.status_code == 422  # falta o header X-User-Email


def test_upload_rejects_unsupported_extension(client):
    response = client.post(
        "/matches/upload",
        headers={"X-User-Email": "dev@example.com"},
        files={"file": ("partida.txt", io.BytesIO(b"nao e video"), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_accepts_video_and_ends_in_error_without_ffmpeg(client):
    # ffmpeg não está instalado nesta sandbox (docs/scope.md): o pipeline
    # deve falhar de forma controlada, marcando a partida como 'error', em
    # vez de derrubar a API.
    response = client.post(
        "/matches/upload",
        headers={"X-User-Email": "dev@example.com"},
        data={"champion_played": "Yasuo", "role": "mid"},
        files={"file": ("partida.mp4", io.BytesIO(b"bytes de um video falso"), "video/mp4")},
    )
    assert response.status_code == 202
    match_id = response.json()["id"]

    status_response = client.get(
        f"/matches/{match_id}/status", headers={"X-User-Email": "dev@example.com"}
    )
    assert status_response.json()["status"] == "error"


def test_meta_patch_404_when_empty(client):
    response = client.get("/meta/patch")
    assert response.status_code == 404
