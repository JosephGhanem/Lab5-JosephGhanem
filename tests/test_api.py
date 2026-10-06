import tempfile
import unittest
from pathlib import Path

from app import create_app


class UserAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "test.db")
        self.app = create_app(self.path)
        self.app.testing = True
        self.client = self.app.test_client()
        self.user = dict(name="John Doe", email="john@example.com", phone="067765434567",
                         address="John Doe Street, Innsbruck", country="Austria")

    def tearDown(self):
        self.temp.cleanup()

    def test_full_crud_and_persistence(self):
        self.assertEqual(self.client.get("/api/users").json, [])
        response = self.client.post("/api/users/add", json=self.user)
        self.assertEqual(response.status_code, 201)
        user = response.json
        self.assertIsInstance(user["user_id"], int)
        url = f'/api/users/{user["user_id"]}'
        self.assertEqual(self.client.get(url).json, user)
        self.assertEqual(create_app(self.path).test_client().get("/api/users").json, [user])
        user["name"] = "Jane Doe"
        updated = self.client.put("/api/users/update", json=user)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.get(url).json, user)
        self.assertEqual(self.client.delete(f'/api/users/delete/{user["user_id"]}').status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.get("/api/users").json, [])

    def test_missing_fields_and_invalid_types(self):
        for body in ({}, [], None, {**self.user, "name": " "}, {**self.user, "phone": 123}):
            with self.subTest(body=body):
                response = self.client.post("/api/users/add", json=body, content_type="application/json")
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/api/users").json, [])

    def test_invalid_update_id(self):
        for value in (None, 0, -1, True, "1"):
            self.assertEqual(self.client.put("/api/users/update", json={**self.user, "user_id": value}).status_code, 400)

    def test_missing_users(self):
        self.assertEqual(self.client.get("/api/users/999").status_code, 404)
        self.assertEqual(self.client.delete("/api/users/delete/999").status_code, 404)
        self.assertEqual(self.client.put("/api/users/update", json={**self.user, "user_id": 999}).status_code, 404)

    def test_malformed_json_and_content_type(self):
        self.assertEqual(self.client.post("/api/users/add", data="{", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/users/add", data="hello").status_code, 415)

    def test_sql_injection_is_stored_as_text(self):
        name = "Robert'); DROP TABLE users;--"
        response = self.client.post("/api/users/add", json={**self.user, "name": name})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get("/api/users").json[0]["name"], name)

    def test_json_errors_and_method_restrictions(self):
        response = self.client.post("/api/users")
        self.assertEqual(response.status_code, 405)
        self.assertIn("error", response.json)
        self.assertEqual(self.client.get("/api/users/not-an-id").status_code, 404)

    def test_patch_preserves_omitted_fields(self):
        user = self.client.post("/api/users/add", json=self.user).json
        url = f'/api/users/{user["user_id"]}'
        response = self.client.patch(url, json={"country": "Lebanon"})
        self.assertEqual(response.status_code, 200)
        expected = {**user, "country": "Lebanon"}
        self.assertEqual(response.json, expected)
        self.assertEqual(create_app(self.path).test_client().get(url).json, expected)

    def test_patch_rejects_invalid_fields_without_changing_user(self):
        user = self.client.post("/api/users/add", json=self.user).json
        url = f'/api/users/{user["user_id"]}'
        for body in ({}, [], {"country": " "}, {"phone": 123}, {"user_id": 9},
                     {"unknown": "value"}, {"name": "Changed", "country": None}):
            with self.subTest(body=body):
                self.assertEqual(self.client.patch(url, json=body).status_code, 400)
                self.assertEqual(self.client.get(url).json, user)

    def test_patch_missing_user(self):
        self.assertEqual(self.client.patch("/api/users/999", json={"name": "Jane"}).status_code, 404)

    def test_cors(self):
        response = self.client.options("/api/users/add", headers={
            "Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")


if __name__ == "__main__":
    unittest.main()
