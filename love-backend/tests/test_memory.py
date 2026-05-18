"""时光档案馆模块接口测试 — 18个端点全覆盖"""

from datetime import datetime


# ==================== 时光线 ====================

def test_create_memory(client, auth_headers):
    res = client.post("/memory/timeline", headers=auth_headers, json={
        "title": "第一次约会", "content": "今天去了公园",
        "event_time": "2026-05-10 14:00:00"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_get_memory_list(client, auth_headers):
    client.post("/memory/timeline", headers=auth_headers, json={
        "title": "记录1", "content": "内容1", "event_time": "2026-05-10 14:00:00"
    })
    client.post("/memory/timeline", headers=auth_headers, json={
        "title": "记录2", "content": "内容2", "event_time": "2026-05-11 14:00:00"
    })
    res = client.get("/memory/timeline", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]["list"]) == 2
    assert data["data"]["total"] == 2


def test_get_memory_detail(client, auth_headers):
    create_res = client.post("/memory/timeline", headers=auth_headers, json={
        "title": "详情测试", "content": "详情内容", "event_time": "2026-05-10 14:00:00"
    })
    memory_id = create_res.json()["data"]["id"]
    res = client.get(f"/memory/timeline/{memory_id}", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "详情测试"


def test_update_memory(client, auth_headers):
    create_res = client.post("/memory/timeline", headers=auth_headers, json={
        "title": "原标题", "content": "原内容", "event_time": "2026-05-10 14:00:00"
    })
    memory_id = create_res.json()["data"]["id"]
    res = client.put(f"/memory/timeline/{memory_id}", headers=auth_headers, json={
        "title": "新标题"
    })
    assert res.json()["code"] == 200
    detail = client.get(f"/memory/timeline/{memory_id}", headers=auth_headers)
    assert detail.json()["data"]["title"] == "新标题"


def test_delete_memory(client, auth_headers):
    create_res = client.post("/memory/timeline", headers=auth_headers, json={
        "title": "待删除", "content": "", "event_time": "2026-05-10 14:00:00"
    })
    memory_id = create_res.json()["data"]["id"]
    res = client.delete(f"/memory/timeline/{memory_id}", headers=auth_headers)
    assert res.json()["code"] == 200
    detail = client.get(f"/memory/timeline/{memory_id}", headers=auth_headers)
    assert detail.json()["code"] == 404


def test_memory_not_found(client, auth_headers):
    res = client.get("/memory/timeline/99999", headers=auth_headers)
    assert res.json()["code"] == 404


def test_memory_list_pagination(client, auth_headers):
    for i in range(15):
        client.post("/memory/timeline", headers=auth_headers, json={
            "title": f"记录{i}", "content": "", "event_time": f"2026-05-{10 + i % 20:02d} 14:00:00"
        })
    res = client.get("/memory/timeline?page=1&page_size=5", headers=auth_headers)
    assert len(res.json()["data"]["list"]) == 5
    assert res.json()["data"]["total"] == 15


# ==================== 纪念日 ====================

def test_create_anniversary(client, auth_headers):
    res = client.post("/memory/anniversary", headers=auth_headers, json={
        "title": "恋爱纪念日", "target_date": "2025-06-15", "is_yearly": True
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_get_anniversary_list(client, auth_headers):
    client.post("/memory/anniversary", headers=auth_headers, json={
        "title": "纪念日1", "target_date": "2025-06-15"
    })
    res = client.get("/memory/anniversary", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1


def test_update_anniversary(client, auth_headers):
    create_res = client.post("/memory/anniversary", headers=auth_headers, json={
        "title": "原标题", "target_date": "2025-06-15"
    })
    aid = create_res.json()["data"]["id"]
    res = client.put(f"/memory/anniversary/{aid}", headers=auth_headers, json={
        "title": "新标题"
    })
    assert res.json()["code"] == 200


def test_delete_anniversary(client, auth_headers):
    create_res = client.post("/memory/anniversary", headers=auth_headers, json={
        "title": "待删除", "target_date": "2025-06-15"
    })
    aid = create_res.json()["data"]["id"]
    res = client.delete(f"/memory/anniversary/{aid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_anniversary_not_found(client, auth_headers):
    res = client.put("/memory/anniversary/99999", headers=auth_headers, json={"title": "x"})
    assert res.json()["code"] == 404


# ==================== 心愿 ====================

def test_create_wish(client, auth_headers):
    res = client.post("/memory/wish", headers=auth_headers, json={
        "content": "一起去看海"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_get_wish_list(client, auth_headers):
    client.post("/memory/wish", headers=auth_headers, json={"content": "心愿1"})
    client.post("/memory/wish", headers=auth_headers, json={"content": "心愿2"})
    res = client.get("/memory/wish", headers=auth_headers)
    assert res.json()["code"] == 200
    assert len(res.json()["data"]) >= 2


def test_complete_wish(client, auth_headers):
    create_res = client.post("/memory/wish", headers=auth_headers, json={
        "content": "想去看海", "type": "couple"
    })
    wid = create_res.json()["data"]["id"]
    res = client.put(f"/memory/wish/{wid}/complete", headers=auth_headers, json={
        "complete_time": "2026-05-11 10:00:00"
    })
    assert res.json()["code"] == 200


def test_delete_wish(client, auth_headers):
    create_res = client.post("/memory/wish", headers=auth_headers, json={"content": "待删除"})
    wid = create_res.json()["data"]["id"]
    res = client.delete(f"/memory/wish/{wid}", headers=auth_headers)
    assert res.json()["code"] == 200


def test_wish_not_found(client, auth_headers):
    res = client.delete("/memory/wish/99999", headers=auth_headers)
    assert res.json()["code"] == 404


# ==================== 悄悄话 ====================

def test_create_whisper(client, couple_headers):
    headers_a, _ = couple_headers
    res = client.post("/memory/whisper", headers=headers_a, json={
        "content": "想你了"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["id"]


def test_create_whisper_no_lover(client, auth_headers):
    res = client.post("/memory/whisper", headers=auth_headers, json={
        "content": "想你了"
    })
    assert res.json()["code"] == 400


def test_get_whisper_list(client, couple_headers):
    headers_a, headers_b = couple_headers
    client.post("/memory/whisper", headers=headers_a, json={"content": "悄悄话1"})
    res = client.get("/memory/whisper", headers=headers_b)
    assert res.json()["code"] == 200
    assert res.json()["data"]["total"] >= 1


def test_mark_whisper_read(client, couple_headers):
    headers_a, headers_b = couple_headers
    create_res = client.post("/memory/whisper", headers=headers_a, json={"content": "读我"})
    wid = create_res.json()["data"]["id"]
    res = client.put(f"/memory/whisper/{wid}/read", headers=headers_b)
    assert res.json()["code"] == 200


def test_whisper_list_empty_no_lover(client, auth_headers):
    res = client.get("/memory/whisper", headers=auth_headers)
    assert res.json()["code"] == 200
    assert res.json()["data"]["total"] == 0
