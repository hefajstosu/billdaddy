def test_api_requires_login(app):
    c = app.test_client()
    assert c.get("/api/receipts").status_code == 401
    assert c.get("/api/products").status_code == 401
    assert c.get("/api/stats/categories").status_code == 401


def test_index_redirects_when_logged_out(app):
    assert app.test_client().get("/").status_code == 302


def test_login_wrong_password(app):
    res = app.test_client().post("/login", data={"username": "test", "password": "nope"})
    assert res.status_code == 200
    assert "dane logowania" in res.get_data(as_text=True)


def test_login_and_logout(app):
    c = app.test_client()
    assert c.post("/login", data={"username": "test", "password": "test"}).status_code == 302
    assert c.get("/api/receipts").status_code == 200

    c.get("/logout")
    assert c.get("/api/receipts").status_code == 401
