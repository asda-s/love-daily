"""生活管家模块接口测试 — 18个端点全覆盖"""


# ==================== 生理期 ====================

def test_create_period(client, auth_headers):
    res = client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-05-01", "cycle_days": 28, "duration_days": 5
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_get_period_detail(client, auth_headers):
    create_res = client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-05-01", "cycle_days": 28, "duration_days": 5
    })
    pid = create_res.json()["data"]["id"]
    res = client.get(f"/life/period/{pid}", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["start_date"] == "2026-05-01"
    assert data["data"]["end_date"] == "2026-05-05"


def test_get_period_list(client, auth_headers):
    client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-04-01", "cycle_days": 28, "duration_days": 5
    })
    client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-05-01", "cycle_days": 28, "duration_days": 5
    })
    res = client.get("/life/period", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2


def test_update_period(client, auth_headers):
    create_res = client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-05-01", "cycle_days": 28, "duration_days": 5
    })
    pid = create_res.json()["data"]["id"]
    res = client.put(f"/life/period/{pid}", headers=auth_headers, json={
        "cycle_days": 30
    })
    assert res.json()["code"] == 200


def test_delete_period(client, auth_headers):
    create_res = client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-05-01"
    })
    pid = create_res.json()["data"]["id"]
    res = client.delete(f"/life/period/{pid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_period_not_found(client, auth_headers):
    res = client.get("/life/period/99999", headers=auth_headers)
    assert res.json()["code"] == 404


def test_period_predict(client, auth_headers):
    client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-04-01", "cycle_days": 28, "duration_days": 5
    })
    client.post("/life/period", headers=auth_headers, json={
        "start_date": "2026-05-01", "cycle_days": 28, "duration_days": 5
    })
    res = client.get("/life/period/predict", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["next_period"]["start_date"]


def test_period_predict_no_records(client, auth_headers):
    res = client.get("/life/period/predict", headers=auth_headers)
    assert res.json()["code"] == 200
    assert res.json()["data"] is None


def test_period_predict_couple_permission(client, couple_headers):
    headers_a, headers_b = couple_headers
    client.post("/life/period", headers=headers_b, json={
        "start_date": "2026-05-01", "cycle_days": 28, "duration_days": 5
    })
    # 获取用户B的ID
    info_b = client.get("/user/info", headers=headers_b)
    uid_b = info_b.json()["data"]["id"]
    res = client.get(f"/life/period/predict?user_id={uid_b}", headers=headers_a)
    assert res.json()["code"] == 200


# ==================== 饮食偏好 ====================

def test_create_diet_preference(client, auth_headers):
    res = client.post("/life/diet", headers=auth_headers, json={
        "liked_food": "火锅", "avoid_food": "香菜", "allergic_food": "海鲜"
    })
    assert res.json()["code"] == 200


def test_get_diet_preference(client, auth_headers):
    client.post("/life/diet", headers=auth_headers, json={
        "liked_food": "火锅", "avoid_food": "香菜"
    })
    res = client.get("/life/diet", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["liked_food"] == "火锅"


def test_get_diet_preference_empty(client, auth_headers):
    res = client.get("/life/diet", headers=auth_headers)
    assert res.json()["code"] == 200
    assert res.json()["data"] is None


def test_update_diet_preference(client, auth_headers):
    client.post("/life/diet", headers=auth_headers, json={"liked_food": "火锅"})
    res = client.post("/life/diet", headers=auth_headers, json={"liked_food": "烤肉"})
    assert res.json()["code"] == 200
    get_res = client.get("/life/diet", headers=auth_headers)
    assert get_res.json()["data"]["liked_food"] == "烤肉"


def test_get_lover_diet_preference(client, couple_headers):
    headers_a, headers_b = couple_headers
    client.post("/life/diet", headers=headers_b, json={"liked_food": "寿司"})
    info_b = client.get("/user/info", headers=headers_b)
    uid_b = info_b.json()["data"]["id"]
    res = client.get(f"/life/diet/{uid_b}", headers=headers_a)
    assert res.json()["code"] == 200
    assert res.json()["data"]["liked_food"] == "寿司"


# ==================== 待办事项 ====================

def test_create_todo(client, auth_headers):
    res = client.post("/life/todo", headers=auth_headers, json={
        "title": "买菜", "type": "personal"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_get_todo_list(client, auth_headers):
    client.post("/life/todo", headers=auth_headers, json={"title": "待办1"})
    client.post("/life/todo", headers=auth_headers, json={"title": "待办2"})
    res = client.get("/life/todo", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2


def test_update_todo(client, auth_headers):
    create_res = client.post("/life/todo", headers=auth_headers, json={"title": "原始"})
    tid = create_res.json()["data"]["id"]
    res = client.put(f"/life/todo/{tid}", headers=auth_headers, json={"title": "修改后"})
    assert res.json()["code"] == 200


def test_delete_todo(client, auth_headers):
    create_res = client.post("/life/todo", headers=auth_headers, json={"title": "待删除"})
    tid = create_res.json()["data"]["id"]
    res = client.delete(f"/life/todo/{tid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_todo_not_found(client, auth_headers):
    res = client.delete("/life/todo/99999", headers=auth_headers)
    assert res.json()["code"] == 404


# ==================== 好物收纳 ====================

def test_create_item(client, auth_headers):
    res = client.post("/life/item", headers=auth_headers, json={
        "name": "洗面奶", "category": "日用品"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_get_item_list(client, auth_headers):
    client.post("/life/item", headers=auth_headers, json={"name": "物品1"})
    client.post("/life/item", headers=auth_headers, json={"name": "物品2"})
    res = client.get("/life/item", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2


def test_update_item(client, auth_headers):
    create_res = client.post("/life/item", headers=auth_headers, json={"name": "原始"})
    iid = create_res.json()["data"]["id"]
    res = client.put(f"/life/item/{iid}", headers=auth_headers, json={"name": "修改后"})
    assert res.json()["code"] == 200


def test_delete_item(client, auth_headers):
    create_res = client.post("/life/item", headers=auth_headers, json={"name": "待删除"})
    iid = create_res.json()["data"]["id"]
    res = client.delete(f"/life/item/{iid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_item_not_found(client, auth_headers):
    res = client.delete("/life/item/99999", headers=auth_headers)
    assert res.json()["code"] == 404


def test_get_expiring_items(client, auth_headers):
    client.post("/life/item", headers=auth_headers, json={
        "name": "临期物品", "expiry_date": "2026-05-15", "remind_days": 30
    })
    res = client.get("/life/item/expiring", headers=auth_headers)
    assert res.json()["code"] == 200
    assert isinstance(res.json()["data"], list)


def test_item_category_filter(client, auth_headers):
    client.post("/life/item", headers=auth_headers, json={"name": "食品1", "category": "食品"})
    client.post("/life/item", headers=auth_headers, json={"name": "日用1", "category": "日用品"})
    res = client.get("/life/item?category=食品", headers=auth_headers)
    items = res.json()["data"]
    assert all(i["category"] == "食品" for i in items)
