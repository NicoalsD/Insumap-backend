API = "/api/v1"


def patient_id(client, headers):
    return client.get(f"{API}/auth/me", headers=headers).json()["id"]


def test_link_flow_and_revoke(client, patient, doctor):
    pid = patient_id(client, patient)
    assert client.get(f"{API}/doctor/patients/{pid}/map", headers=doctor).status_code == 403

    code = client.post(f"{API}/links/codes", headers=patient).json()["code"]
    assert len(code) == 8
    link = client.post(f"{API}/links", json={"code": code.lower()}, headers=doctor)
    assert link.status_code == 201 and link.json()["patient_id"] == pid
    assert (
        client.post(f"{API}/links", json={"code": code}, headers=doctor).json()["error"]["code"] == "INVALID_LINK_CODE"
    )

    client.post(f"{API}/injections", json={"microzone_id": "ABD-I-1-1"}, headers=patient)
    assert client.get(f"{API}/doctor/patients/{pid}/map", headers=doctor).status_code == 200
    hist = client.get(f"{API}/doctor/patients/{pid}/history", headers=doctor).json()
    assert hist["items"][0]["microzone_id"] == "ABD-I-1-1"
    assert client.get(f"{API}/links", headers=patient).json()[0]["doctor_name"] == "Médico Demo"

    assert client.delete(f"{API}/links/{link.json()['id']}", headers=patient).status_code == 204
    assert client.get(f"{API}/doctor/patients/{pid}/map", headers=doctor).status_code == 403


def test_doctor_cannot_create_code(client, doctor):
    assert client.post(f"{API}/links/codes", headers=doctor).status_code == 403
