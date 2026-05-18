"""用户模块接口测试 — 12个端点全覆盖"""


def test_register(client):
    res = client.post("/user/register", json={
        "username": "newuser", "password": "Test123456", "nickname": "新用户"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["invite_code"]


def test_register_duplicate(client):
    client.post("/user/register", json={
        "username": "dupuser", "password": "Test123456", "nickname": "用户A"
    })
    res = client.post("/user/register", json={
        "username": "dupuser", "password": "Test123456", "nickname": "用户B"
    })
    assert res.json()["code"] == 400


def test_login_success(client):
    client.post("/user/register", json={
        "username": "loginuser", "password": "Test123456", "nickname": "登录用户"
    })
    res = client.post("/user/login", json={
        "username": "loginuser", "password": "Test123456"
    })
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["token"]


def test_login_wrong_password(client):
    client.post("/user/register", json={
        "username": "wrongpw", "password": "Test123456", "nickname": "用户"
    })
    res = client.post("/user/login", json={
        "username": "wrongpw", "password": "WrongPassword"
    })
    assert res.json()["code"] == 400


def test_login_nonexistent_user(client):
    res = client.post("/user/login", json={
        "username": "noexist", "password": "Test123456"
    })
    assert res.json()["code"] == 400


def test_get_user_info(client, auth_headers):
    res = client.get("/user/info", headers=auth_headers)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "testuser"
    assert data["data"]["nickname"] == "测试用户"
    assert "invite_code" in data["data"]


def test_get_user_info_unauthorized(client):
    res = client.get("/user/info")
    assert res.status_code in (401, 403)


def test_update_user_info_nickname(client, auth_headers):
    res = client.put("/user/info", headers=auth_headers, json={
        "nickname": "新昵称"
    })
    assert res.json()["code"] == 200
    info = client.get("/user/info", headers=auth_headers)
    assert info.json()["data"]["nickname"] == "新昵称"


def test_update_user_info_password(client, auth_headers):
    res = client.put("/user/info", headers=auth_headers, json={
        "old_password": "Test123456",
        "new_password": "NewPass123"
    })
    assert res.json()["code"] == 200
    # 用新密码登录
    res = client.post("/user/login", json={
        "username": "testuser", "password": "NewPass123"
    })
    assert res.json()["code"] == 200


def test_update_password_wrong_old(client, auth_headers):
    res = client.put("/user/info", headers=auth_headers, json={
        "old_password": "WrongOld",
        "new_password": "NewPass123"
    })
    assert res.json()["code"] == 400


def test_bind_lover(client, couple_headers):
    headers_a, headers_b = couple_headers
    info_a = client.get("/user/info", headers=headers_a)
    info_b = client.get("/user/info", headers=headers_b)
    assert info_a.json()["data"]["lover_id"] is not None
    assert info_b.json()["data"]["lover_id"] is not None


def test_bind_self(client, auth_headers):
    info = client.get("/user/info", headers=auth_headers)
    code = info.json()["data"]["invite_code"]
    res = client.post("/user/bind", headers=auth_headers, json={"invite_code": code})
    assert res.json()["code"] == 400


def test_bind_invalid_code(client, auth_headers):
    res = client.post("/user/bind", headers=auth_headers, json={"invite_code": "XXXXXX"})
    assert res.json()["code"] == 400


def test_bind_already_bound(client, couple_headers):
    headers_a, _ = couple_headers
    # 再注册一个用户
    client.post("/user/register", json={
        "username": "userc", "password": "Test123456", "nickname": "用户C"
    })
    res_c = client.post("/user/login", json={"username": "userc", "password": "Test123456"})
    code_c = client.get("/user/info", headers={"Authorization": f"Bearer {res_c.json()['data']['token']}"}).json()["data"]["invite_code"]
    res = client.post("/user/bind", headers=headers_a, json={"invite_code": code_c})
    assert res.json()["code"] == 400


def test_get_lover_info(client, couple_headers):
    headers_a, headers_b = couple_headers
    res = client.get("/user/lover", headers=headers_a)
    data = res.json()
    assert data["code"] == 200
    assert data["data"]["nickname"] == "用户B"


def test_get_lover_info_unbound(client, auth_headers):
    res = client.get("/user/lover", headers=auth_headers)
    assert res.json()["code"] == 200
    assert res.json()["data"] is None


def test_get_notifications(client, auth_headers):
    res = client.get("/user/notifications", headers=auth_headers)
    assert res.json()["code"] == 200
    assert isinstance(res.json()["data"], list)


def test_unread_count(client, auth_headers):
    res = client.get("/user/notifications/unread-count", headers=auth_headers)
    assert res.json()["code"] == 200
    assert res.json()["data"]["count"] == 0


def test_mark_read_nonexistent(client, auth_headers):
    res = client.put("/user/notifications/99999/read", headers=auth_headers)
    assert res.json()["code"] == 404


def test_mark_all_read(client, auth_headers):
    res = client.put("/user/notifications/read-all", headers=auth_headers)
    assert res.json()["code"] == 200


def test_unbind_not_bound(client, auth_headers):
    res = client.post("/user/unbind", headers=auth_headers)
    assert res.json()["code"] == 400


def test_unbind_lover(client, couple_headers):
    headers_a, headers_b = couple_headers
    res = client.post("/user/unbind", headers=headers_a)
    assert res.json()["code"] == 200
    info_a = client.get("/user/info", headers=headers_a)
    assert info_a.json()["data"]["lover_id"] is None


def test_delete_account(client, auth_headers):
    res = client.delete("/user/account", headers=auth_headers)
    assert res.json()["code"] == 200
    # 登录应失败
    res = client.post("/user/login", json={"username": "testuser", "password": "Test123456"})
    assert res.json()["code"] == 400
