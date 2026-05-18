import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.routers import user as user_module

# Disable rate limiting in tests
app.state.limiter.enabled = False
user_module.limiter.enabled = False

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db):
    """暴露数据库session供测试直接操作数据"""
    return db


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """注册并登录一个测试用户，返回带Token的请求头"""
    client.post("/user/register", json={
        "username": "testuser",
        "password": "Test123456",
        "nickname": "测试用户"
    })
    res = client.post("/user/login", json={
        "username": "testuser",
        "password": "Test123456"
    })
    token = res.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def couple_headers(client):
    """注册两个用户并绑定情侣，返回 (headers_a, headers_b)"""
    # 用户A
    client.post("/user/register", json={
        "username": "usera", "password": "Test123456", "nickname": "用户A"
    })
    res_a = client.post("/user/login", json={
        "username": "usera", "password": "Test123456"
    })
    token_a = res_a.json()["data"]["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 用户B
    client.post("/user/register", json={
        "username": "userb", "password": "Test123456", "nickname": "用户B"
    })
    res_b = client.post("/user/login", json={
        "username": "userb", "password": "Test123456"
    })
    token_b = res_b.json()["data"]["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 获取用户B的邀请码
    info_b = client.get("/user/info", headers=headers_b)
    invite_code = info_b.json()["data"]["invite_code"]

    # 用户A绑定用户B
    client.post("/user/bind", headers=headers_a, json={"invite_code": invite_code})

    return headers_a, headers_b
