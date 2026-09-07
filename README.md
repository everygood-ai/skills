A collection of model-agnostic skills for AI, writen with 20 years of engineering experience.

# Every Good AI — Skills

All skills in this repository are model-agnostic — they work with any AI model or agent runtime that supports the Agent Skills format.

This repository is compliant with the [Agent Skills specification](https://agentskills.io/specification).

Most of the skills come with builtin determenistic checks, linters and validators.

## Skills

| Skill | Description |
|---|---|
| [egai-context-curation](skills/egai-context-curation) | Build and maintain compact, evidence-based Markdown context for a project or codebase area. |
| [egai-skill-maker](skills/egai-skill-maker) | Create, revise, and validate portable Agent Skills, including their documentation and bundled resources. |
| [egai-task-impl](skills/egai-task-impl) | Implement one planned task, verify its acceptance criteria, and keep its completion status current. |
| [egai-task-reader](skills/egai-task-reader) | Read and validate task-plan frontmatter, task criteria, phase batches, and pull request metadata. |
| [egai-tasks-runner](skills/egai-tasks-runner) | Orchestrate a task plan by dispatching implementation work and updating plan progress. |
| [egai-tasks-writing](skills/egai-tasks-writing) | Create phased, execution-ready Markdown task plans with schema-validated task cards. |
| [egai-write-tone](skills/egai-write-tone) | Write or rewrite text at a controlled tone level — prose, terse, or compact. |

## Installation

We recommend fetching this project and running `./install.sh` before using its skills. The script installs their command-line dependencies.

Install any skill with [`npx skills`](https://github.com/vercel-labs/skills) from Vercel:

```bash
npx skills add everygood-ai/skills
```

## License

[MIT](LICENSE)
