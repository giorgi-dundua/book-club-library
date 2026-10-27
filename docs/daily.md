## 2026-10-27 — Daily Scrum and Sprint Planning

**Time:** 09:00–approximately 10:00
**Participants:** Daniel Nilsson, Gowtami Devarent, Robert Kendo, Giorgi Dundua

### Discussion and decisions

- Reviewed and prioritized the Product Backlog.
- Discussed story-point estimates by comparing simpler and more complex stories and explaining the work involved. The team agreed to keep the proposed estimates, totaling 59 points across 15 user stories.
- Selected the first six user stories by priority for Sprint 1, totaling 27 points. The team deliberately left capacity for necessary technical setup tasks.
- Distributed the selected stories:
  - Daniel: #1 — Import book data from Open Library (5 points).
  - Gowtami: #3 — Add a book to the catalogue (3 points).
  - Robert: #4 — Browse and search the catalogue (3 points); #5 — Register a new member (3 points).
  - Giorgi: #6 — Record a book loan (8 points); #7 — Record a book return (5 points).
- Agreed on the Sprint 1 Goal:
  - Establish a working FastAPI and SQLite application that allows volunteers to register and find books and members, providing the foundation for borrowing and returning books.
- Reviewed the existing Definition of Done and Git/PR working rules. Agreed that some adjustments may be needed, with finalization and documentation left for technical issue #20.

### Technical dependencies

- Identified the need for initial FastAPI and SQLite setup to support the selected user stories.
- Technical tasks were anticipated but had not yet been created or estimated during the meeting.
- Loan and return functionality will depend on the shared database schema and connection interface.

### Follow-up after the meeting

- Created three technical issues with provisional estimates:
  - #18 — Initialize the FastAPI application (3 points).
  - #19 — Implement the SQLite database foundation (5 points).
  - #20 — Create team documentation and coding standards (2 points).
- Following further discussion, Giorgi took responsibility for #18 and Daniel for #19.
- Ownership of #20 remains to be decided.

### Next steps

- Complete and review initial setup work.
- Coordinate shared interfaces between database and API development.
- Begin implementing the selected Sprint 1 stories.
- Complete the team working agreement and documentation.
