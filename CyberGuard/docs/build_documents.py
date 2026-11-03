"""Build the CyberGuard PROJECT REPORT and CASE STUDY in the formats used by the
student's own earlier submissions:

  * PROJECT_REPORT.docx follows ExamIQ_Project_Report_*.docx
    (A4, Times New Roman 12, rust/blue headings, certificate, contents, 12 sections)
  * CASE_STUDY.docx follows Case-Study-Portfolio.docx
    (A4, Times New Roman 11, heading colour 8A3B1E, footer with page X of Y, 9 sections)

Run:  python docs\\build_documents.py
"""
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

STUDENT = "Japleen Kaur"
UID = "26MCA20265"
SEMESTER = "1st / Year: 1st"
GUIDE = "Chanchal Sharma"
SUBJECT = "C++, Python & PL/SQL"
DEPARTMENT = "Department of Computer Applications"
UNIVERSITY = "Chandigarh University, Gharuan, Mohali, Punjab, India"
ACADEMIC_YEAR = "2026-2027"
SESSION = "October-November, 2026"
REPO = "github.com/jay-kxz/CyberGuard"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def make_document(body_size=12, heading_colour="365F91", top=2.4, bottom=2.2, left=2.5, right=2.2):
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
    normal.font.size = Pt(body_size)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    normal.font.color.rgb = RGBColor(0x1C, 0x1C, 0x1C)

    for name, size in (("Heading 1", 14), ("Heading 2", 11.5), ("Heading 3", 11)):
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(heading_colour)
        style.paragraph_format.space_before = Pt(10)
        style.paragraph_format.space_after = Pt(4)
    return doc


def centre(doc, text, size=11, bold=False, italic=False, caps=False, space_after=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text.upper() if caps else text)
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    return p


def spaced_title(doc, text, size=13):
    """A  P R O J E C T   R E P O R T  - the letter spacing used on the reference cover."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("  ".join(text.upper()))
    r.bold = True
    r.font.size = Pt(size)
    return p


def para(doc, text, bold=False, italic=False, size=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def table(doc, headers, rows, widths=None, font_size=10):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, head in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(head)
        run.bold = True
        run.font.size = Pt(font_size)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(value))
            run.font.size = Pt(font_size)
    if widths:
        for row in t.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Cm(width)
    doc.add_paragraph()
    return t


def code(doc, text, size=9):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(size)
    return p


def footer_with_pages(doc, left_text):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.text = ""
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT)
    run = p.add_run(left_text + "\tPage ")
    run.font.size = Pt(9)
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        element = OxmlElement("w:fldChar" if kind else "w:instrText")
        if kind:
            element.set(qn("w:fldCharType"), kind)
        else:
            element.set(qn("xml:space"), "preserve")
            element.text = text
        run._r.append(element)
    p.add_run(" of ").font.size = Pt(9)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "NUMPAGES"
    tail = OxmlElement("w:fldChar")
    tail.set(qn("w:fldCharType"), "end")
    run2 = p.add_run()
    run2.font.size = Pt(9)
    run2._r.append(end)
    run2._r.append(instr)
    run2._r.append(tail)


# ---------------------------------------------------------------------------
# PROJECT REPORT  (ExamIQ_Project_Report_* format)
# ---------------------------------------------------------------------------
def build_report():
    doc = make_document(body_size=12, heading_colour="365F91")
    footer_with_pages(doc, "CyberGuard  |  MCA Project Report")

    # ---- cover ----
    spaced_title(doc, "A Project Report")
    centre(doc, "CyberGuard: An Integrated Cybersecurity Analysis and Utility Toolkit",
           size=17, bold=True, space_after=2)
    centre(doc, "(C++, Python and Oracle Database)", size=12, italic=True, space_after=2)
    centre(doc, "Nine analysis tools behind one dashboard, with a database layer that can be absent",
           size=11, italic=True)
    doc.add_paragraph()
    centre(doc, "Submitted By:", bold=True, space_after=2)
    centre(doc, STUDENT, size=13, bold=True, space_after=2)
    centre(doc, "UID: " + UID, space_after=2)
    centre(doc, "Subject: " + SUBJECT, space_after=10)
    centre(doc, "Submitted To:", bold=True, space_after=2)
    centre(doc, GUIDE, size=13, bold=True, space_after=10)
    centre(doc, "in partial fulfillment for the award of the degree of", space_after=2)
    centre(doc, "MASTERS OF COMPUTER APPLICATIONS", size=13, bold=True, space_after=2)
    centre(doc, "IN", space_after=2)
    centre(doc, "UNIVERSITY INSTITUTE OF COMPUTING", size=12, bold=True, space_after=2)
    centre(doc, "CHANDIGARH UNIVERSITY", size=12, bold=True, space_after=10)
    centre(doc, SESSION, bold=True)
    doc.add_page_break()

    # ---- certificate ----
    centre(doc, "BONAFIDE CERTIFICATE", size=14, bold=True)
    doc.add_paragraph()
    para(doc, 'This is to certify that the project report entitled "CyberGuard: An Integrated '
              'Cybersecurity Analysis and Utility Toolkit" submitted by ' + STUDENT + ' (' + UID + '), '
              'in partial fulfillment of the requirements for the award of the degree of Masters of '
              'Computer Applications, is a record of the work carried out under my supervision.')
    para(doc, "The project work embodied in this report has not been submitted to any other University or "
              "Institution for the award of any degree or diploma. The work presented here is original and "
              "complete to the best of my knowledge.")
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph("___________________")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p = doc.add_paragraph("Signature of Supervisor")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p = doc.add_paragraph(GUIDE)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_page_break()

    # ---- contents ----
    centre(doc, "Table of Contents", size=14, bold=True)
    doc.add_paragraph()
    contents = [
        ("1.  Abstract", "4"),
        ("2.  Introduction", "4"),
        ("3.  Objectives", "5"),
        ("4.  Software & Hardware Requirements", "6"),
        ("5.  Implementation", "7"),
        ("6.  Key Functionalities", "10"),
        ("7.  System Analysis & Differentiation", "12"),
        ("8.  Flow Chart", "13"),
        ("9.  Output & Screenshots", "14"),
        ("10.  GitHub Upload", "16"),
        ("11.  Conclusion", "17"),
        ("12.  Future Advancements", "17"),
    ]
    for label, page in contents:
        p = doc.add_paragraph()
        p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        p.add_run(label + "\t" + page)
    doc.add_page_break()

    # ---- 1 Abstract ----
    doc.add_heading("1. Abstract", level=1)
    para(doc, "CyberGuard is an educational cybersecurity toolkit that joins four technologies in one "
              "application: a web dashboard in HTML, CSS and JavaScript; a C++17 server that serves the pages "
              "and performs the numeric analysis; a Python service that analyses passwords, log files and IP "
              "addresses and generates reports; and an Oracle database that stores the activity history, the "
              "assessment records and the file verification results.")
    para(doc, "The report documents the architecture, the nine analysis modules, the ten PL/SQL objects behind "
              "the storage layer, and the way the layers were joined. The data layer is deliberately placed in "
              "one Python module, which calls the procedures and functions the schema already defines, so the "
              "validation rules stated in the database cannot be bypassed by the application.")
    para(doc, "A central design decision is that persistence is an addition to an analysis and never a "
              "precondition for it. The dashboard stays usable when neither the Python service nor Oracle is "
              "running: the analysis is returned, and the reply states that the result was not saved. Each "
              "analysis is stored through insert_analysis_record and its companion procedures when a database "
              "is reachable, and the Overview numbers and Activity History view fill in.")
    para(doc, "The finished system passes 33 C++ checks and 50 Python tests, and its SHA-256 implementation "
              "reproduces the four published test vectors from FIPS 180-4 exactly. The report records the "
              "implementation, the verification evidence and the limitations that follow from building an "
              "educational tool rather than a security product.")

    # ---- 2 Introduction ----
    doc.add_heading("2. Introduction", level=1)
    para(doc, "Security work is learned through small, well-defined checks: counting the character classes in an "
              "identifier, measuring how predictable a password is, reading a log file for failed logins, "
              "confirming that a file has not changed, and checking whether an address belongs to a local "
              "network. Each is simple on its own, which makes them good exercises for one integrated "
              "application.")
    para(doc, "Built as separate scripts, however, they leave a learner with a folder of unrelated programs and "
              "no view of how a real application is assembled. CyberGuard therefore approaches the problem "
              "architecturally: C++, Python, a relational database and a web front end in one system, with a "
              "single interface, a single storage layer and a consistent error model, while each part stays "
              "small enough to be understood.")
    para(doc, "The application is not a penetration-testing tool and not a certified security product. It is a "
              "teaching instrument, and the interface says so wherever a user might mistake its output for a "
              "professional assessment.")

    # ---- 3 Objectives ----
    doc.add_heading("3. Objectives", level=1)
    bullets(doc, [
        "Provide nine analysis tools behind one dashboard: identifier analysis, score calculation, pointer "
        "operations, user assessment, file integrity, password strength, log analysis, IP validation and report "
        "generation.",
        "Demonstrate core C++ language features in use: arrays, strings, loops, functions, variadic arguments, "
        "overflow-safe arithmetic, pointers, classes, encapsulation and vectors.",
        "Demonstrate Python file handling, regular expressions, the standard library ipaddress module and text "
        "report generation.",
        "Create an Oracle schema with tables, constraints, indexes, functions, procedures, an explicit cursor and "
        "triggers, and use it from the application rather than leaving it as a separate deliverable.",
        "Keep the application usable when an optional component is unavailable, and make every failure "
        "explainable in the interface.",
        "Verify the result with automated tests rather than by inspection.",
    ])

    # ---- 4 Requirements ----
    doc.add_heading("4. Software & Hardware Requirements", level=1)
    doc.add_heading("4.1 Software Requirements", level=2)
    table(doc,
          ["Component", "Version used", "Purpose"],
          [["Windows", "10 or 11 (64-bit)", "Host operating system"],
           ["MSYS2 UCRT64 GCC", "g++ 16.2.0", "Builds the C++17 server"],
           ["cpp-httplib", "0.18.7", "HTTP server and client, header only"],
           ["JSON for Modern C++", "3.11.3", "JSON parse and serialise, header only"],
           ["CPython", "3.12 or later", "Runs the analysis service"],
           ["Flask", "3.1", "HTTP layer of the Python service"],
           ["python-oracledb", "26.0.1", "Oracle driver, thin mode, no client libraries needed"],
           ["Oracle Database Free", "23ai", "Tables, PL/SQL procedures, functions and triggers"],
           ["Browser", "Any current browser", "Dashboard front end"]],
          widths=[4.2, 3.4, 8.2])
    doc.add_heading("4.2 Hardware Requirements", level=2)
    table(doc,
          ["Component", "Minimum", "Recommended"],
          [["Processor", "Dual core 2 GHz", "Quad core"],
           ["Memory", "4 GB", "8 GB or more (Oracle Database Free is the largest component)"],
           ["Disk", "1 GB free", "10 GB free including the database"],
           ["Display", "1280 x 720", "1920 x 1080"]],
          widths=[3.6, 4.0, 8.2])

    # ---- 5 Implementation ----
    doc.add_heading("5. Implementation", level=1)
    doc.add_heading("5.1 Architecture", level=2)
    para(doc, "The system has four layers. The browser talks only to the C++ server. The C++ server serves the "
              "front end and answers modules 1 to 5 itself; it forwards the Python modules and the three database "
              "reads to the Python service on port 5001. The Python service is the only component that opens a "
              "connection to Oracle, through a connection pool.")
    code(doc,
         "Browser (index.html + style.css + script.js)\n"
         "     |  fetch() JSON, multipart file upload\n"
         "     v\n"
         "C++ server, 127.0.0.1:8080  (cpp-httplib)\n"
         "  modules 1-4  |  module 5 (SHA-256)  |  relays for the database reads\n"
         "     |  HTTP to 127.0.0.1:5001\n"
         "     v\n"
         "Python service (Flask)  modules 6-9  +  db.py (Module 10)\n"
         "     |  python-oracledb, connection pool, thin mode\n"
         "     v\n"
         "Oracle Database Free  -  tables, PL/SQL procedures, functions, triggers")

    doc.add_heading("5.2 Module 1 to Module 4 (C++)", level=2)
    para(doc, "The identifier analyser walks the input byte by byte and fills a ten-element array, which "
              "demonstrates arrays, strings and loops. The score calculator demonstrates a variadic function and "
              "uses the GCC/Clang built-in __builtin_add_overflow so a sum that cannot be represented is reported "
              "instead of wrapping silently. The pointer module passes two values by address and widens to long "
              "long before arithmetic, so the difference between the largest and smallest int cannot overflow. "
              "The assessment module keeps a fixed array of five scores inside a class whose members are private, "
              "and a board object holds up to one hundred assessments, replacing an entry when the same user is "
              "assessed again.")

    doc.add_heading("5.3 Module 5 - File Integrity Lab (SHA-256)", level=2)
    para(doc, "The File Integrity Lab computes the SHA-256 hash of an uploaded file of up to 25 MB and compares it "
              "with an optional reference hash. The algorithm is implemented in the project rather than taken "
              "from a library, which removes an OpenSSL dependency from the Windows build and exercises byte "
              "handling and bit rotation directly. Data is fed to the hasher block by block, so the same class "
              "hashes a memory buffer and a file on disk.")
    code(doc,
         "void update(const unsigned char* data, std::size_t length) {\n"
         "    totalBits_ += static_cast<std::uint64_t>(length) * 8u;\n"
         "    while (length > 0) {\n"
         "        const std::size_t room = kBlockSize - buffered_;\n"
         "        const std::size_t take = std::min(length, room);\n"
         "        std::memcpy(block_.data() + buffered_, data, take);\n"
         "        buffered_ += take; data += take; length -= take;\n"
         "        if (buffered_ == kBlockSize) { transform(block_.data()); buffered_ = 0; }\n"
         "    }\n"
         "}")
    para(doc, "The upload arrives as multipart form data, so the route reads the file part directly. The "
              "reference hash is trimmed, lower-cased and validated as exactly sixty-four hexadecimal characters "
              "before any comparison, and the result is one of the three values the database column accepts: "
              "MATCH, MISMATCH or NO REFERENCE GIVEN.")

    doc.add_heading("5.4 Module 6 to Module 9 (Python)", level=2)
    para(doc, "The password analyser scores a sample password out of one hundred: three points per character up to "
              "twenty characters, ten points for each character class present, penalties for a repeated group, a "
              "predictable sequence and low variety, and a cap of ten for a password on the common list. It "
              "returns the factors that contributed so the user can see why the rating is what it is.")
    para(doc, "The log analyser counts INFO, WARNING and ERROR lines, failed logins, the busiest addresses and "
              "activity per hour, and returns counts and addresses only, never the log lines themselves. The IP "
              "validator uses the standard library ipaddress module and returns one plain-language "
              "classification in a fixed order so the most specific kind wins. The report generator produces TXT "
              "or CSV, withholds any field whose name indicates a secret, and prefixes CSV cells beginning with a "
              "formula character so a spreadsheet cannot be tricked into executing content.")

    doc.add_heading("5.5 Module 10 - The Database Layer", level=2)
    para(doc, "A new module, python/db.py, is the only file in the project that opens a connection to Oracle. It "
              "reads its configuration from environment variables, optionally supplied by a .env file, creates "
              "one pool on first use, and calls the procedures and functions the schema already defines. Because "
              "the procedures deliberately do not commit, the module commits once per call, so a failure part way "
              "through cannot leave a half-written record.")
    code(doc,
         "def save_analysis(module_name, summary, status=\"SUCCESS\", username=None):\n"
         "    module_name = _check_module(module_name)\n"
         "    if str(status).upper() not in (\"SUCCESS\", \"FAILED\"):\n"
         "        raise ValueError(\"The status must be SUCCESS or FAILED.\")\n"
         "\n"
         "    def work(cursor):\n"
         "        oracledb = driver()\n"
         "        new_id = cursor.var(oracledb.NUMBER)\n"
         "        cursor.callproc(\"insert_analysis_record\",\n"
         "                        [who, module_name, _text(summary, 500), status, new_id])\n"
         "        return int(new_id.getvalue() or 0)\n"
         "\n"
         "    return _run(work)")
    para(doc, "Reads use the functions the schema defines. The newest analyses come from the REF CURSOR function, "
              "which is called through an anonymous block because a function that returns a cursor cannot be "
              "selected from SQL directly:")
    code(doc,
         "ref_cursor = cursor.var(oracledb.CURSOR)\n"
         "cursor.execute(\"BEGIN :1 := get_recent_history(:2); END;\", [ref_cursor, limit])\n"
         "rows = ref_cursor.getvalue()")

    doc.add_heading("5.6 Database Objects", level=2)
    table(doc,
          ["Object", "Type", "Purpose"],
          [["users", "Table", "One row per application user name, unique and format-checked"],
           ["analysis_history", "Table", "One row per analysis, status limited to SUCCESS or FAILED"],
           ["file_integrity_records", "Table", "One row per file check, hash columns validated as 64 hexadecimal characters"],
           ["security_assessments", "Table", "One row per assessment, score 0 to 100"],
           ["activity_logs, reports, audit_log", "Table", "Activity trail, report metadata and row-level audit"],
           ["get_or_create_user, get_user_id", "Function", "User lookup and create-on-demand"],
           ["get_total_analyses, get_total_file_verifications, get_average_assessment_score", "Function", "The Overview numbers"],
           ["get_recent_history", "Function", "Returns the newest analyses as a SYS_REFCURSOR"],
           ["insert_analysis_record, insert_file_integrity_record, insert_security_assessment, insert_report_record", "Procedure", "Saving, with the validation rules inside the database"],
           ["update_assessment_result, generate_user_summary", "Procedure", "Update through a procedure, and a summary built with an explicit cursor"],
           ["trg_users_audit, trg_assessments_audit, trg_assessments_timestamp, trg_files_audit", "Trigger", "Audit rows and the updated_at column"]],
          widths=[6.0, 2.4, 7.4])

    doc.add_heading("5.7 Verification and Test Evidence", level=2)
    table(doc,
          ["Check", "Result"],
          [["C++ build with -Wall -Wextra", "Succeeds with no warnings"],
           ["C++ module checks", "33 passed, including four published SHA-256 vectors"],
           ["Python tests", "50 tests, 49 run and 1 skipped unless a live database is set"],
           ["Every API endpoint called against the running stack", "13 endpoints, results as expected"],
           ["Analyses saved to Oracle", "Each written through insert_analysis_record and its companions"],
           ["Database switched off", "All nine tools answer with persisted: false, read endpoints explain themselves"],
           ["Python service stopped", "Health reports it, four Python tools answer 503, five C++ tools keep working"]],
          widths=[7.0, 8.8])
    table(doc,
          ["Input", "Expected SHA-256 (FIPS 180-4)", "Result"],
          [["empty string", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "match"],
           ["\"abc\"", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "match"],
           ["448-bit two-block message", "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1", "match"],
           ["one million bytes of \"a\"", "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0", "match"]],
          widths=[4.4, 10.0, 1.4])

    # ---- 6 Key functionalities ----
    doc.add_heading("6. Key Functionalities", level=1)
    table(doc,
          ["Module", "Language", "Function", "Endpoint"],
          [["1. Identifier Analyzer", "C++", "Digits, letters and symbols, plus the most frequent digit", "POST /api/analyze"],
           ["2. Score Calculator", "C++", "Count, sum, minimum, maximum and average of 1 to 10 scores", "POST /api/calculate"],
           ["3. Pointer Operations", "C++", "Sum and absolute difference through pointers", "POST /api/pointers"],
           ["4. User Assessment", "C++", "Five scores against a baseline, with a board of users", "POST /api/assessment"],
           ["5. File Integrity Lab", "C++", "SHA-256 of an uploaded file and comparison with a reference", "POST /api/file-hash"],
           ["6. Password Analyzer", "Python", "Rating out of 100, contributing factors and advice", "POST /api/password-strength"],
           ["7. Log Analyzer", "Python", "INFO, WARNING and ERROR counts, failed logins, busiest addresses", "POST /api/log-analysis"],
           ["8. IP Validator", "Python", "IPv4 and IPv6 validation and classification", "POST /api/ip-validation"],
           ["9. Report Generator", "Python", "TXT or CSV report of the latest analysis of a chosen type", "POST /api/report"],
           ["10. Activity History", "Python and Oracle", "Newest analyses read through the REF CURSOR function", "GET /api/history"],
           ["11. Overview numbers", "Python and Oracle", "Analyses, files, assessments and reports", "GET /api/dashboard"],
           ["12. Generated reports", "Python and Oracle", "Newest stored report records", "GET /api/reports"]],
          widths=[3.8, 2.6, 6.2, 3.2])
    para(doc, "Every reply from either server has the same shape, which is what lets the browser use one error "
              "handler for all nine tools, and every analysis reply carries a flag saying whether it was stored:")
    code(doc,
         '{"ok": true,  "data": { ..., "persisted": true }}\n'
         '{"ok": false, "error": "A sentence a person can read."}')

    # ---- 7 System analysis ----
    doc.add_heading("7. System Analysis & Differentiation", level=1)
    doc.add_heading("7.1 Analysis of the Starting Point", level=2)
    para(doc, "Before this phase the project already had a complete dashboard, a working C++ server for four "
              "modules, a working Python service for four more, and a complete Oracle schema. What it did not "
              "have was any connection between the application and the database. The audit that established this "
              "is summarised below.")
    table(doc,
          ["Area", "State found", "Evidence"],
          [["File Integrity Lab", "Interface present, endpoint missing", "POST /api/file-hash answered HTTP 501"],
           ["Activity History", "Interface present, endpoint missing", "GET /api/history answered HTTP 501"],
           ["Overview numbers", "Interface present, endpoint missing", "GET /api/dashboard answered HTTP 501"],
           ["Database access", "Not implemented anywhere", "No Python file imported a driver; no connection was opened"],
           ["Python environment", "Incomplete", "setup_python.bat installed Flask only, so the driver was never present"],
           ["Repository hygiene", "Missing files", "No .gitignore, so generated reports and binaries were untracked"]],
          widths=[3.8, 5.2, 6.8])
    para(doc, "The decisive evidence was in the database code itself: the comment above the function that returns "
              "the newest analyses reads \"the Python service reads it in Phase 8\". Phase 8 had never been "
              "written, so one missing layer held back four features at once.")

    doc.add_heading("7.2 Differentiation", level=2)
    table(doc,
          ["Existing alternative", "What it does", "How CyberGuard differs"],
          [["Online hash calculators", "Return a digest for a pasted string or a file", "CyberGuard also compares the digest with a reference, records the check in the database, and explains that a match proves identity and not authorship"],
           ["Password strength websites", "Return a single colour or score", "The score is returned with the factors that produced it, and the password is never stored, logged or echoed back"],
           ["Standalone log viewers", "Display the file", "CyberGuard returns counts, failed logins and repeated addresses without echoing log content"],
           ["A folder of separate scripts", "Each task solved in isolation", "One interface, one storage layer, one error model, and a history that survives a restart"],
           ["A tool that requires its database", "Fails completely when the database is down", "Every analysis still runs; the reply says it was not saved"]],
          widths=[3.6, 4.4, 7.8])

    # ---- 8 Flow chart ----
    doc.add_heading("8. Flow Chart", level=1)
    para(doc, "The flow below traces one analysis from the browser to the database and back, including the two "
              "optional components. The branch at the bottom is the reason the dashboard never presents a failed "
              "analysis when only the storage layer is missing.")
    code(doc,
         "        Start\n"
         "          |\n"
         "          v\n"
         "  Open the dashboard  -----------------> C++ server serves index.html\n"
         "          |\n"
         "          v\n"
         "  Choose a tool and submit the form\n"
         "          |\n"
         "          v\n"
         "  <Is the tool written in C++?>\n"
         "     yes |                    | no\n"
         "         v                    v\n"
         "  C++ module runs      Is the Python service running?\n"
         "  (1-5)                     no |            | yes\n"
         "         |                    v              v\n"
         "         |             503, start it     Python module runs (6-9)\n"
         "         |                                |\n"
         "         +----------------+---------------+\n"
         "                          |\n"
         "                          v\n"
         "              Result shown in the page\n"
         "                          |\n"
         "                          v\n"
         "          <Is the database reachable?>\n"
         "        no |                        | yes\n"
         "           v                        v\n"
         "  persisted: false        PL/SQL procedure called,\n"
         "  page says it was        transaction committed,\n"
         "  not saved               row visible in History\n"
         "           |                        |\n"
         "           +------------+-----------+\n"
         "                        |\n"
         "                        v\n"
         "                      Finish", size=8.5)

    # ---- 9 Output ----
    doc.add_heading("9. Output & Screenshots", level=1)
    para(doc, "The screenshots below show each view of the running system. Capture them in this order after "
              "starting run_all.bat and opening http://127.0.0.1:8080.")
    table(doc,
          ["Figure", "View to capture", "What the capture should show"],
          [["9.1", "Overview", "The status pill reading All services online, the four numbers filled in, and the recent activity table"],
           ["9.2", "Identifier Analyzer", "The sample input AB12 3C 4@4 99 with the digit table and the most frequent digits"],
           ["9.3", "Score Calculator", "Scores 72, 85, 90 with count 3, sum 247 and average 82.33"],
           ["9.4", "Pointer Operations", "Two numbers with the sum and the absolute difference"],
           ["9.5", "User Assessment", "Five scores with the total, the average and PASS"],
           ["9.6", "File Integrity Lab", "A chosen file with its SHA-256, the copy-hash button, and a MATCH result after pasting the reference hash"],
           ["9.7", "Password Strength Analyzer", "A sample password with its rating, score and the list of factors"],
           ["9.8", "Security Log Analyzer", "sample_data/sample_logs/sample.log with the entry counts and the busiest addresses"],
           ["9.9", "IP Address Validator", "192.168.1.10 classified as private, and one invalid address"],
           ["9.10", "Security Reports", "A generated report with its text preview and the download link"],
           ["9.11", "Activity History", "Rows for the analyses just run, newest first"],
           ["9.12", "Database offline", "The pill reading Database offline and a tool answering with the not-saved message"]],
          widths=[1.8, 4.2, 9.8], font_size=9.5)
    para(doc, "Insert each screenshot under this section with its figure number as the caption. Figure 9.12 is "
              "worth including: it demonstrates the design decision described in the Abstract.")

    # ---- 10 GitHub ----
    doc.add_heading("10. GitHub Upload", level=1)
    para(doc, "The complete source code, the database scripts, the tests and the documentation are published at:")
    p = doc.add_paragraph()
    r = p.add_run(REPO)
    r.bold = True
    r.font.size = Pt(12)
    table(doc,
          ["Item", "Detail"],
          [["Repository", REPO],
           ["Branch holding the completed work", "finish/phase8-database"],
           ["Commits added in this phase", "One for the database layer, the File Integrity Lab and the corrections; one for the report and the case study"],
           ["What is ignored", "Downloaded headers, the Python environment, compiled binaries, generated reports and the .env file"],
           ["How to reproduce", "Clone, run first_time_setup.bat, copy .env.example to .env, run run_all.bat"]],
          widths=[5.0, 10.8])
    para(doc, "The repository keeps the third-party headers out of version control because setup.bat downloads them, "
              "and keeps the database password out of version control because it is a secret. Both decisions are "
              "recorded in the .gitignore file.")

    # ---- 11 Conclusion ----
    doc.add_heading("11. Conclusion", level=1)
    para(doc, "CyberGuard now meets its objectives. Nine analysis tools are reachable from one dashboard, the C++ "
              "modules exercise the language features they were written to demonstrate, the Python modules show "
              "file handling, pattern matching and report generation, and the Oracle schema is used through its own "
              "procedures, functions, cursor and triggers. The application continues to work when its optional "
              "components are absent, and the system is covered by automated checks: 33 C++ checks and 50 Python "
              "tests, with the hashing implementation verified against the published SHA-256 vectors.")
    para(doc, "The most useful lesson is about boundaries. One layer, drawn once at the Python service, proved "
              "easier to test and to reason about than the same logic spread across four layers, and the phase that "
              "completed the project was small in line count but decisive in behaviour.")

    # ---- 12 Future ----
    doc.add_heading("12. Future Advancements", level=1)
    bullets(doc, [
        "Authentication, so that analysis_history records the person rather than a shared application name, with the "
        "existing users table becoming the account table.",
        "A streaming upload path, so files larger than memory can be hashed without buffering them.",
        "A dashboard chart of activity per hour, using data the log analyser already produces.",
        "Pagination on the history view, and a detail view showing the stored summary of one analysis.",
        "A continuous integration job that builds the server and runs both test suites on each push.",
        "A cross-platform build with CMake, so the project is not tied to a Windows batch file and the MSYS2 path.",
        "A portable replacement for the GCC-specific overflow built-in, so the code also builds under MSVC.",
    ])

    path = os.path.join(OUT_DIR, "PROJECT_REPORT.docx")
    doc.save(path)
    return path


# ---------------------------------------------------------------------------
# CASE STUDY  (Case-Study-Portfolio.docx format)
# ---------------------------------------------------------------------------
def build_case_study():
    doc = make_document(body_size=11, heading_colour="8A3B1E", top=2.2, bottom=2.2, left=2.5, right=2.5)
    footer_with_pages(doc, "CyberGuard  |  MCA Case Study")

    # ---- cover ----
    for _ in range(2):
        doc.add_paragraph()
    centre(doc, "CYBERGUARD", size=26, bold=True, space_after=2)
    centre(doc, "INTEGRATED CYBERSECURITY ANALYSIS AND UTILITY TOOLKIT", size=13, bold=True, space_after=2)
    centre(doc, "A C++17, PYTHON 3 AND ORACLE DATABASE PROJECT WITH A WEB DASHBOARD",
           size=11, bold=True, space_after=16)
    centre(doc, "A Case Study Report submitted in partial fulfillment of the requirements for the degree", size=11)
    centre(doc, "of", size=11)
    centre(doc, "MASTER OF COMPUTER APPLICATIONS (MCA)", size=12, bold=True, space_after=16)
    centre(doc, "Submitted By:", bold=True, space_after=2)
    centre(doc, STUDENT, size=13, bold=True, space_after=2)
    centre(doc, "UID: " + UID, space_after=2)
    centre(doc, "Semester: " + SEMESTER, space_after=14)
    centre(doc, "Under the Guidance of:", bold=True, space_after=2)
    centre(doc, GUIDE, size=13, bold=True, space_after=14)
    centre(doc, DEPARTMENT, space_after=2)
    centre(doc, UNIVERSITY, space_after=2)
    centre(doc, "Academic Year: " + ACADEMIC_YEAR, bold=True)
    doc.add_page_break()

    # ---- 1 ----
    doc.add_heading("1. Executive Summary", level=1)
    para(doc, "This case study examines CyberGuard, an educational cybersecurity toolkit that joins a web "
              "dashboard, a C++17 server, a Python analysis service and an Oracle database in one application. "
              "Nine small tools sit behind a single page: identifier analysis, score calculation, pointer "
              "operations, user assessment, file integrity, password strength, log analysis, IP validation and "
              "report generation.")
    para(doc, "The study focuses on the moment the project stopped being a collection of working parts and became "
              "a system. When the study begins, the dashboard is complete and styled, the C++ server answers for "
              "four modules, the Python service passes thirty-four tests and the Oracle schema defines seven "
              "tables, six functions, six procedures and four triggers. When it is examined, one layer is missing "
              "entirely: nothing in the application opens a connection to the database, so four features that "
              "depend on it cannot work.")
    para(doc, "The case study documents how that gap was found, why it had been invisible, the options considered, "
              "the layer that was built to close it, and the evidence that closes it. It also records the "
              "corrections that the work exposed, including a status indicator that reported success while half "
              "the tools were unreachable.")
    para(doc, "The result is a system in which persistence is an addition to an analysis and never a precondition "
              "for it: with or without a database, every tool returns an answer, and the interface states plainly "
              "whether the answer was stored.")

    # ---- 2 ----
    doc.add_heading("2. Introduction & Problem Statement", level=1)
    doc.add_heading("2.1 Background of the Study", level=2)
    para(doc, "Security work is learned through small checks that can be explained in a few sentences: how many "
              "character classes an identifier contains, how predictable a password is, how many logins failed, "
              "whether a file has changed, and whether an address is local or public. Because each check is small, "
              "they are well suited to a single teaching application.")
    para(doc, "The division of labour in CyberGuard is deliberate. C++ performs the arithmetic and the byte-level "
              "work that the syllabus requires to be demonstrated. Python performs text processing, and its "
              "standard library already contains the regular expressions, counters and address handling the "
              "analysis needs. Oracle holds the history, so that a check performed today can be read tomorrow. The "
              "browser never speaks to Oracle, and the C++ server carries no database driver.")
    doc.add_heading("2.2 Problem Statement", level=2)
    para(doc, "The study evaluates how a set of small analysis tools, written in two languages, can be assembled "
              "into one application with a single interface, a single storage layer and a consistent error model, "
              "without any part becoming too large to explain.")
    bullets(doc, [
        "A folder of separate scripts demonstrates each technique but shows nothing about how a real application "
        "is assembled, and leaves no record of what was run.",
        "An interface can look finished while the layer behind it is missing, because a styled form and a "
        "documented endpoint are not the same thing as a working feature.",
        "Unit tests that exercise each module directly cannot detect a missing connection between layers, so every "
        "test can pass while the system as a whole cannot reach its data.",
        "A dependency list that is never installed, and a data layer that is planned but not written, are both "
        "invisible until something asks them to work.",
        "A tool that requires its database in order to answer at all is unusable on a machine where the database "
        "is not running, which is the normal state of a student laptop.",
    ])
    doc.add_heading("2.3 Objectives", level=2)
    bullets(doc, [
        "Assemble the nine analysis tools behind one dashboard with one reply format and one error model.",
        "Place the database connection in exactly one module, and call the PL/SQL objects the schema already "
        "defines rather than writing equivalent SQL in the application.",
        "Keep every analysis available when the database or the Python service is missing, and make the state of "
        "each component visible in the interface.",
        "Verify the finished system with automated tests, including known-answer tests for the cryptographic work.",
        "Record the work in a way that a reader can reproduce, including the exact commands, endpoints and results.",
    ])

    # ---- 3 ----
    doc.add_heading("3. System Analysis & Modeling", level=1)
    doc.add_heading("3.1 Feasibility Study", level=2)
    para(doc, "Technical feasibility was established by building and running the complete stack on one Windows "
              "machine: MSYS2 UCRT64 GCC for the C++ server, CPython with Flask for the analysis service, "
              "python-oracledb in thin mode for the driver, and Oracle Database Free for the schema. Every "
              "component is free, so economic feasibility is trivial. Operational feasibility is limited to a "
              "single-user learning environment on one computer, which matches the scope of an academic project.")
    doc.add_heading("3.2 Functional Requirements", level=2)
    table(doc,
          ["ID", "Requirement", "Description"],
          [["FR1", "Identifier analysis", "Count digits, letters and symbols in up to 1000 characters and report the most frequent digit"],
           ["FR2", "Score statistics", "For one to ten whole numbers, report the count, sum, minimum, maximum and average"],
           ["FR3", "Pointer operations", "Compute a sum and an absolute difference by passing values by address"],
           ["FR4", "User assessment", "Assess five scores from 0 to 100 against a baseline and keep a board of users"],
           ["FR5", "File integrity", "Compute the SHA-256 of a file up to 25 MB and compare it with an optional reference hash"],
           ["FR6", "Password rating", "Rate a sample password out of 100 and return the factors and the advice"],
           ["FR7", "Log analysis", "Count levels, failed logins, repeated addresses and activity per hour for a log up to 5 MB"],
           ["FR8", "IP validation", "Validate an IPv4 or IPv6 address and classify it"],
           ["FR9", "Report generation", "Produce a TXT or CSV report for the most recent analysis of a chosen type"],
           ["FR10", "Persistence", "Store each analysis, file check, assessment and report when the database is reachable, and say when it is not"],
           ["FR11", "Dashboard numbers", "Show the four summary numbers and the recent activity read from the database"],
           ["FR12", "Input validation", "Reject unusable input with a sentence that explains the problem, before any work is attempted"]],
          widths=[1.4, 3.6, 10.8])
    para(doc, "Two requirements are non-functional but decisive: the interface must remain usable when an "
              "optional component is unavailable, and a request body must never be written to a log, because "
              "request bodies may hold a sample password.")

    # ---- 4 ----
    doc.add_heading("4. Proposed Technical Solution & Architecture", level=1)
    doc.add_heading("4.1 Technology Stack", level=2)
    table(doc,
          ["Technology", "Role & Responsibility"],
          [["HTML5 and CSS3", "The five-view dashboard, its dark palette, its card grid and its responsive behaviour"],
           ["Vanilla JavaScript (ES6)", "Event handling, form validation, fetch calls, table rendering; no framework and no build step"],
           ["C++17", "The server and modules 1 to 5: arrays, strings, loops, variadic functions, pointers, classes and byte-level hashing"],
           ["cpp-httplib 0.18.7", "The HTTP server and the outbound client used to reach the Python service"],
           ["JSON for Modern C++ 3.11.3", "Parsing and serialising every request and reply"],
           ["Python 3 standard library", "re, collections, csv and ipaddress: the text analysis and report generation"],
           ["Flask 3.1", "The HTTP layer of the Python service, reached only from the C++ server"],
           ["python-oracledb 26.0.1", "The Oracle driver in thin mode, so no client libraries are installed"],
           ["Oracle Database Free 23ai", "Seven tables, six functions, six procedures and four triggers holding all history"],
           ["MSYS2 UCRT64 GCC", "One compiler invocation builds the server; no make file and no package manager"]],
          widths=[4.0, 11.8])
    doc.add_heading("4.2 Architecture and File Structure", level=2)
    code(doc,
         "Browser  (frontend/index.html, style.css, script.js)\n"
         "   |  fetch() JSON, multipart upload\n"
         "   v\n"
         "C++ server  127.0.0.1:8080        backend/server.cpp\n"
         "   modules 1-4  backend/modules/*.cpp\n"
         "   module 5     backend/modules/file_integrity.cpp\n"
         "   relays       /api/history, /api/dashboard, /api/reports\n"
         "   |  HTTP to 127.0.0.1:5001\n"
         "   v\n"
         "Python service  python/app.py\n"
         "   modules 6-9  password_analyzer.py, log_analyzer.py,\n"
         "                ip_validator.py, report_generator.py\n"
         "   module 10    db.py   <-- the only place Oracle is reached\n"
         "   |  python-oracledb, connection pool\n"
         "   v\n"
         "Oracle Database Free   database/*.sql\n"
         "   tables, functions, procedures, triggers", size=8.5)
    table(doc,
          ["Path", "Contents"],
          [["frontend/", "The dashboard: markup, styling and behaviour"],
           ["backend/server.cpp", "Routes, JSON handling, relaying to Python, error mapping"],
           ["backend/modules/", "Modules 1 to 5"],
           ["python/app.py", "Flask endpoints for modules 6 to 10"],
           ["python/db.py", "Module 10: pool, PL/SQL calls, configuration, graceful degradation"],
           ["database/", "Schema, functions, procedures, triggers, sample data, demonstration queries"],
           ["tests/", "33 C++ checks and 50 Python tests"],
           ["docs/", "This case study and the project report"]],
          widths=[4.2, 11.6])

    # ---- 5 ----
    doc.add_heading("5. Implementation Details", level=1)
    doc.add_heading("5.1 The Missing Layer: One Module Owns the Database", level=2)
    para(doc, "The whole gap was closed by one module. python/db.py reads its configuration from the environment, "
              "optionally supplied by a .env file, creates a single connection pool on first use, and calls the "
              "procedures and functions the schema defines. Nothing in the application writes SQL that duplicates "
              "a rule the database already enforces, so the allowed status values, the sixty-four character hash "
              "rule and the report-code uniqueness cannot be bypassed by another client.")
    code(doc,
         "def save_analysis(module_name, summary, status=\"SUCCESS\", username=None):\n"
         "    module_name = _check_module(module_name)\n"
         "    if str(status).upper() not in (\"SUCCESS\", \"FAILED\"):\n"
         "        raise ValueError(\"The status must be SUCCESS or FAILED.\")\n"
         "\n"
         "    def work(cursor):\n"
         "        oracledb = driver()\n"
         "        new_id = cursor.var(oracledb.NUMBER)\n"
         "        cursor.callproc(\"insert_analysis_record\",\n"
         "                        [who, module_name, _text(summary, 500), status, new_id])\n"
         "        return int(new_id.getvalue() or 0)\n"
         "\n"
         "    return _run(work)")
    para(doc, "Reads take the same route. The newest analyses come from a function that returns a REF CURSOR, "
              "which has to be called through an anonymous block because such a function cannot be selected from "
              "SQL directly:")
    code(doc,
         "ref_cursor = cursor.var(oracledb.CURSOR)\n"
         "cursor.execute(\"BEGIN :1 := get_recent_history(:2); END;\", [ref_cursor, limit])\n"
         "rows = ref_cursor.getvalue()")
    doc.add_heading("5.2 The File Integrity Lab", level=2)
    para(doc, "The File Integrity Lab was the largest missing feature: the view, the report type and the database "
              "table all existed, and the endpoint answered 501. It is now a C++ module implementing SHA-256 "
              "directly, feeding data to the hasher block by block so that a memory buffer and a file on disk use "
              "the same code. The reference hash is validated as sixty-four hexadecimal characters before any "
              "comparison, and the outcome is one of the three values the database accepts.")
    doc.add_heading("5.3 Honest Failure States", level=2)
    para(doc, "The status indicator previously reported that the server was online whenever the C++ server "
              "answered, even when the Python service was down and four tools could not work. It now reports the "
              "Python service and the database separately, and the message under the Overview numbers explains "
              "why they are empty instead of showing zeros as if they were real.")
    code(doc,
         "async function health() {\n"
         "  const p = $(\"#pill\");\n"
         "  try {\n"
         "    const d = (await api(\"/api/health\")).data;\n"
         "    if (!d.python)   { p.textContent = \"Python service offline\"; p.className = \"pill down\"; return; }\n"
         "    if (!d.database) { p.textContent = \"Database offline\";       p.className = \"pill down\"; return; }\n"
         "    p.textContent = \"All services online\"; p.className = \"pill up\";\n"
         "  } catch { p.textContent = \"Server offline\"; p.className = \"pill down\"; }\n"
         "}")
    doc.add_heading("5.4 Recording a Connection Failure Without Blocking the Page", level=2)
    para(doc, "Discovering that no database is listening costs a few seconds, and the dashboard asks for the "
              "connection state on every load. Re-testing a dead host each time makes the page feel broken, so a "
              "failure is remembered for five seconds: the reply becomes immediate during an outage, while a "
              "database that starts is still noticed within seconds.")
    code(doc,
         "if time.monotonic() < _retry_after:\n"
         "    raise DatabaseOffline(\"Oracle is not reachable (%s).\" % _last_error)\n"
         "...\n"
         "except Exception as error:\n"
         "    _last_error = \"%s: %s\" % (type(error).__name__, error)\n"
         "    _retry_after = time.monotonic() + ERROR_BACKOFF   # 5 seconds\n"
         "    raise DatabaseOffline(\"Oracle is not reachable (%s).\" % _last_error)")
    doc.add_heading("5.5 Configuration, Secrets and Repository Hygiene", level=2)
    para(doc, "The database password lives in .env, which is excluded from version control, and .env.example "
              "documents every value without containing a secret. The Python environment now installs the whole "
              "requirements file rather than Flask alone, so the dependency list and the installer can no longer "
              "drift apart. A .gitignore excludes the downloaded headers, the virtual environment, compiled "
              "binaries and generated reports.")

    # ---- 6 ----
    doc.add_heading("6. Testing & Results Analysis", level=1)
    doc.add_heading("6.1 Test Execution Matrix", level=2)
    table(doc,
          ["ID", "Test Scenario", "Expected Result", "Status"],
          [["T1", "Build the C++ server with -Wall -Wextra", "Compiles with no warnings", "Pass"],
           ["T2", "Run the C++ module checks", "All checks pass", "Pass - 33 of 33"],
           ["T3", "Run the Python test suite", "All tests pass, live-database test skipped unless configured", "Pass - 49 run, 1 skipped"],
           ["T4", "Hash the empty string and three published messages", "Digests equal the FIPS 180-4 values", "Pass - 4 of 4"],
           ["T5", "Hash a real 1,382-byte file in C++ and in Python", "Both implementations return the same digest", "Pass"],
           ["T6", "Submit a reference hash that is not 64 hexadecimal characters", "HTTP 400 before any comparison", "Pass"],
           ["T7", "Submit a file with a matching reference hash", "Verification is MATCH and the check is offered for storage", "Pass"],
           ["T8", "Submit a file with a wrong reference hash", "Verification is MISMATCH", "Pass"],
           ["T9", "Run every analysis with the database switched off", "HTTP 200 with persisted false", "Pass"],
           ["T10", "Read history, dashboard and reports with the database switched off", "HTTP 503 with a message a person can act on", "Pass"],
           ["T11", "Enable the database with no listener running", "Health reports the driver error; analyses still answer", "Pass"],
           ["T12", "Stop the Python service and use the tools", "Health reports it, the four Python tools answer 503, the five C++ tools keep working", "Pass"],
           ["T13", "Request an unknown API address", "HTTP 404 in the same JSON error shape", "Pass"],
           ["T14", "Run the complete stack and call all thirteen endpoints", "Every reply as specified in the report", "Pass"]],
          widths=[1.2, 5.6, 6.6, 3.4], font_size=9.5)
    doc.add_heading("6.2 Observations", level=2)
    bullets(doc, [
        "Every unit test passed while the application could not reach its database. The tests measured components, "
        "not connections, and a missing layer is invisible to a component test.",
        "Three of the four remaining features had a styled view, a documented endpoint and a database table, and "
        "none of them worked. Interface completeness is not feature completeness.",
        "The system degraded so politely that the gap survived: it said the database was not connected instead of "
        "failing, so nothing looked broken enough to investigate.",
        "One unwritten layer held back four features at once, which is the cost of deferring a shared dependency.",
        "The database proved to be a participant in validation rather than a passive store: calling the procedures "
        "meant the hash length, the status values and the report-code uniqueness could not be bypassed.",
        "Two defects came from assuming a library's API rather than reading it: the driver's parameter object did "
        "not allow the attributes to be assigned, and the connect string could not be passed to its constructor.",
        "Hashing had to be verified with known answers. Four published vectors and a cross-check against an "
        "independent library gave more confidence than any amount of reading the code.",
        "Performance work was mostly about failure, not success: the healthy path was tens of milliseconds, while "
        "an absent database initially cost several seconds on each page load.",
    ])
    para(doc, "Two negative results are as important as the positive ones. With the database switched off, all "
              "nine tools returned an answer and flagged it as unsaved, and the three read endpoints returned a "
              "message a user can act on. With the Python service stopped, the health reply changed to report it "
              "and the five C++ tools continued to work. The system fails in ways that can be explained.")

    # ---- 7 ----
    doc.add_heading("7. Conclusion & Future Enhancements", level=1)
    doc.add_heading("7.1 Conclusion", level=2)
    para(doc, "CyberGuard is complete in the sense that every view has a working endpoint, every analysis can be "
              "stored, and stored results return to the interface. The work that closed the gap was small in line "
              "count: one new Python module, one new C++ module with its header, six endpoints, one new test file "
              "and a handful of corrections. What makes it worth documenting is that the gap was invisible from "
              "the interface, undetected by the tests and reported politely by the system itself.")
    para(doc, "The project also demonstrates a pattern worth keeping: a boundary drawn once, at the Python "
              "service, is easier to test and to reason about than the same logic distributed across four layers.")
    doc.add_heading("7.2 Future Scope", level=2)
    bullets(doc, [
        "Authentication, so the history records the person rather than a shared application name, using the "
        "existing users table as the account table.",
        "A streaming upload path, so files larger than memory can be hashed without buffering them.",
        "Pagination and a detail view on the History page, so one stored analysis can be examined in full.",
        "A chart of activity per hour, drawn from the data the log analyser already produces.",
        "A continuous integration job that builds the server and runs both suites on each push, so a missing "
        "connection can never again survive a green test run.",
        "A CMake build, so the project is not tied to one Windows batch file and one MSYS2 path.",
        "A portable overflow helper in place of the GCC-specific built-in, so the code also builds under MSVC.",
    ])

    # ---- 8 ----
    doc.add_heading("8. Github Upload/Link", level=1)
    para(doc, "The complete source code, the database scripts, the tests and the documentation are published at:")
    p = doc.add_paragraph()
    r = p.add_run(REPO)
    r.bold = True
    r.font.size = Pt(12)
    table(doc,
          ["Item", "Detail"],
          [["Repository", REPO],
           ["Branch with the completed work", "finish/phase8-database"],
           ["Files added in this phase", "python/db.py, backend/modules/file_integrity.h, backend/modules/file_integrity.cpp, tests/python_tests/test_db.py, .gitignore, .env.example"],
           ["Files changed in this phase", "backend/server.cpp, python/app.py, frontend/script.js, setup_python.bat, build.bat, requirements.txt, README.md, the C++ test suite"],
           ["Ignored on purpose", "backend/vendor headers, .venv, __pycache__, compiled binaries, reports_output, .env"],
           ["Reproduction", "Clone, run first_time_setup.bat, copy .env.example to .env, run run_all.bat, open 127.0.0.1:8080"]],
          widths=[4.4, 11.4])

    # ---- 9 ----
    doc.add_heading("9. References", level=1)
    bullets(doc, [
        "ISO/IEC 14882:2017, Programming languages - C++.",
        "National Institute of Standards and Technology, FIPS PUB 180-4, Secure Hash Standard, 2015.",
        "National Institute of Standards and Technology, SP 800-63B, Digital Identity Guidelines: Authentication "
        "and Lifecycle Management, 2017.",
        "Oracle, Oracle Database PL/SQL Language Reference, 23ai.",
        "Oracle, python-oracledb Documentation, release 26.",
        "Pallets Projects, Flask Documentation, version 3.1.",
        "Y. Hirose, cpp-httplib, version 0.18.7, MIT licence.",
        "N. Lohmann, JSON for Modern C++, version 3.11.3, MIT licence.",
        "Python Software Foundation, The Python Standard Library: re, collections, csv, ipaddress.",
    ])

    path = os.path.join(OUT_DIR, "CASE_STUDY.docx")
    doc.save(path)
    return path


if __name__ == "__main__":
    for built in (build_report(), build_case_study()):
        print("written:", os.path.basename(built), os.path.getsize(built), "bytes")
