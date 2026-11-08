# How I work with AI

Agents write most of my code now. That changes where my attention goes, not whether I own the result.

**What I keep.** Choosing the problem, deciding what good looks like, and judging whether the result is right. If I could not explain a change in review, it does not ship.

**What agents do.** Most of the implementation, first drafts of tests and documentation, and the tedious parts of upgrades and security fixes.

**How I check their work.** Each repository has an `AGENTS.md` with the rules an agent must follow. Changes go through typed contracts, tests and, where it matters, a check against the running system. A green build is evidence, not proof.

**Writing.** Agents may draft. I rewrite everything in my own words before it goes out.

**What I won't do.** Hand an agent a secret, publish what I have not read, or let an agent act on instructions it found in untrusted content.
