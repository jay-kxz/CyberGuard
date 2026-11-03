# RUN ON HER MACHINE - screen-share runbook

Copy-paste, in order. Each step has an **EXPECT** line: if it matches, continue; if not,
read the FIX line, then see the table at the end.

You are driving, so keep this open on your screen and type on hers.

---

## STEP 0 - get the handover files onto her PC (2 minutes)

In `Desktop\CyberGuard_Submission\` on your PC:

    CyberGuard-phase8.bundle      the five commits, verified
    CyberGuard_Handover.zip       the seven Word documents plus these instructions

Transfer them with your remote tool (drag and drop, clipboard file copy), or send them to
her by email / OneDrive / WhatsApp and open them there. Put both in her **Downloads**.

---

## STEP 1 - check her machine (1 minute)

Open Command Prompt (Win+R, `cmd`, Enter):

```bat
where g++ & where python & python --version & where git
```

**EXPECT** - a `g++` path under `msys64\ucrt64\bin`, a `python` path, a version such as
`Python 3.12.x`, and a `git` path.

**FIX** - no `g++` means MSYS2 UCRT64 with `mingw-w64-ucrt-x86_64-gcc` must be installed;
the batch files look for `C:\msys64\ucrt64\bin`.

Then check the database:

```bat
where sqlplus
```

A path means Oracle is installed. No path: decide now whether to skip the database figures
(figure 9.1 and 9.11 will then show the offline state) or install Oracle Database Free
first. Nothing else depends on it.

---

## STEP 2 - put the finished code on her machine (2 minutes)

```bat
cd %USERPROFILE%\Downloads
git clone -b finish/phase8-database CyberGuard-phase8.bundle CyberGuard
cd CyberGuard
cd CyberGuard
```

**EXPECT** - `Cloning into 'CyberGuard'...`, then a listing with `backend  database  docs
frontend  python  sample_data  tests` and the `.bat` files.

**Why two `cd`s:** the repository holds the project inside a folder also called
`CyberGuard`, so the project is `CyberGuard\CyberGuard`. Everything below runs from that
second folder - this is the single most common way this session goes wrong.

Connect it to her repository:

```bat
git remote remove origin
git remote add origin https://github.com/jay-kxz/CyberGuard.git
git log --oneline -5
```

**EXPECT** - five commits, newest first, starting with `Add the screen-share runbook`.

---

## STEP 3 - install, build, test (5 minutes, mostly downloading)

```bat
first_time_setup.bat
```

**EXPECT** - steps 1, 2, 3, then
`ALL DONE. Now double-click run_all.bat to start CyberGuard.`

**FIX** - a WARNING about packages is acceptable: the analysis tools still work, only the
database figures are affected. `BUILD FAILED` means read the first compiler error; the usual
cause is a missing `backend\vendor\httplib.h` - check the connection and run it again.

```bat
tests\cpp_tests\run_tests.bat
```

**EXPECT** - `33 checks passed, 0 failed`

```bat
run_python_tests.bat
```

**EXPECT** - `Ran 49 tests` then `OK (skipped=1)`. The skip is the live-database test.

---

## STEP 4 - the database (10 minutes, only if `where sqlplus` found it)

```bat
sqlplus sys@localhost:1521/FREE as sysdba
```

Inside SQL*Plus:

```sql
@database\00_create_user.sql
```

It asks you to choose a password - note it down. Then:

```sql
exit
sqlplus cyberguard@localhost:1521/FREEPDB1
@database\install_all.sql
```

**EXPECT** - object counts `TABLE 7`, `FUNCTION 6`, `PROCEDURE 6`, `TRIGGER 4`, all `VALID`,
then `no rows selected` from `user_errors`.

Give the application the password:

```bat
copy .env.example .env
notepad .env
```

Set `CYBERGUARD_DB_PASSWORD=` to the password you chose. Save, close.

Run the PL/SQL demonstration script and leave the window open - its output is the evidence
for the PL/SQL report:

```sql
@database\queries.sql
```

**EXPECT** - ten numbered demonstrations (figures 9.1 to 9.9 of
`CyberGuard_Project_Report_PL_SQL.docx`).

---

## STEP 5A - start it (2 minutes)

```bat
run_all.bat
```

Two windows open: the Python service, then the C++ server. Leave both running and open
**http://127.0.0.1:8080**

**EXPECT** - the pill reads `All services online` with a database, `Database offline`
without one, `Python service offline` if the second window failed.

---

## STEP 5B - capture the screenshots so the numbers match the reports

The reports quote exact outputs, so type these values.

| Figure | View | Type or choose exactly this | Must show |
|---|---|---|---|
| 9.1 | Overview | - | the pill, the four numbers, the recent activity table |
| 9.2 | Identifier Analyzer | `AB12 3C 4@4 99` | 7 digits, 3 letters, 4 other; digits 4 and 9 both at 2 |
| 9.3 | Score Calculator | `72, 85, 90` | count 3, sum 247, average 82.33 |
| 9.4 | Pointer Operations | `7` and `-3` | sum 4, absolute difference 10 |
| 9.5 | User Assessment | `Asha`, `60,70,80,90,75`, baseline `50` | total 375, average 75, PASS |
| 9.6 | File Integrity Lab | `sample_data\sample_logs\sample.log`; run once, then paste the hash back as the reference and run again | the hash, the copy button, then MATCH |
| 9.7 | Password Strength Analyzer | `Zx9$kLm2#Qp7wR4!vN` | Very Strong with the factor list |
| 9.8 | Security Log Analyzer | `sample_data\sample_logs\sample.log` | entry counts, failed logins, busiest addresses |
| 9.9 | IP Address Validator | `192.168.1.10`, then `127.0.0.1` | private, then loopback |
| 9.10 | Security Reports | type `Password`, format `TXT` | the preview and the download link |
| 9.11 | Activity History | - | rows for everything just run, newest first |
| 9.12 | Database offline | close the Python window, then use any tool | pill reading Database offline, not-saved message |

Snip with **Win+Shift+S** into one folder, for example `Pictures\CyberGuard`.
Figure 9.12 needs the Python window closed; reopen with `run_all.bat` afterwards.

---

## STEP 6 - put the screenshots into the seven documents (15 minutes)

For each file in `Desktop\CyberGuard_Submission\`:

1. Open in Word.
2. Go to `Output & Screenshots` (project reports, section 9) or
   `6. Testing & Results Analysis` (case studies).
3. Below the figure table press Enter twice, then **Insert -> Pictures -> This Device**.
4. Click the picture, then **References -> Insert Caption**, for example
   `Figure 9.3 - Score Calculator`.
5. Save.

Figure ranges: 9.1-9.12 for the Python and Web Programming reports; 9.1-9.9 in the PL/SQL
report are the SQL*Plus captures and 9.10 is the dashboard; 8.1-8.8 for Computing Aptitude.

---

## STEP 7 - three details only she can confirm (5 minutes)

1. **Guide names** on the covers and certificates - copied from her earlier submissions:
   Mr. Randeep Singh Dhillon (Python case study), Mr. Mohammad Rashid (ADBMS),
   Ms. Saranjeet Kaur (Web Programming), Gurpreet Kaur (Python report),
   Chanchal Sharma (PL/SQL), MS. ASHIMA SOOD (Computing Aptitude).
2. **Contents page numbers** are a plain list, so Word will not renumber them after the
   screenshots are added. Open each document, see where the headings actually landed, and
   correct them.
3. **Sign the certificate pages**, or type her name above the supervisor line if the
   department asks for a typed submission.

---

## STEP 8 - publish from HER machine (5 minutes)

Her machine already has her GitHub credentials, which is why this step is not done on yours.

```bat
cd %USERPROFILE%\Downloads\CyberGuard\CyberGuard
git status
git add docs
git commit -m "Add the case studies and project reports with screenshots"
git push origin finish/phase8-database
```

**EXPECT** - the output ends with `finish/phase8-database -> finish/phase8-database`.

Then either merge on GitHub (**Compare & pull request -> Merge pull request**) or:

```bat
git checkout main
git pull origin main
git merge --no-ff finish/phase8-database
git push origin main
```

The Word files are then in the repository under `CyberGuard\docs\` as well as on her Desktop.

---

## IF SOMETHING GOES WRONG

| Symptom | Cause | Fix |
|---|---|---|
| `cc1plus: error: ... No such file` | wrong folder | `cd` into the **inner** `CyberGuard` folder |
| `Missing backend\vendor\httplib.h` | library download failed | run `setup.bat`, check the connection |
| `Could not start on port 8080` | port already used | `run.bat frontend 8081`, then open :8081 |
| Pill says `Python service offline` | the Python window closed | `run_all.bat` again |
| Pill says `Database offline` | no Oracle, or `.env` has no password | check `.env`; everything else still works |
| `python-oracledb` will not install | Python 3.14 has no wheel | use Python 3.12 or 3.13 for the `.venv` |
| Footer shows `Page  of` with no numbers | field not refreshed | click in the footer, press F9 |
| `git push` asks for a password | GitHub needs a token | use the Git Credential Manager window, or a fine-grained token with Contents: Read and write |
