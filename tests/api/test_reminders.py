API = "/api/v1"
CRON = {"X-Cron-Token": "test-cron"}


def test_schedule_tick_snooze_confirm(client, patient, frozen):
    # 13:00 UTC = 08:00 in America/Bogota
    r = client.put(
        f"{API}/schedule", json={"doses": [{"time": "08:30", "label": "Desayuno"}, {"time": "20:00"}]}, headers=patient
    )
    assert r.status_code == 200 and len(r.json()["doses"]) == 2
    upcoming = client.get(f"{API}/reminders/upcoming", headers=patient).json()
    assert len(upcoming) == 2

    assert client.post(f"{API}/internal/reminders/tick").status_code == 401
    assert client.post(f"{API}/internal/reminders/tick", headers=CRON).json()["reminders_sent"] == 0
    frozen.advance(minutes=31)
    assert client.post(f"{API}/internal/reminders/tick", headers=CRON).json()["reminders_sent"] == 1

    first = client.get(f"{API}/reminders/upcoming", headers=patient).json()[0]
    assert first["status"] == "SENT"
    snoozed = client.post(f"{API}/reminders/{first['id']}/snooze", json={"minutes": 15}, headers=patient).json()
    assert snoozed["status"] == "SNOOZED" and snoozed["snooze_count"] == 1
    frozen.advance(minutes=16)
    assert client.post(f"{API}/internal/reminders/tick", headers=CRON).json()["reminders_sent"] == 1

    confirmed = client.post(f"{API}/reminders/{first['id']}/confirm", headers=patient).json()
    assert confirmed["reminder"]["status"] == "CONFIRMED" and confirmed["suggested_microzone_id"]


def test_schedule_limits(client, patient):
    doses = [{"time": f"0{i}:00"} for i in range(7)]
    assert client.put(f"{API}/schedule", json={"doses": doses}, headers=patient).status_code == 400
    dup = [{"time": "07:00"}, {"time": "07:00"}]
    assert (
        client.put(f"{API}/schedule", json={"doses": dup}, headers=patient).json()["error"]["code"]
        == "DUPLICATED_DOSE_TIME"
    )


def test_push_subscription(client, patient):
    body = {"endpoint": "https://push.example/abc", "p256dh": "k", "auth": "a"}
    r = client.post(f"{API}/push/subscriptions", json=body, headers=patient)
    assert r.status_code == 201
    assert client.delete(f"{API}/push/subscriptions/{r.json()['id']}", headers=patient).status_code == 204
