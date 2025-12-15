# Interview: Participant 004

## Background

Role: Data Scientist
Experience: 4 years
Industry: Healthcare Technology
Company Size: 500+ employees
Location: Boston, USA

## Interview Transcript

**Interviewer:** What does a typical week look like for you?

**Participant:** It varies a lot. Some weeks I'm heads-down building models - that's my favourite. Other weeks are more collaborative: presenting findings to stakeholders, translating business questions into data problems, or debugging production ML systems. There's always more work than time.

**Interviewer:** What tools do you use most?

**Participant:** Python is core - pandas, scikit-learn, PyTorch. Jupyter notebooks for exploration and documentation. We use Databricks for our data platform, MLflow for experiment tracking, and Snowflake for our data warehouse. Git for version control, though I'll admit data scientists aren't always the best at proper git hygiene.

**Interviewer:** What challenges do you face with data quality?

**Participant:** It's the bane of my existence. Healthcare data is messy - missing values, inconsistent formats, errors from manual entry. I spend probably 60% of my time on data cleaning and preprocessing. The actual modelling is the easy part.

**Interviewer:** How do you communicate results to non-technical stakeholders?

**Participant:** Visualisation is key. Executives don't want to hear about model performance metrics - they want to know the business impact. I've learned to lead with the insight, not the methodology. "This model can identify high-risk patients three months earlier" lands better than "We achieved 0.87 AUC."

**Interviewer:** What frustrates you about your work?

**Participant:** Unrealistic expectations about AI. Sometimes stakeholders think machine learning is magic - they want predictions without acknowledging data limitations. Education is part of my job now.

Also, the gap between a working prototype and production deployment. I can build a great model in a notebook, but getting it into production with proper monitoring and scalability is a whole different challenge.

**Interviewer:** How do you handle model monitoring and maintenance?

**Participant:** We check for drift weekly - comparing incoming data distributions to training data. If metrics degrade, we investigate and potentially retrain. But honestly, our monitoring could be better. We've had models silently degrade because nobody was watching the right metrics.

**Interviewer:** What would improve your productivity?

**Participant:** Better MLOps tooling. Right now, deploying a model is a multi-step manual process involving three teams. A proper CI/CD pipeline for ML would be transformative.

Also, more compute resources for experimentation. Our shared cluster gets overloaded, and waiting hours for training jobs kills momentum.
