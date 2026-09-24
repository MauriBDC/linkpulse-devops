def test_create_link_and_read_stats(client):
    response = client.post(
        "/links",
        json={"url": "https://example.com/article"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["original_url"] == "https://example.com/article"
    assert body["clicks"] == 0
    assert body["short_code"]

    stats = client.get(f"/links/{body['short_code']}/stats")
    assert stats.status_code == 200
    assert stats.json()["clicks"] == 0


def test_redirect_increments_click_counter(client):
    created = client.post(
        "/links",
        json={"url": "https://example.com"},
    ).json()

    redirect = client.get(
        f"/{created['short_code']}",
        follow_redirects=False,
    )

    assert redirect.status_code == 302
    assert redirect.headers["location"] == "https://example.com/"

    stats = client.get(f"/links/{created['short_code']}/stats")
    assert stats.json()["clicks"] == 1


def test_missing_link_returns_404(client):
    response = client.get("/links/notfound/stats")

    assert response.status_code == 404
