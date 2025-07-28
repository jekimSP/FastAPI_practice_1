import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.db import get_db,Base
from api.main import app

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async def get_test_db():
        async with async_session() as session:
            yield session
            #의존성 주입 -> fastapi가 테스트용 db를 참조
    
    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

#14-4
import starlette.status

@pytest.mark.asyncio
async def test_create_and_read(async_client):
    response = await async_client.post("/tasks", json={"title": "테스트 작업"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "테스트 작업"

    response = await async_client.get("/tasks")
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "테스트 작업"
    assert response_obj[0]["done"] is False

@pytest.mark.asyncio
async def test_done_flag(async_client):
    response = await async_client.post("/tasks", json={"title": "테스트 작업2"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "테스트 작업2"

    response = await async_client.put("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    response = await async_client.put("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_400_BAD_REQUEST

    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_param, expectation",
    [
        ("2025-07-24", starlette.status.HTTP_200_OK),
        ("2025-07-32", starlette.status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("2025/07/24",starlette.status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("2025-0724",starlette.status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_due_date(input_param, expectation, async_client):
    response = await async_client.post(
        "/tasks", json={"title": "테스트 작업3", "due_date": input_param}
        )
    assert response.status_code == expectation
    
    '''
    input_list = ["2025-07-24", "2025-07-32", "2025/07/24", "2025-0724"]
    expectation_list = [
        starlette.status.HTTP_200_OK,
        starlette.status.HTTP_422_UNPROCESSABLE_ENTITY,
        starlette.status.HTTP_422_UNPROCESSABLE_ENTITY,
        starlette.status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]
    for input_param, expectation in zip(input_list, expectation_list):
        response = await async_client.post("/tasks", json={"title": "테스트 작업3", "due_date": input_param})
        assert response.status_code == expectation
    '''

"""
    response = await async_client.post("/tasks", json={"title": "테스트 작업3", "due_date" : input_param})
    assert response.status_code == expectation

    response = await async_client.post("/tasks", json={"title": "테스트 작업3", "due_date" : input_param})
    assert response.status_code == expectation

    response = await async_client.post("/tasks", json={"title": "테스트 작업3", "due_date" : input_param})
    assert response.status_code == expectation

    response = await async_client.post("/tasks", json={"title": "테스트 작업3", "due_date" : input_param})
    assert response.status_code == expectation
"""