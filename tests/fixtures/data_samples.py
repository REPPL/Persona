"""
Synthetic test data generators.

This module provides functions to generate realistic test data
for various input formats supported by Persona.
"""

import csv
import json
import io
from pathlib import Path
from typing import Any


def generate_interview_csv(
    num_interviews: int = 3,
    include_header: bool = True,
) -> str:
    """
    Generate synthetic interview data in CSV format.

    Args:
        num_interviews: Number of interview records to generate
        include_header: Whether to include column headers

    Returns:
        CSV string with interview data
    """
    interviews = [
        {
            "participant_id": "P001",
            "date": "2024-01-15",
            "role": "Software Developer",
            "experience_years": "5",
            "transcript": (
                "I primarily use command-line tools for my daily work. "
                "The main frustration is when documentation is outdated. "
                "I wish there was a single tool that could handle all my needs."
            ),
            "key_themes": "CLI preference, documentation issues, tool consolidation",
        },
        {
            "participant_id": "P002",
            "date": "2024-01-16",
            "role": "UX Designer",
            "experience_years": "3",
            "transcript": (
                "I need quick visual feedback when making design decisions. "
                "Our current tools are too slow for rapid prototyping. "
                "Collaboration with developers is always a challenge."
            ),
            "key_themes": "visual feedback, speed, collaboration",
        },
        {
            "participant_id": "P003",
            "date": "2024-01-17",
            "role": "Product Manager",
            "experience_years": "7",
            "transcript": (
                "Tracking user feedback across multiple channels is overwhelming. "
                "I need better ways to synthesise research findings. "
                "Stakeholder communication takes up most of my time."
            ),
            "key_themes": "feedback tracking, research synthesis, communication",
        },
        {
            "participant_id": "P004",
            "date": "2024-01-18",
            "role": "Data Analyst",
            "experience_years": "4",
            "transcript": (
                "Data quality issues slow down my analysis work significantly. "
                "I prefer Python scripts over visual tools for data processing. "
                "Reproducibility of analysis is crucial for my work."
            ),
            "key_themes": "data quality, Python preference, reproducibility",
        },
        {
            "participant_id": "P005",
            "date": "2024-01-19",
            "role": "DevOps Engineer",
            "experience_years": "6",
            "transcript": (
                "Automation is key to everything I do. "
                "Security configurations take too much manual effort. "
                "I need tools that integrate well with our CI/CD pipeline."
            ),
            "key_themes": "automation, security, CI/CD integration",
        },
    ]

    # Select requested number of interviews
    selected = interviews[:num_interviews]

    output = io.StringIO()
    if selected:
        fieldnames = list(selected[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        if include_header:
            writer.writeheader()
        writer.writerows(selected)

    return output.getvalue()


def generate_survey_json(
    num_responses: int = 5,
) -> str:
    """
    Generate synthetic survey response data in JSON format.

    Args:
        num_responses: Number of survey responses to generate

    Returns:
        JSON string with survey data
    """
    responses = [
        {
            "response_id": "R001",
            "timestamp": "2024-01-20T10:30:00Z",
            "satisfaction_score": 4,
            "likelihood_to_recommend": 8,
            "most_useful_feature": "Quick search functionality",
            "biggest_pain_point": "Slow loading times on mobile",
            "open_feedback": (
                "Great product overall, but the mobile experience needs improvement. "
                "I often work on the go and find myself switching to desktop."
            ),
        },
        {
            "response_id": "R002",
            "timestamp": "2024-01-20T11:15:00Z",
            "satisfaction_score": 5,
            "likelihood_to_recommend": 10,
            "most_useful_feature": "Integration with other tools",
            "biggest_pain_point": "Initial setup complexity",
            "open_feedback": (
                "Once set up, this tool is amazing. The learning curve was steep "
                "but worth it. Would love more onboarding tutorials."
            ),
        },
        {
            "response_id": "R003",
            "timestamp": "2024-01-20T14:00:00Z",
            "satisfaction_score": 3,
            "likelihood_to_recommend": 5,
            "most_useful_feature": "Collaboration features",
            "biggest_pain_point": "Pricing for small teams",
            "open_feedback": (
                "The collaboration features are exactly what we need, but the pricing "
                "model doesn't work well for our small team of 3."
            ),
        },
        {
            "response_id": "R004",
            "timestamp": "2024-01-21T09:00:00Z",
            "satisfaction_score": 4,
            "likelihood_to_recommend": 7,
            "most_useful_feature": "Automation capabilities",
            "biggest_pain_point": "Documentation gaps",
            "open_feedback": (
                "Powerful automation features but sometimes hard to figure out "
                "how to use them. Better docs would help a lot."
            ),
        },
        {
            "response_id": "R005",
            "timestamp": "2024-01-21T16:30:00Z",
            "satisfaction_score": 5,
            "likelihood_to_recommend": 9,
            "most_useful_feature": "Customisation options",
            "biggest_pain_point": "No offline mode",
            "open_feedback": (
                "I can customise everything to fit my workflow perfectly. "
                "Only wish it worked offline for when I'm travelling."
            ),
        },
    ]

    selected = responses[:num_responses]
    return json.dumps({"survey_responses": selected}, indent=2)


def generate_feedback_markdown(
    num_entries: int = 3,
) -> str:
    """
    Generate synthetic user feedback in Markdown format.

    Args:
        num_entries: Number of feedback entries to generate

    Returns:
        Markdown string with feedback data
    """
    entries = [
        """## User Feedback: Mobile App Experience

**Date:** 2024-01-22
**User Type:** Power User
**Platform:** iOS

### Summary
The mobile app lacks several features available on desktop. Users expect
feature parity or at least clear communication about limitations.

### Key Points
- Push notifications are unreliable
- Cannot access advanced settings on mobile
- Sync between devices sometimes fails

### User Quote
> "I love using this on my laptop, but the mobile app feels like an afterthought."
""",
        """## User Feedback: Onboarding Experience

**Date:** 2024-01-23
**User Type:** New User
**Platform:** Web

### Summary
New users feel overwhelmed by the number of options presented during onboarding.
A guided tour or progressive disclosure would improve first-time experience.

### Key Points
- Too many options presented at once
- No clear "getting started" path
- Tutorial videos are too long

### User Quote
> "I signed up expecting simplicity but was hit with a wall of settings."
""",
        """## User Feedback: Team Collaboration

**Date:** 2024-01-24
**User Type:** Team Admin
**Platform:** Desktop (Windows)

### Summary
Team features work well but permission management is confusing. Admins need
clearer visibility into what team members can access.

### Key Points
- Role definitions are unclear
- Cannot easily audit team permissions
- Invitation workflow has too many steps

### User Quote
> "I never know what my team members can actually see until they ask me."
""",
    ]

    selected = entries[:num_entries]
    return "\n---\n".join(selected)


def write_synthetic_data_files(output_dir: Path) -> dict[str, Path]:
    """
    Write all synthetic test data files to the specified directory.

    Args:
        output_dir: Directory to write files to

    Returns:
        Dict mapping file type to file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {}

    # CSV files
    csv_small = output_dir / "interviews_small.csv"
    csv_small.write_text(generate_interview_csv(num_interviews=3))
    files["csv_small"] = csv_small

    csv_medium = output_dir / "interviews_medium.csv"
    csv_medium.write_text(generate_interview_csv(num_interviews=5))
    files["csv_medium"] = csv_medium

    # JSON file
    json_file = output_dir / "survey_responses.json"
    json_file.write_text(generate_survey_json(num_responses=5))
    files["json"] = json_file

    # Markdown file
    md_file = output_dir / "user_feedback.md"
    md_file.write_text(generate_feedback_markdown(num_entries=3))
    files["markdown"] = md_file

    # Mixed format directory
    mixed_dir = output_dir / "mixed_format"
    mixed_dir.mkdir(exist_ok=True)
    (mixed_dir / "interviews.csv").write_text(generate_interview_csv(num_interviews=2))
    (mixed_dir / "survey.json").write_text(generate_survey_json(num_responses=2))
    (mixed_dir / "feedback.md").write_text(generate_feedback_markdown(num_entries=1))
    files["mixed_dir"] = mixed_dir

    return files
