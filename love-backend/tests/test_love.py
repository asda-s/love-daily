"""恋爱养成模块接口测试 — 8个端点全覆盖"""

import os


def test_love_overview(client, auth_headers):
    res = client.get("/love/overview", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert "level" in data["data"]
    assert "heart_points" in data["data"]
    assert "progress" in data["data"]


def test_get_levels(client):
    res = client.get("/love/levels")
    data = res.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)


def test_get_achievements(client, auth_headers):
    res = client.get("/love/achievements", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)
    # 注册时会初始化成就
    assert len(data["data"]) > 0


def test_unlock_achievement(client, auth_headers):
    # 获取成就列表
    achieve_res = client.get("/love/achievements", headers=auth_headers)
    achievements = achieve_res.json()["data"]
    # 找一个未解锁的
    locked = [a for a in achievements if not a["is_unlocked"]]
    assert len(locked) > 0
    name = locked[0]["name"]
    res = client.post(f"/love/unlock-achievement?achievement_name={name}", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["reward_points"] > 0


def test_unlock_already_unlocked(client, auth_headers):
    achieve_res = client.get("/love/achievements", headers=auth_headers)
    achievements = achieve_res.json()["data"]
    locked = [a for a in achievements if not a["is_unlocked"]]
    name = locked[0]["name"]
    client.post(f"/love/unlock-achievement?achievement_name={name}", headers=auth_headers)
    res = client.post(f"/love/unlock-achievement?achievement_name={name}", headers=auth_headers)
    assert res.json()["code"] == 400


def test_add_points_requires_internal_key(client, auth_headers):
    res = client.post("/love/add-points", headers=auth_headers, json={
        "points": 10, "reason": "测试"
    })
    assert res.json()["code"] == 403


def test_add_points_with_internal_key(client, auth_headers):
    internal_key = os.getenv("INTERNAL_API_KEY", "")
    if not internal_key:
        # 跳过：未配置INTERNAL_API_KEY
        return
    headers = {**auth_headers, "X-Internal-Key": internal_key}
    res = client.post("/love/add-points", headers=headers, json={
        "points": 10, "reason": "测试加分"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["points_added"] == 10


def test_points_history(client, auth_headers):
    res = client.get("/love/points-history", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)


def test_love_health(client):
    res = client.get("/love/health")
    data = res.json()
    assert data["code"] == 200


def test_love_stats(client, auth_headers):
    res = client.get("/love/stats", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert "days_together" in data["data"]
    assert "heart_points" in data["data"]
    assert "memory_count" in data["data"]
    assert "emotion_count" in data["data"]


def test_points_history_after_unlock(client, auth_headers):
    achieve_res = client.get("/love/achievements", headers=auth_headers)
    achievements = achieve_res.json()["data"]
    locked = [a for a in achievements if not a["is_unlocked"]]
    if locked:
        name = locked[0]["name"]
        client.post(f"/love/unlock-achievement?achievement_name={name}", headers=auth_headers)
    res = client.get("/love/points-history", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    # 至少有一条记录（解锁成就产生的）
