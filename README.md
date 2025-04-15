## 🎯 Objectives & Success Criteria

### 1.1 Clarify Your Vision

#### 🔹 Short-term (College Demo)

- **Scope**: Single-course system tailored for B.Tech CSE fundamentals.
- **Depth**: Core topics only (e.g., programming basics, data structures, algorithms).
- **Use-Case**: Self-study companion for college students preparing for exams.
- **Target Audience**: New, intermediate, and mixed-level B.Tech CSE students with basic programming background.

#### 🔹 Long-term (Production / Subscription Model)

- **Scope**: Multi-course support across disciplines.
- **Depth**: From fundamentals to advanced modules.
- **Use-Case**: Commercial subscription service for exam prep, corporate training, and lifelong learning.
- **Target Audience**: Broader learner base (K-12, university, professional upskilling).

> 💡 **Elevator Pitch**:  
> “An AI-driven tutor that adapts in real-time to each student’s performance—guiding B.Tech CSE learners through fundamentals today, and scaling to full multi-course mastery tomorrow.”

---

### 1.2 Success Metrics

| Metric Type | Metric              | Description                                                             | Initial Target |
|-------------|---------------------|-------------------------------------------------------------------------|----------------|
| **Offline** | Coverage            | % of users for whom the system can generate ≥1 valid recommendation     | ≥ 95%          |
|             | Rule-MVP Accuracy   | % match between rule-based suggestions and a gold-standard topic sequence | ≥ 60%          |
|             | CF Precision@5      | Precision of top-5 collaborative-filtering recommendations              | ≥ 0.30         |
|             | DKT AUC             | AUC of deep-knowledge-tracing model predicting mastery on next topic    | ≥ 0.70         |
| **Online**  | Engagement (CTR)    | Click-through rate on recommended topics                                | ≥ 20%          |
|             | Completion Rate     | % of recommended modules that learners finish                            | ≥ 70%          |
|             | Feedback Score      | Average self-reported usefulness rating (1–5 scale)                      | ≥ 4.0          |
