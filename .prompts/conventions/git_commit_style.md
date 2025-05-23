# Git Commit Message Convention

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Rules

### 1. Type (Required)

Must be one of:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (updating dependencies, build process, etc.)
- **ci**: CI/CD configuration changes
- **build**: Build system or external dependency changes
- **revert**: Reverting a previous commit

### 2. Scope (Optional)

The part of the codebase affected:

- **agents**: Agent implementations
- **tools**: Tool functions
- **api**: API endpoints
- **db**: Database/migrations
- **ui**: Frontend changes
- **auth**: Authentication
- **docs**: Documentation
- **tests**: Test suite
- **deps**: Dependencies

Example: `feat(agents): add ContractorAgent implementation`

### 3. Subject (Required)

- Use imperative mood ("add" not "adds" or "added")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters
- Complete the sentence: "If applied, this commit will..."

### 4. Body (Optional)

- Separate from subject with blank line
- Wrap at 72 characters
- Explain what and why, not how
- Can use bullet points with "-" or "*"

### 5. Footer (Optional)

- Reference issues: `Fixes #123` or `Closes #456`
- Breaking changes: `BREAKING CHANGE: description`
- Co-authors: `Co-authored-by: Name <email>`

## Examples

### Simple Feature
```
feat(agents): add image analysis to HomeownerAgent
```

### Bug Fix with Detail
```
fix(tools): handle RLS errors in save_project

The save_project tool was not properly handling RLS policy
violations, causing silent failures. Now returns specific
error messages when permissions are denied.

Fixes #234
```

### Breaking Change
```
refactor(api)!: change project endpoint response format

BREAKING CHANGE: The /projects endpoint now returns data
in a nested structure. Clients must update to handle:
{
  "data": { "projects": [...] },
  "meta": { "total": 10 }
}
```

### Multiple Changes
```
feat(agents): implement OutboundRecruiterAgent

- Add contractor matching algorithm
- Integrate with notification service
- Support multi-channel outreach (email, SMS)
- Add comprehensive test coverage

Part of contractor invitation feature.

Relates to #156
```

### Documentation Update
```
docs: update ADK best practices guide

Add section on state management patterns and
update examples to use ADK 1.0.0 syntax.
```

### Dependency Update
```
chore(deps): upgrade google-adk to 1.0.1

Includes fix for create_session issue (#808).
No breaking changes.
```

### Revert
```
revert: "feat(agents): add parallel processing"

This reverts commit 123abc456.

Parallel processing causing race conditions in
state updates. Need to implement proper locking
first.
```

## Bad Examples (Don't Do This)

❌ `Fixed bug` - Too vague
❌ `Added new feature.` - Has period, not specific
❌ `FEAT: Add HomeownerAgent` - Wrong capitalization
❌ `add tests for everything` - Not capitalized
❌ `Update code` - Too generic
❌ `WIP` - Not descriptive

## Commit Message Template

Save as `.gitmessage` in project root:

```
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
#
# Type: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
# Scope: agents, tools, api, db, ui, auth, docs, tests, deps
# Subject: imperative mood, no capital, no period, <50 chars
# Body: what and why, not how, wrap at 72 chars
# Footer: fixes #issue, breaking changes, co-authors
```

Configure git to use template:
```bash
git config --local commit.template .gitmessage
```

## Enforcement

### 1. Git Hook (`.git/hooks/commit-msg`)

```bash
#!/bin/bash
# Validate commit message format

commit_regex='^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\([a-z]+\))?!?: .{1,50}$'

if ! grep -qE "$commit_regex" "$1"; then
    echo "Invalid commit message format!"
    echo "Format: <type>(<scope>): <subject>"
    echo "Example: feat(agents): add HomeownerAgent"
    exit 1
fi
```

### 2. CI Validation

```yaml
# .github/workflows/commit-lint.yml
name: Lint Commits
on: [pull_request]

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: wagoid/commitlint-github-action@v5
```

### 3. Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.2.1
    hooks:
      - id: commitizen
```

## Tools

### Commitizen
```bash
# Interactive commit
pnpm run commit
# or
npx cz
```

### Generate Changelog
```bash
# Generate CHANGELOG.md from commits
npx conventional-changelog -p angular -i CHANGELOG.md -s
```