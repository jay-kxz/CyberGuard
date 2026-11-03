# CyberGuard: Integrated Cybersecurity Analysis & Utility Toolkit

An educational MCA project that joins a web dashboard (HTML, CSS, JavaScript), a C++17 server,
Python analysis modules and an Oracle database. It is a learning tool, not a professional
security product.

## Quick start (Windows)
1. Install MSYS2 UCRT64 with `mingw-w64-ucrt-x86_64-gcc`, and install Python 3.
2. Double-click `first_time_setup.bat` (downloads libraries, sets up Python, builds the server).
3. Copy `.env.example` to `.env` and fill in the Oracle password (optional, see below).
4. Double-click `run_all.bat`, then open http://127.0.0.1:8080

The dashboard works with or without the database. Without it, every tool still runs and the
page says the result was not saved; with it, the Overview numbers and Activity History fill in.

## The database (Oracle Database Free)
The application never talks to Oracle directly: `python/db.py` is the only place a connection is
opened, and it calls the PL/SQL objects the schema already defines.

1. Run `database\00_create_user.sql` once as SYS (it creates the `cyberguard` user).
2. Log in as `cyberguard` and run `@"C:\path\to\CyberGuard\database\install_all.sql"`.
3. Put the password in `.env`:
   ```
   CYBERGUARD_DB_PASSWORD=the-password-you-chose
   ```
4. Start the Python service; `GET /api/health` reports `"database": true` when it is connected.

Useful switches: `CYBERGUARD_DB=off` skips the database entirely, and `CYBERGUARD_DB_DSN`
points at another host (`localhost:1521/FREEPDB1` is the default). To check the live
connection from the tests, run `set CYBERGUARD_DB_TEST=1` before the Python tests.

## Tests
- `tests\cpp_tests\run_tests.bat` : C++ modules 1-5 (includes the four published SHA-256 vectors)
- `run_python_tests.bat` : Python modules, the Flask service and the database layer

## Status
| Part | State |
|---|---|
| Web dashboard (12 views) | Done |
| C++ server and modules 1-4 (identifier, score, pointers, assessment) | Done |
| File Integrity Lab (SHA-256, Module 5) | Done - hashing written in C++, no external library needed |
| Python service (password, log, IP, reports) | Done |
| Oracle schema, PL/SQL procedures, functions, cursors, triggers (`database/`) | Done - install with `database\install_all.sql` |
| Connecting the app to Oracle (history, dashboard numbers) | Done - `python/db.py` calls the PL/SQL (Phase 8) |
| Reports on disk (`reports_output/`) | Done, generated at run time and git-ignored |

## API
Every reply is `{"ok": true, "data": ...}` or `{"ok": false, "error": "..."}`.
`"persisted"` in `data` says whether the result reached the database.

| Method | Address | What it does |
|---|---|---|
| GET | `/api/health` | Server, Python service and database status |
| POST | `/api/analyze` | Module 1, digit and letter counts |
| POST | `/api/calculate` | Module 2, count, sum, minimum, maximum, average |
| POST | `/api/pointers` | Module 3, sum and absolute difference through pointers |
| POST | `/api/assessment` | Module 4, five scores against a baseline |
| POST | `/api/file-hash` | Module 5, SHA-256 of an uploaded file (multipart) and a reference comparison |
| POST | `/api/password-strength` | Module 6, password rating and tips |
| POST | `/api/log-analysis` | Module 7, log summary |
| POST | `/api/ip-validation` | Module 8, IPv4/IPv6 check |
| POST | `/api/report` | Module 9, TXT or CSV report of the latest result |
| GET | `/api/history` | Newest analyses (needs the database) |
| GET | `/api/dashboard` | The four Overview numbers (needs the database) |
| GET | `/api/reports` | Newest generated reports (needs the database) |

Python-only helpers the C++ server calls: `POST /api/record`, `/api/assessment`,
`/api/file-check`.

## Layout
`frontend/` page | `backend/` C++ server and modules | `python/` Flask service, analysis modules
and `db.py` (the Oracle connection) | `tests/` | `sample_data/` synthetic logs |
`reports_output/` generated reports (git-ignored)

## Third-party libraries (MIT)
cpp-httplib (v0.18.7) and nlohmann/json (v3.11.3), downloaded by `setup.bat`; Flask and
python-oracledb for the Python service.
