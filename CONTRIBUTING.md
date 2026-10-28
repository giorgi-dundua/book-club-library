# Contributing

## Definition of Done

A story or task is Done when:

1. The acceptance criteria are met.
2. The Product Owner or stakeholder has accepted the work, where applicable.
3. At least one other team member has reviewed and approved the pull request.
4. Relevant tests have passed, including error cases. Functionality is tested in `/docs` and `client.py` where applicable.
5. Security requirements are met, and no secrets are committed.
6. The changes work with existing functionality without breaking it.
7. Documentation is updated where needed, including README instructions for installation, database setup, seeding and running the application.
8. The pull request is merged into `main`, and the application still works.

## Coding standards

- Follow PEP 8.
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Use clear names and keep functions focused on one task.
- Write docstrings where they are useful.
- Keep code organized in separate modules.
- Handle errors where something can go wrong.
- Use parameterized SQL queries, not string formatting.
- Do not leave dead code or commented-out experiments in `main`.

## Git and pull requests

- Every story or task is tracked as a GitHub issue.
- Create a separate branch for each issue. Include the issue number in the branch name, for example `feature/6-record-book-loan` or `chore/18-fastapi-setup`.
- Do not push directly to `main`.
- Keep pull requests reasonably small and link them to the relevant issue.
- Explain what changed and how it was tested.
- At least one other team member must review and approve a PR before merging.
- Address review comments before merging.
- If a merge conflict involves someone else's changes, resolve it together.

## Scrum workflow

- Daily Scrum takes place at 09:00 and should last no more than 15 minutes.
- The Scrum Master records each Daily Scrum in `docs/daily.md`, with the date and one line per team member.
- Keep the GitHub Project board updated: Todo > In Progress > Review > Done.
- Each developer works on at most one In Progress issue at a time.
- Review pending pull requests regularly.
- All team members contribute to both database and API development.
- Each team member must create at least three merged PRs and review at least three PRs during the project.
- The Scrum Master and Product Owner also participate in development.
- Record Sprint Retrospectives in `docs/retro-sprint-1.md` and `docs/retro-sprint-2.md`.
- Sprint 1 Review and Retrospective: Friday, 30 October.
- Sprint 2 Retrospective: Thursday, 5 November.
- Final presentation: Friday, 6 November.