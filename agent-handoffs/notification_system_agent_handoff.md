# Django Real-Time Notification System: Project Guide and Agent Handoff

## Purpose and instructions for the next agent

Guide the learner through building a Django real-time notification system **one exercise at a time**. This is a learning project, not a request for a complete implementation. Explain the relevant Django internals, define concrete requirements and tests, review the learner's submitted code, and advance only when the current exercise is complete. **Do not supply full solutions or implement features for the learner unless explicitly requested.** Keep guidance focused and allow the learner to investigate and write the code.

**Current progress marker: Phase 1, Exercise 1.5, Parts A and B (not yet submitted).** Exercises 1.1 through 1.4 have been reviewed and marked complete. The next agent should request or review the existing PostgreSQL indexes and the initial `QuerySet.explain()` output **before** asking the learner to add a composite index.

## Technology and environment

- Django 6.1.3, Python 3.15.0 (as reported in pytest output)
- PostgreSQL with `psycopg`
- pytest 9.2.0 and pytest-django 4.14.0
- `uv` dependency management
- Django settings module: `project.settings` (project package is `project/`, not `config/`)
- Django app: `notifications`
- Planned later technologies: Django Channels, Redis, React
- Environment secrets stored in `.env`, excluded by `.gitignore`; Django uses `django-environ` with `environ.Env(DEBUG=(bool, False))` and `environ.Env.read_env(BASE_DIR / '.env')`.

Project setup was verified by the learner: `./manage.py check` reported no issues, migrations were up to date, and pytest-django initialized successfully. Subsequent tests were reported passing by the learner; later reviews were based on submitted source, not independent execution.

## Overall six-phase roadmap

| Phase | Work | Django concepts | Key testing goal |
|---|---|---|---|
| 1 | Notification models, QuerySets, managers, ORM performance, indexes | Models, relationships, lazy evaluation, query planning | Avoid N+1 queries and inspect indexes |
| 2 | Notification events and services | Signals, transactions, `transaction.atomic()`, `on_commit()` | Rolled-back transactions must not publish external notification events |
| 3 | Notification API and request diagnostics | Middleware, authentication, sessions, sync/async views, CSRF | Middleware behavior when a view raises an exception |
| 4 | Real-time WebSocket delivery | ASGI, Channels, Redis channel layer, async consumers, DB bridging, authorization | User A's notification must never reach User B; disconnect/reconnect/unauthorized cases |
| 5 | React notification interface embedded in a Django-rendered dashboard | Templates, static assets, CSRF, frontend integration | Connection, display, unread count, mark-as-read, reconnection behavior |
| 6 | Advanced testing and concurrency | Async tests, transactions, mocking, `F()` expressions, `select_for_update()`, locks | Race conditions, rollback, authorization and query efficiency |

The original plan estimates 15–25 hours, but the learner's actual pace takes precedence.

## Completed Phase 1 exercises

### Exercise 1.1: Project initialization — COMPLETE

Django project and notifications app, PostgreSQL connection, migrations, environment-based secrets, and pytest-django configuration. Project uses `project.settings`. Initial `pytest` collected zero tests, as expected before tests were written.

### Exercise 1.2: Notification model — COMPLETE

Most recently reviewed model source (`models(1).py` uploaded in conversation) contains:

- `NotificationModel(models.Model)`
- Nested `NotificationType(models.TextChoices)` with `NORMAL='1'`, `IMPORTANT='2'`, `CRITICAL='3'`
- `recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')`
- `type = models.CharField(choices=NotificationType.choices, default=NotificationType.NORMAL)`
- `message = models.CharField(max_length=500)`
- `created_at = models.DateTimeField(auto_now_add=True)`
- `is_read = models.BooleanField(default=False)`
- `Meta.ordering = ['-created_at']`
- `__str__` returns recipient username and message.

Tests verify creation, default unread status, timestamp type, recipient relationship, cascade deletion, and default newest-first ordering. Ordering test assigns deterministic timestamps using `QuerySet.update()` rather than sleeping.

### Exercise 1.3: Custom QuerySets and managers — COMPLETE

Most recently reviewed model adds:

- `NotificationQuerySet(models.QuerySet)`
- `.unread()` filters `is_read=False`
- `.for_user(user)` filters `recipient=user`
- `.recent()` returns `self.order_by('-created_at', '-pk')[:10]`
- Manager exposed through `NotificationQuerySet.as_manager()`; learner used `cast(NotificationQuerySet, ...)` for static typing, although the runtime object is a Manager, not a QuerySet.

Tests cover unread, recipient filtering, recent limit and ordering, method chaining before slicing, and lazy evaluation with `django_assert_num_queries(0)` for constructing unsliced and sliced QuerySets and one query on evaluation.

Note: `recent()` slices, so further filtering after `.recent()` may not work; chaining filters before `.recent()` is appropriate.

### Exercise 1.4: ORM N+1 performance — COMPLETE

Latest submitted test file was `test_models(4).py`. A `notifications_100` fixture creates 10 users and 100 notifications, reusing stored user objects instead of querying for each one. Tests assert:

- No relationship optimization: **101** SQL queries for 100 notifications and their recipient usernames.
- `select_related('recipient')`: **1** SQL query.
- `prefetch_related('recipient')`: **2** SQL queries.
- Both optimized and unoptimized results contain identical notification IDs, messages and recipient usernames; QuerySets are converted to lists before comparison.

The learner uses `@pytest.mark.django_db`, plain pytest classes and `django_assert_num_queries`. The review marked Exercise 1.4 complete. Minor optional improvement: collect usernames instead of printing them inside the query-count tests.

## CURRENT EXERCISE: Phase 1, Exercise 1.5 — Database Indexes and Query Planning

**Objective:** Understand how PostgreSQL retrieves rows, when indexes help, and how to inspect query execution plans from Django.

### Part A: Inspect existing indexes (CURRENT)

Ask the learner to:

1. Inspect indexes PostgreSQL already created for the notification table.
2. Identify indexes created automatically by Django.
3. Determine whether `recipient`, `is_read`, and `created_at` are indexed.
4. Investigate how to inspect indexes through migrations or SQL.

### Part B: Capture an initial execution plan (CURRENT)

Ask the learner to:

1. Construct a QuerySet filtering by recipient and unread status.
2. Order the results newest first.
3. Call Django's `QuerySet.explain()` and save the output.
4. Identify whether PostgreSQL chooses a sequential scan, index scan, bitmap scan, or another strategy.

**Do not prescribe the final composite index until the learner has supplied Part A and Part B observations.** The prior agent explicitly set this as the next checkpoint.

### Part C: Add and evaluate an index (AFTER A/B REVIEW)

Guide the learner to investigate `models.Index`, choose fields and field order appropriate for the filtered-and-sorted query, create and apply a migration, and compare the new plan against the baseline. Explain that PostgreSQL may ignore indexes on small tables and chooses plans based on estimated cost. Do not demand that a specific index scan appear.

### Exercise 1.5 testing requirements

1. Query returns only unread notifications for the selected user.
2. Query returns newest first.
3. Composite index exists in PostgreSQL.
4. Query execution plan can be inspected with `explain()`.

Questions for the learner: Why does Django index most ForeignKeys? Why might a 100-row table use a sequential scan? How do single-column and composite indexes differ? Why does composite index column order matter? What are the write/storage costs of indexing?

Completion: existing indexes inspected; baseline plan captured; index migration applied; post-index plan captured; four tests written; plans compared with a reasoned explanation.

## Guidance style and review contract

- Focus on **guidance only**, not code generation or completing the learner's implementation.
- Review uploaded code precisely and distinguish confirmed source observations from claimed test results.
- Point out correctness issues and provide targeted exercises, not wholesale rewrites.
- Keep exercises incremental and avoid moving to later phases prematurely.
- It is acceptable for multiple behaviors to be tested in one function when assertions remain clear.
- Prefer deterministic test data and pytest-django's query-count fixture; avoid `sleep()` in ordering tests.
- If a specific earlier source file is needed and not present in the new agent's context, ask the learner to reattach it rather than claiming to have inspected it.

## Next response expected from the new agent

Continue with Exercise 1.5, Parts A and B. Ask the learner to share PostgreSQL's existing notification indexes and the initial query plan, or review those outputs if supplied. Do not restart the project or assign a new exercise yet.
