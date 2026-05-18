"""根路径和健康检查端点测试"""


def test_root(client):
    res = client.get("/")
    data = res.json()
    assert data["code"] == 200


def test_health(client):
    res = client.get("/health")
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["status"] == "healthy"
