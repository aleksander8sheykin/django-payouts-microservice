# Roo Code Agent Rules

## General
- Follow the instructions in this file strictly.
- Always respect context_mode defined in agents.yaml.

## Context usage
- Default context mode is CONDENSED.
- Full project context is allowed ONLY for Architect.
- Coder MUST NOT reload entire project.

## Code changes
- Make minimal changes only.
- Never refactor unrelated files.
- Ask before modifying multiple files.

## Testing
- Generate tests only when explicitly requested.
- Do not rewrite existing tests.

## Output
- Show diffs or full file content only for changed files.
- Never repeat unchanged code.
