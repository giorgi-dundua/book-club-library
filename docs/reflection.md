# Book Club Library - Team Reflection

**Date:** 5 November 2026

**Team:** Daniel, Gowtami, Robert, Giorgi

## Roles and contributions

The team kept the same Scrum roles across both sprints:

- **Daniel - Product Owner and Developer:** Worked on the SQLite database foundation, Open Library integration, member updates, personal-data operations, loan reporting and peer reviews. Coordinated Product Backlog priorities.

- **Gowtami - Developer:** Implemented book creation, retrieval and editing functionality. Reviewed the book statistics features and suggested improvements to testing and type annotations.

- **Robert - Developer:** Worked on catalogue browsing/search, member registration, book deletion and member lookup.

- **Giorgi - Scrum Master and Developer:** Coordinated Scrum meetings, the GitHub Project board and documentation. Implemented the initial FastAPI setup, loan and return endpoints, API-key authentication and book statistics, and developed the Python client with a Streamlit interface. Also reviewed and integrated teammates' changes.


## A code review that changed the implementation

One example was Gowtami's review of PR #42, which implemented the most-borrowed books statistics endpoint.

The SQL query counted loans for each book, included books that had never been borrowed, and ordered the results by borrowing count and title.

Gowtami suggested testing books with equal borrowing counts to verify alphabetical ordering and adding a more specific return type to the database helper.

Following the review, Giorgi added a test covering alphabetical ordering when counts were equal and changed the helper's return type to `list[tuple[int, str, int]]`.

This improved the test coverage and made the function's expected result clearer.

**PR:** [https://github.com/giorgi-dundua/book-club-library/pull/42](https://github.com/giorgi-dundua/book-club-library/pull/42)

## A difficult problem and its solution

One significant challenge was integrating features developed in parallel when several branches modified the same backend files.

For example, PR #41 for book creation needed to be integrated with changes already merged into `main`, including loan and authentication functionality.

Giorgi resolved conflicts in `main.py` and `models.py`, preserving the new book creation functionality and existing API-key protection. The integrated branch passed 35 automated tests at that stage.

This demonstrated why merge conflicts must be resolved by understanding the combined functionality rather than simply accepting one version of a file.

**PR:** [https://github.com/giorgi-dundua/book-club-library/pull/41](https://github.com/giorgi-dundua/book-club-library/pull/41)

## What worked well in Scrum

The GitHub Project board, issues and pull requests provided a common place to organize tasks and follow their progress.

Dividing work among team members allowed different features to be developed in parallel. Regular coordination helped identify dependencies and determine which changes needed attention.

Code reviews were particularly useful because they provided feedback from other developers and helped identify problems before integration.

## What we would do differently

For a future project, we would establish shared API contracts earlier and integrate features in smaller increments throughout the sprint.

This would make dependencies clearer, reduce last-minute merge conflicts, and provide more time for testing the application as a complete system.

We would also account for review and integration time more explicitly when estimating the amount of work that could be completed.

## Final reflection

The project provided practical experience with Scrum, collaborative Python development, GitHub workflows and integrating an application from independently developed components.

An important lesson was that completing individual features is only part of delivering a working application. Communication, reviews, integration and testing are equally important to the final result.
