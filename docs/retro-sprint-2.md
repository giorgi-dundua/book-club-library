# Sprint 2 Retrospective - 5 November 2026

**Project:** Book Club Library

**Team:** Daniel, Gowtami, Robert, Giorgi

**Scrum Master:** Giorgi

## What went well

- The team completed and integrated many of the required features, including book management, member registration and updates, borrowing and returns, authentication, and reporting.

- Team members worked on separate features and coordinated through GitHub Issues, pull requests and code reviews.

- Reviews identified functional issues and improved error handling, database operations, validation and test coverage.

- The team continued adapting to technical dependencies and integration problems as the project developed.


## Challenges and observations

- **Integration:** Multiple branches changed shared files such as `main.py`, `models.py` and `database.py`. Merging these changes required resolving conflicts carefully to preserve existing functionality.

- **Code reviews:** Some PRs required several rounds of corrections and testing. Reviews improved code quality but took longer than initially expected.

- **Dependencies:** The Python client depended on backend endpoints being available and returning consistent data. Delayed integration of some endpoints also affected client development.

- **Time management:** Several features were still being reviewed and merged on the final development day, leaving limited time for integrated testing and documentation.


## Follow-up on Sprint 1 improvements

- **Self-review:** Review comments continued to identify issues that could sometimes have been found earlier through local testing and code inspection.

- **Acceptance criteria:** Existing criteria helped guide development, while some API behaviour and implementation details required further clarification during reviews.

- **Prioritization:** The team focused on completing core functionality and integrating features, although the amount of remaining work made prioritization difficult.

- **Review time:** Reviews remained an important part of development and needed more time than originally anticipated.


## What could be improved

The most useful change for a similar project would be to agree on shared API interfaces earlier and integrate completed features more frequently.

This would help identify incompatible implementations sooner, reduce conflicts near the deadline, and give the client developer more time to test against the integrated backend.

It would also be useful to reserve more time for peer reviews, corrections and final end-to-end testing rather than treating implementation as the last step.

## Conclusion

Sprint 2 resulted in substantial progress toward an integrated Book Club Library application. The team gained practical experience with collaborative development, pull requests, code reviews, conflict resolution and testing.

The main lesson is that integration and review need to be planned as part of development from the beginning, especially when several people are working on shared code and dependent features.
