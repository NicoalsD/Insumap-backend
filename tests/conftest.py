import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["AI_SERVICE_URL"] = ""
os.environ["CRON_TOKEN"] = "test-cron"
os.environ["JWT_ACCESS_MINUTES"] = "600"  # tests advance the clock by hours

from collections.abc import Iterator  # noqa: E402
from datetime import UTC, datetime, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core import clock  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.seed import DEMO_PASSWORD, seed  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services import auth_service, reminder_service, state_service  # noqa: E402


class FrozenClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 10, 20, 13, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.current

    def advance(self, **kwargs: float) -> None:
        self.current += timedelta(**kwargs)


@pytest.fixture(autouse=True)
def frozen() -> Iterator[FrozenClock]:
    fc = FrozenClock()
    clock.set_clock(fc)
    yield fc
    clock.reset_clock()


@pytest.fixture(autouse=True)
def fresh_db(frozen: FrozenClock) -> Iterator[None]:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    state_service.clear()
    reminder_service.scheduler.clear()
    auth_service.login_attempts.clear()
    yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def login(client: TestClient, email: str, password: str = DEMO_PASSWORD) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def patient(client: TestClient) -> dict[str, str]:
    return login(client, "paciente@demo.insumap")


@pytest.fixture
def doctor(client: TestClient) -> dict[str, str]:
    return login(client, "medico@demo.insumap")
