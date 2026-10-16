# CareerProof API Design (V0)

Status: draft. Scope: authentication and career profile.

## 1. Conventions

- **Base path:** `/api/v1`. The version lives in the path so we can ship `/v2` later without breaking existing clients.
- **Format:** JSON, `snake_case` field names. Dates are ISO 8601 (`2026-10-16`); timestamps are UTC with timezone.
- **Auth:** `Authorization: Bearer <access_token>`. Access tokens last 60 minutes. No refresh tokens in V0.
- **Identity:** the user is always taken from the token, never from the URL or request body. There is no `/users/{id}/skills`.
- **Ownership:** a user can only see and change their own records. A record belonging to someone else returns **404**, not 403, so we don't reveal that it exists.
- **Resources:** plural nouns (`/skills`). Actions use HTTP methods, not verbs in paths.
- **Errors:** FastAPI's standard shape `{"detail": "..."}`. Validation errors return `422` with a list of field problems.
- **Status codes:** `200` OK, `201` created (returns the new object), `204` deleted (no body), `400` malformed request, `401` missing/invalid token or bad credentials, `404` not found (or not yours), `409` conflict (duplicate), `422` validation error.
- **Lists:** unpaginated in V0 (each user has few records). Pagination is added in V1 for applications.
- **Secrets:** `password_hash` is never returned by any endpoint.
- **Health:** `GET /health` (no auth) for deployment checks.

## 2. Endpoints

### Auth and account

| Method | Path | Auth | Request | Success | Errors |
|---|---|---|---|---|---|
| POST | /api/v1/auth/register | No | `{email, password}` | 201 + user (no password) | 409 email taken, 422 invalid email or password under 8 characters |
| POST | /api/v1/auth/login | No | form: `username` (email), `password` | 200 + `{access_token, token_type}` | 401 incorrect email or password (same message for both) |
| GET | /api/v1/users/me | Yes | none | 200 + user | 401 |
| GET | /api/v1/users/me/export | Yes | none | 200 + JSON of all the user's data | 401 |
| DELETE | /api/v1/users/me | Yes | `{password}` | 204 | 401 not logged in or wrong password |

### Profile

| Method | Path | Auth | Request | Success | Errors |
|---|---|---|---|---|---|
| GET | /api/v1/profile | Yes | none | 200 + profile | 401 |
| PATCH | /api/v1/profile | Yes | any subset of profile fields | 200 + updated profile | 401, 422 |

### Career records (same pattern for each resource)

Resources: `skills`, `experiences`, `projects`, `educations`, `certifications`.

| Method | Path | Auth | Request | Success | Errors |
|---|---|---|---|---|---|
| GET | /api/v1/{resource} | Yes | none | 200 + list (own records only) | 401 |
| POST | /api/v1/{resource} | Yes | resource fields | 201 + created record | 401, 422, 409 (skills: duplicate name) |
| GET | /api/v1/{resource}/{id} | Yes | none | 200 + record | 401, 404 |
| PATCH | /api/v1/{resource}/{id} | Yes | any subset of fields | 200 + updated record | 401, 404, 422, 409 |
| DELETE | /api/v1/{resource}/{id} | Yes | none | 204 | 401, 404 |

## 3. Behaviors worth stating

- Emails are lowercased and trimmed before storage and lookup.
- Registering also creates an empty profile in the same transaction.
- Deleting an account removes the user and every dependent row, atomically.
- Date rules (`end_date >= start_date`) are enforced by the database and return 422 from the API.

## 4. Deferred (not in V0)

Refresh tokens, email verification, password reset, pagination, account lockout.