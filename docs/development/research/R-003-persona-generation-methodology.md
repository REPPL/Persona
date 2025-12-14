# R-003: AI Persona Generation Methodology

## Executive Summary

Academic research (IEEE/ACM ICSE 2024) validates the combination of LLMs with personas for adaptive UX frameworks. Industry adoption is accelerating, with half of Research Week 2025 dedicated to AI methods. The key insight is that **AI-generated personas must be grounded in real research data** to be effective. Persona's experiment-centric workflow (ADR-0003) aligns perfectly with this methodology, emphasising reproducibility and data provenance.

## Current State of the Art (2025)

### Industry Standards

The UX research community has rapidly adopted AI for persona development:

1. **Synthetic Personas** - AI-generated archetypes for stress-testing research methodology
2. **Data-Grounded Personas** - AI extracts patterns from real user data
3. **Interactive Personas** - Stakeholders can "chat" with persona representations

**Key Principle:** AI personas should augment, not replace, traditional research methods. They excel at:
- Processing large volumes of qualitative data
- Identifying patterns humans might miss
- Generating consistent persona structures
- Enabling rapid iteration

### Academic Research

**Shin et al. (IEEE/ACM ICSE 2024)** - "Generating User Experience Based on Personas with AI Assistants"

Key findings:
- Traditional UX development creates "one size fits all" solutions
- LLM + persona combination enables adaptive, personalised UX
- Three research areas: (1) adaptive UX practices, (2) persona effectiveness, (3) LLM integration framework
- Methodology supports real-time adaptation to user feedback

**Vector Personas (JUX 2024)** - Explores mathematical representations of personas for programmatic manipulation and comparison.

### Open Source Ecosystem

| Tool | Approach | Key Features |
|------|----------|--------------|
| **UXPressia AI Generator** | Data-grounded | Structured templates, team collaboration |
| **ChatGPT (direct)** | General purpose | Flexible but requires prompt engineering |
| **Persona (this project)** | Experiment-centric | Reproducibility, multi-provider, version control |

## Alternatives Analysis

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **Data-Grounded Generation** | Evidence-based, defensible, accurate | Requires real data | **Recommended** |
| **Synthetic Generation** | Quick, no data needed | Not grounded in reality | Use for testing only |
| **Hybrid (data + synthesis)** | Fills gaps in data | Risk of confabulation | Use carefully |
| **Manual Persona Creation** | Traditional, proven | Time-consuming, doesn't scale | Complement with AI |

## Recommendation

### Primary Approach

Implement **data-grounded persona generation** with these principles:

1. **Data First** - Always require user research data as input
2. **Transparency** - Show data sources in output metadata
3. **Reproducibility** - Same data + same config = same personas (experiment-centric)
4. **Validation** - Provide mechanisms to verify personas against source data

```python
# Persona generation flow
class PersonaGenerationWorkflow:
    def generate(self, experiment: Experiment) -> List[Persona]:
        # 1. Load and validate data
        data = self.data_loader.load(experiment.data_path)
        
        # 2. Estimate costs (user approval)
        cost = self.cost_estimator.estimate(data, experiment.config)
        
        # 3. Generate with provenance
        personas = self.llm.generate(
            data=data,
            prompt=experiment.prompt_template,
            config=experiment.config
        )
        
        # 4. Attach metadata
        for persona in personas:
            persona.metadata = {
                "source_files": data.file_names,
                "generation_timestamp": datetime.now(),
                "model": experiment.config.model,
                "prompt_hash": hash(experiment.prompt_template)
            }
        
        return personas
```

### Rationale

1. **Scientific Rigour** - Data-grounded approach aligns with UX research best practices
2. **Traceability** - Experiment workflow enables auditing and verification
3. **Reproducibility** - Timestamped outputs with full configuration capture
4. **Validation** - Future work can add persona-to-data verification (v0.2.0+)

### Implementation Notes

**Prompt Design for Persona Extraction:**

```jinja2
You are a UX researcher analysing qualitative data to identify user personas.

## Source Data
{{ user_data }}

## Instructions
1. Identify {{ persona_count }} distinct user personas from the data
2. Each persona should represent a meaningful user segment
3. Ground all persona attributes in evidence from the data
4. Include direct quotes where available

## Output Format
Return a JSON array of personas, each with:
- name: A realistic name
- age: Estimated age range
- occupation: Role or job title
- goals: What they want to achieve
- frustrations: Pain points and challenges
- quote: A characteristic statement (from data if available)
- evidence: List of data points supporting this persona
```

**Quality Indicators:**
- Personas should be **distinct** (low overlap)
- Personas should be **grounded** (evidence field populated)
- Personas should be **actionable** (clear goals and frustrations)

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0003 (Experiment-Centric Workflow)** should be updated to:
- Reference Shin et al. paper as academic validation
- Add data provenance as explicit requirement
- Note importance of reproducibility for research credibility

### Feature Spec Updates

**F-004 (Persona Generation)** should specify:
- Data-grounded generation as default mode
- Evidence field in persona schema
- Metadata capture requirements

**F-007 (Basic Persona Extraction)** should specify:
- Minimum data requirements for generation
- Handling of insufficient data (warn user)

## Sources

- [Shin et al. - Generating UX Based on Personas with AI (IEEE/ACM ICSE 2024)](https://arxiv.org/abs/2405.01051)
- [Vector Personas for UX Research (JUX 2024)](https://uxpajournal.org/leveraging-ai-toward-the-development-of-vector-personas-for-ux-research/)
- [AI for UX Research: Practical Guide 2025](https://greatquestion.co/ux-research/ai-guide)
- [How to Create Research-Backed User Personas (IxDF 2025)](https://www.interaction-design.org/literature/article/user-persona-guide)
- [Using AI to Streamline Persona Creation (UX Collective)](https://uxdesign.cc/using-ai-to-streamline-persona-and-journey-map-creation-37fa859dafb0)

---

## Related Documentation

- [ADR-0003: Experiment-Centric Workflow](../decisions/adrs/ADR-0003-experiment-centric-workflow.md)
- [F-004: Persona Generation](../roadmap/features/completed/F-004-persona-generation.md)
- [Acknowledgements](../lineage/acknowledgements.md)
