"""双人互动模块接口测试 — 22个端点全覆盖"""


# ==================== 打卡项目 ====================

def test_create_checkin_project(client, auth_headers):
    res = client.post("/interact/checkin/project", headers=auth_headers, json={
        "name": "早起打卡", "points": 5, "is_joint": False
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_list_projects(client, auth_headers):
    client.post("/interact/checkin/project", headers=auth_headers, json={"name": "项目1"})
    client.post("/interact/checkin/project", headers=auth_headers, json={"name": "项目2"})
    res = client.get("/interact/checkin/project", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2


def test_delete_project(client, auth_headers):
    create_res = client.post("/interact/checkin/project", headers=auth_headers, json={"name": "待删除"})
    pid = create_res.json()["data"]["id"]
    res = client.delete(f"/interact/checkin/project/{pid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_delete_project_not_found(client, auth_headers):
    res = client.delete("/interact/checkin/project/99999", headers=auth_headers)
    assert res.json()["code"] == 404


# ==================== 打卡记录 ====================

def test_do_checkin(client, auth_headers):
    create_res = client.post("/interact/checkin/project", headers=auth_headers, json={"name": "打卡项目", "points": 5})
    pid = create_res.json()["data"]["id"]
    res = client.post("/interact/checkin", headers=auth_headers, json={"project_id": pid})
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["points_earned"] == 5


def test_do_checkin_duplicate(client, auth_headers):
    create_res = client.post("/interact/checkin/project", headers=auth_headers, json={"name": "打卡项目"})
    pid = create_res.json()["data"]["id"]
    client.post("/interact/checkin", headers=auth_headers, json={"project_id": pid})
    res = client.post("/interact/checkin", headers=auth_headers, json={"project_id": pid})
    assert res.json()["code"] == 400


def test_checkin_history(client, auth_headers):
    create_res = client.post("/interact/checkin/project", headers=auth_headers, json={"name": "打卡项目"})
    pid = create_res.json()["data"]["id"]
    client.post("/interact/checkin", headers=auth_headers, json={"project_id": pid})
    res = client.get("/interact/checkin/history", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1


def test_checkin_stats(client, auth_headers):
    res = client.get("/interact/checkin/stats", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert "total_checkins" in data["data"]
    assert "heart_points" in data["data"]


# ==================== 积分福利 ====================

def test_create_benefit(client, auth_headers):
    res = client.post("/interact/benefit", headers=auth_headers, json={
        "name": "看电影", "points": 50
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_list_benefits(client, auth_headers):
    client.post("/interact/benefit", headers=auth_headers, json={"name": "福利1", "points": 10})
    client.post("/interact/benefit", headers=auth_headers, json={"name": "福利2", "points": 20})
    res = client.get("/interact/benefit", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2


def test_update_benefit(client, auth_headers):
    create_res = client.post("/interact/benefit", headers=auth_headers, json={"name": "原始", "points": 10})
    bid = create_res.json()["data"]["id"]
    res = client.put(f"/interact/benefit/{bid}", headers=auth_headers, json={"name": "修改后"})
    assert res.json()["code"] == 200


def test_delete_benefit(client, auth_headers):
    create_res = client.post("/interact/benefit", headers=auth_headers, json={"name": "待删除", "points": 10})
    bid = create_res.json()["data"]["id"]
    res = client.delete(f"/interact/benefit/{bid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_benefit_not_found(client, auth_headers):
    res = client.delete("/interact/benefit/99999", headers=auth_headers)
    assert res.json()["code"] == 404


def test_exchange_benefit(client, auth_headers, db_session):
    from app.models import User
    user = db_session.query(User).filter(User.username == "testuser").first()
    user.heart_points = 100
    db_session.commit()

    create_res = client.post("/interact/benefit", headers=auth_headers, json={"name": "福利", "points": 50})
    bid = create_res.json()["data"]["id"]
    res = client.post(f"/interact/benefit/{bid}/exchange", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["points_consumed"] == 50


def test_exchange_insufficient_points(client, auth_headers):
    create_res = client.post("/interact/benefit", headers=auth_headers, json={"name": "贵福利", "points": 9999})
    bid = create_res.json()["data"]["id"]
    res = client.post(f"/interact/benefit/{bid}/exchange", headers=auth_headers)
    assert res.json()["code"] == 400


def test_exchange_history(client, auth_headers):
    res = client.get("/interact/exchange/history", headers=auth_headers)
    assert res.json()["code"] == 200
    assert isinstance(res.json()["data"], list)


def test_fulfill_exchange(client, auth_headers, db_session):
    from app.models import User
    user = db_session.query(User).filter(User.username == "testuser").first()
    user.heart_points = 100
    db_session.commit()

    create_res = client.post("/interact/benefit", headers=auth_headers, json={"name": "福利", "points": 50})
    bid = create_res.json()["data"]["id"]
    exchange_res = client.post(f"/interact/benefit/{bid}/exchange", headers=auth_headers)
    rid = exchange_res.json()["data"]["id"]
    res = client.put(f"/interact/exchange/{rid}/fulfill", headers=auth_headers)
    assert res.json()["code"] == 200


# ==================== 情绪树洞 ====================

def test_create_emotion(client, auth_headers):
    res = client.post("/interact/emotion", headers=auth_headers, json={
        "emotion_type": "happy", "content": "今天很开心"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_create_negative_emotion_has_warm_reply(client, auth_headers):
    res = client.post("/interact/emotion", headers=auth_headers, json={
        "emotion_type": "sad", "content": "难过"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["warm_reply"] is not None


def test_list_emotions(client, auth_headers):
    client.post("/interact/emotion", headers=auth_headers, json={
        "emotion_type": "happy", "content": "开心"
    })
    res = client.get("/interact/emotion", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1


def test_delete_emotion(client, auth_headers):
    create_res = client.post("/interact/emotion", headers=auth_headers, json={
        "emotion_type": "happy", "content": "待删除"
    })
    eid = create_res.json()["data"]["id"]
    res = client.delete(f"/interact/emotion/{eid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_emotion_not_found(client, auth_headers):
    res = client.delete("/interact/emotion/99999", headers=auth_headers)
    assert res.json()["code"] == 404


# ==================== 情侣账本 ====================

def test_create_bill(client, auth_headers):
    res = client.post("/interact/bill", headers=auth_headers, json={
        "amount": 99.5, "type": "food", "pay_time": "2026-05-11 12:00:00", "payer": "me"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_list_bills(client, auth_headers):
    client.post("/interact/bill", headers=auth_headers, json={
        "amount": 50, "type": "food", "pay_time": "2026-05-11 12:00:00", "payer": "me"
    })
    res = client.get("/interact/bill?year=2026&month=5", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1


def test_update_bill(client, auth_headers):
    create_res = client.post("/interact/bill", headers=auth_headers, json={
        "amount": 50, "type": "food", "pay_time": "2026-05-11 12:00:00", "payer": "me"
    })
    bid = create_res.json()["data"]["id"]
    res = client.put(f"/interact/bill/{bid}", headers=auth_headers, json={"amount": 80})
    assert res.json()["code"] == 200


def test_delete_bill(client, auth_headers):
    create_res = client.post("/interact/bill", headers=auth_headers, json={
        "amount": 50, "type": "food", "pay_time": "2026-05-11 12:00:00", "payer": "me"
    })
    bid = create_res.json()["data"]["id"]
    res = client.delete(f"/interact/bill/{bid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_bill_not_found(client, auth_headers):
    res = client.delete("/interact/bill/99999", headers=auth_headers)
    assert res.json()["code"] == 404


def test_monthly_summary(client, auth_headers):
    client.post("/interact/bill", headers=auth_headers, json={
        "amount": 100, "type": "food", "pay_time": "2026-05-11 12:00:00", "payer": "me"
    })
    res = client.get("/interact/bill/monthly-summary?year=2026&month=5", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert "total" in data["data"]
    assert "my_total" in data["data"]


# ==================== 健康检查 ====================

def test_interact_health(client):
    res = client.get("/interact/health")
    data = res.json()
    assert data["code"] == 200
