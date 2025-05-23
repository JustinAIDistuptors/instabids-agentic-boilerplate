## Convention: Git Commit Message Style

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, semicolons, etc)
- **refactor**: Code refactoring without feature changes
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system or dependency changes
- **ci**: CI/CD configuration changes
- **chore**: Routine tasks, maintenance
- **revert**: Reverting a previous commit

### Scope Examples

- **agents**: Agent-related changes
- **tools**: Tool implementations
- **api**: API endpoints
- **db**: Database schemas or migrations
- **auth**: Authentication/authorization
- **ui**: Frontend changes
- **deps**: Dependencies
- **config**: Configuration files

### Subject Guidelines

1. **Use imperative mood**: "add" not "adds" or "added"
2. **Don't capitalize**: "fix bug" not "Fix bug"
3. **No period at end**: "add feature" not "add feature."
4. **Limit to 50 characters**
5. **Be specific but concise**

### Body Guidelines

1. **Wrap at 72 characters**
2. **Explain what and why, not how**
3. **Include motivation for change**
4. **Contrast with previous behavior**
5. **Use bullet points for multiple items**

### Footer Guidelines

1. **Reference issues**: "Fixes #123"
2. **Note breaking changes**: "BREAKING CHANGE: ..."
3. **Co-authors**: "Co-authored-by: Name <email>"

### Examples

#### Simple Feature
```
feat(agents): add image analysis to homeowner agent
```

#### Bug Fix with Details
```
fix(tools): correct state prefix validation in save_project

The validation was checking for "user-" instead of "user:"
prefix, causing valid state keys to be rejected.

Fixes #456
```

#### Breaking Change
```
refactor(api): restructure project endpoints

Consolidated project-related endpoints under /api/v1/projects
to improve API organization and consistency.

BREAKING CHANGE: All project endpoints now use /api/v1/projects
prefix instead of /projects
```

#### Multiple Changes
```
feat(db): add contractor matching tables

- Add contractors table with skills and service areas
- Add contractor_invitations table for tracking
- Add indexes for efficient geo-queries
- Include RLS policies for all new tables

Part of contractor matching feature #789
```

#### Dependency Update
```
build(deps): update google-adk to 1.0.1

Includes fix for create_session issue (#808) and
improved error messages for tool validation.
```

#### Test Addition
```
test(agents): add integration tests for project creation flow

Tests cover:
- Successful project creation with all fields
- Validation of required fields
- Image upload handling
- Preference learning from conversation
```

#### Documentation
```
docs: update ADK best practices with streaming patterns

Added examples for LiveAgent streaming responses and
error handling in async contexts.
```

#### Performance
```
perf(db): add composite index for project queries

Reduces query time for user project lists from 200ms to 5ms
by adding composite index on (owner_id, created_at DESC).
```

### Commit Message Templates

#### For AI Agents

When committing as an AI agent, include agent identifier:

```
feat(agents): implement contractor bidding logic

[AI: MasterCodeBuilder]

Implemented bid evaluation algorithm that considers:
- Price competitiveness
- Contractor ratings
- Previous project history
- Availability alignment
```

#### For Fixes

```
fix(<scope>): <what was broken>

<Description of the issue>
<How it was fixed>
<Impact of the fix>

Fixes #<issue-number>
```

#### For Features

```
feat(<scope>): <what was added>

<Why this feature is needed>
<How it works>
<Any configuration required>

Closes #<issue-number>
```

### Anti-patterns to Avoid

❌ **Bad Examples**:
- "fix" (too vague)
- "Fix the thing" (not imperative, too vague)
- "added new feature" (past tense)
- "FEAT: Add feature!!!" (wrong format, excessive punctuation)
- "various fixes and improvements" (too broad)

✅ **Good Examples**:
- "fix(auth): validate JWT expiration correctly"
- "feat(tools): add batch operations for preferences"
- "refactor(agents): extract common base configuration"
- "docs(api): add webhook integration guide"

### Commit Workflow

1. **Stage related changes**: `git add -p`
2. **Write commit message**: Follow format above
3. **Review diff**: Ensure message matches changes
4. **Commit**: `git commit`
5. **Push with PR**: Create descriptive PR

### Enforcing Standards

Use commit hooks or CI checks:

```bash
# .gitmessage template
# <type>(<scope>): <subject>
# 
# <body>
# 
# <footer>

# Example pre-commit hook
if ! grep -qE "^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z]+\))?: .{1,50}$" "$1"; then
    echo "Commit message does not follow conventional format"
    exit 1
fi
```