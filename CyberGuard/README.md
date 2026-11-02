# CyberGuard: Integrated Cybersecurity Analysis & Utility Toolkit

An educational MCA project that joins a web dashboard (HTML, CSS, JavaScript), a C++17 server,
Python analysis modules and (planned) an Oracle database. It is a learning tool, not a
professional security product.

## Quick start (Windows)
1. Install MSYS2 UCRT64 with `mingw-w64-ucrt-x86_64-gcc`, and install Python 3.
2. Double-click `first_time_setup.bat` (downloads libraries, sets up Python, builds the server).
3. Double-click `run_all.bat`, then open http://127.0.0.1:8080

## Tests
- `tests\cpp_tests\run_tests.bat` : C++ modules 1-4
- `run_python_tests.bat` : Python modules and service

## Status
| Part | State |
|---|---|
| Web dashboard (12 views) | Done |
| C++ server and modules 1-4 (identifier, score, pointers, assessment) | Done |
| Python service (password, log, IP, reports) | Done |
| File Integrity Lab (SHA-256, OpenSSL) | Written separately, not included yet |
| Oracle schema, PL/SQL procedures, functions, cursors, triggers (`database/`) | Written, install with `database\install_all.sql` |
| Connecting the app to Oracle (history, dashboard numbers) | Planned (Phase 8) |

## Layout
`frontend/` page | `backend/` C++ server and modules | `python/` Flask service and modules |
`tests/` | `sample_data/` synthetic logs | `reports_output/` generated reports (git-ignored)

## Third-party libraries (MIT)
cpp-httplib (v0.18.7) and nlohmann/json (v3.11.3), downloaded by `setup.bat`; Flask for the Python service.
