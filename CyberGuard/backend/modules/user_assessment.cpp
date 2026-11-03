#include "user_assessment.h"

#include <algorithm>
#include <numeric>
#include <stdexcept>
#include <utility>

UserAssessment::UserAssessment(std::string name, const std::vector<int>& scores)
    : name_(std::move(name)) {
    if (name_.empty() || name_.size() > 40)
        throw std::invalid_argument("User name must be 1 to 40 characters.");
    for (unsigned char c : name_)
        if (c < 0x20) throw std::invalid_argument("User name contains invalid characters.");
    if (scores.size() != kScoreCount)
        throw std::invalid_argument("Exactly 5 scores are required.");
    for (std::size_t i = 0; i < kScoreCount; ++i) {
        if (scores[i] < 0 || scores[i] > 100)
            throw std::invalid_argument("Each score must be between 0 and 100.");
        scores_[i] = scores[i];
    }
}

int UserAssessment::total() const {
    return std::accumulate(scores_.begin(), scores_.end(), 0);
}

double UserAssessment::average() const {
    return static_cast<double>(total()) / kScoreCount;
}

std::string UserAssessment::result(double baseline) const {
    return average() >= baseline ? "PASS" : "BELOW BASELINE";
}

void AssessmentBoard::add(const UserAssessment& assessment) {
    auto same = std::find_if(list_.begin(), list_.end(),
                             [&](const UserAssessment& u) { return u.name() == assessment.name(); });
    if (same != list_.end()) { *same = assessment; return; }
    if (list_.size() >= kMaxUsers) list_.erase(list_.begin());   // drop the oldest
    list_.push_back(assessment);
}

AssessmentSummary AssessmentBoard::summarize(double baseline) const {
    if (list_.empty()) throw std::logic_error("No assessments recorded.");
    AssessmentSummary s;
    s.baseline = baseline;
    s.users = static_cast<int>(list_.size());
    s.highestUser = s.lowestUser = list_[0].name();
    s.highestAverage = s.lowestAverage = list_[0].average();
    for (const auto& u : list_) {
        double avg = u.average();
        if (avg >= baseline) s.atOrAboveBaseline++;
        if (avg > s.highestAverage) { s.highestAverage = avg; s.highestUser = u.name(); }
        if (avg < s.lowestAverage)  { s.lowestAverage = avg;  s.lowestUser = u.name(); }
    }
    return s;
}
