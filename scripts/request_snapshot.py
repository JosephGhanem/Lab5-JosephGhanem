"""Run one exported collection request with curl for a real Terminal screenshot.

Run steps 1 through 10 in order, using the same --state path each time.
This executes the request; it does not display a saved Postman response.
"""

import argparse
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", type=int)
    parser.add_argument("--base-url", default="http://localhost:5000")
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    collection = json.loads((ROOT / "postman/Flask_user_app.postman_collection.json").read_text())
    item = collection["item"][args.step - 1]
    state = json.loads(args.state.read_text()) if args.state.exists() else {}

    def resolve(value):
        return value.replace("{{base_url}}", args.base_url).replace("{{user_id}}", str(state.get("user_id", "")))

    request = item["request"]
    command = ["curl", "--silent", "--show-error", "--include", "--max-time", "10",
               "--request", request["method"], resolve(request["url"])]
    for header in request["header"]:
        command += ["--header", f'{header["key"]}: {header["value"]}']
    if "body" in request:
        command += ["--data", json.dumps(json.loads(resolve(request["body"]["raw"])), separators=(",", ":"))]

    print("LAB 5 - LIVE API REQUEST AND RESPONSE")
    print(item["name"])
    print("\nREQUEST (executed with curl)")
    print("$ " + shlex.join(command))
    print("\n\nRESPONSE (received from the running Flask server)")
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    headers, body = result.stdout.split("\n\n", 1)
    parsed = json.loads(body)
    print(headers)
    print()
    print(json.dumps(parsed, indent=2))
    actual_status = int(headers.splitlines()[0].split()[1])
    expected_status = item["response"][0]["code"]
    if actual_status != expected_status:
        raise RuntimeError(f"Expected {expected_status}; received {actual_status}")
    if args.step == 1:
        state["user_id"] = parsed["user_id"]
        args.state.write_text(json.dumps(state))
    print(f"\nCHECK: HTTP {actual_status} matches the expected status.")
    print("[Request completed]")


if __name__ == "__main__":
    main()
