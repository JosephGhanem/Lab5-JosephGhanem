# Lab 5 - Postman and APIs

Flask REST API for creating, reading, updating, and deleting users in SQLite.

## Run

Requires Python 3.9 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The server is accessible at `http://localhost:5000`. The repository includes
`database.db` with an initialized, empty `users` table. The app also creates
the database/table if absent. SQLite is included with Python; no separate
`sqlite3` package is needed. Stop the server with Ctrl+C.

If port 5000 is busy, run `PORT=5001 python app.py` and change the Postman
environment's `base_url` to `http://127.0.0.1:5001`.

The launcher serves both IPv4 (`127.0.0.1`) and IPv6 (`::1`) loopback so that
clients resolving `localhost` either way reach the app. If IPv6 is unavailable,
it reports a warning and still serves IPv4; use `http://127.0.0.1:5000` in that
case. Both listeners are local to this computer.

## Endpoints

| Method | Path | Purpose | Success |
| --- | --- | --- | --- |
| GET | `/api/users` | List users | 200 |
| GET | `/api/users/<user_id>` | Get one user | 200 |
| POST | `/api/users/add` | Add a user | 201 |
| PUT | `/api/users/update` | Update a user | 200 |
| PATCH | `/api/users/<user_id>` | Update selected fields | 200 |
| DELETE | `/api/users/delete/<user_id>` | Delete a user | 200 |

POST and PUT require `Content-Type: application/json` and nonempty string
values for `name`, `email`, `phone`, `address`, and `country`. PUT also requires
a positive integer `user_id`. SQLite generates the ID for POST.

PATCH accepts one or more of the five editable fields and preserves omitted
fields. For example, `PATCH /api/users/1` with
`{"address": "Hamra Street, Beirut"}` changes only the address. The ID belongs
in the URL; unknown fields and changes to `user_id` are rejected.

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "067765434567",
  "address": "John Doe Street, Innsbruck",
  "country": "Austria"
}
```

Missing users return 404, invalid JSON/fields return 400, and a non-JSON request
body returns 415. Responses, including errors, are JSON. SQL parameters protect
the database from injection. Connections close after each database operation.
CORS is enabled for the lab API; this local learning app has no authentication.

## Postman graded exercise

1. Start the app.
2. Import `postman/Flask_user_app.postman_collection.json` and
   `postman/Lab5_Local.postman_environment.json` into Postman.
3. Select the **Lab 5 Local** environment. Alternatively, create your own
   environment with `base_url` set to `http://localhost:5000` (include `http://`).
4. Open **Flask user app** and run its ten requests in numbered order with
   the Collection Runner. The first request saves the newly generated
   `user_id`; later requests use it automatically.
5. Expand a request to view its saved response example.

Every request uses `{{base_url}}`, stored in the environment. The collection
covers GET, POST, PUT, PATCH, and DELETE, verifies both full and partial updates, confirms that a deleted
user returns 404, and checks the final list. It has automated status and JSON
assertions plus checks on returned data. It creates and deletes only its own
test user, so it can be run against a database that already contains users.

The saved examples were captured by making real HTTP requests to a temporary
instance of this app. They use sample data and do not modify `database.db`.
These are importable Postman files; generating them does not create a workspace
in a hosted Postman account.

## Request screenshots

The [screenshots folder](screenshots/README.md) contains ten genuine Terminal
window screenshots showing live curl commands and their corresponding HTTP
status, headers, and JSON responses from `http://localhost:5000`. They cover
the full sequence, including PUT, PATCH, DELETE, and GET verification.
Each PNG has a matching text transcript. These are Terminal/curl screenshots;
the Postman collection and its saved response examples are provided separately.

## Verification

```bash
python -m unittest discover -s tests -v
python scripts/export_postman.py
```

The eleven automated tests cover the full CRUD lifecycle and persistence,
validation, missing records, malformed requests, SQL injection handling,
method restrictions, CORS, and partial updates. The export script runs ten HTTP checks and
regenerates the collection, examples, and environment using a temporary database.

Validation completed: all eleven Python tests passed, and the exported collection
passed all ten requests and 48 assertions in Postman's Newman runner using the
included `base_url=http://localhost:5000` environment. See the complete
[Newman results](screenshots/newman-results.txt).

## Git workflow

The initial `main` commit contains the database functions. The `rest-api`
branch adds Flask routes, tests, and Postman artifacts. After verification it
is merged into `main` with a merge commit, preserving the lab's branch history.

## Submission

Upload `github_repo_link.txt` to the course submission page.
It contains the GitHub repository URL: https://github.com/JosephGhanem/Lab5-JosephGhanem.
The repository includes `database.py`, `app.py`, `database.db`, API request
screenshots, the importable Postman collection/environment, requirements, and
tests. The virtual environment is excluded from Git; the required `database.db`
is explicitly included.
