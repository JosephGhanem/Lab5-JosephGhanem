"""Exercise a temporary HTTP server and save its responses as Postman examples."""

import copy
import json
import sys
import tempfile
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app

USER = dict(name="John Doe", email="john@example.com", phone="067765434567",
            address="John Doe Street, Innsbruck", country="Austria")
UPDATED = {**USER, "name": "Jane Doe", "country": "Lebanon"}


def main():
    items = []
    with tempfile.TemporaryDirectory() as temp:
        server = make_server("127.0.0.1", 0, create_app(str(Path(temp) / "examples.db")))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        actual_base = f"http://127.0.0.1:{server.server_port}"
        steps = [
            ("01 - Add user", "POST", "/api/users/add", USER, 201),
            ("02 - Get all users", "GET", "/api/users", None, 200),
            ("03 - Get user by ID", "GET", "/api/users/{{user_id}}", None, 200),
            ("04 - Update user", "PUT", "/api/users/update", {**UPDATED, "user_id": "{{user_id}}"}, 200),
            ("05 - Verify updated user", "GET", "/api/users/{{user_id}}", None, 200),
            ("06 - Delete user", "DELETE", "/api/users/delete/{{user_id}}", None, 200),
            ("07 - Verify user was deleted", "GET", "/api/users/{{user_id}}", None, 404),
            ("08 - Get all users after deletion", "GET", "/api/users", None, 200),
        ]
        user_id = None
        try:
            for index, (name, method, path, body, status) in enumerate(steps):
                headers = [{"key": "Accept", "value": "application/json"}]
                request = {"method": method, "header": headers, "url": "{{base_url}}" + path}
                data = None
                if body is not None:
                    headers.append({"key": "Content-Type", "value": "application/json"})
                    raw = json.dumps(body, indent=2).replace('"{{user_id}}"', "{{user_id}}")
                    request["body"] = {"mode": "raw", "raw": raw, "options": {"raw": {"language": "json"}}}
                    data = raw.replace("{{user_id}}", str(user_id)).encode()
                real_request = Request(actual_base + path.replace("{{user_id}}", str(user_id)),
                                       data=data, method=method,
                                       headers={h["key"]: h["value"] for h in headers})
                try:
                    response = urlopen(real_request, timeout=10)
                except HTTPError as error:
                    response = error
                with response:
                    response_body = json.loads(response.read())
                    assert response.status == status, (name, response.status, response_body)
                    reason = response.reason
                tests = [
                    f'pm.test("Status is {status}", function () {{ pm.response.to.have.status({status}); }});',
                    'pm.test("Response is JSON", function () { pm.response.to.be.json; });',
                    'const body = pm.response.json();',
                ]
                if index == 0:
                    user_id = response_body["user_id"]
                    assert response_body == {**USER, "user_id": user_id}
                    tests += [
                        'pm.test("Created user has an ID", function () { pm.expect(body.user_id).to.be.a("number"); });',
                        'pm.environment.set("user_id", body.user_id);',
                        'pm.test("Name is saved", function () { pm.expect(body.name).to.eql("John Doe"); });',
                    ]
                elif index in (1, 7):
                    assert response_body == ([{**USER, "user_id": user_id}] if index == 1 else [])
                    tests += ['pm.test("Returns a list", function () { pm.expect(body).to.be.an("array"); });']
                    if index == 1:
                        tests += ['pm.test("List includes created user", function () { pm.expect(body.some(u => u.user_id === Number(pm.environment.get("user_id")))).to.eql(true); });']
                    else:
                        tests += ['pm.test("List excludes deleted user", function () { pm.expect(body.some(u => u.user_id === Number(pm.environment.get("user_id")))).to.eql(false); });']
                elif index in (2, 3, 4):
                    expected = USER if index == 2 else UPDATED
                    assert response_body == {**expected, "user_id": user_id}
                    tests += [
                        'pm.test("Correct user ID", function () { pm.expect(body.user_id).to.eql(Number(pm.environment.get("user_id"))); });',
                        f'pm.test("Correct name", function () {{ pm.expect(body.name).to.eql({json.dumps(expected["name"])}); }});',
                        f'pm.test("Correct country", function () {{ pm.expect(body.country).to.eql({json.dumps(expected["country"])}); }});',
                    ]
                elif index == 5:
                    assert response_body == {"status": "User deleted successfully"}
                    tests += ['pm.test("Deletion succeeded", function () { pm.expect(body.status).to.eql("User deleted successfully"); });']
                else:
                    assert response_body == {"error": "User not found."}
                    tests += ['pm.test("User is missing", function () { pm.expect(body.error).to.eql("User not found."); });']
                items.append({
                    "name": name, "request": request,
                    "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}],
                    "response": [{
                        "name": f"{status} - {reason}", "originalRequest": copy.deepcopy(request),
                        "status": reason, "code": status, "_postman_previewlanguage": "json",
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "cookie": [], "body": json.dumps(response_body, indent=2),
                    }],
                })
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    collection = {"info": {
        "name": "Flask user app",
        "description": "Lab 5: Flask/SQLite CRUD. Select the Lab 5 Local environment and run in order. Saved examples were captured from real HTTP requests using scripts/export_postman.py. The Add user test saves the generated ID in the environment.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    }, "item": items}
    environment = {"name": "Lab 5 Local", "values": [
        {"key": "base_url", "value": "http://127.0.0.1:5000", "type": "default", "enabled": True},
        {"key": "user_id", "value": "", "type": "default", "enabled": True},
    ], "_postman_variable_scope": "environment"}
    out = ROOT / "postman"
    out.mkdir(exist_ok=True)
    (out / "Flask_user_app.postman_collection.json").write_text(json.dumps(collection, indent=2) + "\n")
    (out / "Lab5_Local.postman_environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    print(f"Captured {len(items)} successful HTTP checks and saved one response example for every request.")


if __name__ == "__main__":
    main()
