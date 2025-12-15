# Interview: Participant 005

## Background

Role: DevOps Engineer
Experience: 7 years
Industry: Media & Entertainment
Company Size: 1000+ employees
Location: Amsterdam, Netherlands

## Interview Transcript

**Interviewer:** What does your day-to-day work involve?

**Participant:** A mix of infrastructure maintenance, automation, and firefighting. On a good day, I'm improving our CI/CD pipelines, writing Terraform modules, or optimising our Kubernetes clusters. On a bad day, I'm debugging production incidents at 3 AM.

**Interviewer:** What tools are central to your work?

**Participant:** Kubernetes is the backbone - we run everything containerised. Terraform for infrastructure as code, ArgoCD for GitOps deployments, Prometheus and Grafana for monitoring. We use GitHub Actions for CI, and Vault for secrets management. Oh, and a lot of shell scripting still - some things never change.

**Interviewer:** What are your biggest infrastructure challenges?

**Participant:** Cost management in the cloud. It's easy to spin up resources but hard to track what's actually being used. We've had surprise AWS bills that made finance very unhappy. I've been implementing better tagging and automated cleanup policies.

Also, keeping environments consistent. We have dev, staging, and production, and drift happens despite our best efforts. Infrastructure as code helps, but it's not a silver bullet.

**Interviewer:** How do you handle incidents?

**Participant:** We have an on-call rotation and use PagerDuty for alerting. When something breaks, we follow a runbook if one exists - which it often doesn't for novel issues. Post-incident, we do blameless retrospectives. The goal is to learn, not to point fingers.

**Interviewer:** What frustrates you about DevOps work?

**Participant:** Being seen as a service desk. Developers sometimes treat infrastructure like magic - they want resources immediately but don't want to understand the systems. I spend too much time on tickets that could be self-service.

The other frustration is technical debt in infrastructure. Everyone's excited about the next shiny tool, but nobody wants to maintain the boring stuff that actually keeps things running.

**Interviewer:** How do you approach security?

**Participant:** Shift left as much as possible. Security scanning in CI, policy-as-code with OPA, regular vulnerability assessments. We encrypt everything in transit and at rest. But honestly, the weakest link is usually human - people still commit secrets to repos despite all our guardrails.

**Interviewer:** What would improve your productivity?

**Participant:** Better documentation. Not just for external tools, but internal runbooks. When I'm on call at 2 AM, I don't want to reverse-engineer someone's clever automation.

Also, more investment in platform engineering. If we built better self-service tools, developers could be more autonomous, and I could focus on actually improving infrastructure instead of fielding requests.

**Interviewer:** How do you stay current?

**Participant:** The CNCF landscape changes constantly. I follow KubeCon talks, read engineering blogs from companies like Netflix and Spotify, and experiment with new tools in my home lab before proposing them at work. You can't adopt everything, so picking the right battles matters.
