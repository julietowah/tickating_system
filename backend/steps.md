## 1. Choose the implementation stack

  A practical FastAPI stack would be:

  - FastAPI and Uvicorn
  - SQLAlchemy for ORM
  - Alembic for migrations
  - SQLite for the exam database
  - Pydantic settings for environment configuration
  - An established password-hashing library using Argon2 or bcrypt
  - JWT bearer tokens
  - Pytest and HTTPX for testing

  Keep dependency versions pinned in requirements.txt or pyproject.toml.

  ## 2. Create the project structure

  backend/
  ├── app/
  │   ├── main.py
  │   ├── core/
  │   │   ├── config.py
  │   │   ├── security.py
  │   │   └── exceptions.py
  │   ├── db/
  │   │   ├── base.py
  │   │   └── session.py
  │   ├── models/
  │   │   ├── user.py
  │   │   ├── ticket.py
  │   │   └── comment.py
  │   ├── schemas/
  │   │   ├── auth.py
  │   │   ├── user.py
  │   │   ├── ticket.py
  │   │   └── comment.py
  │   ├── routes/
  │   │   ├── auth.py
  │   │   ├── users.py
  │   │   └── tickets.py
  │   ├── dependencies/
  │   │   ├── auth.py
  │   │   └── permissions.py
  │   └── services/
  │       ├── auth.py
  │       └── tickets.py
  ├── migrations/
  ├── scripts/
  │   └── create_admin.py
  ├── tests/
  ├── alembic.ini
  ├── .env.example
  ├── .gitignore
  ├── requirements.txt
  └── README.md

  ## 3. Add configuration

  Put configurable values in environment variables:

  DATABASE_URL=sqlite:///./service_desk.db
  SECRET_KEY=replace-with-a-secure-random-value
  ACCESS_TOKEN_EXPIRE_MINUTES=60

  Commit .env.example, but do not commit the real .env or SQLite database.

  ## 4. Define the database models

  ### User

  - id
  - full_name
  - email, normalized and unique
  - password_hash
  - role: user or admin
  - created_at

  Never accept role from public registration. New registrations should always become normal users.

  ### Ticket

  - id
  - title
  - description
  - priority: low, medium, or high
  - status: open, in_progress, or resolved
  - owner_id, foreign key to users
  - created_at
  - updated_at

  New tickets should automatically start as open.

  ### Comment

  - id
  - ticket_id, foreign key to tickets
  - author_id, foreign key to users
  - body
  - created_at

  Add relationships and database constraints, then create an Alembic migration. Do not depend only on Base.metadata.create_all() for the final
  submission.

  ## 5. Create Pydantic schemas and validation

  Use separate input and output schemas so sensitive fields cannot leak.

  Required validation:

  - Valid, unique email address
  - Reasonable password length, such as at least 8 characters
  - Ticket title between 5 and 120 characters
  - Ticket description of at least 20 characters
  - Priority and status restricted to their enums
  - Comment body must contain non-whitespace text

  Do not include password_hash in any response schema.

  Create separate ticket update schemas:

  - TicketContentUpdate: title, description and priority
  - TicketStatusUpdate: status only

  That separation makes admin-only status authorization easier to enforce.

  ## 6. Implement authentication

  Required flow:

  1. Register a user.
  2. Hash the password before database insertion.
  3. Login by email and password.
  4. Issue a signed JWT containing the user ID and expiration.
  5. Read the bearer token on protected endpoints.
  6. Load the current user from the database.
  7. Reject missing, expired or invalid tokens with HTTP 401.

  Recommended authentication endpoints:

   Method    Endpoint          Purpose
  ━━━━━━━━  ━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   POST      /auth/register    Register a normal user
  ────────  ────────────────  ──────────────────────────────────
   POST      /auth/login       Return an access token
  ────────  ────────────────  ──────────────────────────────────
   GET       /users/me         Return the authenticated profile

  Use the same generic login error for an unknown email and an incorrect password.

  ## 7. Centralize authorization rules

  Create reusable dependencies or service functions such as:

  - get_current_user
  - require_admin
  - get_visible_ticket

  The permission rules should be:

   Operation               Normal user           Administrator
  ━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━
   Create ticket           Yes                   Yes
  ──────────────────────  ────────────────────  ───────────────
   List tickets            Own only              All
  ──────────────────────  ────────────────────  ───────────────
   Retrieve ticket         Own only              Any
  ──────────────────────  ────────────────────  ───────────────
   Edit ticket content     Own, if unresolved    Any
  ──────────────────────  ────────────────────  ───────────────
   Change ticket status    No                    Any
  ──────────────────────  ────────────────────  ───────────────
   Add comment             Own visible ticket    Any
  ──────────────────────  ────────────────────  ───────────────
   Delete ticket           Prefer admin-only     Any

  The specification is slightly flexible about owner deletion. Making deletion administrator-only is the simplest clearly compliant policy.
  Document that decision in the README.

  For another user’s ticket, consistently return either 403 or 404. Returning 404 avoids revealing that the ticket exists.

  ## 8. Implement ticket endpoints

  A clean route design would be:

   Method    Endpoint                         Behaviour
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   POST      /tickets                         Create a ticket
  ────────  ───────────────────────────────  ───────────────────────────────
   GET       /tickets                         Paginated and filtered list
  ────────  ───────────────────────────────  ───────────────────────────────
   GET       /tickets/{ticket_id}             Retrieve an accessible ticket
  ────────  ───────────────────────────────  ───────────────────────────────
   PATCH     /tickets/{ticket_id}             Update ticket content
  ────────  ───────────────────────────────  ───────────────────────────────
   PATCH     /tickets/{ticket_id}/status      Admin-only status change
  ────────  ───────────────────────────────  ───────────────────────────────
   DELETE    /tickets/{ticket_id}             Admin-only deletion
  ────────  ───────────────────────────────  ───────────────────────────────
   POST      /tickets/{ticket_id}/comments    Add a comment
  ────────  ───────────────────────────────  ───────────────────────────────
   GET       /tickets/{ticket_id}/comments    Return accessible comments

  For listing, support parameters such as:

  GET /tickets?page=1&page_size=20&status=open&priority=high

  Return pagination metadata:

  {
    "items": [],
    "page": 1,
    "page_size": 20,
    "total": 0
  }

  Always apply the ownership filter for normal users before pagination.

  ## 9. Use meaningful HTTP responses

  Recommended status codes:

  - 201 Created for registration, tickets and comments
  - 200 OK for retrieval, login and updates
  - 204 No Content for deletion
  - 401 Unauthorized for missing or invalid authentication
  - 403 Forbidden for an authenticated user lacking permission
  - 404 Not Found for missing or intentionally hidden resources
  - 409 Conflict for duplicate email
  - 422 Unprocessable Entity for request validation errors

  Use one predictable error structure, for example:

  {
    "error": {
      "code": "forbidden",
      "message": "You do not have permission to perform this action",
      "details": null
    }
  }

  FastAPI’s validation and HTTP exception handlers can be overridden to produce this consistently.

  ## 10. Add the health endpoint

  GET /health

  Expected response:

  {
    "status": "ok"
  }

  It should return 200 without authentication and avoid expensive operations.

  ## 11. Provide an administrator creation method

  Add an idempotent command or script:

  python -m scripts.create_admin

  It can read the administrator’s name, email and password from environment variables or prompt securely for the password. It must:

  - Hash the password
  - Assign the admin role
  - Reject or safely handle an existing email
  - Never place default credentials in source control

  Document the exact command in the README.

  ## 12. Write automated tests

  The brief requires at least eight; aim for 12–15. Include:

  1. Successful registration
  2. Duplicate email rejection
  3. Successful login
  4. Invalid login rejection
  5. Protected endpoint without a token
  6. Valid ticket creation
  7. Invalid short title or description
  8. Owner can retrieve their ticket
  9. Another user cannot retrieve it
  10. Owner can edit an unresolved ticket
  11. Owner cannot edit a resolved ticket
  12. Normal user cannot change status
  13. Admin can change status
  14. Comment creation and blank-comment rejection
  15. Pagination/filter behaviour
  16. Missing ticket response

  Use a separate temporary test database and dependency overrides so tests never modify the development database.

  ## 13. Finish the README

  The README must contain:

  - Candidate name
  - FastAPI as the selected framework
  - Supported Python version
  - Installation command
  - Environment setup
  - Migration command
  - Exact startup command
  - Exact test command
  - Authentication format
  - Endpoint summary
  - Admin creation instructions
  - Known limitations or incomplete requirements

  Also mention that interactive documentation is available at /docs and /redoc.

  ## 14. Final verification order

  Before submission, verify:

  1. Delete or move the local database and reproduce it from migrations.
  2. Start the application using only README instructions.
  3. Create an admin using the documented method.
  4. Run the complete test suite.
  5. Manually exercise authentication and permissions through /docs.
  6. Confirm password hashes never appear in responses.
  7. Confirm another user cannot access someone else’s ticket.
  8. Confirm only admins can change status.
  9. Check .gitignore excludes .env, databases, virtual environments and caches.
  10. Clone the repository into a fresh directory and repeat setup.

  A sensible implementation order is: project setup → models and migrations → authentication → ticket CRUD → authorization → comments → filters/
  pagination → error normalization → tests → README and clean-run verification.


Use this requirements.txt for the FastAPI project:

  fastapi>=0.115,<1.0
  uvicorn[standard]>=0.30,<1.0

  SQLAlchemy>=2.0,<3.0
  alembic>=1.13,<2.0

  pydantic-settings>=2.5,<3.0
  email-validator>=2.2,<3.0
  python-dotenv>=1.0,<2.0

  pwdlib[argon2]>=0.2,<1.0
  PyJWT>=2.9,<3.0
  python-multipart>=0.0.9,<1.0

  pytest>=8.0,<10.0
  httpx>=0.27,<1.0

  
- fastapi: API framework
  - uvicorn: development/application server
  - SQLAlchemy: database ORM
  - alembic: database migrations
  - pydantic-settings: environment configuration
  - email-validator: supports Pydantic EmailStr
  - python-dotenv: loads .env files
  - pwdlib[argon2]: secure password hashing
  - PyJWT: JWT access tokens
  - python-multipart: OAuth2 form-based login support
  - pytest: automated tests
  - httpx: FastAPI test client support