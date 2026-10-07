API = "/api/v1"


def register(client, headers, frozen, zones):
    for z in zones:
        assert client.post(f"{API}/injections", json={"microzone_id": z}, headers=headers).status_code == 201
        frozen.advance(hours=1)


def test_pagination_with_cursor(client, patient, frozen):
    zones = ["ABD-I-1-1", "ABD-I-1-2", "MUS-D-1-1", "BRA-I-2-2", "GLU-D-3-3"]
    register(client, patient, frozen, zones)
    p1 = client.get(f"{API}/history?limit=2", headers=patient).json()
    assert [i["microzone_id"] for i in p1["items"]] == ["GLU-D-3-3", "BRA-I-2-2"]
    p2 = client.get(f"{API}/history?limit=2&cursor={p1['next_cursor']}", headers=patient).json()
    assert [i["microzone_id"] for i in p2["items"]] == ["MUS-D-1-1", "ABD-I-1-2"]
    p3 = client.get(f"{API}/history?limit=2&cursor={p2['next_cursor']}", headers=patient).json()
    assert [i["microzone_id"] for i in p3["items"]] == ["ABD-I-1-1"] and p3["next_cursor"] is None
    asc = client.get(f"{API}/history?order=asc&macro=ABD", headers=patient).json()
    assert [i["microzone_id"] for i in asc["items"]] == ["ABD-I-1-1", "ABD-I-1-2"]


def test_exports(client, patient, frozen):
    assert client.get(f"{API}/history/export?format=csv", headers=patient).json()["error"]["code"] == "EMPTY_HISTORY"
    register(client, patient, frozen, ["ABD-I-1-1", "MUS-D-1-1"])
    csv = client.get(f"{API}/history/export?format=csv", headers=patient)
    assert csv.status_code == 200
    text = csv.content.decode("utf-8-sig")
    assert text.splitlines()[0] == "Fecha,Hora,Microzona,Zona macro,Lado,Estado"
    assert "ABD-I-1-1,Abdomen,izquierdo,Registrada" in text
    pdf = client.get(f"{API}/history/export?format=pdf", headers=patient)
    assert pdf.content[:4] == b"%PDF"
    xlsx = client.get(f"{API}/history/export?format=xlsx", headers=patient)
    assert xlsx.content[:2] == b"PK"
