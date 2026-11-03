"""Build the seven subject documents for the CyberGuard project.

Formats are copied from the student's own earlier submissions, one per subject:

  CyberGuard_Case_Study_Python.docx          -> ExamIQ_Case_Study_Python_*.docx
  CyberGuard_Case_Study_ADBMS.docx           -> ExamIQ_Case_Study_ADBMS_*.docx
  CyberGuard_Case_Study_Web_Programming.docx -> Case-Study-Portfolio.docx
  CyberGuard_Project_Report_Python_Programming.docx -> ExamIQ_Project_Report_Python_Programming.docx
  CyberGuard_Project_Report_PL_SQL.docx             -> ExamIQ_Project_Report_PL_SQL.docx
  CyberGuard_Project_Report_Web_Programming.docx    -> the same 12-section report skeleton
  CyberGuard_Project_Report_Computing_Aptitude.docx -> ExamIQ_Project_Report_Computing_Aptitude.docx
                                                       (10 sections, no flow chart, 26MCA-4B block)

Run:  python docs\\build_subject_documents.py
"""
import os
import shutil

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
STUDENT = "Japleen Kaur"
UID = "26MCA20265"
REPO = "github.com/jay-kxz/CyberGuard"
TITLE = "CyberGuard: An Integrated Cybersecurity Analysis and Utility Toolkit"


# ---------------------------------------------------------------------------
# low level helpers
# ---------------------------------------------------------------------------
def make_document(body=12, colour="365F91", top=2.4, bottom=2.2, left=2.5, right=2.2):
    doc = Document()
    s = doc.sections[0]
    s.page_height = Cm(29.7)
    s.page_width = Cm(21.0)
    s.top_margin = Cm(top)
    s.bottom_margin = Cm(bottom)
    s.left_margin = Cm(left)
    s.right_margin = Cm(right)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(body)
    normal.font.color.rgb = RGBColor(0x1C, 0x1C, 0x1C)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    for name, size in (("Heading 1", 14), ("Heading 2", 11.5), ("Heading 3", 11)):
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(colour)
        st.paragraph_format.space_before = Pt(10)
        st.paragraph_format.space_after = Pt(4)
    return doc


def centre(doc, text, size=11, bold=False, italic=False, after=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    return p


def footer(doc, left_text):
    p = doc.sections[0].footer.paragraphs[0]
    p.text = ""
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT)
    first = p.add_run(left_text + "\tPage ")
    first.font.size = Pt(9)
    for kind, instruction in (("begin", None), (None, "PAGE"), ("end", None)):
        el = OxmlElement("w:fldChar" if kind else "w:instrText")
        if kind:
            el.set(qn("w:fldCharType"), kind)
        else:
            el.set(qn("xml:space"), "preserve")
            el.text = instruction
        first._r.append(el)
    p.add_run(" of ").font.size = Pt(9)
    tail = p.add_run()
    tail.font.size = Pt(9)
    for kind, instruction in (("begin", None), (None, "NUMPAGES"), ("end", None)):
        el = OxmlElement("w:fldChar" if kind else "w:instrText")
        if kind:
            el.set(qn("w:fldCharType"), kind)
        else:
            el.set(qn("xml:space"), "preserve")
            el.text = instruction
        tail._r.append(el)


def render(doc, blocks):
    for block in blocks:
        kind = block[0]
        if kind == "h1":
            doc.add_heading(block[1], level=1)
        elif kind == "h2":
            doc.add_heading(block[1], level=2)
        elif kind == "p":
            doc.add_paragraph(block[1])
        elif kind == "b":
            for item in block[1]:
                doc.add_paragraph(item, style="List Bullet")
        elif kind == "n":
            for item in block[1]:
                doc.add_paragraph(item, style="List Number")
        elif kind == "c":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.space_after = Pt(8)
            r = p.add_run(block[1])
            r.font.name = "Consolas"
            r.font.size = Pt(block[2] if len(block) > 2 else 9)
        elif kind == "t":
            headers, rows, widths = block[1], block[2], (block[3] if len(block) > 3 else None)
            size = block[4] if len(block) > 4 else 10
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for i, head in enumerate(headers):
                cell = table.rows[0].cells[i]
                cell.text = ""
                run = cell.paragraphs[0].add_run(head)
                run.bold = True
                run.font.size = Pt(size)
            for row in rows:
                cells = table.add_row().cells
                for i, value in enumerate(row):
                    cells[i].text = ""
                    run = cells[i].paragraphs[0].add_run(str(value))
                    run.font.size = Pt(size)
            if widths:
                for row in table.rows:
                    for i, width in enumerate(widths):
                        row.cells[i].width = Cm(width)
            doc.add_paragraph()
        elif kind == "pb":
            doc.add_page_break()


# ---------------------------------------------------------------------------
# covers
# ---------------------------------------------------------------------------
def case_study_cover(doc, name, tagline, guide):
    for _ in range(2):
        doc.add_paragraph()
    centre(doc, name, size=26, bold=True, after=2)
    centre(doc, tagline[0], size=13, bold=True, after=2)
    if len(tagline) > 1:
        centre(doc, tagline[1], size=13, bold=True, after=2)
    centre(doc, tagline[2] if len(tagline) > 2 else "", size=11, bold=True, after=16)
    centre(doc, "A Case Study Report submitted in partial fulfillment of the requirements for the degree")
    centre(doc, "of")
    centre(doc, "MASTER OF COMPUTER APPLICATIONS (MCA)", size=12, bold=True, after=16)
    centre(doc, "Submitted By:", bold=True, after=2)
    centre(doc, STUDENT, size=13, bold=True, after=2)
    centre(doc, "UID: " + UID, after=2)
    centre(doc, "Semester: 1st / Year: 1st", after=14)
    centre(doc, "Under the Guidance of:", bold=True, after=2)
    centre(doc, guide, size=13, bold=True, after=14)
    centre(doc, "Department of Computer Applications", after=2)
    centre(doc, "Chandigarh University, Gharuan, Mohali, Punjab, India", after=2)
    centre(doc, "Academic Year: 2026-2027", bold=True)
    doc.add_page_break()


def report_cover(doc, subject, subtitle, guide, variant="standard"):
    if variant == "aptitude":
        centre(doc, TITLE, size=17, bold=True, after=2)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("A  PROJECT  REPORT")
        r.bold = True
        r.font.size = Pt(14)
        doc.add_paragraph()
        centre(doc, "Submitted To", bold=True, after=2)
        centre(doc, guide, size=13, bold=True, after=14)
        centre(doc, "Submitted By", bold=True, after=2)
        centre(doc, STUDENT, size=13, bold=True, after=2)
        centre(doc, "UID: " + UID, after=2)
        centre(doc, "26MCA-4B", after=14)
        centre(doc, "in partial fulfillment for the award of the degree of", after=2)
        centre(doc, "MASTERS OF COMPUTER APPLICATIONS", size=13, bold=True, after=2)
        centre(doc, "IN", after=2)
        centre(doc, "UNIVERSITY INSTITUTE OF COMPUTING", size=12, bold=True, after=2)
        centre(doc, "CHANDIGARH UNIVERSITY", size=12, bold=True, after=10)
        centre(doc, "October-November, 2026", bold=True)
        doc.add_page_break()
        return

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("  ".join("A PROJECT REPORT".upper()))
    r.bold = True
    r.font.size = Pt(13)
    centre(doc, TITLE, size=17, bold=True, after=2)
    centre(doc, "(" + subject + ")", size=12, italic=True, after=2)
    centre(doc, subtitle, size=11, italic=True, after=8)
    doc.add_paragraph()
    centre(doc, "Submitted By:", bold=True, after=2)
    centre(doc, STUDENT, size=13, bold=True, after=2)
    centre(doc, "UID: " + UID, after=2)
    centre(doc, "Subject: " + subject, after=10)
    centre(doc, "Submitted To:", bold=True, after=2)
    centre(doc, guide, size=13, bold=True, after=10)
    centre(doc, "in partial fulfillment for the award of the degree of", after=2)
    centre(doc, "MASTERS OF COMPUTER APPLICATIONS", size=13, bold=True, after=2)
    centre(doc, "IN", after=2)
    centre(doc, "UNIVERSITY INSTITUTE OF COMPUTING", size=12, bold=True, after=2)
    centre(doc, "CHANDIGARH UNIVERSITY", size=12, bold=True, after=10)
    centre(doc, "October-November, 2026", bold=True)
    doc.add_page_break()


def certificate(doc, guide):
    centre(doc, "BONAFIDE CERTIFICATE", size=14, bold=True)
    doc.add_paragraph()
    doc.add_paragraph(
        'This is to certify that the project report entitled "' + TITLE + '" submitted by ' + STUDENT +
        ' (' + UID + '), in partial fulfillment of the requirements for the award of the degree of Masters of '
        'Computer Applications, is a record of the work carried out under my supervision.')
    doc.add_paragraph(
        "The project work embodied in this report has not been submitted to any other University or Institution "
        "for the award of any degree or diploma. The work presented here is original and complete to the best of "
        "my knowledge.")
    doc.add_paragraph()
    doc.add_paragraph()
    for text in ("___________________", "Signature of Supervisor", guide):
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_page_break()


def contents(doc, entries, with_pages=True):
    centre(doc, "Table of Contents", size=14, bold=True)
    doc.add_paragraph()
    for label, page in entries:
        p = doc.add_paragraph()
        p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        p.add_run(label + ("\t" + page if with_pages else ""))
    doc.add_page_break()


# ---------------------------------------------------------------------------
# shared, verified facts
# ---------------------------------------------------------------------------
SHA_TABLE = (["Input", "Expected SHA-256 (FIPS 180-4)", "Result"],
             [["empty string", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "match"],
              ["\"abc\"", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "match"],
              ["448-bit two-block message", "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1", "match"],
              ["one million bytes of \"a\"", "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0", "match"]],
             [4.4, 10.0, 1.4])

CANONICAL = ("Nine analysis tools behind a single dashboard: identifier analysis, score calculation, pointer "
             "operations, user assessment, file integrity, password strength, log analysis, IP validation and "
             "report generation.")

HISTORY = [
    ["Identifier / Score / Pointer / Assessment", "C++17", "POST /api/analyze, /api/calculate, /api/pointers, /api/assessment"],
    ["File integrity", "C++17", "POST /api/file-hash"],
    ["Password / Log / IP / Report", "Python 3", "POST /api/password-strength, /api/log-analysis, /api/ip-validation, /api/report"],
    ["History / Dashboard / Reports", "Python 3 and Oracle", "GET /api/history, /api/dashboard, /api/reports"],
]

DB_OBJECTS = [
    ["users", "Table", "One row per application user name; unique and format-checked"],
    ["analysis_history", "Table", "One row per analysis; status limited to SUCCESS or FAILED"],
    ["file_integrity_records", "Table", "One row per file check; both hash columns validated as 64 hexadecimal characters"],
    ["security_assessments", "Table", "One row per assessment; score between 0 and 100"],
    ["activity_logs", "Table", "Activity trail for each analysis"],
    ["reports", "Table", "Report metadata; report code is unique"],
    ["audit_log", "Table", "Row-level audit written by triggers, with no trigger of its own"],
    ["get_user_id, get_or_create_user", "Function", "User lookup and create-on-demand"],
    ["get_total_analyses, get_total_file_verifications, get_average_assessment_score", "Function", "The four Overview numbers"],
    ["get_recent_history", "Function", "Returns the newest analyses as a SYS_REFCURSOR"],
    ["insert_analysis_record", "Procedure", "Saves an analysis and its activity row in one transaction"],
    ["insert_file_integrity_record", "Procedure", "Decides MATCH, MISMATCH or NO REFERENCE GIVEN inside the database"],
    ["insert_security_assessment, insert_report_record", "Procedure", "Saves an assessment or a report record"],
    ["update_assessment_result, generate_user_summary", "Procedure", "Update through a procedure; summary built with an explicit cursor"],
    ["trg_users_audit, trg_assessments_audit, trg_assessments_timestamp, trg_files_audit", "Trigger", "Audit rows and the updated_at column"],
]

DB_COUNTS = ("The schema defines seven tables, six functions, six procedures and four triggers, all of which the "
             "application now uses.")

UI_VIEWS = [
    ["9.1", "Overview", "The pill reading All services online, the four numbers filled in, recent activity listed"],
    ["9.2", "Identifier Analyzer", "Input AB12 3C 4@4 99 with the digit table and the most frequent digits"],
    ["9.3", "Score Calculator", "72, 85, 90 with count 3, sum 247 and average 82.33"],
    ["9.4", "Pointer Operations", "Two numbers with the sum and the absolute difference"],
    ["9.5", "User Assessment", "Five scores with the total, average and PASS"],
    ["9.6", "File Integrity Lab", "A chosen file with its SHA-256, the copy button, and a MATCH result"],
    ["9.7", "Password Strength Analyzer", "A sample password with its rating, score and factors"],
    ["9.8", "Security Log Analyzer", "sample.log with the entry counts and the busiest addresses"],
    ["9.9", "IP Address Validator", "192.168.1.10 classified as private, and one invalid address"],
    ["9.10", "Security Reports", "A generated report with its preview and the download link"],
    ["9.11", "Activity History", "Rows for the analyses just run, newest first"],
    ["9.12", "Database offline", "The pill reading Database offline and the not-saved message"],
]

GITHUB_TABLE = (["Item", "Detail"],
                [["Repository", REPO],
                 ["Branch with the completed work", "finish/phase8-database"],
                 ["Files added", "python/db.py, backend/modules/file_integrity.h, backend/modules/file_integrity.cpp, tests/python_tests/test_db.py, .gitignore, .env.example"],
                 ["Ignored on purpose", "backend/vendor headers, .venv, __pycache__, compiled binaries, reports_output and .env"],
                 ["Reproduction", "Clone, run first_time_setup.bat, copy .env.example to .env, run run_all.bat, open 127.0.0.1:8080"]],
                [4.4, 11.4])


# ---------------------------------------------------------------------------
# 1. CASE STUDY - PYTHON
# ---------------------------------------------------------------------------
PYTHON_CASE = [
    ("h1", "1. Executive Summary"),
    ("p", "This case study examines the Python service of CyberGuard, an educational cybersecurity toolkit. The "
          "service is a small Flask application that performs four of the toolkit's nine analyses - password "
          "strength, log summarisation, IP validation and report generation - and holds the only database "
          "connection in the project."),
    ("p", "The study concentrates on the part of the work that made the service complete. Before it, the service "
          "answered four addresses correctly and passed thirty-four tests, yet it could not store a single result: "
          "nothing imported a database driver and no connection was ever opened, so the Activity History view and "
          "the four Overview numbers had nothing to read. A dependency list mentioned the driver; the installer "
          "never installed it; and the module that was meant to use it did not exist."),
    ("p", "The implementation described here adds that module and the six endpoints that depend on it. The account "
          "covers the parts of Python that the work actually exercises: regular expressions and Counter for the "
          "log analyser, the standard library ipaddress module, csv with a formula guard for reports, Flask error "
          "handlers that return one shape for every failure, unittest with stand-in driver objects, and the "
          "transaction handling that a PL/SQL call requires because the procedures deliberately do not commit."),
    ("p", "The finished service holds 50 tests, of which 49 run without a database; the remaining one is skipped "
          "unless a live Oracle connection is configured."),

    ("h1", "2. Introduction & Problem Statement"),
    ("h2", "2.1 Background of the Study"),
    ("p", "Python was chosen for this layer because four of the nine analyses are text processing, and the standard "
          "library already contains everything they need. Counting levels in a log is a regular expression and a "
          "Counter; validating an address is a call to ipaddress; writing a CSV report is csv.writer; and scrubbing "
          "secret fields is a dictionary walk. No third-party package is required for any of it, so the analysis "
          "half of the service has no installation step at all."),
    ("p", "What Python does need is a boundary. The service is reached only by the C++ server on the loopback "
          "interface, so the browser cannot call it directly, and the database is reached only from this service, "
          "so the C++ server carries no driver. That single rule - one language owns the data - is the reason the "
          "missing layer could be added in one file."),
    ("h2", "2.2 Problem Statement"),
    ("p", "The study evaluates how a Python analysis service can be given a durable storage layer without making "
          "storage a precondition for analysis, and how that layer can be tested on a machine where no database is "
          "installed."),
    ("b", ["A service that raises an error whenever its database is absent is unusable on a student laptop, which is "
           "the normal deployment for an academic project.",
           "Validation rules duplicated in Python and in the database drift apart, and the copy in the application "
           "is the one that can be bypassed.",
           "A driver whose API is assumed rather than read fails at run time: in this project two defects came from "
           "an assumed signature that the installed version did not have.",
           "A failure to connect that is re-tested on every page load makes a dashboard feel broken, because the "
           "browser asks for the connection state whenever it starts.",
           "A test suite that needs a database in order to run is a suite that stops being run."]),
    ("h2", "2.3 Objectives"),
    ("b", ["Confirm the four analysis modules with unit tests that need no network and no database.",
           "Place every Oracle call in one module, and call the PL/SQL objects the schema already defines rather "
           "than writing equivalent SQL in Python.",
           "Return one reply shape from every endpoint, so the browser needs one error handler.",
           "Keep every analysis available when the database is missing, and report the missing storage explicitly.",
           "Make the storage layer testable without Oracle, using stand-in driver objects that record what was "
           "asked of them."]),

    ("h1", "3. System Analysis & Modeling"),
    ("h2", "3.1 Feasibility Study"),
    ("p", "Technical feasibility was established by running the service under CPython with Flask 3.1 and "
          "python-oracledb 26.0.1 in thin mode, so no Oracle client libraries had to be installed. Economic "
          "feasibility is trivial because every component is free. Operational feasibility is limited to a "
          "single-user learning environment on one computer, which matches the scope of the project."),
    ("h2", "3.2 Functional Requirements"),
    ("t", ["ID", "Requirement", "Description"],
     [["FR1", "Password analysis", "Rate a sample password out of 100 and return the factors and the advice"],
      ["FR2", "Log analysis", "Count levels, failed logins, repeated addresses and activity per hour for up to 5 MB"],
      ["FR3", "IP validation", "Validate an IPv4 or IPv6 address and return one classification"],
      ["FR4", "Report generation", "Produce a TXT or CSV report for the latest analysis of a chosen type"],
      ["FR5", "Persistence", "Store each analysis, file check, assessment and report when the database is reachable"],
      ["FR6", "Read-back", "Return the newest analyses, the four summary numbers and the newest report records"],
      ["FR7", "Failure reporting", "Answer with 503 and a readable sentence when the database is unusable"],
      ["FR8", "Secrecy", "Never store, echo or log a password, a log body or a file body"]],
     [1.4, 3.6, 10.8]),

    ("h1", "4. Proposed Technical Solution & Architecture"),
    ("h2", "4.1 Technology Stack"),
    ("t", ["Technology", "Role & Responsibility"],
     [["CPython 3.12+", "Runs the service; no third-party package is needed for the four analyses"],
      ["Flask 3.1", "The HTTP layer, bound to 127.0.0.1:5001 and reached only by the C++ server"],
      ["re, collections", "Compiled level and failure patterns; Counter for level, address and hourly counts"],
      ["csv, io", "Report output with a guard against spreadsheet formula injection"],
      ["ipaddress", "IPv4 and IPv6 parsing, version detection and classification"],
      ["python-oracledb 26", "The Oracle driver in thin mode, with a connection pool"],
      ["unittest", "The test suite: 50 tests, 49 of which need no database"],
      ["Oracle Database Free", "Seven tables and sixteen PL/SQL objects behind the storage layer"]],
     [3.6, 12.2]),
    ("h2", "4.2 Architecture and File Structure"),
    ("c", "python/\n"
          "  app.py               Flask endpoints, error handlers, best-effort saving\n"
          "  db.py                Module 10: pool, PL/SQL calls, configuration, backoff\n"
          "  password_analyzer.py Module 6: scoring bands, penalties, common-password cap\n"
          "  log_analyzer.py      Module 7: compiled patterns, Counter, per-hour activity\n"
          "  ip_validator.py      Module 8: ipaddress plus a classification ladder\n"
          "  report_generator.py  Module 9: TXT and CSV, secret scrubbing, formula guard\n"
          "  demo.py              Runs each module once for screenshots\n"
          "tests/python_tests/\n"
          "  test_app.py  test_db.py  test_ip.py  test_log.py  test_password.py  test_report.py", 8.5),

    ("h1", "5. Implementation Details"),
    ("h2", "5.1 One Reply Shape and One Error Handler"),
    ("p", "Every endpoint returns either {\"ok\": true, \"data\": ...} or {\"ok\": false, \"error\": \"...\"}. "
          "Validation problems raise ValueError and are turned into a 400 by a single registered handler, while a "
          "database problem raises a dedicated exception and becomes a 503 with a sentence a person can act on. "
          "Because the shape never changes, the browser's tool code contains one try/catch block for all nine "
          "modules."),
    ("c", "@app.errorhandler(ValueError)\n"
          "def bad_input(error):\n"
          "    return fail(str(error), 400)\n"
          "\n"
          "@app.errorhandler(db.DatabaseOffline)\n"
          "def database_offline(error):\n"
          "    return fail(\"The database is not connected yet. \" + str(error), 503)"),
    ("h2", "5.2 The Password Analyser"),
    ("p", "The score is additive and explainable rather than a single opaque number: three points per character up "
          "to twenty characters, ten points for each character class present, minus twenty for a repeated group, "
          "minus fifteen for a predictable sequence and minus ten when fewer than half of the characters are "
          "different. A password on the common list is capped at ten. The factors are returned to the caller, so "
          "the interface can show why the rating is what it is, and the password itself is never stored, printed or "
          "echoed."),
    ("c", "raw = reduce(lambda total, f: total + f[\"points\"], factors, 0)\n"
          "score = max(0, min(100, raw))\n"
          "if password.lower() in COMMON_PASSWORDS:\n"
          "    score = min(score, 10)"),
    ("h2", "5.3 The Log Analyser"),
    ("p", "Four compiled patterns and three Counters do the work. Addresses are validated with ipaddress before "
          "they are counted, so a version string such as 999.1.1.1 is not mistaken for an address, and only counts "
          "and addresses are returned - the log body never leaves the request. The module also refuses input larger "
          "than 5 MB or longer than 100 000 lines, which keeps a single request from exhausting memory."),
    ("h2", "5.4 The IP Validator"),
    ("p", "The classification is a ladder, ordered so that the most specific kind wins: unspecified, loopback, "
          "link-local, multicast, private, global, and finally reserved. Returning one plain-language label rather "
          "than a set of flags is what makes the result useful to a beginner."),
    ("h2", "5.5 The Report Generator"),
    ("p", "A report has an identifier of its own, a timestamp, the input summary, the results, observations, "
          "recommendations and a conclusion. Two safety properties are implemented in Python: any field whose name "
          "indicates a secret is replaced with the word withheld, and a CSV cell beginning with =, +, - or @ is "
          "prefixed with an apostrophe so a spreadsheet cannot be tricked into executing it. The file name is "
          "created by the module and never taken from the user, so a report cannot be written outside its folder."),
    ("h2", "5.6 The Database Layer"),
    ("p", "db.py is the only place a connection is opened. It reads configuration from the environment, optionally "
          "supplied by a .env file, creates one pool on first use, and wraps every PL/SQL call in a committed "
          "transaction. Because a procedure that returns a REF CURSOR cannot be selected from SQL directly, the "
          "newest analyses are fetched through an anonymous block with a cursor bind variable."),
    ("c", "ref_cursor = cursor.var(oracledb.CURSOR)\n"
          "cursor.execute(\"BEGIN :1 := get_recent_history(:2); END;\", [ref_cursor, limit])\n"
          "rows = ref_cursor.getvalue()"),
    ("p", "Discovering that no database is listening costs a few seconds, and the dashboard asks for the connection "
          "state on every load. A failure is therefore remembered for five seconds: the reply becomes immediate "
          "during an outage, while a database that starts is noticed within seconds."),
    ("h2", "5.7 Tests Without a Database"),
    ("p", "The database tests replace the driver module and the pool with stand-in objects and assert what was "
          "asked of them: that insert_analysis_record receives the module, the summary and the status; that a "
          "summary longer than the column is cut to 500 characters; that the caller commits; that a pool is built "
          "with the configured user, DSN, pool size and connect timeout; and that one failure is remembered rather "
          "than retried on every request. A separate group runs only when CYBERGUARD_DB_TEST is set and performs a "
          "real round trip."),

    ("h1", "6. Testing & Results Analysis"),
    ("h2", "6.1 Test Execution Matrix"),
    ("t", ["ID", "Test Scenario", "Expected Result", "Status"],
     [["T1", "Run the service test suite", "All endpoint tests pass", "Pass"],
      ["T2", "Submit a password that must not appear in the reply", "Rating returned, password absent from the whole reply", "Pass"],
      ["T3", "Submit unusable input to each endpoint", "400 with a sentence, no traceback", "Pass"],
      ["T4", "Switch the database off and run every analysis", "200 with persisted false", "Pass"],
      ["T5", "Read history, dashboard and reports with the database off", "503 with a readable message", "Pass"],
      ["T6", "Run the database unit tests", "Call construction, commit and column-width checks pass", "Pass - 15 run, 1 skipped"],
      ["T7", "Configure a missing password", "A clear message, no stack trace", "Pass"],
      ["T8", "Point the service at a host with no listener", "Health reports the driver error, analyses still answer", "Pass"],
      ["T9", "Run the complete suite", "49 tests pass, one skipped unless a live database is set", "Pass"]],
     [1.2, 5.8, 6.4, 3.4], 9.5),
    ("h2", "6.2 Observations"),
    ("b", ["All thirty-four tests passed while the service could not store a single result. Component tests cannot "
           "detect a missing connection, which is why the storage layer now has its own tests.",
           "The polite failure was itself a risk: because the page said the database was not connected instead of "
           "crashing, nothing looked broken enough to investigate.",
           "Two defects came from assuming the driver's API. In the installed version the user, password and DSN of "
           "a connection parameter object could not be assigned after construction, and the connect string was not "
           "a constructor argument. Reading the signature took less time than the failure did.",
           "Creating a pool does not prove a usable connection. The layer now proves it with a trivial query and "
           "discards a pool that cannot answer.",
           "The healthy path costs tens of milliseconds; the unhealthy path initially cost several seconds per page "
           "load. Most of the performance work in this project was about failure, not success."]),

    ("h1", "7. Conclusion & Future Enhancements"),
    ("h2", "7.1 Conclusion"),
    ("p", "The Python service now stores what it analyses and reads it back. The work needed one new module, six "
          "endpoints and a test file, and it converted four features from decorative to functional: the Activity "
          "History view, the four Overview numbers, the report records and the file checks. The design decision that "
          "made it safe was to treat persistence as an addition to an analysis rather than a precondition for it, "
          "which is why the toolkit still works on a machine without Oracle."),
    ("h2", "7.2 Future Scope"),
    ("b", ["Authentication, so the history records the person rather than one configured application name.",
           "A streaming upload path for the log analyser, so files larger than memory can be read.",
           "Pagination and a detail view for the history endpoint.",
           "Replacing the driver stand-ins with a containerised Oracle instance in continuous integration, so the "
           "live path is exercised on every push.",
           "Type hints and a static check, which would have caught the driver-API assumptions at review time."]),

    ("h1", "8. Github Upload/Link"),
    ("p", "The complete source code, the database scripts, the tests and the documentation are published at:"),
    ("p", REPO),
    ("t", GITHUB_TABLE[0], GITHUB_TABLE[1], GITHUB_TABLE[2]),

    ("h1", "9. References"),
    ("n", ["Python Software Foundation. The Python Standard Library: re, collections, csv, ipaddress, unittest. "
           "https://docs.python.org/3/library/",
           "Pallets Projects. Flask Documentation, version 3.1. https://flask.palletsprojects.com/",
           "Oracle. python-oracledb Documentation, release 26. https://python-oracledb.readthedocs.io/",
           "Oracle. Oracle Database PL/SQL Language Reference, 23ai. https://docs.oracle.com/en/database/",
           "National Institute of Standards and Technology. SP 800-63B, Digital Identity Guidelines: "
           "Authentication and Lifecycle Management, 2017.",
           "Japleen Kaur. CyberGuard GitHub repository. https://" + REPO]),
]

# ---------------------------------------------------------------------------
# 2. CASE STUDY - ADBMS
# ---------------------------------------------------------------------------
ADBMS_CASE = [
    ("h1", "1. Executive Summary"),
    ("p", "This case study examines the database layer of CyberGuard, an educational cybersecurity toolkit whose "
          "nine analysis tools record what they did. The layer is an Oracle Database Free schema of seven tables, "
          "six functions, six procedures and four triggers, and a single application module that calls it."),
    ("p", "The study is about the moment the schema stopped being a separate deliverable and became the storage of "
          "a working application. When the study begins, the schema is complete and carefully constrained, and the "
          "application never touches it: no connection is opened, no procedure is called, and the three views that "
          "should read from it - Activity History, the Overview numbers and the generated-report list - answer with "
          "HTTP 501 because their endpoints were never written."),
    ("p", "The account covers the design of the schema, the reasons for its constraints, the PL/SQL that protects "
          "its rules, the transaction handling that the procedures require, and the demonstration queries that "
          "prove each mechanism works. It also records why the application calls procedures instead of writing "
          "inserts: a rule stated in the database cannot be bypassed by another client, and the coursework schema "
          "is genuinely used rather than reimplemented in Python."),
    ("p", DB_COUNTS),

    ("h1", "2. Introduction & Problem Statement"),
    ("h2", "2.1 Background of the Study"),
    ("p", "A security toolkit produces records: an analysis ran, a file was checked, a score was assessed, a report "
          "was written. Those records are only useful if they are complete and trustworthy, which means the "
          "database has to enforce what a record may contain rather than trusting the application to do so."),
    ("p", "The schema therefore declares its own integrity rules. Identity columns generate the keys. A status "
          "column accepts exactly two values. A hash column is validated as sixty-four hexadecimal characters. A "
          "score is bounded between zero and one hundred. Four triggers write an audit row whenever a user or an "
          "assessment changes, and one keeps an updated_at column correct without the application having to "
          "remember it."),
    ("h2", "2.2 Problem Statement"),
    ("p", "The study evaluates how a relational schema can be used as an active participant in an application, "
          "rather than as passive storage that receives whatever the application sends."),
    ("b", ["A schema that is complete but unconnected is a document, not a database layer: nothing it declares can "
           "have any effect on the running system.",
           "Validation implemented twice - once in the application and once in the database - drifts, and the copy "
           "in the application is the one an alternative client can skip.",
           "Procedures that do not commit are safer for the caller but require the caller to understand "
           "transactions, which an application that never commits will silently leave half-written.",
           "A rule that the schema states but never exercises cannot be demonstrated: the constraint exists but no "
           "evidence shows it firing."]),
    ("h2", "2.3 Objectives"),
    ("b", ["Model the activity of nine analysis tools in normalised relations with declared keys and constraints.",
           "Move every rule the application depends on into the database, and call it from the application.",
           "Demonstrate each syllabus mechanism in use: joins, aggregates, GROUP BY, HAVING, sub-queries, an "
           "explicit cursor, a REF CURSOR function, triggers, exceptions and transaction control.",
           "Prove the mechanisms with a demonstration script whose output can be recorded as evidence.",
           "Keep the application usable when the database is absent."]),

    ("h1", "3. System Analysis & Modeling"),
    ("h2", "3.1 Feasibility Study"),
    ("p", "The layer was built and tested against Oracle Database Free 23ai on a single Windows machine, reached "
          "from CPython through python-oracledb in thin mode, so no Oracle client libraries were required. All "
          "components are free. The design is feasible for a single-user learning environment, which is the stated "
          "scope."),
    ("h2", "3.2 Functional Requirements"),
    ("t", ["ID", "Requirement", "Description"],
     [["FR1", "Record an analysis", "Store the module, a summary of at most 500 characters and a status limited to SUCCESS or FAILED"],
      ["FR2", "Record a file check", "Store the file name, size, digest, optional reference and the verification outcome decided by the database"],
      ["FR3", "Record an assessment", "Store the type, a score between 0 and 100, and a result limited to two values"],
      ["FR4", "Record a report", "Store a unique report code, its type and its location"],
      ["FR5", "History", "Return the newest analyses through a cursor function"],
      ["FR6", "Aggregates", "Return counts and averages through functions that treat a null user as all users"],
      ["FR7", "Audit", "Write an audit row automatically when a user or an assessment changes"],
      ["FR8", "Integrity", "Reject a status, a hash, a score or a report code that violates a declared constraint"]],
     [1.4, 3.6, 10.8]),

    ("h1", "4. Proposed Technical Solution & Architecture"),
    ("h2", "4.1 Technology Stack"),
    ("t", ["Technology", "Role & Responsibility"],
     [["Oracle Database Free 23ai", "The relational engine: tables, constraints, indexes, PL/SQL and triggers"],
      ["SQL", "DDL for the schema, DML for the sample data, and the demonstration queries"],
      ["PL/SQL", "Six functions, six procedures, an explicit cursor, a REF CURSOR and four triggers"],
      ["python-oracledb 26", "The client library, in thin mode, with a connection pool"],
      ["SQL*Plus", "Runs install_all.sql and the demonstration script, producing the recorded output"],
      ["Flask service", "The only application component that opens a connection"]],
     [3.8, 12.0]),
    ("h2", "4.2 Architecture and File Structure"),
    ("c", "database/\n"
          "  00_create_user.sql     run once as SYS: creates the cyberguard user and grants\n"
          "  schema.sql             7 tables, keys, check constraints, indexes\n"
          "  functions.sql          6 functions, including a REF CURSOR function\n"
          "  procedures.sql         6 procedures, none of which commit\n"
          "  triggers.sql           4 triggers: audit rows and updated_at\n"
          "  sample_data.sql        demonstration rows under demo_* user names\n"
          "  queries.sql            10 numbered demonstrations for the report\n"
          "  install_all.sql        runs the files in the right order, then prints the object counts\n"
          "  reset.sql              drops and rebuilds\n"
          "  remove_sample_data.sql removes only the demonstration rows\n"
          "\n"
          "python/db.py             the only module that opens a connection", 8.5),
    ("h2", "4.3 Data Model"),
    ("p", "The model separates one entity from its activity. The users table holds an identity; the activity tables "
          "reference it; and none of them repeat a name, so renaming a user cannot leave inconsistent rows behind. "
          "The audit_log table is written by triggers and carries no trigger of its own, which is what prevents an "
          "audit write from triggering another audit."),
    ("t", ["Table", "Type", "Purpose and constraints"], DB_OBJECTS[:7], [3.6, 2.0, 10.2], 9.5),

    ("h1", "5. Implementation Details"),
    ("h2", "5.1 Tables and Declared Integrity"),
    ("p", "Every rule the application relies on is declared rather than assumed. A CHECK constraint on the status "
          "column means a row can only be SUCCESS or FAILED, so a typo cannot become a new state. A regular "
          "expression constraint on the hash columns means a 63-character digest is rejected at the only place that "
          "can be certain. A foreign key on every activity table means a row cannot refer to a user who does not "
          "exist. Indexes on the user-and-time columns keep the history query from scanning the table as it grows."),
    ("h2", "5.2 Functions"),
    ("p", "Two functions exist because the application needs them: get_user_id returns a primary key or null, and "
          "get_or_create_user returns a key, creating the user when it is new and recovering from a duplicate "
          "insert if another session created it a moment earlier. Three aggregate functions accept a null user id "
          "to mean all users, which is how the Overview panel gets its numbers in one round trip. The sixth returns "
          "a SYS_REFCURSOR, so the newest analyses arrive as a cursor the client can read without an intermediate "
          "table."),
    ("h2", "5.3 Procedures That Do Not Commit"),
    ("p", "None of the procedures commits. The caller decides, which means a procedure can be called twice inside "
          "one transaction, or wrapped in a savepoint, without surprising anyone. The application module therefore "
          "commits once per call. The demonstration script uses the same property in reverse: it shows a change, "
          "then rolls it back so the sample data is left unchanged."),
    ("c", "CREATE OR REPLACE PROCEDURE insert_analysis_record (\n"
          "  p_username IN VARCHAR2, p_module_name IN VARCHAR2,\n"
          "  p_result_summary IN VARCHAR2, p_status IN VARCHAR2 DEFAULT 'SUCCESS',\n"
          "  p_analysis_id OUT NUMBER\n"
          ") IS\n"
          "  e_invalid_status EXCEPTION;\n"
          "BEGIN\n"
          "  IF p_status IS NULL OR p_status NOT IN ('SUCCESS', 'FAILED') THEN\n"
          "    RAISE e_invalid_status;\n"
          "  END IF;\n"
          "  v_user_id := get_or_create_user(p_username);\n"
          "  INSERT INTO analysis_history (user_id, module_name, result_summary, status)\n"
          "  VALUES (v_user_id, p_module_name, SUBSTR(p_result_summary, 1, 500), p_status)\n"
          "  RETURNING analysis_id INTO p_analysis_id;\n"
          "  ...", 8.5),
    ("h2", "5.4 An Explicit Cursor"),
    ("p", "generate_user_summary builds a text summary of one user and walks a parameterised cursor over the "
          "modules that user has run. The cursor is explicit so the grouping and the ordering are visible in the "
          "code, and the loop appends only while the summary stays inside its declared length, which is what keeps "
          "a long history from raising an exception."),
    ("h2", "5.5 Triggers and the Audit Trail"),
    ("p", "Four triggers keep the history trustworthy. Two write an audit row for a user or an assessment change, "
          "recording the old value beside the new one. One maintains updated_at before an update, so no client can "
          "leave it stale. One records the deletion of a file record. Because audit_log has no trigger of its own, "
          "the audit write cannot recurse."),
    ("h2", "5.6 The Application Side"),
    ("p", "The application calls the procedures with callproc and reads the results back through output bind "
          "variables, which is the boundary where the two languages meet. The database decides the verification "
          "status of a file check, and Python reports what the database decided, so the outcome shown on the page "
          "and the outcome stored in the row cannot disagree."),
    ("c", "new_id = cursor.var(oracledb.NUMBER)\n"
          "verification = cursor.var(oracledb.STRING, 20)\n"
          "cursor.callproc(\"insert_file_integrity_record\",\n"
          "                [who, name, size, digest, reference or None, new_id, verification])\n"
          "return {\"file_id\": int(new_id.getvalue()), \"verification\": verification.getvalue()}"),

    ("h1", "6. Testing & Results Analysis"),
    ("h2", "6.1 Demonstration Matrix"),
    ("t", ["#", "Demonstration (queries.sql)", "What it proves", "Status"],
     [["1", "JOIN of analyses with their user", "Referential integrity and a readable history", "Pass"],
      ["2", "GROUP BY with ORDER BY", "Runs per module, used by the summary procedure", "Pass"],
      ["3", "HAVING", "Only users with at least two analyses", "Pass"],
      ["4", "Aggregates with CASE", "File checks and matches in one row", "Pass"],
      ["5", "The three functions with a null user", "The Overview numbers", "Pass"],
      ["6", "generate_user_summary", "The explicit cursor and the length guard", "Pass"],
      ["7", "update_assessment_result and the triggers", "The audit row and the maintained updated_at", "Pass"],
      ["8", "SAVEPOINT, ROLLBACK and COMMIT", "Transaction control with the sample data unchanged", "Pass"],
      ["9", "Custom exception, DUP_VAL_ON_INDEX, NO_DATA_FOUND", "Errors raised as designed", "Pass"],
      ["10", "get_recent_history(3)", "A REF CURSOR read from SQL*Plus", "Pass"]],
     [1.0, 5.0, 6.6, 2.2], 9.5),
    ("h2", "6.2 Object Verification"),
    ("p", "install_all.sql ends by printing the object counts and then selecting from user_errors, so a successful "
          "installation is visible rather than assumed: the expected result is seven tables, six functions, six "
          "procedures and four triggers, all VALID, and no rows selected from user_errors."),
    ("h2", "6.3 Observations"),
    ("b", ["No procedure commits. That single rule made the transaction demonstrations possible and makes the "
           "application's commit policy its own decision.",
           "The database decides the file verification outcome; the application only reports it. That removed an "
           "entire class of disagreement between the page and the row.",
           "Constraints caught the mistakes the application would otherwise have stored: an unknown status, a short "
           "digest, a duplicate report code.",
           "The most useful test of the layer was the negative one: with the database stopped, every tool still "
           "answered and clearly said the result was not saved."]),

    ("h1", "7. Conclusion & Future Enhancements"),
    ("h2", "7.1 Conclusion"),
    ("p", "The schema is now used rather than merely delivered. Every analysis, file check, assessment and report "
          "passes through a procedure or function that validates it, and every read is answered by a function the "
          "database owns. The design decision that makes this durable is that rule enforcement sits in one place, "
          "which is also the only place that can be certain."),
    ("h2", "7.2 Future Scope"),
    ("b", ["A package that groups the procedures by concern, and a synonym so the schema can be moved without "
           "touching the application.",
           "An account table replacing the shared application name, so the history records the person.",
           "Materialised views for the Overview numbers, refreshed on a schedule rather than computed per request.",
           "Partitioning analysis_history by month, with an archive job for old rows.",
           "A continuous integration job that installs the schema into a container and runs the demonstration "
           "script on every push."]),

    ("h1", "8. Github Upload/Link"),
    ("p", "The schema, the demonstration script and the application module are published at:"),
    ("p", REPO),
    ("t", GITHUB_TABLE[0], GITHUB_TABLE[1], GITHUB_TABLE[2]),

    ("h1", "9. References"),
    ("n", ["Oracle. Oracle Database SQL Language Reference: CREATE TABLE, constraints and CASE. "
           "https://docs.oracle.com/en/database/",
           "Oracle. Oracle Database PL/SQL Language Reference: procedures, functions, cursors and triggers. "
           "https://docs.oracle.com/en/database/",
           "Oracle. Oracle Database Error Messages: ORA-02290, ORA-00001, ORA-01400. "
           "https://docs.oracle.com/en/database/",
           "Oracle. python-oracledb Documentation, release 26. https://python-oracledb.readthedocs.io/",
           "Oracle. Oracle Database Free. https://www.oracle.com/database/free/",
           "Elmasri, R. and Navathe, S. Fundamentals of Database Systems, seventh edition.",
           "Japleen Kaur. CyberGuard GitHub repository. https://" + REPO]),
]

# ---------------------------------------------------------------------------
# 3. CASE STUDY - WEB PROGRAMMING
# ---------------------------------------------------------------------------
WEB_CASE = [
    ("h1", "1. Executive Summary"),
    ("p", "This case study examines the front end of CyberGuard, an educational cybersecurity toolkit presented as a "
          "single-page dashboard. The page is written in HTML5, CSS3 and vanilla JavaScript with no framework, no "
          "build step and no external assets."),
    ("p", "Twelve views share one document. Navigation swaps views by toggling the hidden attribute, the palette is "
          "held in CSS custom properties so a single attribute on the root element switches the whole page between "
          "light and dark, and every tool is a form whose submitted data is validated in the browser before it is "
          "sent. Results arrive as JSON and are rendered with DOM methods rather than markup strings."),
    ("p", "The study concentrates on the part of the work that changed the page's honesty. The header indicator "
          "previously reported that the server was online whenever the C++ server answered, even when the Python "
          "service was down and four of the nine tools could not work. It now reports three states separately, and "
          "every tool says whether its result reached the database. Two smaller corrections belong to the same "
          "theme: a flag that was read from the wrong level of the reply and so always reported success, and a "
          "null value that was printed as the word null instead of the word none."),
    ("p", "The front end holds no secrets and performs no analysis. Its job is to make the state of a four-layer "
          "system legible to a person in one screen."),

    ("h1", "2. Introduction & Problem Statement"),
    ("h2", "2.1 Background of the Study"),
    ("p", "A dashboard is judged by what it says when something is missing. The interesting states of this "
          "application are not the happy path but the others: the database is stopped, the Python service is not "
          "running, the reference hash is malformed, the file is too large. Each of those states has to be visible, "
          "specific and non-destructive, because a learner who cannot tell which component failed cannot fix it."),
    ("p", "The page is therefore built around a contract. Every server reply is either {\"ok\": true, \"data\": ...} "
          "or {\"ok\": false, \"error\": \"...\"}, and every analysis reply carries a persisted flag. One error "
          "handler in the browser can then serve all nine tools, and no tool needs its own failure logic."),
    ("h2", "2.2 Problem Statement"),
    ("p", "The study evaluates how a single static page can present a system whose components fail independently, "
          "without a framework, without a build step and without ever showing a raw error or a silent success."),
    ("b", ["A status indicator that reports only that some server answered is worse than no indicator, because it "
           "asserts health that the application cannot guarantee.",
           "Results inserted into the page as markup strings let user-supplied text execute; text inserted with DOM "
           "methods cannot.",
           "A success message shown after a failed save teaches the user something false and hides a defect.",
           "A form that submits before validating sends work to the server that the browser could have refused "
           "instantly.",
           "A page that needs a network fetch for its fonts, icons or images breaks silently when it is moved, "
           "zipped or opened from a different folder."]),
    ("h2", "2.3 Objectives"),
    ("b", ["Present nine tools in one document with a navigation model that needs no page reload.",
           "Hold the palette in custom properties, so one attribute switches the theme and the choice survives a "
           "reload.",
           "Validate every form in the browser and announce the failure in the interface.",
           "Render every server reply with DOM methods, never with markup strings.",
           "Reflect the state of the server, the Python service and the database separately and truthfully."]),

    ("h1", "3. System Analysis & Modeling"),
    ("h2", "3.1 Feasibility Study"),
    ("p", "The page runs in any current browser from a local folder served by the C++ server. It needs no "
          "installation, no package manager and no build step, which makes it feasible for a lab machine and "
          "reproducible from a repository clone. The only network calls are to the loopback server."),
    ("h2", "3.2 Functional Requirements"),
    ("t", ["ID", "Requirement", "Description"],
     [["FR1", "Single document", "Twelve views in one page, switched without a reload"],
      ["FR2", "Navigation state", "The current view is marked in the navigation and announced with aria-current"],
      ["FR3", "Theme", "Light and dark palettes from custom properties, remembered across reloads"],
      ["FR4", "Responsive layout", "One column on a small screen, a side rail and a wider grid above 900 pixels"],
      ["FR5", "Validation", "Each form checks its own input and explains a failure in the interface"],
      ["FR6", "Submission", "JSON for the analyses, multipart for the file upload"],
      ["FR7", "Rendering", "Nested replies become tables; a report is offered as a download"],
      ["FR8", "Honest state", "The header reports server, Python service and database separately"],
      ["FR9", "Accessibility", "Labels on every control, live regions for results, visible focus, keyboard operation"]],
     [1.4, 3.6, 10.8]),

    ("h1", "4. Proposed Technical Solution & Architecture"),
    ("h2", "4.1 Technology Stack"),
    ("t", ["Technology", "Role & Responsibility"],
     [["HTML5", "Semantic structure: header, nav, main, section, form, table, footer"],
      ["CSS3", "Custom properties, grid, flexbox, two palettes and two breakpoints"],
      ["JavaScript (ES6)", "Navigation, validation, fetch, table rendering and the status indicator"],
      ["fetch and async/await", "One call path for every endpoint, with a single failure handler"],
      ["FormData", "Multipart upload for the file integrity tool"],
      ["Blob and URL.createObjectURL", "The report download link"],
      ["No framework, no build", "The page is readable as written, which is the point of the exercise"]],
     [3.8, 12.0]),
    ("h2", "4.2 Architecture and File Structure"),
    ("c", "frontend/\n"
          "  index.html   12 views: overview, 8 tools, reports, history, about\n"
          "  style.css    custom properties, palettes, layout, cards, tables, forms\n"
          "  script.js    navigation, validation, fetch, rendering, health, toast\n"
          "\n"
          "Every request goes to the C++ server:\n"
          "  POST  /api/analyze /api/calculate /api/pointers /api/assessment\n"
          "  POST  /api/file-hash (multipart)  /api/password-strength\n"
          "  POST  /api/log-analysis /api/ip-validation /api/report\n"
          "  GET   /api/health /api/history /api/dashboard /api/reports", 8.5),

    ("h1", "5. Implementation Details"),
    ("h2", "5.1 Navigation Without Reloads"),
    ("p", "Views are sections in one document. Choosing a tool hides every section except the chosen one, marks the "
          "button that was used and moves the heading, so the page needs no router, no history API and no "
          "duplicate markup per view. The mobile menu closes on selection and on the Escape key."),
    ("c", "function show(id) {\n"
          "  $$(\".view\").forEach(v => (v.hidden = v.id !== \"v-\" + id));\n"
          "  $$(\"nav button\").forEach(b => {\n"
          "    const on = b.dataset.view === id;\n"
          "    b.classList.toggle(\"on\", on);\n"
          "    on ? b.setAttribute(\"aria-current\", \"page\") : b.removeAttribute(\"aria-current\");\n"
          "    if (on) $(\"#title\").textContent = b.textContent;\n"
          "  });\n"
          "}"),
    ("h2", "5.2 One Palette, Two Themes"),
    ("p", "Colour is declared once as custom properties on the root element, and the dark palette redefines the "
          "same names under a data-theme attribute. A single assignment therefore restyles every component, and no "
          "component needs its own dark-mode rule. The choice is written to local storage, so a reload does not "
          "forget it."),
    ("h2", "5.3 Validation Before the Network"),
    ("p", "Each tool declares how to check and package its input in one table, so the submit handler stays short. "
          "Whole numbers are checked with a regular expression and a safe-integer test, the reference hash is "
          "checked for exactly sixty-four hexadecimal characters, and the two file limits are checked before the "
          "upload begins. A failure throws an Error whose message is shown to the user, so the same code path "
          "reports a client mistake and a server refusal."),
    ("c", "const int = (v, name) => {\n"
          "  if (!/^-?\\d+$/.test(String(v).trim())) throw new Error(name + \" must be a whole number.\");\n"
          "  const x = Number(v);\n"
          "  if (!Number.isSafeInteger(x)) throw new Error(name + \" is too large.\");\n"
          "  return x;\n"
          "};"),
    ("h2", "5.4 Rendering Replies Safely"),
    ("p", "Replies are nested objects, so a small recursive helper turns them into key-and-value tables, and a "
          "second helper turns a list of records into a table with one column per key. Both use textContent, so text "
          "that arrived from a server or from a file name is displayed literally and can never execute as markup. A "
          "null value is shown as none rather than as the word null."),
    ("h2", "5.5 Telling the Truth About State"),
    ("p", "The health reply now carries the state of the Python service and of the database separately, and the "
          "header renders three outcomes instead of two. The same principle applies inside each tool: the reply's "
          "persisted flag decides whether the message says Done or says that the result was not saved."),
    ("c", "const d = (await api(\"/api/health\")).data;\n"
          "if (!d.python)   { p.textContent = \"Python service offline\"; p.className = \"pill down\"; return; }\n"
          "if (!d.database) { p.textContent = \"Database offline\";       p.className = \"pill down\"; return; }\n"
          "p.textContent = \"All services online\"; p.className = \"pill up\";"),
    ("h2", "5.6 Accessibility"),
    ("b", ["Every control has a visible label; the file inputs and selects are labelled by association.",
           "Results sit in regions marked aria-live, so a screen reader announces them when they change.",
           "The menu button carries aria-expanded and aria-controls, kept in step with the panel it opens.",
           "The status indicator is a live region, so a change of state is announced rather than only coloured.",
           "Focus is never removed, and the dark palette keeps contrast above the minimum for body text."]),

    ("h1", "6. Testing & Results Analysis"),
    ("h2", "6.1 Test Execution Matrix"),
    ("t", ["ID", "Test Scenario", "Expected Result", "Status"],
     [["T1", "Open the page with the server running", "All twelve views reachable, no console errors", "Pass"],
      ["T2", "Choose each tool in turn", "The view changes, the heading follows, the button is marked", "Pass"],
      ["T3", "Reload after choosing dark", "The dark palette is still applied", "Pass"],
      ["T4", "Resize below and above 900 pixels", "The rail collapses to a button and returns", "Pass"],
      ["T5", "Submit an empty or malformed field", "The message appears in the interface, nothing is sent", "Pass"],
      ["T6", "Submit a reference hash that is not 64 characters", "A specific message, no request", "Pass"],
      ["T7", "Upload a file and copy the hash", "Hash shown, the copy button confirms", "Pass"],
      ["T8", "Generate a report", "Preview shown with a working download link", "Pass"],
      ["T9", "Run with the database stopped", "The pill reads Database offline and the result says it was not saved", "Pass"],
      ["T10", "Run with the Python service stopped", "The pill reads Python service offline; the four Python tools explain it", "Pass"],
      ["T11", "Open the page with the server stopped", "The pill reads Server offline instead of a blank page", "Pass"]],
     [1.2, 5.6, 6.6, 2.4], 9.5),
    ("h2", "6.2 Observations"),
    ("b", ["The most valuable screen in the application turned out to be the one showing a failure. Once the header "
           "distinguished the three components, the four unreachable tools explained themselves without any further "
           "work.",
           "Rendering with DOM methods removed an entire category of risk for no extra effort; the shortcut of "
           "building markup strings would have been shorter to write and unsafe to keep.",
           "The persistence flag was read from the wrong level of the reply, so the page always said Done. A "
           "one-line correction turned a misleading message into an accurate one, which shows how much of the "
           "interface's honesty lives in small places.",
           "Declaring validation rules in one table kept the submit handler small enough to read, and made adding a "
           "tool a matter of one entry."]),

    ("h1", "7. Conclusion & Future Enhancements"),
    ("h2", "7.1 Conclusion"),
    ("p", "The dashboard now reflects the system behind it. Every view has a working endpoint, every failure has a "
          "sentence, and the state of the four layers is visible in one line of the header. The page needs no "
          "framework, no build step and no network beyond the loopback server, which keeps it readable and "
          "reproducible."),
    ("h2", "7.2 Future Scope"),
    ("b", ["A service worker, so the shell loads instantly and states that it is offline explicitly.",
           "Charts on the Overview drawn with the Canvas API, using activity-per-hour data the log analyser already "
           "produces.",
           "Pagination and a detail view on the History page.",
           "An automated accessibility check in continuous integration, alongside a keyboard-only walkthrough.",
           "A print stylesheet, so a report can be produced from the page itself."]),

    ("h1", "8. Github Upload/Link"),
    ("p", "The three front-end files and the rest of the project are published at:"),
    ("p", REPO),
    ("t", GITHUB_TABLE[0], GITHUB_TABLE[1], GITHUB_TABLE[2]),

    ("h1", "9. References"),
    ("n", ["WHATWG. HTML Living Standard. https://html.spec.whatwg.org/",
           "W3C. CSS Custom Properties for Cascading Variables Module Level 1. https://www.w3.org/TR/css-variables-1/",
           "MDN Web Docs. Fetch API, FormData, Blob and URL.createObjectURL. https://developer.mozilla.org/",
           "W3C. Web Content Accessibility Guidelines (WCAG) 2.2.",
           "Y. Hirose. cpp-httplib, version 0.18.7, MIT licence.",
           "Japleen Kaur. CyberGuard GitHub repository. https://" + REPO]),
]

# ---------------------------------------------------------------------------
# 4-7. PROJECT REPORTS
# ---------------------------------------------------------------------------
TOC_12 = [("1.   Abstract", "4"), ("2.   Introduction", "4"), ("3.   Objectives", "5"),
          ("4.   Software & Hardware Requirements", "6"), ("5.   Implementation", "7"),
          ("6.   Key Functionalities", "10"), ("7.   System Analysis & Differentiation", "11"),
          ("8.   Flow Chart", "13"), ("9.   Output & Screenshots", "14"), ("10.   GitHub Upload", "16"),
          ("11.   Conclusion", "17"), ("12.   Future Advancements", "17")]

TOC_10 = [("1.\tAbstract", ""), ("2.\tIntroduction", ""), ("3.\tObjectives", ""),
          ("4.\tSoftware & Hardware Requirements", ""), ("5.\tImplementation", ""),
          ("6.\tKey Functionalities", ""), ("7.\tSystem Analysis & Differentiation", ""),
          ("8.\tOutput & Screenshots", ""), ("9.\tConclusion", ""), ("10.\tFuture Advancements", "")]


def common_requirements_table(software_rows):
    return ("t", ["Component", "Version used", "Purpose"], software_rows, [4.2, 3.4, 8.2])


def hardware_table():
    return ("t", ["Component", "Minimum", "Recommended"],
            [["Processor", "Dual core 2 GHz", "Quad core"],
             ["Memory", "4 GB", "8 GB or more (Oracle Database Free is the largest component)"],
             ["Disk", "1 GB free", "10 GB free including the database"],
             ["Display", "1280 x 720", "1920 x 1080"]],
            [3.6, 4.0, 8.2])


PYTHON_REPORT = [
    ("h1", "1. Abstract"),
    ("p", "CyberGuard is an educational cybersecurity toolkit that joins a web dashboard, a C++17 server, a Python "
          "service and an Oracle database in one application. " + CANONICAL),
    ("p", "This report documents the Python half of the system: four analysis modules built on the standard library, "
          "a Flask service that exposes them to the C++ server, a report generator that produces TXT and CSV, and a "
          "database module that is the only place in the project where Oracle is reached. The service returns one "
          "reply shape from every endpoint, so the browser needs a single error handler, and every analysis reply "
          "carries a flag stating whether the result was stored."),
    ("p", "The work described here converted four features from decorative to functional. Before it, the Activity "
          "History view, the Overview numbers and the report records had no data behind them and three endpoints "
          "answered with HTTP 501. The finished service holds 50 tests, of which 49 run with no database present, "
          "and it remains fully usable when Oracle is absent."),

    ("h1", "2. Introduction"),
    ("p", "Python was chosen for this layer because four of the nine analyses are text processing, and the standard "
          "library already contains what they need: regular expressions for log levels, a Counter for frequency "
          "counting, the ipaddress module for address validation, and csv for report output. No third-party package "
          "is required for any of it, which means the analysis half of the service installs nothing."),
    ("p", "The service also owns the project's only database connection. That decision keeps the connection string, "
          "the pool and the PL/SQL calls in one file, and leaves the C++ server without a database driver, so the "
          "C++ build stays a single compiler invocation. The browser cannot reach the service directly; the C++ "
          "server is the only client."),

    ("h1", "3. Objectives"),
    ("n", ["Implement four analysis modules on the standard library, with no third-party analysis dependency.",
           "Expose them through a Flask service whose replies all share one shape.",
           "Generate TXT and CSV reports that withhold sensitive fields and resist spreadsheet formula injection.",
           "Place every Oracle call in one module and call the PL/SQL objects the schema defines.",
           "Keep every analysis available when the database is missing, and report the missing storage in the "
           "reply.",
           "Hold the whole service to a test suite that runs without a database."]),

    ("h1", "4. Software & Hardware Requirements"),
    ("h2", "4.1 Software Requirements"),
    common_requirements_table([
        ["Windows", "10 or 11 (64-bit)", "Host operating system"],
        ["CPython", "3.12 or later", "Runs the service"],
        ["Flask", "3.1", "The HTTP layer"],
        ["python-oracledb", "26.0.1", "Oracle driver in thin mode, no client libraries needed"],
        ["python-dotenv", "optional", "Reads .env when present; the module also parses it directly"],
        ["Oracle Database Free", "23ai", "Storage, needed only for the history features"],
        ["unittest", "standard library", "The test suite"]]),
    ("h2", "4.2 Hardware Requirements"),
    hardware_table(),

    ("h1", "5. Implementation"),
    ("h2", "5.1 Service Structure"),
    ("p", "The service keeps one responsibility per file: one module per analysis, one module for reports, one for "
          "the database and one for the HTTP layer. The HTTP layer does three things only: read the request, call a "
          "module, and shape the reply. Because the shape never changes, the browser can handle every failure in one "
          "place."),
    ("c", "def ok(data):\n"
          "    return jsonify({\"ok\": True, \"data\": data})\n"
          "\n"
          "def fail(message, status=400):\n"
          "    return jsonify({\"ok\": False, \"error\": message}), status\n"
          "\n"
          "@app.errorhandler(ValueError)\n"
          "def bad_input(error):\n"
          "    return fail(str(error), 400)"),
    ("h2", "5.2 Password Strength Analysis"),
    ("p", "The score is additive and explainable: three points per character up to twenty characters, ten points "
          "for each character class present, minus twenty for a repeated group, minus fifteen for a predictable "
          "sequence and minus ten for low variety. A password on the common list is capped at ten. The factors are "
          "returned so the interface can show why the rating is what it is, and the password is never stored, "
          "printed or echoed."),
    ("c", "factors = [{\"factor\": \"Length\", \"detail\": \"%d characters\" % length,\n"
          "            \"points\": min(length, 20) * 3}]\n"
          "for key, present in character_classes(password).items():\n"
          "    factors.append({\"factor\": CLASS_LABELS[key], \"points\": 10 if present else 0})\n"
          "raw = reduce(lambda total, f: total + f[\"points\"], factors, 0)\n"
          "score = max(0, min(100, raw))"),
    ("h2", "5.3 Log Analysis"),
    ("p", "Four compiled patterns and three counters produce the summary: level counts, failed logins, the busiest "
          "addresses and activity per hour. Addresses are validated before they are counted, so a version string "
          "cannot be mistaken for an address. The module refuses input above 5 MB or 100 000 lines, and it returns "
          "counts and addresses only - the log body never leaves the request."),
    ("h2", "5.4 IP Address Validation"),
    ("p", "The validator returns one plain-language classification through an ordered ladder - unspecified, "
          "loopback, link-local, multicast, private, global, reserved - so the most specific kind wins. For IPv6 it "
          "adds the compressed and exploded forms and any mapped IPv4 address."),
    ("h2", "5.5 Report Generation"),
    ("p", "A report carries an identifier of its own, a timestamp, the input summary, the results, observations, "
          "recommendations and a conclusion. Two safety properties are implemented: any field whose name indicates "
          "a secret is replaced with the word withheld, and a CSV cell beginning with a formula character is "
          "prefixed with an apostrophe. The file name is created by the module, never taken from the user."),
    ("h2", "5.6 The Database Module"),
    ("p", "db.py reads its configuration from the environment, creates one pool on first use, proves the connection "
          "with a trivial query, and commits once per call because the procedures deliberately do not commit. A "
          "failure is remembered for five seconds so that a page load during an outage is answered immediately "
          "instead of waiting for a connection attempt."),
    ("c", "ref_cursor = cursor.var(oracledb.CURSOR)\n"
          "cursor.execute(\"BEGIN :1 := get_recent_history(:2); END;\", [ref_cursor, limit])\n"
          "rows = ref_cursor.getvalue()"),
    ("h2", "5.7 Verification and Test Evidence"),
    ("t", ["Check", "Result"],
     [["C++ build with -Wall -Wextra", "Succeeds with no warnings"],
      ["C++ module checks", "33 passed, including four published SHA-256 vectors"],
      ["Python tests", "50 tests, 49 run and 1 skipped unless a live database is set"],
      ["Every endpoint called against the running stack", "13 endpoints, results as expected"],
      ["Analyses stored in Oracle", "Each written through insert_analysis_record and its companions"],
      ["Database switched off", "All nine tools answer with persisted false"],
      ["Python service stopped", "Health reports it; five C++ tools keep working"]],
     [7.0, 8.8]),
    ("t", SHA_TABLE[0], SHA_TABLE[1], SHA_TABLE[2]),

    ("h1", "6. Key Functionalities"),
    ("t", ["Module", "Language", "Function", "Endpoint"],
     [["6. Password Analyzer", "Python", "Rating out of 100 with factors and advice", "POST /api/password-strength"],
      ["7. Log Analyzer", "Python", "Level counts, failures, busiest addresses, hourly activity", "POST /api/log-analysis"],
      ["8. IP Validator", "Python", "IPv4 and IPv6 validation and classification", "POST /api/ip-validation"],
      ["9. Report Generator", "Python", "TXT or CSV report of the latest analysis", "POST /api/report"],
      ["10. Database layer", "Python and PL/SQL", "Save and read every result", "GET /api/history, /api/dashboard, /api/reports"],
      ["Helpers", "Python", "Write helpers used by the C++ server", "POST /api/record, /api/assessment, /api/file-check"]],
     [3.8, 3.0, 6.0, 3.0]),
    ("p", "Every reply has the same shape, and every analysis reply states whether it was stored:"),
    ("c", '{"ok": true,  "data": { ..., "persisted": true }}\n'
          '{"ok": false, "error": "A sentence a person can read."}'),

    ("h1", "7. System Analysis & Differentiation"),
    ("h2", "7.1 Analysis of the Starting Point"),
    ("t", ["Area", "State found", "Evidence"],
     [["Database access", "Not implemented", "No Python file imported a driver; no connection was opened"],
      ["Dependency install", "Incomplete", "setup_python.bat installed Flask only"],
      ["History endpoint", "Missing", "GET /api/history answered HTTP 501"],
      ["Overview endpoint", "Missing", "GET /api/dashboard answered HTTP 501"],
      ["Report records", "Missing", "No endpoint and no call to insert_report_record"]],
     [3.8, 5.2, 6.8]),
    ("h2", "7.2 Differentiation"),
    ("t", ["Existing alternative", "What it does", "How CyberGuard differs"],
     [["Online password meters", "Return a colour or a score", "Returns the factors behind the score, and never stores or echoes the password"],
      ["Log viewer tools", "Display the file", "Returns counts, failures and repeated addresses without echoing content"],
      ["Hash utilities", "Return a digest", "Compares with a reference and stores the outcome decided by the database"],
      ["A folder of scripts", "Each task solved alone", "One reply shape, one storage layer and a history that survives a restart"],
      ["A tool that needs its database", "Fails when the database is down", "Every analysis still runs and says it was not saved"]],
     [3.6, 4.4, 7.8]),

    ("h1", "8. Flow Chart"),
    ("c", "        Start\n"
          "          |\n"
          "          v\n"
          "  Browser submits a form  ---->  C++ server (127.0.0.1:8080)\n"
          "          |\n"
          "          v\n"
          "  <Is the tool written in Python?>\n"
          "     yes |                        | no\n"
          "         v                        v\n"
          "  Forward to 127.0.0.1:5001   C++ module answers\n"
          "         |\n"
          "         v\n"
          "  Validate the input -----> invalid ----> 400 with a sentence\n"
          "         | valid\n"
          "         v\n"
          "  Run the module (password / log / IP / report)\n"
          "         |\n"
          "         v\n"
          "  <Is the database reachable?>\n"
          "   no  |                        | yes\n"
          "       v                        v\n"
          "  persisted: false       call the PL/SQL procedure,\n"
          "  result still returned  commit, row visible in History\n"
          "       |                        |\n"
          "       +-----------+------------+\n"
          "                   |\n"
          "                   v\n"
          "                 Finish", 8.5),

    ("h1", "9. Output & Screenshots"),
    ("p", "Capture these after starting run_all.bat and opening http://127.0.0.1:8080."),
    ("t", ["Figure", "View to capture", "What the capture should show"],
     [row for row in UI_VIEWS if row[0] in ("9.1", "9.6", "9.7", "9.8", "9.9", "9.10", "9.11", "9.12")],
     [1.8, 4.2, 9.8], 9.5),
    ("p", "For the Python Programming submission, figures 9.7 to 9.11 are the essential ones; figure 9.12 "
          "demonstrates the graceful-degradation decision described in the abstract."),

    ("h1", "10. GitHub Upload"),
    ("p", "The complete source, the tests and the documentation are published at:"),
    ("p", REPO),
    ("t", GITHUB_TABLE[0], GITHUB_TABLE[1], GITHUB_TABLE[2]),

    ("h1", "11. Conclusion"),
    ("p", "The Python service now performs its four analyses, stores what they produced and reads it back. The work "
          "needed one new module, six endpoints and a test file, and it made four features functional: the Activity "
          "History view, the Overview numbers, the report records and the file checks. The decision that keeps the "
          "toolkit usable is that persistence is an addition to an analysis rather than a precondition for it."),

    ("h1", "12. Future Advancements"),
    ("b", ["Authentication, so the history records the person rather than one configured application name.",
           "A streaming path for the log analyser, so files larger than memory can be read.",
           "Pagination and a detail view for the history endpoint.",
           "A containerised Oracle instance in continuous integration, so the live path is tested on every push.",
           "Type hints and a static check, which would have caught the driver-API assumptions at review time."]),
]


PLSQL_REPORT = [
    ("h1", "1. Abstract"),
    ("p", "CyberGuard is an educational cybersecurity toolkit whose nine analysis tools record what they did. " +
          CANONICAL),
    ("p", "This report documents the database layer: seven tables, six functions, six procedures and four triggers, "
          "and the application module that calls them. The layer is written in SQL and PL/SQL for Oracle Database "
          "Free and is exercised by a numbered demonstration script whose output forms the evidence in this report."),
    ("p", "The organising idea is that the database enforces its own rules. A status column accepts exactly two "
          "values, a hash column is validated as sixty-four hexadecimal characters, a score is bounded, a report "
          "code is unique, and four triggers audit the changes that matter. The application calls the procedures "
          "instead of writing inserts, so those rules cannot be bypassed by another client, and the database decides "
          "outcomes such as whether a file check matched its reference rather than accepting the application's "
          "opinion."),

    ("h1", "2. Introduction"),
    ("p", "An examination of any record-keeping system has to answer two questions: what may a record contain, and "
          "who is allowed to decide. This project answers both in the database. The schema declares what a row may "
          "contain through keys, check constraints and regular expressions, and it decides outcomes through "
          "procedures that compute a result rather than accept one."),
    ("p", "The layer is also expected to survive a missing database, which sounds contradictory but is not: the "
          "application treats storage as optional and reports honestly, so the schema can be absent without the "
          "toolkit becoming unusable. That property is what makes an academic project demonstrable on a machine "
          "where Oracle is not installed."),

    ("h1", "3. Objectives"),
    ("n", ["Model the activity of nine analysis tools in normalised relations with declared keys and constraints.",
           "Demonstrate joins, aggregates, GROUP BY, HAVING, sub-queries and CASE in queries the application "
           "actually uses.",
           "Implement functions that return values and a cursor function that returns a result set.",
           "Implement procedures with input and output parameters, an explicit cursor, and a custom exception.",
           "Implement triggers that audit changes and maintain a timestamp column.",
           "Demonstrate transaction control, including a savepoint and a rollback that leaves the data unchanged.",
           "Call every object from the application with output bind variables."]),

    ("h1", "4. Software & Hardware Requirements"),
    ("h2", "4.1 Software Requirements"),
    common_requirements_table([
        ["Oracle Database Free", "23ai", "The relational engine and PL/SQL runtime"],
        ["SQL*Plus", "bundled", "Runs install_all.sql and the demonstration script"],
        ["python-oracledb", "26.0.1", "Client library used by the application, thin mode"],
        ["CPython", "3.12 or later", "Runs the module that calls the schema"],
        ["Windows", "10 or 11 (64-bit)", "Host operating system"]]),
    ("h2", "4.2 Hardware Requirements"),
    hardware_table(),

    ("h1", "5. Implementation"),
    ("h2", "5.1 Schema"),
    ("p", "Seven tables separate an entity from its activity. Identity columns generate the keys, so no client can "
          "choose one. Every activity table references users with a foreign key, so a row cannot refer to a user who "
          "does not exist. Indexes on the user-and-time columns keep the history query from scanning as the table "
          "grows, and the audit table deliberately carries no trigger of its own so that an audit write cannot "
          "recurse."),
    ("t", ["Table", "Type", "Purpose and constraints"], DB_OBJECTS[:7], [3.6, 2.0, 10.2], 9.5),
    ("h2", "5.2 Functions"),
    ("p", "Six functions cover lookup, creation and aggregation. get_user_id returns a key or null; "
          "get_or_create_user returns a key and recovers from a duplicate insert if another session created the user "
          "a moment earlier. Three aggregate functions take a null user id to mean all users, which is how the "
          "Overview panel gets its numbers in one round trip. The sixth returns a SYS_REFCURSOR so the newest "
          "analyses arrive as a cursor."),
    ("c", "CREATE OR REPLACE FUNCTION get_recent_history (p_limit IN NUMBER DEFAULT 20)\n"
          "  RETURN SYS_REFCURSOR IS\n"
          "  v_cursor SYS_REFCURSOR;\n"
          "BEGIN\n"
          "  IF p_limit IS NULL OR p_limit < 1 OR p_limit > 200 THEN\n"
          "    RAISE_APPLICATION_ERROR(-20011, 'The limit must be between 1 and 200.');\n"
          "  END IF;\n"
          "  OPEN v_cursor FOR\n"
          "    SELECT h.analysis_id, u.username, h.module_name, h.analysis_timestamp,\n"
          "           h.result_summary, h.status\n"
          "      FROM analysis_history h JOIN users u ON u.user_id = h.user_id\n"
          "     ORDER BY h.analysis_timestamp DESC, h.analysis_id DESC\n"
          "     FETCH FIRST p_limit ROWS ONLY;\n"
          "  RETURN v_cursor;\n"
          "END get_recent_history;", 8.5),
    ("h2", "5.3 Procedures"),
    ("p", "None of the procedures commits; the caller decides. insert_analysis_record validates the status with a "
          "custom exception, then writes both the analysis and its activity row. insert_file_integrity_record "
          "decides whether the check matched, so the outcome in the row and the outcome on the page cannot differ. "
          "generate_user_summary walks an explicit parameterised cursor and appends only while the summary stays "
          "inside its declared length."),
    ("c", "CREATE OR REPLACE PROCEDURE insert_analysis_record (\n"
          "  p_username IN VARCHAR2, p_module_name IN VARCHAR2,\n"
          "  p_result_summary IN VARCHAR2, p_status IN VARCHAR2 DEFAULT 'SUCCESS',\n"
          "  p_analysis_id OUT NUMBER\n"
          ") IS\n"
          "  e_invalid_status EXCEPTION;\n"
          "  v_user_id NUMBER;\n"
          "BEGIN\n"
          "  IF p_status IS NULL OR p_status NOT IN ('SUCCESS', 'FAILED') THEN\n"
          "    RAISE e_invalid_status;\n"
          "  END IF;\n"
          "  v_user_id := get_or_create_user(p_username);\n"
          "  INSERT INTO analysis_history (user_id, module_name, result_summary, status)\n"
          "  VALUES (v_user_id, p_module_name, SUBSTR(p_result_summary, 1, 500), p_status)\n"
          "  RETURNING analysis_id INTO p_analysis_id;\n"
          "  INSERT INTO activity_logs (user_id, activity_type, activity_status)\n"
          "  VALUES (v_user_id, 'Analysis: ' || p_module_name, p_status);\n"
          "EXCEPTION\n"
          "  WHEN e_invalid_status THEN\n"
          "    RAISE_APPLICATION_ERROR(-20001, 'The status must be SUCCESS or FAILED.');\n"
          "END insert_analysis_record;", 8.5),
    ("h2", "5.4 Triggers"),
    ("p", "Four triggers keep the history trustworthy. trg_users_audit records an insert, an update or a delete with "
          "the old value beside the new one. trg_assessments_audit does the same for assessment changes, and "
          "trg_assessments_timestamp maintains updated_at before an update so no client can leave it stale. "
          "trg_files_audit records the deletion of a file record."),
    ("h2", "5.5 Transactions"),
    ("p", "Because the procedures do not commit, the caller owns the transaction. The demonstration script uses that "
          "property directly: it changes an assessment, shows the audit row and the maintained timestamp, then rolls "
          "the change back so the sample data is unchanged. A second demonstration shows a savepoint, a delete, a "
          "rollback to the savepoint and a final clean-up."),
    ("h2", "5.6 The Application Side"),
    ("p", "The application calls the procedures with output bind variables, which is the boundary where Python and "
          "PL/SQL meet. It commits once per call, and it sends only the values the procedures expect - no SQL that "
          "duplicates a rule the database already enforces."),
    ("c", "new_id = cursor.var(oracledb.NUMBER)\n"
          "verification = cursor.var(oracledb.STRING, 20)\n"
          "cursor.callproc(\"insert_file_integrity_record\",\n"
          "                [who, name, size, digest, reference or None, new_id, verification])"),
    ("h2", "5.7 Verification and Test Evidence"),
    ("t", ["Check", "Result"],
     [["install_all.sql object counts", "7 tables, 6 functions, 6 procedures, 4 triggers, all VALID"],
      ["user_errors after installation", "No rows selected"],
      ["Demonstration script, 10 numbered sections", "All complete as expected"],
      ["Schema rules exercised", "Custom error, DUP_VAL_ON_INDEX and NO_DATA_FOUND each raised and caught"],
      ["Application round trip", "Analyses stored and read back through the history endpoint"],
      ["Database stopped", "Every tool still answers and states the result was not saved"]],
     [7.0, 8.8]),

    ("h1", "6. Key Functionalities"),
    ("t", ["Object", "Type", "Purpose"],
     DB_OBJECTS, [6.0, 2.4, 7.4], 9.5),

    ("h1", "7. System Analysis & Differentiation"),
    ("h2", "7.1 Analysis of the Starting Point"),
    ("p", "The schema was complete before this phase and the application never touched it. No Python file imported "
          "a driver, no connection was opened and the three endpoints that should read from the database answered "
          "with HTTP 501. The comment above the cursor function still read that \"the Python service reads it in "
          "Phase 8\"; Phase 8 had not been written, so four features waited on one missing file."),
    ("h2", "7.2 Differentiation"),
    ("t", ["Alternative", "What it does", "How this design differs"],
     [["SQL written inside the application", "Works, but rules live in the client", "The rules live in the schema, so another client cannot bypass them"],
      ["Validation only in the application", "Acceptable for one client", "Check constraints and procedures enforce the same rules for every client"],
      ["The application deciding a file outcome", "Two places can disagree", "The procedure decides; the page only reports what the database decided"],
      ["Procedures that commit internally", "Convenient for one caller", "The caller commits, so calls can be composed inside one transaction"],
      ["A schema delivered but unused", "Reads well as a document", "Every object is called by the running application and demonstrated by a script"]],
     [4.0, 4.6, 7.2]),

    ("h1", "8. Flow Chart"),
    ("c", "        Start: install_all.sql\n"
          "          |\n"
          "          v\n"
          "  00_create_user.sql  (run once as SYS)\n"
          "          |\n"
          "          v\n"
          "  schema.sql  ->  functions.sql  ->  procedures.sql  ->  triggers.sql\n"
          "          |\n"
          "          v\n"
          "  sample_data.sql  (demonstration rows)\n"
          "          |\n"
          "          v\n"
          "  Print object counts, then select from user_errors\n"
          "          |\n"
          "          v\n"
          "  <Errors?>\n"
          "   yes |                | no\n"
          "       v                v\n"
          "  Fix and rerun    queries.sql: 10 demonstrations\n"
          "                          |\n"
          "                          v\n"
          "  Application: db.py -> callproc -> commit -> /api/history\n"
          "                          |\n"
          "                          v\n"
          "                        Finish", 8.5),

    ("h1", "9. Output & Screenshots"),
    ("p", "The evidence for this submission comes from SQL*Plus. Capture the following after running install_all.sql "
          "and then queries.sql as the cyberguard user."),
    ("t", ["Figure", "What to capture", "What it should show"],
     [["9.1", "Object counts printed by install_all.sql", "TABLE 7, FUNCTION 6, PROCEDURE 6, TRIGGER 4, all VALID"],
      ["9.2", "The same script's user_errors query", "No rows selected"],
      ["9.3", "Demonstration 1: the JOIN", "Analyses listed with their user name"],
      ["9.4", "Demonstration 3: GROUP BY with HAVING", "Only users with at least two analyses"],
      ["9.5", "Demonstration 5: the three functions", "Analyses, average score and file checks in one row"],
      ["9.6", "Demonstration 6: generate_user_summary", "The summary line from DBMS_OUTPUT"],
      ["9.7", "Demonstration 7: update and audit", "The audit row and the maintained updated_at, then the rollback"],
      ["9.8", "Demonstration 9: exceptions", "The custom error, the duplicate key and the missing user"],
      ["9.9", "Demonstration 10: the REF CURSOR", "Three rows printed from get_recent_history(3)"],
      ["9.10", "The dashboard's Activity History view", "Rows that match the database, read through the API"]],
     [1.8, 6.0, 8.0], 9.5),

    ("h1", "10. GitHub Upload"),
    ("p", "The schema, the demonstration script and the application module are published at:"),
    ("p", REPO),
    ("t", GITHUB_TABLE[0], GITHUB_TABLE[1], GITHUB_TABLE[2]),

    ("h1", "11. Conclusion"),
    ("p", "The schema is now used rather than delivered. Every analysis, file check, assessment and report passes "
          "through a procedure that validates it, every read is answered by a function the database owns, and every "
          "mechanism in the syllabus is demonstrated by a numbered query whose output can be recorded. Enforcing the "
          "rules in one place is what makes the results trustworthy, and it is also what made the application "
          "shorter."),

    ("h1", "12. Future Advancements"),
    ("b", ["A package grouping the procedures by concern, and synonyms so the schema can be moved without touching "
           "the application.",
           "An account table replacing the shared application name.",
           "Materialised views for the Overview numbers, refreshed on a schedule.",
           "Partitioning analysis_history by month with an archive job for old rows.",
           "A containerised Oracle instance in continuous integration, so the demonstration script runs on every "
           "push."]),
]


WEB_REPORT = [
    ("h1", "1. Abstract"),
    ("p", "CyberGuard is an educational cybersecurity toolkit presented as a single-page dashboard written in HTML5, "
          "CSS3 and vanilla JavaScript. " + CANONICAL),
    ("p", "This report documents the front end: twelve views in one document, a palette held in CSS custom properties "
          "so that one attribute switches the theme, a responsive layout built on grid and flexbox, and a small "
          "JavaScript layer that validates every form before it sends anything and renders every reply with DOM "
          "methods. There is no framework, no build step and no external asset."),
    ("p", "The report also documents the part of the interface that changed most: its honesty. The header now reports "
          "the C++ server, the Python service and the database separately instead of claiming that everything is "
          "online whenever one of them answers, and each tool states whether its result reached the database."),

    ("h1", "2. Introduction"),
    ("p", "A dashboard for a four-layer system has to answer one question continuously: which part are you talking "
          "to, and what did it just do? This front end answers it in the header and inside each tool, and it does so "
          "without a framework, which keeps the whole page readable as written - the point of the exercise."),
    ("p", "The page also has to be safe with text it did not create. File names, log extracts and server messages all "
          "reach the interface, and none of them may be interpreted as markup. Every one of them is inserted with "
          "textContent, not with a markup string."),

    ("h1", "3. Objectives"),
    ("n", ["Present twelve views in one document with navigation that needs no reload.",
           "Hold both palettes in custom properties and remember the choice across a reload.",
           "Build a layout that collapses to one column on a small screen and expands to a side rail above 900 "
           "pixels.",
           "Validate every form in the browser and announce the outcome in the interface.",
           "Send JSON for the analyses and multipart data for the file upload.",
           "Render every reply with DOM methods, and reflect the state of each server component truthfully."]),

    ("h1", "4. Software & Hardware Requirements"),
    ("h2", "4.1 Software Requirements"),
    common_requirements_table([
        ["Browser", "Any current version", "Chrome, Edge, Firefox or Safari"],
        ["HTML5", "Living Standard", "Semantic structure"],
        ["CSS3", "Grid, flexbox, custom properties", "Layout and theming"],
        ["JavaScript", "ES6", "Navigation, validation, fetch, rendering"],
        ["C++ server", "built from backend/", "Serves the page and answers the API"],
        ["Python service", "Flask 3.1", "Needed by four of the nine tools"]]),
    ("h2", "4.2 Hardware Requirements"),
    hardware_table(),

    ("h1", "5. Implementation"),
    ("h2", "5.1 Document Structure"),
    ("p", "One document holds a side rail of twelve buttons, a header with the title and the status indicator, and "
          "twelve sections, one per view. Only three files are involved, and the markup for each view is written "
          "once: the navigation does not duplicate content, it reveals it."),
    ("c", "&lt;aside class=\"side\" id=\"side\"&gt;\n"
          "  &lt;nav aria-label=\"Tools\"&gt;\n"
          "    &lt;button data-view=\"overview\"&gt;Overview&lt;/button&gt;\n"
          "    &lt;button data-view=\"identifier\" data-desc=\"Count digits, letters and symbols in text.\"&gt;\n"
          "      Identifier Analyzer&lt;/button&gt;\n"
          "    ...\n"
          "  &lt;/nav&gt;\n"
          "&lt;/aside&gt;\n"
          "&lt;main&gt;\n"
          "  &lt;section class=\"view\" id=\"v-overview\"&gt; ... &lt;/section&gt;\n"
          "  &lt;section class=\"view\" id=\"v-identifier\" hidden&gt; ... &lt;/section&gt;\n"
          "&lt;/main&gt;", 8.5),
    ("h2", "5.2 Navigation"),
    ("p", "Choosing a tool hides every section except the chosen one, moves the heading, marks the button that was "
          "used and sets aria-current, so the current view is announced as well as coloured. On a small screen the "
          "rail becomes a panel that closes when a tool is chosen and when Escape is pressed."),
    ("h2", "5.3 Theming with Custom Properties"),
    ("p", "Every colour is declared once on the root element, and the dark palette redefines the same names under a "
          "data-theme attribute. One assignment restyles every component, which means no component carries a "
          "dark-mode rule of its own. The chosen theme is written to local storage."),
    ("c", ":root { --bg: #f7f4ef; --fg: #1c1c1c; --card: #ffffff; --accent: #8b5cf6; }\n"
          "[data-theme=\"dark\"] { --bg: #0b0715; --fg: #f2eefb; --card: #171025; }\n"
          "body { background: var(--bg); color: var(--fg); }\n"
          ".card { background: var(--card); }"),
    ("h2", "5.4 Layout"),
    ("p", "The layout is a two-column grid above 900 pixels and a single column below it, built with grid for the "
          "page and flexbox inside each component. The tool cards on the Overview page are generated from the same "
          "navigation data, so adding a tool adds a card without a second place to edit."),
    ("h2", "5.5 Validation and Submission"),
    ("p", "Each tool declares how to check and package its input in one table, which keeps the submit handler small "
          "enough to read. Whole numbers are checked with a regular expression and a safe-integer test, the reference "
          "hash is checked for sixty-four hexadecimal characters, and both file limits are checked before an upload "
          "starts. A failure throws an Error whose message is shown in the interface, so a client mistake and a "
          "server refusal arrive by the same path."),
    ("c", "const TOOLS = {\n"
          "  identifier: { url: \"/api/analyze\", build: f =&gt; {\n"
          "    if (!f.text.value.trim()) throw new Error(\"Enter some text first.\");\n"
          "    return { text: f.text.value }; } },\n"
          "  pointers: { url: \"/api/pointers\", build: f =&gt;\n"
          "    ({ a: int(f.a.value, \"First number\"), b: int(f.b.value, \"Second number\") }) },\n"
          "  ...\n"
          "};", 8.5),
    ("h2", "5.6 Rendering Replies"),
    ("p", "Two helpers turn a nested reply into tables: one walks objects into key-and-value rows, the other turns a "
          "list of records into a table with one column per key. Both use textContent, so a file name or a log "
          "extract is displayed literally. A null value is shown as none rather than as the word null."),
    ("h2", "5.7 The Status Indicator"),
    ("p", "The header reads the health reply, which now carries the state of the Python service and of the database "
          "separately, and renders four outcomes: server offline, Python offline, database offline and all services "
          "online. Inside each tool the reply's persisted flag decides whether the message says Done or says the "
          "result was not saved."),
    ("c", "async function health() {\n"
          "  const p = $(\"#pill\");\n"
          "  try {\n"
          "    const d = (await api(\"/api/health\")).data;\n"
          "    if (!d.python)   { p.textContent = \"Python service offline\"; p.className = \"pill down\"; return; }\n"
          "    if (!d.database) { p.textContent = \"Database offline\";       p.className = \"pill down\"; return; }\n"
          "    p.textContent = \"All services online\"; p.className = \"pill up\";\n"
          "  } catch { p.textContent = \"Server offline\"; p.className = \"pill down\"; }\n"
          "}"),
    ("h2", "5.8 Accessibility"),
    ("b", ["Every control has a visible label, and results sit in regions marked aria-live so they are announced.",
           "The menu button carries aria-expanded and aria-controls, kept in step with the panel.",
           "The status indicator is a live region, so a change of state is announced rather than only coloured.",
           "Navigation links set aria-current, and focus is never removed from an interactive element.",
           "The dark palette keeps body-text contrast above the guideline minimum."]),
    ("h2", "5.9 Verification and Test Evidence"),
    ("t", ["Check", "Result"],
     [["Page loads with the server running", "Twelve views reachable, no console errors"],
      ["Every tool chosen in turn", "The view changes and the heading follows"],
      ["Theme after a reload", "The choice is remembered"],
      ["Resize below and above 900 pixels", "The rail collapses and returns"],
      ["Malformed input in each form", "A specific message, and no request is sent"],
      ["File upload and hash comparison", "Hash shown, MATCH demonstrated with a reference"],
      ["Database stopped", "Database offline in the header, not-saved message in the tool"],
      ["Python service stopped", "Python service offline, and the four Python tools explain it"],
      ["Server stopped", "Server offline instead of a blank page"]],
     [7.0, 8.8]),

    ("h1", "6. Key Functionalities"),
    ("t", ["View", "What the user does", "What the interface shows"],
     [["Overview", "Opens the page", "Four numbers, a card per tool and the recent activity"],
      ["Identifier Analyzer", "Types up to 1000 characters", "Digit table, totals and the most frequent digits"],
      ["Score Calculator", "Enters one to ten numbers", "Count, sum, minimum, maximum and average"],
      ["Pointer Operations", "Enters two numbers", "Sum and absolute difference"],
      ["User Assessment", "Enters a name, five scores and a baseline", "Total, average, result and board summary"],
      ["File Integrity Lab", "Chooses a file and an optional reference hash", "SHA-256 with a copy button and MATCH, MISMATCH or no reference"],
      ["Password Strength Analyzer", "Types a sample password", "Rating, score, factors and advice"],
      ["Security Log Analyzer", "Uploads a .log or .txt file", "Level counts, failures, busiest addresses"],
      ["IP Address Validator", "Types an address", "Version, classification and flags"],
      ["Security Reports", "Chooses a type and a format", "A preview of the report and a download link"],
      ["Activity History", "Opens the view", "Stored analyses, newest first"],
      ["About", "Opens the view", "What the toolkit is and what it is not"]],
     [3.4, 5.4, 7.0], 9.5),

    ("h1", "7. System Analysis & Differentiation"),
    ("h2", "7.1 Analysis of the Starting Point"),
    ("t", ["Area", "State found", "Evidence"],
     [["Status indicator", "Reported one of two states", "Claimed the server was online while four tools could not work"],
      ["Persistence message", "Always reported success", "The flag was read from the wrong level of the reply"],
      ["Empty values", "Printed as null", "A null reply cell rendered the word null"],
      ["Database views", "No data possible", "History and Overview endpoints answered HTTP 501"]],
     [3.8, 5.2, 6.8]),
    ("h2", "7.2 Differentiation"),
    ("t", ["Alternative", "What it does", "How this page differs"],
     [["A dashboard built on a framework", "Faster to scaffold", "This page has no dependency, no build step and can be read end to end"],
      ["Static demo pages", "Look complete", "Every view here is wired to a working endpoint"],
      ["An interface that assumes success", "Shows a confirmation after submitting", "The confirmation depends on what the server reports"],
      ["Markup-string rendering", "Short to write", "DOM methods make user-supplied text structurally incapable of executing"]],
     [4.0, 4.6, 7.2]),

    ("h1", "8. Flow Chart"),
    ("c", "        Start: open http://127.0.0.1:8080\n"
          "          |\n"
          "          v\n"
          "  script.js runs: show(overview), health(), loadDash()\n"
          "          |\n"
          "          v\n"
          "  <Health reachable?>\n"
          "   no |                          | yes\n"
          "      v                          v\n"
          "  Pill: Server offline      Pill: Python / database / all online\n"
          "      |                          |\n"
          "      +------------+-------------+\n"
          "                   |\n"
          "                   v\n"
          "  User chooses a view  ->  section revealed, heading moved\n"
          "                   |\n"
          "                   v\n"
          "  User submits a form\n"
          "                   |\n"
          "                   v\n"
          "  <Validation passes?> --- no ---> message in the interface, nothing sent\n"
          "          | yes\n"
          "          v\n"
          "  fetch() to the C++ server\n"
          "          |\n"
          "          v\n"
          "  <ok?>\n"
          "   no |                    | yes\n"
          "      v                    v\n"
          "  Error text shown     Tables rendered with textContent,\n"
          "      |                report offered as a download\n"
          "      +---------+----------+\n"
          "                |\n"
          "                v\n"
          "              Finish", 8.5),

    ("h1", "9. Output & Screenshots"),
    ("p", "Capture these after starting run_all.bat and opening http://127.0.0.1:8080."),
    ("t", ["Figure", "View to capture", "What the capture should show"], UI_VIEWS, [1.8, 4.2, 9.8], 9.5),

    ("h1", "10. GitHub Upload"),
    ("p", "The three front-end files and the rest of the project are published at:"),
    ("p", REPO),
    ("t", GITHUB_TABLE[0], GITHUB_TABLE[1], GITHUB_TABLE[2]),

    ("h1", "11. Conclusion"),
    ("p", "The dashboard now reflects the system behind it: every view has a working endpoint, every failure has a "
          "sentence, and the state of the four layers is visible in one line of the header. It achieves this with "
          "three files and no dependency, which keeps the page readable and reproducible from a repository clone."),

    ("h1", "12. Future Advancements"),
    ("b", ["A service worker, so the shell loads instantly and states explicitly that it is offline.",
           "Charts drawn with the Canvas API, using the activity-per-hour data the log analyser produces.",
           "Pagination and a detail view on the History page.",
           "An automated accessibility check in continuous integration, alongside a keyboard-only walkthrough.",
           "A print stylesheet, so a report can be produced from the page itself."]),
]


APTITUDE_REPORT = [
    ("h1", "1. Abstract"),
    ("p", "CyberGuard is an educational cybersecurity toolkit whose nine analysis tools each answer a small, "
          "well-defined question. " + CANONICAL),
    ("p", "This report examines the project as a set of computational problems rather than as a product. Each tool is "
          "stated as a problem, solved with a named data structure, and analysed for the number of operations it "
          "needs. Counting the digits in a string is a frequency array of ten counters; summarising scores is a "
          "single aggregation pass; comparing two values through pointers is an exercise in the memory model; "
          "hashing a file is a fixed sequence of bit operations over a byte stream; and classifying an address is a "
          "decision ladder whose order is the algorithm."),
    ("p", "The report records each solution as a specification, a trace and a complexity statement, and it shows how "
          "the same reasoning carries into the database layer, where a set-based query replaces a loop and the "
          "indexes decide how many rows are read."),

    ("h1", "2. Introduction"),
    ("p", "Computing aptitude is demonstrated by taking a problem statement that looks ordinary and asking precise "
          "questions about it: what are the inputs, what is the smallest complete set of outputs, which structure "
          "holds the intermediate state, what does an invalid input look like, and how does the cost grow?"),
    ("p", "The nine tools in this project are useful for that exercise because they are small enough to solve "
          "completely and varied enough to require different structures. Each is solved once, and the same solution "
          "is then used by an application, which is what distinguishes a worked example from a program."),

    ("h1", "3. Objectives"),
    ("n", ["Interpret each tool as a problem with stated inputs, outputs and invalid inputs, before writing code.",
           "Apply fundamental constructs to a real problem: arrays, pointers, functions, loops and selection.",
           "Choose the structure that makes the solution obvious: a frequency array, an accumulator, a ladder, a "
           "counter set.",
           "Solve a number-manipulation problem with an array of counters and report the tie case correctly.",
           "Design a stable contract between two programs, so a computation written in one language can be used by "
           "another.",
           "Keep every routine linear in its input, and state the bound for each one."]),

    ("h1", "4. Software & Hardware Requirements"),
    ("h2", "4.1 Software Requirements"),
    common_requirements_table([
        ["C++ compiler", "g++ 16.2.0 (C++17)", "For the modules that demonstrate arrays, pointers and classes"],
        ["CPython", "3.12 or later", "For the modules built on the standard library"],
        ["cpp-httplib, JSON for Modern C++", "0.18.7, 3.11.3", "The contract between the two languages"],
        ["Flask", "3.1", "The Python service"],
        ["Oracle Database Free", "23ai", "Optional: the stored history"]]) ,
    ("h2", "4.2 Hardware Requirements"),
    hardware_table(),

    ("h1", "5. Implementation"),
    ("h2", "5.1 Problem 1: Digit Frequency in a String"),
    ("p", "The input is a string of up to 1000 characters. The output is the count of digits, letters and other "
          "characters, the highest digit frequency, and every digit that reaches it. The structure is an array of ten "
          "integers indexed by the digit itself, which turns the counting step into a single increment - no search, "
          "no comparison."),
    ("c", "for (unsigned char ch : text) {\n"
          "    if (ch >= '0' && ch <= '9') { r.digitFrequency[ch - '0']++; r.totalDigits++; }\n"
          "    else if ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z')) r.totalLetters++;\n"
          "    else r.totalOthers++;\n"
          "}"),
    ("p", "A reason to use an array rather than a map is the tie case: with an array the second pass visits the "
          "digits in order, so the report lists every digit that shares the maximum, in ascending order. A map would "
          "have made the same answer possible but the order accidental. The cost is one pass to count and one pass "
          "over ten entries, so the time is linear in the input and the working memory is constant."),
    ("h2", "5.2 Problem 2: Summarising a Set of Scores"),
    ("p", "The input is between one and ten whole numbers. The output is the count, the sum, the smallest, the "
          "largest and the average. One pass maintains all five quantities, so the cost is linear and no array of "
          "intermediate results is needed. Two details make the solution safe rather than merely correct: the first "
          "value initialises both bounds, so a set of positive numbers cannot leave a bound at zero; and every "
          "addition is checked, so a total that cannot be represented is reported instead of wrapping."),
    ("c", "r.minimum = r.maximum = scores[0];\n"
          "for (int s : scores) {\n"
          "    if (!safeAdd(r.sum, s, r.sum)) throw std::overflow_error(\"The sum is too large.\");\n"
          "    if (s < r.minimum) r.minimum = s;\n"
          "    if (s > r.maximum) r.maximum = s;\n"
          "}\n"
          "r.average = static_cast<double>(r.sum) / r.count;"),
    ("p", "A trace of the sample input 72, 85, 90 gives count 3, sum 247, minimum 72, maximum 90 and average 82.33. "
          "The interesting boundary cases are one value, ten values, and two values whose sum exceeds the range of "
          "the type used, which is where the overflow check becomes part of the algorithm rather than a decoration."),
    ("h2", "5.3 Problem 3: Two Values Through the Memory Model"),
    ("p", "The input is two integers. The output is their sum and the absolute difference, produced through pointers "
          "rather than returned as a pair. The exercise is to work with addresses: the caller passes the address of "
          "a variable, the callee writes through it, and the caller reads the result without any return value."),
    ("c", "void computeWithPointers(const int* pa, const int* pb, long long* pSum, long long* pDiff) {\n"
          "    if (!pa || !pb || !pSum || !pDiff) throw std::invalid_argument(\"Null pointer received.\");\n"
          "    long long x = *pa;                 // widen BEFORE calculating\n"
          "    long long y = *pb;\n"
          "    *pSum = x + y;\n"
          "    long long d = x - y;\n"
          "    *pDiff = (d < 0) ? -d : d;\n"
          "}"),
    ("p", "The subtle point is the order of operations. The largest and smallest 32-bit integers have a difference "
          "of 4294967295, which does not fit in a 32-bit signed integer, so the widening to a 64-bit type has to "
          "happen before the subtraction. A solution that computes the difference first and widens afterwards is "
          "wrong for exactly one pair of inputs, which is the kind of defect a boundary test finds and a "
          "demonstration does not."),
    ("h2", "5.4 Problem 4: Classification by an Ordered Ladder"),
    ("p", "The input is text that may or may not be an address. The output is a validity decision and, when valid, "
          "one label. The solution is a ladder of tests whose order is the algorithm: unspecified, loopback, "
          "link-local, multicast, private, global, reserved. Reordering the rungs changes the answer, because the "
          "first test that succeeds decides the result."),
    ("c", "def classify(ip):\n"
          "    if ip.is_unspecified: return \"Unspecified\"\n"
          "    if ip.is_loopback:    return \"Loopback (this computer)\"\n"
          "    if ip.is_link_local:  return \"Link-local\"\n"
          "    if ip.is_multicast:   return \"Multicast\"\n"
          "    if ip.is_private:     return \"Private (not routable on the public internet)\"\n"
          "    if ip.is_global:      return \"Public (global)\"\n"
          "    return \"Reserved or special-purpose\""),
    ("p", "The classification is a decision problem, and its correctness is established by cases rather than by "
          "formula: 127.0.0.1 is loopback even though it is also private, so loopback must be tested first; "
          "169.254.x.x is link-local even though it is also private, so link-local must come before private."),
    ("h2", "5.5 Problem 5: A Fixed Sequence of Operations"),
    ("p", "Hashing a file is the one problem here with no shortcut. The algorithm is a fixed sequence: pad the "
          "message, split it into 512-bit blocks, run sixty-four rounds per block with an eight-word state, and "
          "append the length in bits. The cost is linear in the size of the input, the working memory is constant, "
          "and the order of the operations is defined by the specification rather than chosen by the solver."),
    ("p", "The implementation is verified the only way a fixed sequence can be: with known answers. The four "
          "published test vectors, including a message that spans more than one block and one of a million bytes, "
          "are checked by the test suite, and the digests are cross-checked against an independent implementation."),
    ("t", SHA_TABLE[0], SHA_TABLE[1], SHA_TABLE[2]),
    ("h2", "5.6 Problem 6: The Same Reasoning in a Database"),
    ("p", "The database layer shows that the reasoning transfers. A question such as \"how many analyses has each "
          "module run\" is answered by a grouped query rather than a loop over rows, because the engine can use an "
          "index and process sets. Writing the loop in the application would produce the same answer with far more "
          "operations."),
    ("c", "SELECT module_name, COUNT(*) AS runs\n"
          "  FROM analysis_history\n"
          " GROUP BY module_name\n"
          " ORDER BY runs DESC, module_name;"),
    ("p", "The chosen structure matters in SQL for the same reason it matters in C++: an index on the user-and-time "
          "columns turns the history query from a scan into a lookup, which is a difference in the order of growth "
          "rather than a constant improvement."),
    ("h2", "5.7 Verification and Test Evidence"),
    ("t", ["Check", "Result"],
     [["C++ build with -Wall -Wextra", "Succeeds with no warnings"],
      ["C++ module checks", "33 passed, including boundary values such as INT_MAX and INT_MIN"],
      ["Digit frequency against AB12 3C 4@4 99", "7 digits, 3 letters, 4 other; digits 4 and 9 tie at 2"],
      ["Score summary of 72, 85, 90", "count 3, sum 247, minimum 72, maximum 90, average 82.33"],
      ["Pointer arithmetic at the limits", "sum -1 and difference 4294967295 for INT_MAX and INT_MIN"],
      ["SHA-256 known answers", "4 of 4 published vectors match"],
      ["Python tests", "50 tests, 49 run with no database present"],
      ["Classification cases", "Loopback, link-local, private, public and invalid each return the right label"]],
     [7.0, 8.8]),

    ("h1", "6. Key Functionalities"),
    ("t", ["Problem", "Structure", "Cost", "Where it runs"],
     [["Digit and letter counts", "Frequency array of ten counters", "One pass, constant memory", "C++ module 1"],
      ["Score summary", "Five accumulators in one pass", "One pass, constant memory", "C++ module 2"],
      ["Sum and absolute difference", "Pointers and address arithmetic", "Constant", "C++ module 3"],
      ["Assessment against a baseline", "Fixed array inside a class", "Constant per user, linear over the board", "C++ module 4"],
      ["File digest", "Streaming 512-bit blocks", "Linear in the file, constant memory", "C++ module 5"],
      ["Password rating", "Additive factors and a cap", "Linear in the password", "Python module 6"],
      ["Log summary", "Patterns and counters", "Linear in the log", "Python module 7"],
      ["Address classification", "Ordered decision ladder", "Constant", "Python module 8"],
      ["Report generation", "Flattening a nested structure", "Linear in the report size", "Python module 9"],
      ["History and totals", "Grouped queries and indexes", "Set-based, index-assisted", "Oracle"]],
     [3.6, 4.2, 4.4, 3.6], 9.5),

    ("h1", "7. System Analysis & Differentiation"),
    ("h2", "7.1 Analysis of the Starting Point"),
    ("p", "The computation was complete before this phase and the connections were not. The C++ modules passed "
          "twenty-two checks and the Python tests passed thirty-four, while four features could not work at all: the "
          "file digest, the stored history, the Overview numbers and the report records. The lesson is about scope: "
          "a problem solved in isolation and a problem solved inside a system are different problems, and only the "
          "second one is finished."),
    ("h2", "7.2 Differentiation"),
    ("t", ["Alternative approach", "What it does", "How this solution differs"],
     [["Counting with a map or a nested loop", "Works for any symbol set", "A ten-element array is constant memory and gives the tie order for free"],
      ["Computing the difference then widening", "Looks equivalent", "Overflows for one pair of inputs; the widening must come first"],
      ["Classifying by a set of independent flags", "Returns every property", "An ordered ladder returns the one label that matters, and its order is the algorithm"],
      ["Hashing with a library call", "Shorter", "Writing the sequence exposes the bit operations and is verified with known answers"],
      ["Solving each exercise as a script", "Demonstrates the technique", "Each solution here is used by a running application, so its contract is tested"]],
     [4.0, 4.2, 7.6]),

    ("h1", "8. Output & Screenshots"),
    ("p", "Capture these after starting run_all.bat and opening http://127.0.0.1:8080."),
    ("t", ["Figure", "What to capture", "What it should show"],
     [["8.1", "Identifier Analyzer", "AB12 3C 4@4 99 with digits 4 and 9 tied at a frequency of 2"],
      ["8.2", "Score Calculator", "72, 85, 90 giving count 3, sum 247 and average 82.33"],
      ["8.3", "Pointer Operations", "Two values with the sum and the absolute difference"],
      ["8.4", "User Assessment", "Five scores against a baseline with the total and the result"],
      ["8.5", "File Integrity Lab", "A file with its digest and a MATCH result"],
      ["8.6", "IP Address Validator", "A loopback address and a private address showing two different labels"],
      ["8.7", "C++ test output", "33 checks passed, 0 failed"],
      ["8.8", "Python test output", "49 tests passing with one skip"]],
     [1.8, 4.2, 9.8], 9.5),

    ("h1", "9. Conclusion"),
    ("p", "Nine small problems, solved completely and then used, produced a toolkit that will pass its checks on any "
          "machine. The recurring lesson is that the choice of structure decides how simple the solution looks: a "
          "frequency array makes the tie case fall out for free, one pass with five accumulators removes the need "
          "for any intermediate list, an ordered ladder turns a classification into a sequence of decisions, and a "
          "set-based query replaces a loop in the one place where the number of rows can grow."),
    ("p", "The second lesson is about boundaries. Every solution here is exercised through a contract - a JSON reply "
          "or a scalar return - and the contract is what makes the answer checkable by a test rather than by "
          "inspection."),

    ("h1", "10. Future Advancements"),
    ("b", ["State the complexity bound next to each function in the code, so the property is reviewed with the "
           "implementation.",
           "Add a property-based test for the aggregation routines, generating thousands of inputs rather than a few "
           "hand-chosen ones.",
           "Extend the digit analyser into a general character-frequency tool, comparing an array with a map to "
           "measure the difference.",
           "Add a second hashing algorithm and compare their digests on the same inputs.",
           "Introduce a small benchmark that records the time of each routine at increasing input sizes, so the "
           "stated bounds can be confirmed by measurement."]),
]

DOCUMENTS = [
    ("CyberGuard_Case_Study_Python.docx", "case", "case_study_cover",
     dict(name="CYBERGUARD", tagline=["A PYTHON 3 ANALYSIS SERVICE", "WITH A DURABLE STORAGE LAYER",
                                     "FLASK, STANDARD LIBRARY AND ORACLE"],
          guide="Mr. Randeep Singh Dhillon"), PYTHON_CASE),
    ("CyberGuard_Case_Study_ADBMS.docx", "case", "case_study_cover",
     dict(name="CYBERGUARD", tagline=["A RELATIONAL SCHEMA & PL/SQL", "REPORTING SYSTEM",
                                     "ORACLE DATABASE FREE: TABLES, FUNCTIONS, PROCEDURES, TRIGGERS"],
          guide="Mr. Mohammad Rashid"), ADBMS_CASE),
    ("CyberGuard_Case_Study_Web_Programming.docx", "case", "case_study_cover",
     dict(name="CYBERGUARD", tagline=["A SINGLE-PAGE DASHBOARD", "IN HTML, CSS AND VANILLA JAVASCRIPT",
                                     "TWELVE VIEWS, TWO THEMES, ONE HONEST STATUS LINE"],
          guide="Ms. Saranjeet Kaur"), WEB_CASE),

    ("CyberGuard_Project_Report_Python_Programming.docx", "report", "report_cover",
     dict(subject="Python Programming",
          subtitle="A Flask analysis service, its report generator and the Oracle layer behind it",
          guide="Gurpreet Kaur"), PYTHON_REPORT),
    ("CyberGuard_Project_Report_PL_SQL.docx", "report", "report_cover",
     dict(subject="PL/SQL (Oracle Database)",
          subtitle="Database schema, PL/SQL procedures, functions, cursors and triggers",
          guide="Chanchal Sharma"), PLSQL_REPORT),
    ("CyberGuard_Project_Report_Web_Programming.docx", "report", "report_cover",
     dict(subject="Web Programming",
          subtitle="A single-page dashboard in HTML5, CSS3 and vanilla JavaScript",
          guide="Ms. Saranjeet Kaur"), WEB_REPORT),
    ("CyberGuard_Project_Report_Computing_Aptitude.docx", "report", "report_cover",
     dict(subject="Computing Aptitude",
          subtitle="Nine small problems, solved completely and then used",
          guide="MS. ASHIMA SOOD", variant="aptitude"), APTITUDE_REPORT),
]


def build():
    written = []
    for filename, kind, cover, cover_args, blocks in DOCUMENTS:
        if kind == "case":
            doc = make_document(body=11, colour="8A3B1E", top=2.2, bottom=2.2, left=2.5, right=2.5)
            footer(doc, "CyberGuard  |  MCA Case Study")
            case_study_cover(doc, cover_args["name"], cover_args["tagline"], cover_args["guide"])
            render(doc, blocks)
        else:
            doc = make_document(body=12, colour="365F91")
            footer(doc, "CyberGuard  |  MCA Project Report")
            report_cover(doc, cover_args["subject"], cover_args["subtitle"], cover_args["guide"],
                         cover_args.get("variant", "standard"))
            if cover_args.get("variant") != "aptitude":
                certificate(doc, cover_args["guide"])
                contents(doc, TOC_12, with_pages=True)
            else:
                contents(doc, TOC_10, with_pages=False)
                doc.add_page_break()
            render(doc, blocks)
        path = os.path.join(HERE, filename)
        doc.save(path)
        written.append(path)
    return written


if __name__ == "__main__":
    for path in build():
        print("written: %-52s %6d bytes" % (os.path.basename(path), os.path.getsize(path)))
