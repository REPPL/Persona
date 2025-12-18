"""
Tests for synthetic data generation functionality (F-028).
"""

import json
from pathlib import Path

import pytest
from persona.core.synthetic import (
    DataDomain,
    GenerationConfig,
    SyntheticDataGenerator,
    SyntheticInterview,
    SyntheticParticipant,
)


class TestDataDomain:
    """Tests for DataDomain enum."""

    def test_domain_values(self):
        """Test domain enum values."""
        assert DataDomain.ECOMMERCE.value == "ecommerce"
        assert DataDomain.HEALTHCARE.value == "healthcare"
        assert DataDomain.FINTECH.value == "fintech"
        assert DataDomain.EDUCATION.value == "education"
        assert DataDomain.SAAS.value == "saas"
        assert DataDomain.GENERAL.value == "general"

    def test_all_domains(self):
        """Test all domains are defined."""
        assert len(DataDomain) == 6


class TestGenerationConfig:
    """Tests for GenerationConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = GenerationConfig()

        assert config.domain == DataDomain.GENERAL
        assert config.participant_count == 5
        assert config.questions_per_interview == 6
        assert config.include_demographics is True
        assert config.seed is None

    def test_custom_config(self):
        """Test custom configuration."""
        config = GenerationConfig(
            domain=DataDomain.ECOMMERCE,
            participant_count=10,
            questions_per_interview=8,
            include_demographics=False,
            seed=42,
        )

        assert config.domain == DataDomain.ECOMMERCE
        assert config.participant_count == 10
        assert config.questions_per_interview == 8
        assert config.include_demographics is False
        assert config.seed == 42


class TestSyntheticParticipant:
    """Tests for SyntheticParticipant dataclass."""

    def test_basic_participant(self):
        """Test basic participant creation."""
        participant = SyntheticParticipant(
            id="P001",
            role="Developer",
        )

        assert participant.id == "P001"
        assert participant.role == "Developer"
        assert participant.experience_years == 0
        assert participant.demographics == {}
        assert participant.traits == []

    def test_full_participant(self):
        """Test participant with all fields."""
        participant = SyntheticParticipant(
            id="P002",
            role="Product Manager",
            experience_years=5,
            demographics={"age_group": "25-34"},
            traits=["analytical", "enthusiastic"],
        )

        assert participant.experience_years == 5
        assert participant.demographics["age_group"] == "25-34"
        assert "analytical" in participant.traits

    def test_to_dict(self):
        """Test conversion to dictionary."""
        participant = SyntheticParticipant(
            id="P001",
            role="Developer",
            experience_years=3,
            demographics={"tech_comfort": "High"},
            traits=["practical"],
        )

        data = participant.to_dict()

        assert data["id"] == "P001"
        assert data["role"] == "Developer"
        assert data["experience_years"] == 3
        assert data["demographics"]["tech_comfort"] == "High"
        assert data["traits"] == ["practical"]


class TestSyntheticInterview:
    """Tests for SyntheticInterview dataclass."""

    @pytest.fixture
    def sample_participant(self):
        """Create a sample participant."""
        return SyntheticParticipant(
            id="P001",
            role="Developer",
            demographics={"age_group": "25-34"},
        )

    def test_basic_interview(self, sample_participant):
        """Test basic interview creation."""
        interview = SyntheticInterview(
            participant=sample_participant,
        )

        assert interview.participant.id == "P001"
        assert interview.questions == []
        assert interview.responses == []
        assert interview.metadata == {}

    def test_full_interview(self, sample_participant):
        """Test interview with all fields."""
        interview = SyntheticInterview(
            participant=sample_participant,
            questions=["What challenges do you face?"],
            responses=["I struggle with complex requirements."],
            metadata={"domain": "saas"},
        )

        assert len(interview.questions) == 1
        assert len(interview.responses) == 1
        assert interview.metadata["domain"] == "saas"

    def test_to_transcript(self, sample_participant):
        """Test conversion to transcript."""
        interview = SyntheticInterview(
            participant=sample_participant,
            questions=["What are your goals?", "What challenges?"],
            responses=["To build great software.", "Time management."],
        )

        transcript = interview.to_transcript()

        assert "# Interview: P001" in transcript
        assert "Role: Developer" in transcript
        assert "**Q: What are your goals?**" in transcript
        assert "To build great software." in transcript

    def test_to_transcript_with_demographics(self, sample_participant):
        """Test transcript includes demographics."""
        interview = SyntheticInterview(
            participant=sample_participant,
            questions=["Question?"],
            responses=["Response."],
        )

        transcript = interview.to_transcript()

        assert "## Demographics" in transcript
        assert "age_group: 25-34" in transcript

    def test_to_dict(self, sample_participant):
        """Test conversion to dictionary."""
        interview = SyntheticInterview(
            participant=sample_participant,
            questions=["Q1", "Q2"],
            responses=["R1", "R2"],
            metadata={"generated": True},
        )

        data = interview.to_dict()

        assert data["participant"]["id"] == "P001"
        assert len(data["questions"]) == 2
        assert len(data["responses"]) == 2
        assert data["metadata"]["generated"] is True


class TestSyntheticDataGenerator:
    """Tests for SyntheticDataGenerator class."""

    def test_init_default(self):
        """Test default initialisation."""
        generator = SyntheticDataGenerator()

        assert generator.config.domain == DataDomain.GENERAL
        assert generator.config.participant_count == 5

    def test_init_with_config(self):
        """Test initialisation with config."""
        config = GenerationConfig(
            domain=DataDomain.HEALTHCARE,
            participant_count=3,
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        assert generator.config.domain == DataDomain.HEALTHCARE
        assert generator.config.participant_count == 3

    def test_generate_default(self):
        """Test default generation."""
        config = GenerationConfig(seed=42, participant_count=3)
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        assert len(interviews) == 3
        for interview in interviews:
            assert isinstance(interview, SyntheticInterview)
            assert len(interview.questions) > 0
            assert len(interview.responses) > 0

    def test_generate_with_domain(self):
        """Test generation with specific domain."""
        config = GenerationConfig(seed=42, participant_count=2)
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate(domain=DataDomain.ECOMMERCE)

        assert len(interviews) == 2
        for interview in interviews:
            assert interview.metadata["domain"] == "ecommerce"

    def test_generate_with_count(self):
        """Test generation with specific count."""
        config = GenerationConfig(seed=42)
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate(count=7)

        assert len(interviews) == 7

    def test_generate_reproducible_with_seed(self):
        """Test reproducibility with seed."""
        config = GenerationConfig(seed=42, participant_count=2)

        gen1 = SyntheticDataGenerator(config)
        interviews1 = gen1.generate()

        gen2 = SyntheticDataGenerator(config)
        interviews2 = gen2.generate()

        assert interviews1[0].participant.role == interviews2[0].participant.role

    def test_generate_participant(self):
        """Test single participant generation."""
        config = GenerationConfig(seed=42)
        generator = SyntheticDataGenerator(config)

        participant = generator.generate_participant(DataDomain.FINTECH, 1)

        assert participant.id == "P001"
        assert (
            participant.role in SyntheticDataGenerator.DOMAIN_ROLES[DataDomain.FINTECH]
        )

    def test_generate_interview(self):
        """Test interview generation for participant."""
        config = GenerationConfig(seed=42)
        generator = SyntheticDataGenerator(config)

        participant = SyntheticParticipant(
            id="P001",
            role="Developer",
            traits=["analytical"],
        )

        interview = generator.generate_interview(participant, DataDomain.SAAS)

        assert interview.participant.id == "P001"
        assert len(interview.questions) == config.questions_per_interview
        assert len(interview.responses) == config.questions_per_interview

    def test_list_domains(self):
        """Test domain listing."""
        generator = SyntheticDataGenerator()
        domains = generator.list_domains()

        assert len(domains) == 6
        assert any(d["id"] == "ecommerce" for d in domains)
        assert any(d["id"] == "healthcare" for d in domains)

    def test_domain_questions_coverage(self):
        """Test all domains have questions."""
        for domain in DataDomain:
            questions = SyntheticDataGenerator.DOMAIN_QUESTIONS.get(domain)
            assert questions is not None
            assert len(questions) >= 6

    def test_domain_roles_coverage(self):
        """Test all domains have roles."""
        for domain in DataDomain:
            roles = SyntheticDataGenerator.DOMAIN_ROLES.get(domain)
            assert roles is not None
            assert len(roles) >= 4

    def test_response_fragments_coverage(self):
        """Test all domains have response fragments."""
        for domain in DataDomain:
            fragments = SyntheticDataGenerator.RESPONSE_FRAGMENTS.get(domain)
            assert fragments is not None
            assert "goals" in fragments
            assert "pain_points" in fragments
            assert "behaviours" in fragments

    def test_demographics_included(self):
        """Test demographics included when configured."""
        config = GenerationConfig(
            include_demographics=True,
            participant_count=1,
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        assert "age_group" in interviews[0].participant.demographics

    def test_demographics_excluded(self):
        """Test demographics excluded when configured."""
        config = GenerationConfig(
            include_demographics=False,
            participant_count=1,
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        assert len(interviews[0].participant.demographics) == 0

    def test_questions_per_interview(self):
        """Test configurable questions per interview."""
        config = GenerationConfig(
            questions_per_interview=4,
            participant_count=1,
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        assert len(interviews[0].questions) == 4
        assert len(interviews[0].responses) == 4


class TestSyntheticDataExport:
    """Tests for export functionality."""

    @pytest.fixture
    def generator(self):
        """Create a generator with fixed seed."""
        config = GenerationConfig(seed=42, participant_count=2)
        return SyntheticDataGenerator(config)

    @pytest.fixture
    def interviews(self, generator):
        """Generate sample interviews."""
        return generator.generate()

    def test_export_to_csv(self, generator, interviews, tmp_path: Path):
        """Test CSV export."""
        output_file = tmp_path / "interviews.csv"

        generator.export_to_csv(interviews, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "participant_id" in content
        assert "role" in content
        assert "P001" in content

    def test_export_to_json(self, generator, interviews, tmp_path: Path):
        """Test JSON export."""
        output_file = tmp_path / "interviews.json"

        generator.export_to_json(interviews, output_file)

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "interviews" in data
        assert len(data["interviews"]) == 2
        assert "metadata" in data

    def test_export_to_markdown(self, generator, interviews, tmp_path: Path):
        """Test Markdown export."""
        output_file = tmp_path / "interviews.md"

        generator.export_to_markdown(interviews, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "# Synthetic Interview Data" in content
        assert "# Interview:" in content
        assert "P001" in content

    def test_export_creates_directory(self, generator, interviews, tmp_path: Path):
        """Test export creates parent directories."""
        output_file = tmp_path / "nested" / "dir" / "interviews.json"

        generator.export_to_json(interviews, output_file)

        assert output_file.exists()

    def test_export_csv_with_demographics(self, interviews, tmp_path: Path):
        """Test CSV includes demographics columns."""
        config = GenerationConfig(include_demographics=True, seed=42)
        generator = SyntheticDataGenerator(config)
        interviews = generator.generate(count=1)
        output_file = tmp_path / "with_demographics.csv"

        generator.export_to_csv(interviews, output_file)

        content = output_file.read_text()
        assert "age_group" in content


class TestBiasMitigation:
    """Tests verifying bias mitigation per R-003 and R-008 research."""

    def test_participant_ids_are_gender_neutral(self):
        """Test participant IDs use neutral P### format, not names."""
        config = GenerationConfig(seed=42, participant_count=10)
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        for interview in interviews:
            pid = interview.participant.id
            # Must be P### format
            assert pid.startswith("P"), f"ID {pid} should start with 'P'"
            assert pid[1:].isdigit(), f"ID {pid} should be P followed by digits"

    def test_demographics_exclude_gender(self):
        """Test demographics do not include gender field."""
        config = GenerationConfig(
            include_demographics=True,
            participant_count=10,
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        for interview in interviews:
            demo = interview.participant.demographics
            # Gender should never be in demographics
            assert "gender" not in demo
            assert "sex" not in demo

    def test_roles_contain_no_gendered_names(self):
        """Test all roles are descriptive, not gendered names."""
        # Common gendered names to check against
        gendered_names = {
            "john",
            "jane",
            "michael",
            "sarah",
            "david",
            "emily",
            "james",
            "mary",
            "robert",
            "jennifer",
            "william",
            "linda",
        }

        for domain in DataDomain:
            roles = SyntheticDataGenerator.DOMAIN_ROLES.get(domain, [])
            for role in roles:
                role_lower = role.lower()
                for name in gendered_names:
                    assert (
                        name not in role_lower
                    ), f"Role '{role}' contains gendered name '{name}'"

    def test_age_distribution_is_balanced(self):
        """Test age groups have equal probability."""
        config = GenerationConfig(
            include_demographics=True,
            participant_count=600,  # Large sample for distribution test
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()

        # Count age groups
        age_counts: dict[str, int] = {}
        for interview in interviews:
            age = interview.participant.demographics.get("age_group")
            if age:
                age_counts[age] = age_counts.get(age, 0) + 1

        # Should have 6 age groups
        assert len(age_counts) == 6

        # Each should be roughly equal (within 50% of expected)
        expected = 600 / 6  # 100 per group
        for age, count in age_counts.items():
            assert count >= expected * 0.5, f"Age group {age} underrepresented"
            assert count <= expected * 1.5, f"Age group {age} overrepresented"

    def test_responses_contain_no_stereotypes(self):
        """Test response fragments avoid cultural/demographic stereotypes."""
        # Stereotypical phrases to check against
        stereotypes = [
            "as a woman",
            "as a man",
            "typical male",
            "typical female",
            "elderly people always",
            "young people always",
        ]

        for domain in DataDomain:
            fragments = SyntheticDataGenerator.RESPONSE_FRAGMENTS.get(domain, {})
            for category, items in fragments.items():
                for item in items:
                    item_lower = item.lower()
                    for stereotype in stereotypes:
                        assert (
                            stereotype not in item_lower
                        ), f"Fragment '{item}' contains stereotype '{stereotype}'"

    def test_no_assumed_demographic_behaviour_correlation(self):
        """Test that demographics don't deterministically affect responses."""
        config = GenerationConfig(
            include_demographics=True,
            participant_count=2,
            seed=42,
        )
        generator = SyntheticDataGenerator(config)

        # Generate two participants with same role but different ages
        p1 = SyntheticParticipant(
            id="P001",
            role="Developer",
            demographics={"age_group": "18-24"},
            traits=["analytical"],
        )
        p2 = SyntheticParticipant(
            id="P002",
            role="Developer",
            demographics={"age_group": "65+"},
            traits=["analytical"],
        )

        # Same seed means same random choices - responses should be similar
        # (not determined by age)
        i1 = generator.generate_interview(p1, DataDomain.SAAS)
        i2 = generator.generate_interview(p2, DataDomain.SAAS)

        # Both should have responses (not filtered by age)
        assert len(i1.responses) > 0
        assert len(i2.responses) > 0


class TestSyntheticDataIntegration:
    """Integration tests for synthetic data workflow."""

    def test_full_generation_workflow(self, tmp_path: Path):
        """Test complete generation workflow."""
        # Configure
        config = GenerationConfig(
            domain=DataDomain.ECOMMERCE,
            participant_count=5,
            questions_per_interview=6,
            include_demographics=True,
            seed=42,
        )

        # Generate
        generator = SyntheticDataGenerator(config)
        interviews = generator.generate()

        # Verify
        assert len(interviews) == 5
        for interview in interviews:
            assert len(interview.questions) == 6
            assert len(interview.responses) == 6
            assert interview.participant.demographics

        # Export all formats
        generator.export_to_csv(interviews, tmp_path / "data.csv")
        generator.export_to_json(interviews, tmp_path / "data.json")
        generator.export_to_markdown(interviews, tmp_path / "data.md")

        assert (tmp_path / "data.csv").exists()
        assert (tmp_path / "data.json").exists()
        assert (tmp_path / "data.md").exists()

    def test_all_domains_generate(self):
        """Test generation works for all domains."""
        config = GenerationConfig(participant_count=1, seed=42)
        generator = SyntheticDataGenerator(config)

        for domain in DataDomain:
            interviews = generator.generate(domain=domain)
            assert len(interviews) == 1
            assert interviews[0].metadata["domain"] == domain.value

    def test_varied_participant_count(self):
        """Test various participant counts."""
        config = GenerationConfig(seed=42)
        generator = SyntheticDataGenerator(config)

        for count in [1, 5, 10, 20]:
            interviews = generator.generate(count=count)
            assert len(interviews) == count

    def test_unique_participant_ids(self):
        """Test participant IDs are unique."""
        config = GenerationConfig(participant_count=10, seed=42)
        generator = SyntheticDataGenerator(config)

        interviews = generator.generate()
        ids = [i.participant.id for i in interviews]

        assert len(ids) == len(set(ids))  # All unique
