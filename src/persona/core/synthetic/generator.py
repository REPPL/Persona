"""
Synthetic data generation functionality.

This module provides the SyntheticDataGenerator class for creating
realistic synthetic interview data for demos and testing.
"""

import json
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DataDomain(Enum):
    """Domain categories for synthetic data."""

    ECOMMERCE = "ecommerce"
    HEALTHCARE = "healthcare"
    FINTECH = "fintech"
    EDUCATION = "education"
    SAAS = "saas"
    GENERAL = "general"


@dataclass
class GenerationConfig:
    """
    Configuration for synthetic data generation.

    Attributes:
        domain: Target domain for data.
        participant_count: Number of participants to generate.
        questions_per_interview: Questions per interview.
        include_demographics: Whether to include demographics.
        seed: Random seed for reproducibility.
    """

    domain: DataDomain = DataDomain.GENERAL
    participant_count: int = 5
    questions_per_interview: int = 6
    include_demographics: bool = True
    seed: int | None = None


@dataclass
class SyntheticParticipant:
    """
    A synthetic research participant.

    Attributes:
        id: Unique participant identifier.
        role: Job role or title.
        experience_years: Years of experience.
        demographics: Demographic information.
        traits: Personality traits affecting responses.
    """

    id: str
    role: str
    experience_years: int = 0
    demographics: dict[str, str] = field(default_factory=dict)
    traits: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "experience_years": self.experience_years,
            "demographics": self.demographics,
            "traits": self.traits,
        }


@dataclass
class SyntheticInterview:
    """
    A synthetic interview transcript.

    Attributes:
        participant: The participant.
        questions: List of questions asked.
        responses: List of responses.
        metadata: Additional metadata.
    """

    participant: SyntheticParticipant
    questions: list[str] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_transcript(self) -> str:
        """Convert to interview transcript format."""
        lines = [
            f"# Interview: {self.participant.id}",
            f"Role: {self.participant.role}",
            "",
        ]

        if self.participant.demographics:
            lines.append("## Demographics")
            for key, value in self.participant.demographics.items():
                lines.append(f"- {key}: {value}")
            lines.append("")

        lines.append("## Interview")
        for q, r in zip(self.questions, self.responses):
            lines.append(f"**Q: {q}**")
            lines.append(f"{r}")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "participant": self.participant.to_dict(),
            "questions": self.questions,
            "responses": self.responses,
            "metadata": self.metadata,
        }


class SyntheticDataGenerator:
    """
    Generates realistic synthetic interview data.

    Creates synthetic participants and interviews for demos,
    testing, and tutorials without requiring real research data.

    IMPORTANT: Synthetic data is for testing and demos ONLY.
    It is NOT grounded in real research data and should not be
    used for actual UX decisions. See R-003 and R-008 for details
    on bias concerns with synthetic personas.

    Bias Mitigation (per R-008 research):
    - Uses gender-neutral participant IDs (P001, P002, etc.)
    - Avoids gendered names entirely
    - Uses role-based identification instead of personal names
    - Balanced age group distribution
    - Avoids cultural or demographic stereotypes in responses
    - Does not assume correlations between demographics and behaviour

    Example:
        generator = SyntheticDataGenerator()
        interviews = generator.generate(
            domain=DataDomain.ECOMMERCE,
            count=5,
        )
        for interview in interviews:
            print(interview.to_transcript())
    """

    # Domain-specific question templates
    DOMAIN_QUESTIONS = {
        DataDomain.ECOMMERCE: [
            "What challenges do you face when shopping online?",
            "How do you typically discover new products?",
            "What makes you trust an online store?",
            "Describe your ideal checkout experience.",
            "What frustrates you most about returns?",
            "How do you compare prices across sites?",
            "What influences your purchasing decisions?",
            "How important are customer reviews to you?",
        ],
        DataDomain.HEALTHCARE: [
            "How do you currently manage your health appointments?",
            "What challenges do you face accessing healthcare?",
            "How do you keep track of medications?",
            "What would make telehealth visits better?",
            "How do you prefer to receive health information?",
            "What concerns do you have about health data privacy?",
            "How do you choose healthcare providers?",
            "What frustrates you about health insurance?",
        ],
        DataDomain.FINTECH: [
            "How do you currently manage your finances?",
            "What banking tasks do you find most frustrating?",
            "How comfortable are you with mobile payments?",
            "What would help you save more effectively?",
            "How do you track your spending?",
            "What security concerns do you have with digital banking?",
            "How do you prefer to receive financial advice?",
            "What features would your ideal banking app have?",
        ],
        DataDomain.EDUCATION: [
            "How do you prefer to learn new skills?",
            "What challenges do you face with online learning?",
            "How do you stay motivated during courses?",
            "What makes educational content engaging?",
            "How do you track your learning progress?",
            "What tools help you study effectively?",
            "How important is certification to you?",
            "What would improve your learning experience?",
        ],
        DataDomain.SAAS: [
            "What tools do you use daily for work?",
            "How do you evaluate new software?",
            "What frustrates you about your current tools?",
            "How important is integration between tools?",
            "What would make onboarding easier?",
            "How do you handle software training?",
            "What features do you wish your tools had?",
            "How do you provide feedback to vendors?",
        ],
        DataDomain.GENERAL: [
            "What are your main goals in this area?",
            "What challenges do you face most often?",
            "How do you currently solve this problem?",
            "What would an ideal solution look like?",
            "What has worked well for you in the past?",
            "What hasn't worked and why?",
            "How do you prioritise your needs?",
            "What would make your life easier?",
        ],
    }

    # Domain-specific roles
    DOMAIN_ROLES = {
        DataDomain.ECOMMERCE: [
            "Frequent Online Shopper",
            "Bargain Hunter",
            "Brand Loyalist",
            "Impulse Buyer",
            "Research-Driven Shopper",
            "Mobile-First Shopper",
            "Occasional Browser",
            "Subscription Enthusiast",
        ],
        DataDomain.HEALTHCARE: [
            "Chronic Condition Manager",
            "Caregiver",
            "Health-Conscious Individual",
            "New Parent",
            "Senior Patient",
            "Fitness Enthusiast",
            "Mental Health Advocate",
            "Healthcare Professional",
        ],
        DataDomain.FINTECH: [
            "Young Professional",
            "Small Business Owner",
            "Retirement Planner",
            "Budget-Conscious Saver",
            "Crypto Curious",
            "Traditional Banker",
            "Freelancer",
            "Family Financial Manager",
        ],
        DataDomain.EDUCATION: [
            "Career Changer",
            "Lifelong Learner",
            "Student",
            "Corporate Trainer",
            "Self-Taught Developer",
            "Academic Researcher",
            "Hobbyist Learner",
            "Professional Upskiller",
        ],
        DataDomain.SAAS: [
            "Startup Founder",
            "Enterprise IT Manager",
            "Remote Worker",
            "Team Lead",
            "Solo Entrepreneur",
            "Digital Marketer",
            "Product Manager",
            "Developer",
        ],
        DataDomain.GENERAL: [
            "Early Adopter",
            "Practical User",
            "Power User",
            "Casual User",
            "Tech-Savvy Professional",
            "Traditional User",
            "Budget-Conscious Consumer",
            "Quality-Focused Individual",
        ],
    }

    # Response patterns based on traits
    TRAIT_RESPONSES = {
        "frustrated": [
            "This is really frustrating because",
            "I've struggled with",
            "It's annoying when",
            "I wish they would fix",
        ],
        "enthusiastic": [
            "I love how",
            "It's amazing when",
            "I'm excited about",
            "The best part is",
        ],
        "analytical": [
            "I've noticed that",
            "Based on my experience",
            "The data shows",
            "I've compared and found",
        ],
        "practical": [
            "What works for me is",
            "I just need something that",
            "The simple solution is",
            "I prefer straightforward",
        ],
        "cautious": [
            "I'm concerned about",
            "I need to be careful with",
            "I always check first",
            "Security is important because",
        ],
    }

    # Response content fragments
    RESPONSE_FRAGMENTS = {
        DataDomain.ECOMMERCE: {
            "goals": [
                "finding the best deals",
                "getting products quickly",
                "avoiding scams",
                "comparing options easily",
            ],
            "pain_points": [
                "hidden shipping costs",
                "complicated returns",
                "inconsistent sizing",
                "slow delivery",
            ],
            "behaviours": [
                "read reviews thoroughly",
                "compare prices across sites",
                "wait for sales",
                "use price tracking tools",
            ],
        },
        DataDomain.HEALTHCARE: {
            "goals": [
                "staying healthy",
                "managing conditions effectively",
                "accessing care easily",
                "understanding my health",
            ],
            "pain_points": [
                "long wait times",
                "confusing insurance",
                "lack of coordination",
                "expensive medications",
            ],
            "behaviours": [
                "track symptoms daily",
                "research conditions online",
                "schedule preventive care",
                "use health apps",
            ],
        },
        DataDomain.FINTECH: {
            "goals": [
                "building savings",
                "managing debt",
                "investing wisely",
                "tracking spending",
            ],
            "pain_points": [
                "hidden fees",
                "complex interfaces",
                "security concerns",
                "poor customer support",
            ],
            "behaviours": [
                "check accounts daily",
                "automate transfers",
                "use budgeting apps",
                "compare rates regularly",
            ],
        },
        DataDomain.EDUCATION: {
            "goals": [
                "advancing my career",
                "learning new skills",
                "staying current",
                "earning certifications",
            ],
            "pain_points": [
                "lack of time",
                "boring content",
                "expensive courses",
                "no practical application",
            ],
            "behaviours": [
                "learn in short bursts",
                "take notes actively",
                "practice immediately",
                "join study groups",
            ],
        },
        DataDomain.SAAS: {
            "goals": [
                "improving productivity",
                "streamlining workflows",
                "reducing manual work",
                "better collaboration",
            ],
            "pain_points": [
                "too many tools",
                "poor integrations",
                "steep learning curves",
                "expensive subscriptions",
            ],
            "behaviours": [
                "try free trials first",
                "read user reviews",
                "request demos",
                "compare features carefully",
            ],
        },
        DataDomain.GENERAL: {
            "goals": [
                "solving problems efficiently",
                "saving time",
                "reducing stress",
                "achieving balance",
            ],
            "pain_points": [
                "complexity",
                "lack of support",
                "inconsistent quality",
                "poor communication",
            ],
            "behaviours": [
                "research before deciding",
                "ask for recommendations",
                "test before committing",
                "provide feedback",
            ],
        },
    }

    def __init__(self, config: GenerationConfig | None = None) -> None:
        """
        Initialise the generator.

        Args:
            config: Generation configuration.
        """
        self.config = config or GenerationConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)

    def generate(
        self,
        domain: DataDomain | None = None,
        count: int | None = None,
    ) -> list[SyntheticInterview]:
        """
        Generate synthetic interviews.

        Args:
            domain: Target domain (overrides config).
            count: Number of interviews (overrides config).

        Returns:
            List of synthetic interviews.
        """
        domain = domain or self.config.domain
        count = count or self.config.participant_count

        interviews = []
        for i in range(count):
            participant = self._generate_participant(domain, i + 1)
            interview = self._generate_interview(domain, participant)
            interviews.append(interview)

        return interviews

    def generate_participant(
        self,
        domain: DataDomain | None = None,
        participant_id: int = 1,
    ) -> SyntheticParticipant:
        """
        Generate a single synthetic participant.

        Args:
            domain: Target domain.
            participant_id: Numeric ID.

        Returns:
            Synthetic participant.
        """
        domain = domain or self.config.domain
        return self._generate_participant(domain, participant_id)

    def generate_interview(
        self,
        participant: SyntheticParticipant,
        domain: DataDomain | None = None,
    ) -> SyntheticInterview:
        """
        Generate an interview for a participant.

        Args:
            participant: The participant.
            domain: Target domain.

        Returns:
            Synthetic interview.
        """
        domain = domain or self.config.domain
        return self._generate_interview(domain, participant)

    def export_to_csv(
        self,
        interviews: list[SyntheticInterview],
        output_path: Path,
    ) -> None:
        """
        Export interviews to CSV format.

        Args:
            interviews: Interviews to export.
            output_path: Output file path.
        """
        import csv

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            headers = ["participant_id", "role"]
            if interviews and interviews[0].participant.demographics:
                headers.extend(interviews[0].participant.demographics.keys())
            headers.extend(
                [f"q{i+1}" for i in range(len(interviews[0].questions))]
                if interviews
                else []
            )
            headers.extend(
                [f"r{i+1}" for i in range(len(interviews[0].responses))]
                if interviews
                else []
            )
            writer.writerow(headers)

            # Data rows
            for interview in interviews:
                row = [
                    interview.participant.id,
                    interview.participant.role,
                ]
                row.extend(interview.participant.demographics.values())
                row.extend(interview.questions)
                row.extend(interview.responses)
                writer.writerow(row)

    def export_to_json(
        self,
        interviews: list[SyntheticInterview],
        output_path: Path,
    ) -> None:
        """
        Export interviews to JSON format.

        Args:
            interviews: Interviews to export.
            output_path: Output file path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "interviews": [i.to_dict() for i in interviews],
            "metadata": {
                "domain": self.config.domain.value,
                "count": len(interviews),
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def export_to_markdown(
        self,
        interviews: list[SyntheticInterview],
        output_path: Path,
    ) -> None:
        """
        Export interviews to Markdown format.

        Args:
            interviews: Interviews to export.
            output_path: Output file path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = ["# Synthetic Interview Data", ""]
        content.append(f"Domain: {self.config.domain.value}")
        content.append(f"Participants: {len(interviews)}")
        content.append("")
        content.append("---")
        content.append("")

        for interview in interviews:
            content.append(interview.to_transcript())
            content.append("---")
            content.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    def list_domains(self) -> list[dict[str, str]]:
        """
        List available domains.

        Returns:
            List of domain info dictionaries.
        """
        return [
            {"id": d.value, "name": d.name.replace("_", " ").title()}
            for d in DataDomain
        ]

    def _generate_participant(
        self,
        domain: DataDomain,
        participant_id: int,
    ) -> SyntheticParticipant:
        """Generate a participant for the domain."""
        roles = self.DOMAIN_ROLES.get(domain, self.DOMAIN_ROLES[DataDomain.GENERAL])
        role = random.choice(roles)

        traits = random.sample(
            list(self.TRAIT_RESPONSES.keys()),
            k=random.randint(1, 3),
        )

        demographics = {}
        if self.config.include_demographics:
            demographics = {
                "age_group": random.choice(
                    ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
                ),
                "experience": random.choice(
                    ["Novice", "Intermediate", "Advanced", "Expert"]
                ),
                "tech_comfort": random.choice(["Low", "Medium", "High"]),
            }

        return SyntheticParticipant(
            id=f"P{participant_id:03d}",
            role=role,
            experience_years=random.randint(0, 20),
            demographics=demographics,
            traits=traits,
        )

    def _generate_interview(
        self,
        domain: DataDomain,
        participant: SyntheticParticipant,
    ) -> SyntheticInterview:
        """Generate an interview for the participant."""
        questions_pool = self.DOMAIN_QUESTIONS.get(
            domain, self.DOMAIN_QUESTIONS[DataDomain.GENERAL]
        )

        # Select random questions
        num_questions = min(
            self.config.questions_per_interview,
            len(questions_pool),
        )
        questions = random.sample(questions_pool, num_questions)

        # Generate responses
        responses = []
        for question in questions:
            response = self._generate_response(domain, participant, question)
            responses.append(response)

        return SyntheticInterview(
            participant=participant,
            questions=questions,
            responses=responses,
            metadata={
                "domain": domain.value,
                "generated": True,
            },
        )

    def _generate_response(
        self,
        domain: DataDomain,
        participant: SyntheticParticipant,
        question: str,
    ) -> str:
        """Generate a response for a question."""
        fragments = self.RESPONSE_FRAGMENTS.get(
            domain, self.RESPONSE_FRAGMENTS[DataDomain.GENERAL]
        )

        # Pick a trait-based opener
        trait = random.choice(participant.traits) if participant.traits else "practical"
        openers = self.TRAIT_RESPONSES.get(trait, self.TRAIT_RESPONSES["practical"])
        opener = random.choice(openers)

        # Build response from fragments
        parts = []

        # Add goal-related content
        if "goal" in question.lower() or "want" in question.lower():
            goal = random.choice(fragments["goals"])
            parts.append(f"{opener} {goal}.")

        # Add pain point content
        if "challenge" in question.lower() or "frustrat" in question.lower():
            pain = random.choice(fragments["pain_points"])
            parts.append(f"I often deal with {pain}.")

        # Add behaviour content
        if "how do you" in question.lower():
            behaviour = random.choice(fragments["behaviours"])
            parts.append(f"I usually {behaviour}.")

        # Ensure we have content
        if not parts:
            goal = random.choice(fragments["goals"])
            pain = random.choice(fragments["pain_points"])
            parts.append(f"{opener} {goal}.")
            parts.append(f"But sometimes {pain} gets in the way.")

        # Add role-specific context
        parts.append(f"As a {participant.role.lower()}, this really matters to me.")

        return " ".join(parts)
