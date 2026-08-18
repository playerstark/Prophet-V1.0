import pytest
from src.database import Base, engine
from src import models  # noqa: F401 - ensure all models are registered on Base


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    """Ensure all tables exist before any test runs.

    Individual test files instantiate `TestClient(app)` at module scope
    without using it as a context manager, so FastAPI's startup event
    (which normally calls Base.metadata.create_all) never fires. This
    session-scoped, autouse fixture guarantees the schema exists
    regardless of import order or how TestClient is constructed.
    """
    Base.metadata.create_all(bind=engine)
    yield
