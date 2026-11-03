// CyberGuard HTTP server: serves the frontend and the JSON API for the C++ modules.
#include "server.h"

#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <iostream>
#include <map>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "httplib.h"
#include "json.hpp"
#include "modules/file_integrity.h"
#include "modules/identifier_analyzer.h"
#include "modules/pointer_operations.h"
#include "modules/score_calculator.h"
#include "modules/user_assessment.h"

using json = nlohmann::json;

namespace {

constexpr std::size_t kMaxJsonBody = 100 * 1024;          // JSON requests: 100 KB
constexpr std::size_t kMaxUpload = 26 * 1024 * 1024;      // room for the 25 MB file limit (Phase 3B)
constexpr std::size_t kMaxFileBytes = 25 * 1024 * 1024;   // Module 5: the documented file limit

AssessmentBoard g_board;       // assessments kept in memory while the server runs
std::mutex g_boardMutex;       // the server handles requests on several threads

const char* kPythonHost = "127.0.0.1";                  // the Python service (this computer only)
constexpr int kPythonPort = 5001;
constexpr std::size_t kMaxLogBody = 6 * 1024 * 1024;    // a 5 MB log plus JSON overhead

// The latest result of each analysis type: (input summary, results). Used to build reports.
std::map<std::string, std::pair<json, json>> g_lastResults;
std::mutex g_lastMutex;

double round2(double v) { return std::round(v * 100.0) / 100.0; }

// ---- Response helpers: every reply is {"ok":true,"data":...} or {"ok":false,"error":"..."} ----
// dump(..., replace) swaps invalid UTF-8 for a placeholder instead of throwing,
// so a file name or log line pasted from another encoding can never break a reply.
std::string dump(const json& value) {
    return value.dump(-1, ' ', false, json::error_handler_t::replace);
}
void sendOk(httplib::Response& res, const json& data) {
    res.status = 200;
    res.set_content(dump(json{{"ok", true}, {"data", data}}), "application/json");
}
void sendError(httplib::Response& res, int status, const std::string& message) {
    res.status = status;
    res.set_content(dump(json{{"ok", false}, {"error", message}}), "application/json");
}

std::string lowerCase(std::string s) {
    for (char& c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

// Removes leading and trailing spaces/tabs/newlines.
std::string trimmed(const std::string& text) {
    std::size_t first = 0, last = text.size();
    while (first < last && std::isspace(static_cast<unsigned char>(text[first]))) ++first;
    while (last > first && std::isspace(static_cast<unsigned char>(text[last - 1]))) --last;
    return text.substr(first, last - first);
}

void rememberResult(const std::string& type, const json& inputSummary, const json& results) {
    std::lock_guard<std::mutex> lock(g_lastMutex);
    g_lastResults[lowerCase(type)] = std::make_pair(inputSummary, results);
}

// ---- Input helpers ----
bool toInt(const json& v, int& out) {
    if (!v.is_number_integer()) return false;
    if (v.is_number_unsigned()) {
        unsigned long long u = v.get<unsigned long long>();
        if (u > static_cast<unsigned long long>(INT_MAX)) return false;
        out = static_cast<int>(u);
        return true;
    }
    long long x = v.get<long long>();
    if (x < INT_MIN || x > INT_MAX) return false;
    out = static_cast<int>(x);
    return true;
}

int intField(const json& b, const std::string& key, const std::string& label) {
    int x = 0;
    if (!b.contains(key) || !toInt(b[key], x))
        throw std::invalid_argument(label + " must be a whole number between -2147483648 and 2147483647.");
    return x;
}

std::vector<int> intList(const json& b, const std::string& key, std::size_t minN, std::size_t maxN) {
    if (!b.contains(key) || !b[key].is_array())
        throw std::invalid_argument("'" + key + "' must be a list of numbers.");
    const json& arr = b[key];
    if (arr.size() < minN || arr.size() > maxN)
        throw std::invalid_argument("'" + key + "' must contain " + std::to_string(minN) + " to " +
                                    std::to_string(maxN) + " numbers.");
    std::vector<int> out;
    for (const auto& item : arr) {
        int x = 0;
        if (!toInt(item, x)) throw std::invalid_argument("Every value in '" + key + "' must be a whole number.");
        out.push_back(x);
    }
    return out;
}

std::string stringField(const json& b, const std::string& key) {
    if (!b.contains(key) || !b[key].is_string())
        throw std::invalid_argument("'" + key + "' must be text.");
    return b[key].get<std::string>();
}

// ---- API handlers: each takes the request JSON and returns the "data" JSON ----
json handleAnalyze(const json& b) {
    std::string text = stringField(b, "text");
    if (text.empty() || text.size() > 1000) throw std::invalid_argument("Text must be 1 to 1000 characters.");
    IdentifierResult r = analyzeIdentifier(text);
    json freq = json::object();
    for (int d = 0; d < 10; ++d) freq[std::to_string(d)] = r.digitFrequency[d];
    json data = {{"digit_frequency", freq},       {"total_digits", r.totalDigits},
                 {"total_letters", r.totalLetters}, {"total_other_characters", r.totalOthers},
                 {"max_digit_frequency", r.maxFrequency}, {"most_frequent_digits", r.mostFrequentDigits}};
    rememberResult("Identifier", {{"characters", text.size()}}, data);
    return data;
}

json handleCalculate(const json& b) {
    ScoreResult r = calculateScores(intList(b, "scores", 1, 10));
    json data = {{"count", r.count}, {"sum", r.sum}, {"minimum", r.minimum},
                 {"maximum", r.maximum}, {"average", round2(r.average)}};
    rememberResult("Score", {{"count", r.count}}, data);
    return data;
}

json handlePointers(const json& b) {
    PointerResult r = runPointerOperations(intField(b, "a", "First number"), intField(b, "b", "Second number"));
    json data = {{"first_value", r.first}, {"second_value", r.second},
                 {"sum", r.sum}, {"absolute_difference", r.absoluteDifference}};
    rememberResult("Pointer", {{"first_value", r.first}, {"second_value", r.second}}, data);
    return data;
}

json handleAssessment(const json& b) {
    UserAssessment user(stringField(b, "user"), intList(b, "scores", 5, 5));
    int baseline = intField(b, "baseline", "Baseline");
    if (baseline < 0 || baseline > 100) throw std::invalid_argument("Baseline must be between 0 and 100.");
    AssessmentSummary s;
    {
        std::lock_guard<std::mutex> lock(g_boardMutex);
        g_board.add(user);
        s = g_board.summarize(baseline);
    }
    json data = {{"user", user.name()},
                 {"scores", std::vector<int>(user.scores().begin(), user.scores().end())},
                 {"total", user.total()}, {"average", round2(user.average())},
                 {"result", user.result(baseline)}, {"baseline", baseline},
                 {"users_assessed", s.users}, {"users_at_or_above_baseline", s.atOrAboveBaseline},
                 {"highest_average", round2(s.highestAverage)}, {"highest_user", s.highestUser},
                 {"lowest_average", round2(s.lowestAverage)}, {"lowest_user", s.lowestUser}};
    rememberResult("Assessment", {{"user", user.name()}}, data);
    return data;
}

// ---- Module 5: file integrity ----
// Declared here because the reply is reported to Python further down the file.
bool postToPython(const std::string& path, const json& payload, json& reply);

// Hash an uploaded file in C++ and compare it with an optional reference hash.
// The check is then offered to the Python service, which calls
// insert_file_integrity_record() so the result is stored in Oracle.
json handleFileHash(const httplib::Request& req) {
    if (!req.has_file("file")) throw std::invalid_argument("Choose a file first.");
    const httplib::MultipartFormData& upload = req.get_file_value("file");
    if (upload.content.size() > kMaxFileBytes)
        throw std::invalid_argument("That file is larger than 25 MB.");

    std::string reference;
    if (req.has_file("reference"))
        reference = lowerCase(trimmed(req.get_file_value("reference").content));

    const std::string digest = sha256Hex(upload.content);
    const std::string verification = verifyHash(digest, reference);   // throws on a bad reference

    json data = {{"filename", upload.filename},
                 {"size", static_cast<unsigned long long>(upload.content.size())},
                 {"sha256", digest},
                 {"reference", reference.empty() ? json(nullptr) : json(reference)},
                 {"verification", verification}};

    json stored;
    if (postToPython("/api/file-check",
                     {{"filename", upload.filename}, {"size", data["size"]},
                      {"sha256", digest}, {"reference", data["reference"]}},
                     stored)) {
        if (stored.value("persisted", false)) data["persisted"] = true;
    }
    return data;
}
// ---- Recording and relaying ----
// The C++ modules finish their work first. Only then is the result handed to the
// Python service, which is the single part of CyberGuard that talks to Oracle.
// If that service (or the database) is unavailable the analysis is still a
// success: the reply simply carries "persisted": false and the page says so.
bool postToPython(const std::string& path, const json& payload, json& reply) {
    httplib::Client client(kPythonHost, kPythonPort);
    client.set_connection_timeout(2);
    client.set_read_timeout(5);
    auto answer = client.Post(path, dump(payload), "application/json");
    if (!answer || answer->status != 200) return false;
    json parsed = json::parse(answer->body, nullptr, false);
    if (!parsed.is_object() || !parsed.value("ok", false) || !parsed.contains("data")) return false;
    reply = parsed["data"];
    return true;
}

bool getFromPython(const std::string& target, json& reply) {
    httplib::Client client(kPythonHost, kPythonPort);
    client.set_connection_timeout(2);
    client.set_read_timeout(15);
    auto answer = client.Get(target);
    if (!answer || answer->status != 200) return false;
    json parsed = json::parse(answer->body, nullptr, false);
    if (!parsed.is_object() || !parsed.value("ok", false) || !parsed.contains("data")) return false;
    reply = parsed["data"];
    return true;
}

// Relays a GET to Python and passes the reply through untouched, so the Python
// error message ("the database is not connected yet") reaches the page as-is.
void relayGet(const std::string& target, httplib::Response& res) {
    httplib::Client client(kPythonHost, kPythonPort);
    client.set_connection_timeout(2);
    client.set_read_timeout(15);
    auto answer = client.Get(target);
    if (!answer) return sendError(res, 503, "The Python service is not running. Start it with run_all.bat.");
    res.status = answer->status;
    res.set_content(answer->body, "application/json");
}

// One line for analysis_history.result_summary (VARCHAR2(500) in the schema).
std::string dbSummary(const std::string& module, const json& d) {
    std::ostringstream out;
    if (module == "Identifier")
        out << d.value("total_digits", 0) << " digits, " << d.value("total_letters", 0)
            << " letters, " << d.value("total_other_characters", 0) << " other";
    else if (module == "Score")
        out << "count " << d.value("count", 0) << ", sum " << d.value("sum", 0)
            << ", average " << d.value("average", 0.0);
    else if (module == "Pointer")
        out << "sum " << d.value("sum", 0) << ", absolute difference " << d.value("absolute_difference", 0);
    else if (module == "Assessment")
        out << d.value("user", std::string("?")) << ": total " << d.value("total", 0)
            << ", average " << d.value("average", 0.0) << ", " << d.value("result", std::string(""));
    else if (module == "File integrity")
        out << d.value("verification", std::string("NO REFERENCE GIVEN")) << ", "
            << d.value("filename", std::string("(file)")) << " (" << d.value("size", 0) << " bytes)";
    return out.str();
}

bool recordResult(const std::string& module, const json& data) {
    json reply;
    if (!postToPython("/api/record", {{"module", module}, {"summary", dbSummary(module, data)}}, reply))
        return false;
    return reply.value("persisted", false);
}

// Reads the JSON body, runs the handler, saves the result when it can, and turns
// exceptions into clean error replies.
template <typename Handler, typename After>
void serveJson(const httplib::Request& req, httplib::Response& res, const std::string& module,
               Handler handler, After after) {
    if (req.body.size() > kMaxJsonBody) return sendError(res, 413, "The request is too large.");
    json body = json::parse(req.body, nullptr, false);       // false = do not throw on bad JSON
    if (body.is_discarded() || !body.is_object())
        return sendError(res, 400, "The request body must be a JSON object.");
    try {
        json data = handler(body);
        after(data);                                        // extra saving specific to one module
        const bool recorded = recordResult(module, data);
        data["persisted"] = recorded || data.value("persisted", false);
        sendOk(res, data);
    } catch (const std::invalid_argument& e) {
        sendError(res, 400, e.what());
    } catch (const std::overflow_error& e) {
        sendError(res, 400, e.what());
    } catch (const std::exception&) {
        sendError(res, 500, "Internal server error.");
    }
}

template <typename Handler>
void serveJson(const httplib::Request& req, httplib::Response& res, const std::string& module,
               Handler handler) {
    serveJson(req, res, module, handler, [](json&) {});
}

// ---- Python gateway ----
// Sends a JSON body to the Python service and relays its reply unchanged.
// Returns false (after sending a 503 reply) if the Python service cannot be reached.
bool callPython(const std::string& path, const std::string& body, httplib::Response& res, json& reply) {
    httplib::Client client(kPythonHost, kPythonPort);
    client.set_connection_timeout(2);
    client.set_read_timeout(15);
    auto answer = client.Post(path, body, "application/json");
    if (!answer) {
        sendError(res, 503, "The Python service is not running. Start it with run_all.bat.");
        return false;
    }
    res.status = answer->status;
    res.set_content(answer->body, "application/json");
    reply = json::parse(answer->body, nullptr, false);
    return true;
}

std::string shortText(const json& v) { return v.is_string() ? v.get<std::string>().substr(0, 100) : ""; }

// Forwards a request to Python. On success it keeps a SHORT summary (never the password
// or the log text) together with the results, so a report can be created later.
void forwardToPython(const httplib::Request& req, httplib::Response& res, const std::string& path,
                     std::size_t maxBody, const std::string& type) {
    if (req.body.size() > maxBody) return sendError(res, 413, "The request is too large.");
    json body = json::parse(req.body, nullptr, false);
    if (body.is_discarded() || !body.is_object())
        return sendError(res, 400, "The request body must be a JSON object.");
    json reply;
    if (!callPython(path, req.body, res, reply)) return;
    if (res.status != 200 || !reply.is_object() || !reply.value("ok", false)) return;

    json summary = json::object();
    if (type == "Password" && body.contains("password") && body["password"].is_string())
        summary["length"] = body["password"].get<std::string>().size();
    else if (type == "Log")
        summary = {{"filename", body.contains("filename") ? shortText(body["filename"]) : ""},
                   {"characters", body.contains("content") && body["content"].is_string() ? body["content"].get<std::string>().size() : 0}};
    else if (type == "IP address")
        summary["input"] = body.contains("address") ? shortText(body["address"]) : "";
    rememberResult(type, summary, reply["data"]);
}

// The report form sends only {type, format}. The latest result of that type is attached here.
void handleReport(const httplib::Request& req, httplib::Response& res) {
    if (req.body.size() > kMaxJsonBody) return sendError(res, 413, "The request is too large.");
    json b = json::parse(req.body, nullptr, false);
    if (b.is_discarded() || !b.is_object()) return sendError(res, 400, "The request body must be a JSON object.");
    try {
        std::string type = stringField(b, "type"), format = stringField(b, "format");
        std::pair<json, json> last;
        {
            std::lock_guard<std::mutex> lock(g_lastMutex);
            auto it = g_lastResults.find(lowerCase(type));
            if (it == g_lastResults.end())
                return sendError(res, 400, "Run the " + type + " tool first, then create its report.");
            last = it->second;
        }
        json payload = {{"analysis_type", type}, {"input_summary", last.first},
                        {"results", last.second}, {"format", format}};
        json reply;
        callPython("/api/report", payload.dump(), res, reply);
    } catch (const std::invalid_argument& e) {
        sendError(res, 400, e.what());
    } catch (const std::exception&) {
        sendError(res, 500, "Internal server error.");
    }
}

}  // namespace

int runServer(const std::string& frontendDir, int port) {
    httplib::Server svr;
    svr.set_payload_max_length(kMaxUpload);

    if (!svr.set_mount_point("/", frontendDir)) {
        std::cerr << "Frontend folder not found: " << frontendDir
                  << "\nStart the program from the CyberGuard folder (use run.bat).\n";
        return 1;
    }

    svr.Get("/api/health", [](const httplib::Request&, httplib::Response& res) {
        json data = {{"status", "up"}, {"python", false}, {"database", false},
                     {"detail", "The Python service is not running, so the tools that use it are unavailable."}};
        json python;
        if (getFromPython("/api/health", python)) {      // Python is up: ask it about Oracle
            data["python"] = true;
            data["database"] = python.value("database", false);
            data["detail"] = python.value("database_detail", "");
        }
        sendOk(res, data);
    });
    svr.Post("/api/analyze", [](const httplib::Request& q, httplib::Response& r) {
        serveJson(q, r, "Identifier", handleAnalyze); });
    svr.Post("/api/calculate", [](const httplib::Request& q, httplib::Response& r) {
        serveJson(q, r, "Score", handleCalculate); });
    svr.Post("/api/pointers", [](const httplib::Request& q, httplib::Response& r) {
        serveJson(q, r, "Pointer", handlePointers); });
    svr.Post("/api/assessment", [](const httplib::Request& q, httplib::Response& r) {
        serveJson(q, r, "Assessment", handleAssessment, [](json& d) {
            // An assessment also gets its own row in security_assessments.
            json reply;
            if (postToPython("/api/assessment",
                             {{"type", "Five-score assessment"},
                              {"score", d.value("average", 0.0)},
                              {"result", d.value("result", std::string())}}, reply))
                d["persisted"] = reply.value("persisted", false);
        });
    });

    // Module 5: the file arrives as multipart data, not JSON, so it has its own route.
    svr.Post("/api/file-hash", [](const httplib::Request& req, httplib::Response& res) {
        try {
            json data = handleFileHash(req);
            const bool recorded = recordResult("File integrity", data);
            data["persisted"] = recorded || data.value("persisted", false);
            sendOk(res, data);
        } catch (const std::invalid_argument& e) {
            sendError(res, 400, e.what());
        } catch (const std::exception&) {
            sendError(res, 500, "Internal server error.");
        }
    });

    // Python service (Phase 6)
    svr.Post("/api/password-strength", [](const httplib::Request& q, httplib::Response& r) {
        forwardToPython(q, r, "/api/password-strength", kMaxJsonBody, "Password"); });
    svr.Post("/api/log-analysis", [](const httplib::Request& q, httplib::Response& r) {
        forwardToPython(q, r, "/api/log-analysis", kMaxLogBody, "Log"); });
    svr.Post("/api/ip-validation", [](const httplib::Request& q, httplib::Response& r) {
        forwardToPython(q, r, "/api/ip-validation", kMaxJsonBody, "IP address"); });
    svr.Post("/api/report", handleReport);

    // Phase 8: Oracle lives behind the Python service, so these three are relays.
    for (const char* path : {"/api/history", "/api/dashboard", "/api/reports"})
        svr.Get(path, [](const httplib::Request& req, httplib::Response& res) {
            relayGet(req.target, res); });

    svr.set_error_handler([](const httplib::Request& req, httplib::Response& res) {
        if (req.path.rfind("/api/", 0) == 0 && res.body.empty())
            sendError(res, res.status, res.status == 404 ? "Unknown API address." : "Request failed.");
    });
    svr.set_exception_handler([](const httplib::Request&, httplib::Response& res, std::exception_ptr) {
        sendError(res, 500, "Internal server error.");
    });
    // Log only method, path and status. Request bodies (which may hold passwords) are never printed.
    svr.set_logger([](const httplib::Request& req, const httplib::Response& res) {
        std::cout << req.method << " " << req.path << " -> " << res.status << "\n";
    });

    std::cout << "CyberGuard is running. Open http://127.0.0.1:" << port << " in your browser.\n"
              << "Press Ctrl+C to stop.\n";
    if (!svr.listen("127.0.0.1", port)) {     // 127.0.0.1 = this computer only
        std::cerr << "Could not start on port " << port << ". Is another program using it?\n";
        return 1;
    }
    return 0;
}
