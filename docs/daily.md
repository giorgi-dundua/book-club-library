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

## 2026-10-28 - Daily Scrum

### Team updates

- Daniel: Completed the SQLite database foundation (#19) and continued Open Library integration (#1). Database validation (#23) remains a follow-up.
- Gowtami: Working on adding books to the catalogue (#3).
- Robert: Working on catalogue browsing/search (#4) and member registration (#5).
- Giorgi: Working on loan and return functionality (#6, #7) and team documentation (#20).

### Blockers and decisions

- No outstanding development blockers reported.
- Team members could not update issue statuses on the GitHub Project board because they had repository access but not Project access.
- Giorgi granted Project Admin access to the team, resolving the permissions issue.

### Next steps

- Continue Sprint 1 work and keep the GitHub Project board updated.
- Review pending pull requests and coordinate shared database and API interfaces.

## 2026-11-02 - Daily Scrum and Sprint Planning 2

### Team updates

- **Daniel:** Continued database validation and Open Library integration. PRs #28 and #25 were reviewed and merged during the day.
- **Gowtami:** Continued book catalogue development (#3), with PR #29 awaiting integration.
- **Robert:** Opened PRs #37 (browse/search) and #38 (member registration).
- **Giorgi:** Approved the updated database validation PR #28, completed integration of loan and return functionality through PRs #30 and #31, and worked on API-key authentication (#33), merged through PR #39.

### Sprint Planning 2

**Date:** 2 November 2026

**Scrum roles**

- Product Owner: Daniel Nilsson.
- Scrum Master: Giorgi Dundua.
- The team agreed to retain the same roles for Sprint 2.

**Sprint Goal**

Deliver an integrated, usable Book Club Library application with working book and member management, borrowing and returns, external API integration, required reporting, authentication, and a Python client with a web GUI (Streamlit).

**Sprint Backlog and scope**

- Carry over all unfinished Sprint 1 stories and integration work.
- Complete the remaining required book and member management functionality, including browsing, searching, creation, updates and deletion.
- Integrate borrowing and returns with the shared SQLite database.
- Complete and integrate the Open Library external API functionality.
- Include API-key authentication (#33) and the Python client (#34), both added as technical issues on October 30.
- Include the required statistics and reporting functionality, including most-borrowed books (#12) and never-borrowed books (#13).
- Complete essential testing, integration and documentation.

**Responsibilities**

- Daniel: Database and external API integration, member-related backend functionality and reviews.
- Gowtami: Book catalogue functionality and reviews.
- Robert: Catalogue browsing/search, member registration and other backend functionality.
- Giorgi: Loan and return functionality, API authentication, reporting, Streamlit client development, reviews and integration.

The team coordinated responsibilities during planning, with individual issue assignments continuing as work progressed during the sprint.

**Estimates and priorities**

- Discussed the remaining workload and available time.
- Agreed to attempt all remaining required functionality rather than deliberately exclude features from the sprint.
- Prioritized the most important functionality, working API integration, essential tests and a usable client.
- Recognized that development, peer reviews and integration would need to fit within the remaining project time.

### Blockers and decisions

- Integration depended on coordinating the shared database, API endpoints and client interfaces.

### Next steps

- Prioritize a functioning application before the November 5 feature freeze and hand-in.
- Continue developing, reviewing, and integrating core API functionality and outstanding features.
- Coordinate shared interfaces and integration across the system.
- Progress the Python API client (#34).
- Review and merge PRs after completing necessary corrections and testing.

## 2026-11-03 - Daily Scrum

### Team updates

- **Daniel:** Developed member update functionality (#15) and personal-data deletion/anonymization (#17). Reviewed Robert's PRs #37 and #38 and requested corrections.
- **Gowtami:** Opened PR #41 for book creation and worked through multiple rounds of review corrections.
- **Robert:** Continued browsing/search (#4) and member registration (#5), and opened PR #45 for book deletion (#11).
- **Giorgi:** Developed borrowing statistics (#12) and never-borrowed books (#13), opening PRs #42 and #43. Reviewed Daniel's PR #40 and Gowtami's PR #41, testing their implementations and requesting corrections. Continued work on the Streamlit client (#34).

### Integration and coordination

- Robert's original terminal/SQLite functions needed to be exposed as FastAPI endpoints for the Python client.
- Haithem approved Streamlit as an alternative client interface, using `requests` to communicate with FastAPI.
- PR #40 was approved following corrections and merged later that evening.
- PR #41 required further corrections and integration with the latest `main`.

### Next steps

- Complete pending PR reviews and corrections.
- Integrate remaining API endpoints and continue client development.
- Prepare for the November 5 feature freeze.

## 2026-11-04 - Daily Scrum

**Participants:** Daniel, Gowtami, Robert and Giorgi (all present).

### Team updates

- **Daniel:** Continued member and loan-related API development, including PRs #44, #46 and #48.
- **Gowtami:** Took responsibility for reviewing PRs #42 (most-borrowed statistics) and #43 (never-borrowed books). Continued book catalogue functionality.
- **Robert:** Continued work on browsing/search, member registration and book deletion.
- **Giorgi:** Completed integration of PR #41 with the latest `main`, including conflict resolution and testing. All 35 tests passed on the integrated branch. Continued Streamlit client development (#34).

### Discussion and decisions

- Reviewed the requirement that every team member must author at least three merged PRs and review at least three PRs.
- Gowtami agreed to complete the outstanding reviews of PRs #42 and #43.
- Giorgi pointed out that documentation PR #36 was also available for review.
- Giorgi asked Gowtami and Robert to coordinate their contributions and reviews so everyone could meet the minimum requirements.

### Follow-up after the meeting

- Gowtami reviewed and approved PRs #42 and #43 following requested improvements. Both were merged.
- Gowtami's book-detail and editing work was integrated through PRs #29 and #47, which were also merged.
- Daniel continued reviewing Robert's API implementations and requesting corrections.
- Further member and loan functionality remained under development and review.

### Next steps

- Complete remaining API features and reviews.
- Integrate the Streamlit client against the merged endpoints.
- Verify functionality and tests on `main`.
- Prepare the Sprint 2 retrospective, team reflection and final delivery.