# Future gaps

- **Access control:** Standard, validator-enforced `access-mode` semantics for no-tool, read-only, and write-capable skills.
- **Command control:** Standard, validator-enforced `command-mode` semantics for no commands, bundled scripts only, or explicitly declared commands.
- **Skill graph:** Skills need lazy, composable dependencies while remaining independently invocable. Example: `implementer → backend → {api-specs, layered-architecture}` and `implementer → {frontend, mobile}`.
- **Skill paths:** Activate only the selected dependency path. Installing every graph node currently exposes irrelevant skills to discovery context; mobile should not load layered-architecture metadata, and frontend should not load API metadata.
- **Shared knowledge:** Multiple skills need reusable knowledge libraries that load on demand without becoming independently discoverable skills unless explicitly configured.
