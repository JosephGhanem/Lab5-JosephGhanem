# Live API request screenshots

These PNGs are genuine macOS Terminal window captures of curl requests made
to the running Flask app at `http://localhost:5000`. Each image shows the
executed command and the server's actual status, headers, and JSON response.
They are Terminal screenshots, not Postman UI screenshots. Matching `.txt`
files provide the Terminal transcripts.

The same ten requests are in the importable
[Flask user app collection](../postman/Flask_user_app.postman_collection.json).
The [environment](../postman/Lab5_Local.postman_environment.json) defines
`base_url` as `http://localhost:5000`; the POST test saves `user_id` automatically.

| Screenshot | Request | Result |
| --- | --- | --- |
| [01 - Create](01-post-create.png) | POST `/api/users/add` | 201, created user |
| [02 - List](02-get-list.png) | GET `/api/users` | 200, list contains user |
| [03 - Read](03-get-user.png) | GET `/api/users/1` | 200, user details |
| [04 - Full update](04-put-update.png) | PUT `/api/users/update` | 200, name and country updated |
| [05 - Verify PUT](05-get-after-put.png) | GET `/api/users/1` | 200, saved changes returned |
| [06 - Partial update](06-patch-update.png) | PATCH `/api/users/1` | 200, address updated; other fields preserved |
| [07 - Verify PATCH](07-get-after-patch.png) | GET `/api/users/1` | 200, partial update persisted |
| [08 - Delete](08-delete-user.png) | DELETE `/api/users/delete/1` | 200, deletion confirmation |
| [09 - Verify deletion](09-get-deleted-user.png) | GET `/api/users/1` | 404, user no longer exists |
| [10 - Final list](10-get-final-list.png) | GET `/api/users` | 200, empty list |

The sample user was deleted by the sequence. The committed database retains
the initialized table with zero users. IDs are generated dynamically when
the collection is run again.

## Reproduce the Terminal requests

With the server running, execute the following from the repository root,
changing the step number from 1 through 10 in order:

```bash
python scripts/request_snapshot.py 1 --state /tmp/lab5-request-state.json
```

The helper reads the exported collection and executes curl. It prints the live
response, rather than the collection's saved examples. The state file stores
the newly created user ID for subsequent requests.

The separate [Newman results](newman-results.txt) record the automated run of
the Postman collection: 10 requests and 48 passing assertions.
