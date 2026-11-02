// Module 4: User Assessment (classes, constructors, encapsulation, vectors)
#ifndef USER_ASSESSMENT_H
#define USER_ASSESSMENT_H
#include <array>
#include <cstddef>
#include <string>
#include <vector>

class UserAssessment {
public:
    static constexpr std::size_t kScoreCount = 5;

    // Throws std::invalid_argument for a bad name, a wrong score count or a score outside 0..100.
    UserAssessment(std::string name, const std::vector<int>& scores);

    const std::string& name() const { return name_; }
    const std::array<int, kScoreCount>& scores() const { return scores_; }
    int total() const;
    double average() const;
    std::string result(double baseline) const;   // "PASS" or "BELOW BASELINE"

private:                                         // encapsulation: data is hidden
    std::string name_;
    std::array<int, kScoreCount> scores_{};
};

struct AssessmentSummary {
    int users = 0;
    int atOrAboveBaseline = 0;
    double baseline = 0.0;
    std::string highestUser, lowestUser;
    double highestAverage = 0.0, lowestAverage = 0.0;
};

// Keeps many assessments (a vector of objects). Re-assessing a name replaces the old entry.
class AssessmentBoard {
public:
    void add(const UserAssessment& assessment);
    AssessmentSummary summarize(double baseline) const;   // throws std::logic_error if empty
    std::size_t size() const { return list_.size(); }
private:
    static constexpr std::size_t kMaxUsers = 100;
    std::vector<UserAssessment> list_;
};
#endif
