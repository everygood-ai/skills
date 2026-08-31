# Gaps

- The Agent Skills specification does not define a standard mechanism for one skill to spawn an isolated sub-agent that runs another skill. This skill assumes the host product provides one (for example, an agent-spawning tool). Workaround: on a host without sub-agent spawning, run each dispatched unit sequentially in the current agent context instead of as an isolated sub-agent, preserving the same ordering and `index.md`-ownership rules.
