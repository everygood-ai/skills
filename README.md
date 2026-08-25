A collection of model-agnostic skills for AI, writen with 20 years of engineering experience.

# Every Good AI — Skills

All skills in this repository are model-agnostic — they work with any AI model or agent runtime that supports the Agent Skills format.

This repository is compliant with the [Agent Skills specification](https://agentskills.io/specification).

Most of the skills come with builtin determenistic checks, linters and validators.

## Skills

| Skill | Description |
|---|---|
| [egai-context-curation](skills/egai-context-curation) | Build and maintain compact, evidence-based Markdown context for a project or codebase area. |
| [egai-write-tone](skills/egai-write-tone) | Write or rewrite text at a controlled tone level — prose, terse, or compact. |

## Installation

First run `install.sh` to have all of the tools.

Install any skill with [`npx skills`](https://github.com/vercel-labs/skills) from Vercel:

```bash
npx skills add everygood-ai/skills
```

## License

[MIT](LICENSE)
