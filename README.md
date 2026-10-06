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

The server listens at `http://127.0.0.1:5000`. It automatically creates
`database.db` and the `users` table. SQLite is included with Python; no separate
`sqlite3` package is needed. Stop the server with Ctrl+C.

If port 5000 is busy, run `PORT=5001 python app.py` and change the Postman
environment's `base_url` to `http://127.0.0.1:5001`.

## Endpoints

| Method | Path | Purpose | Success |
| --- | --- | --- | --- |
| GET | `/api/users` | List users | 200 |
| GET | `/api/users/<user_id>` | Get one user | 200 |
| POST | `/api/users/add` | Add a user | 201 |
| PUT | `/api/users/update` | Update a user | 200 |
| DELETE | `/api/users/delete/<user_id>` | Delete a user | 200 |

POST and PUT require `Content-Type: application/json` and nonempty string
values for `name`, `email`, `phone`, `address`, and `country`. PUT also requires
a positive integer `user_id`. SQLite generates the ID for POST.

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
3. Select the **Lab 5 Local** environment.
4. Open **Flask user app** and run its eight requests in numbered order with
   the Collection Runner. The first request saves the newly generated
   `user_id`; later requests use it automatically.
5. Expand a request to view its saved response example.

Every request uses `{{base_url}}`, stored in the environment. The collection
covers all five required endpoints, verifies an update, confirms that a deleted
user returns 404, and checks the final list. It has automated status and JSON
assertions plus checks on returned data. It creates and deletes only its own
test user, so it can be run against a database that already contains users.

The saved examples were captured by making real HTTP requests to a temporary
instance of this app. They use sample data and do not modify `database.db`.
These are importable Postman files; generating them does not create a workspace
in a hosted Postman account.

## Verification

```bash
python -m unittest discover -s tests -v
python scripts/export_postman.py
```

The eight automated tests cover the full CRUD lifecycle and persistence,
validation, missing records, malformed requests, SQL injection handling,
method restrictions, and CORS. The export script runs eight HTTP checks and
regenerates the collection, examples, and environment using a temporary database.

Validation completed: all eight Python tests passed, and the exported collection
passed all eight requests and 33 assertions in Postman's Newman runner.

## Git workflow

The initial `main` commit contains the database functions. The `rest-api`
branch adds Flask routes, tests, and Postman artifacts. After verification it
is merged into `main` with a merge commit, preserving the lab's branch history.

## Submission

Upload `github_repo_link.txt` to the course submission page.
It contains the GitHub repository URL: https://github.com/JosephGhanem/Lab5-JosephGhanem.
The repository includes the source code, requirements,
tests, and Postman collection/environment. The virtual environment and local
database are excluded from Git.
