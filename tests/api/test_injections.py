API = "/api/v1"


def cell(map_json, microzone_id):
    for zone in map_json["zones"]:
        for side in zone["sides"]:
            for c in side["cells"]:
                if c["id"] == microzone_id:
                    return c
    raise AssertionError(microzone_id)


def test_map_shape(client, patient):
    r = client.get(f"{API}/map", headers=patient)
    assert r.status_code == 200
    data = r.json()
    assert data["grid_size"] == 4
    assert [z["macro"] for z in data["zones"]] == ["ABD", "MUS", "BRA", "GLU"]
    assert sum(len(s["cells"]) for z in data["zones"] for s in z["sides"]) == 128
    assert all(c["color"] == "GREEN" for z in data["zones"] for s in z["sides"] for c in s["cells"])


def test_register_warn_confirm_and_undo(client, patient, frozen):
    r = client.post(f"{API}/injections", json={"microzone_id": "MUS-I-1-2"}, headers=patient)
    assert r.status_code == 201
    assert r.json()["microzone"]["color"] == "RED" and r.json()["can_undo"]

    frozen.advance(hours=2)
    r = client.post(f"{API}/injections", json={"microzone_id": "MUS-I-1-2"}, headers=patient)
    assert r.status_code == 409
    err = r.json()["error"]
    assert err["code"] == "MICROZONE_NOT_RECOVERED" and err["detail"]["color"] == "RED"
    assert err["detail"]["suggested_microzone_id"]

    r = client.post(
        f"{API}/injections", json={"microzone_id": "MUS-I-1-2", "confirm_not_recovered": True}, headers=patient
    )
    assert r.status_code == 201

    r = client.post(f"{API}/injections/undo", headers=patient)
    assert r.status_code == 200 and r.json()["injection"]["status"] == "UNDONE"
    r = client.post(f"{API}/injections/undo", headers=patient)
    assert r.status_code == 200
    assert r.json()["microzone"]["color"] == "GREEN" and r.json()["microzone"]["last_used"] is None
    assert client.post(f"{API}/injections/undo", headers=patient).json()["error"]["code"] == "NOTHING_TO_UNDO"


def test_state_survives_cache_rebuild(client, patient, frozen):
    from app.services import state_service

    client.post(f"{API}/injections", json={"microzone_id": "ABD-D-2-2"}, headers=patient)
    before = cell(client.get(f"{API}/map", headers=patient).json(), "ABD-D-2-2")
    state_service.clear()
    after = cell(client.get(f"{API}/map", headers=patient).json(), "ABD-D-2-2")
    assert before == after


def test_invalid_microzone(client, patient):
    r = client.post(f"{API}/injections", json={"microzone_id": "ABD-I-5-1"}, headers=patient)
    assert r.json()["error"]["code"] == "INVALID_MICROZONE"
    assert client.get(f"{API}/microzones/XYZ", headers=patient).status_code == 400


def test_suggestions_avoid_used_zone(client, patient):
    client.post(f"{API}/injections", json={"microzone_id": "GLU-D-1-1"}, headers=patient)
    sug = client.get(f"{API}/suggestions?k=5", headers=patient).json()["suggestions"]
    assert len(sug) == 5
    assert "GLU-D-1-1" not in [s["microzone_id"] for s in sug]
    assert set(sug[0]["breakdown"]) == {"ratio", "forgotten_bonus", "overuse_penalty", "neighbor_penalty"}


def test_grid_change_projects_history(client, patient):
    client.post(f"{API}/injections", json={"microzone_id": "GLU-I-4-3"}, headers=patient)
    r = client.put(f"{API}/settings/grid", json={"grid_size": 2}, headers=patient)
    assert r.json()["grid_size"] == 2
    assert cell(r.json(), "GLU-I-2-2")["color"] == "RED"


def test_doctor_cannot_register(client, doctor):
    r = client.post(f"{API}/injections", json={"microzone_id": "MUS-I-1-2"}, headers=doctor)
    assert r.status_code == 403
