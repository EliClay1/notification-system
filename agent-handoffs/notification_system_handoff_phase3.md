# Django Real-Time Notification System: Project Guide and Agent Handoff

## Purpose and mandatory guidance for the next agent

Guide the learner through building a Django real-time notification system **one exercise at a time**. This is a learning project, **not a request for complete implementation**. Explain only what is needed for the current exercise, give concrete requirements and a small number of meaningful tests, review submitted code, and advance when the exercise is complete. **Do not provide complete implementations unless explicitly requested.**

**CURRENT PROGRESS MARKER: Phases 1 and 2 are COMPLETE. Next: Phase 3, Exercise 3.1 (not yet started).** Do not revisit indexes, signals, commit callbacks, or prior test corrections unless the learner raises a current issue. The user explicitly confirmed that the final Phase 2 tests pass and requested this handoff. Start the next conversation with the first small Phase 3 exercise, not with a review of Phase 2.

### Anti-spiral rules: especially important

1. **Keep the scope narrow.** Give one exercise with a clear goal, minimal implementation requirements, and 2–4 focused test expectations. No sprawling sub-exercises or speculative future architecture.
2. **Do not gate progress on trivia.** Ask conceptual questions only when essential to the exercise. Do not repeatedly ask for explanations of minor index ordering, callback edge cases, or other already-finished concepts.
3. **Honor completion.** When the learner says tests pass and source demonstrates the objective, mark the exercise complete and move forward. Optional polish is not a reason to stall.
4. **Review precisely and briefly.** Identify genuine correctness issues, distinguish observed source from reported test results, and avoid rewriting entire files or proposing unrelated improvements.
5. **No full solutions by default.** Prefer concise hints and relevant Django APIs, allowing the learner to write the implementation.
6. **Avoid unnecessary requests for more files or confirmation.** Use material already in the conversation; ask for code only when needed to assess the current exercise.
7. **Prioritize practical Django concepts** and incremental progress toward a working notification system over exhaustive treatment of PostgreSQL or framework internals.
8. **Keep explanations short (preferably 1–3 focused paragraphs)** unless the learner asks for depth. No repetitive recaps.

## Technology and environment

- Django 6.1.3 and Python 3.15.0 (as reported in prior pytest output)
- PostgreSQL with `psycopg`
- pytest 9.2.0 and pytest-django 4.14.0; `pytest-mock` used in Phase 2
- `uv` dependency management
- Django settings module: `project.settings` (project package `project/`, not `config/`)
- Django app: `notifications`
- Planned later technologies: Django Channels, Redis, React
- Environment secrets in gitignored `.env`; `django-environ` configured in Django settings

Prior project initialization and migrations were verified by the learner. Test outcomes reported as passing have generally **not** been independently executed by an agent; reviews were based on submitted code and learner reports.

## Six-phase roadmap and current status

| Phase | Work | Core concepts | Status |
|---|---|---|---|
| 1 | Notification model, QuerySets, ORM performance, indexes | Models, relationships, lazy evaluation, N+1, query plans | **COMPLETE** |
| 2 | Notification events and services | Signals, service layer, `atomic()`, `on_commit()`, integration tests | **COMPLETE** |
| 3 | Notification API and request diagnostics | Views, URL routing, auth/session access, CSRF, middleware, sync/async | **NEXT** |
| 4 | Real-time WebSocket delivery | ASGI, Channels, Redis, consumers, authorization, async DB access | Not started |
| 5 | React notification interface in Django dashboard | Templates, static assets, CSRF, UI integration | Not started |
| 6 | Advanced testing and concurrency | Async tests, mocking, `F()`, locks, `select_for_update()` | Not started |

The original timeline estimated 15–25 hours; learner pace takes precedence.

## Phase 1: COMPLETE

### Exercise 1.1: Project initialization — COMPLETE
Django project, `notifications` app, PostgreSQL, migrations, environment-based secrets, pytest-django configuration.

### Exercise 1.2: Notification model — COMPLETE
`NotificationModel` includes:
- `recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')`
- `type` with nested `NotificationType(models.TextChoices)`: `NORMAL='1'`, `IMPORTANT='2'`, `CRITICAL='3'`
- `message = models.CharField(max_length=500)`
- `created_at = models.DateTimeField(auto_now_add=True)`
- `is_read = models.BooleanField(default=False)`
- `Meta.ordering = ['-created_at']`
- `__str__` involving recipient username and message

Model tests covered creation, timestamp, relationships, deletion, and ordering.

### Exercise 1.3: Custom QuerySets — COMPLETE
`NotificationQuerySet` has `.unread()` (`is_read=False`), `.for_user(user)` (`recipient=user`), and `.recent()` (`order_by('-created_at', '-pk')[:10]`). It is exposed using `.as_manager()`. Tests covered chaining, ordering, and lazy evaluation.

### Exercise 1.4: N+1 query performance — COMPLETE
A fixture built 100 notifications for 10 users. Tests demonstrated 101 queries without optimization, 1 with `select_related('recipient')`, and 2 with `prefetch_related('recipient')`; same resulting data.

### Exercise 1.5: Indexes and query planning — COMPLETE
Learner inspected PostgreSQL indexes, captured Django `.explain()` plans, and successfully migrated a composite B-tree index suitable for `for_user(user).unread().recent()`. Verified SQL index definition:

```sql
CREATE INDEX notificatio_recipie_8d067d_idx
ON public.notifications_notificationmodel
USING btree (recipient_id, is_read, created_at DESC, id DESC);
```

The baseline test plan used the existing recipient FK index with a separate unread filter and sort. The learner explicitly asked the prior agent to stop digging into indexing minutiae and move on; Phase 1 was declared complete. Do **not** reopen this exercise.

## Phase 2: COMPLETE

### Exercise 2.1: Django signals — COMPLETE
- `notifications/signals.py` registers a `post_save` receiver for `django.contrib.auth.models.User`, creating one welcome notification only when `created=True`.
- `notifications/apps.py` imports signals in `NotificationsConfig.ready()`.
- Signal tests verify one welcome notification on creation and none extra on update.
- Creating users began affecting older model test counts. Learner built a setup/teardown fixture that disconnects/reconnects the receiver for unrelated tests.
- **Important current test setup:** learner subsequently configured the signal disabler **globally by default**, with a custom pytest marker to enable it for signal-dependent tests. Do not instruct the learner to add the same fixture again.

### Exercise 2.2: Notification service layer — COMPLETE
- `notifications/services.py` has `create_notification(recipient, message, notification_type='1')`; saves and returns a `NotificationModel` instance.
- Welcome signal calls this service instead of creating the model directly.
- Tests verify return type, recipient, message, default and explicit type, and persistence. Learner reported passing.

### Exercise 2.3: Database transactions — COMPLETE
- Tests create two notifications inside successful `transaction.atomic()` and verify both persist.
- Failed transaction raises `RuntimeError` inside `atomic()` and catches it outside, verifying rollback.
- Learner correctly explained that an ordinary exception caught and suppressed **inside** `atomic()` can allow the block to commit normally. Exercise marked complete.

### Exercise 2.4: `transaction.on_commit()` — COMPLETE
Latest reviewed service structure:

```python
notification = NotificationModel.objects.create(
    recipient=recipient, message=message, type=notification_type
)
transaction.on_commit(lambda: publish_notification(notification))
return notification
```

- `publish_notification(notification)` currently **logs** a publishing message; no WebSocket infrastructure exists yet. This is an intentional placeholder.
- Commit tests use `@pytest.mark.django_db(transaction=True)` and mock `notifications.services.publish_notification` with `pytest-mock`.
- Tests cover successful commit, rollback, and immediate execution without an active transaction. Prior agent suggested checking the callback had not yet run while inside the transaction; learner reported all relevant tests passing.
- Earlier source included an unnecessary `if notification is None: return` check after `.objects.create()`. This is optional cleanup, **not a blocker**.

### Exercise 2.5: Integration testing — COMPLETE
Last submitted `test_integration.py` contained:
- Class marked `@pytest.mark.keep_user_signal` and `@pytest.mark.django_db(transaction=True)`.
- `test_successful_user_creation`: creates a user inside `atomic()`, asserts a welcome notification exists but publishing has not happened; after commit, asserts publisher called once.
- `test_failed_user_creation`: raises a `RuntimeError` inside `atomic()`, catches outside, asserts nothing published and the welcome notification does not persist.
- `test_multi_notification_creation`: uses `@pytest.mark.disable_user_signal`, creates 3 notifications inside `atomic()`, verifies no publishing inside; after commit, checks notification count and publishing.

The agent requested two small improvements: explicitly assert the user itself is absent after rollback, and replace weak `mock_publish.assert_called()` in the third test with `assert mock_publish.call_count == 3`. **The learner explicitly confirmed that those corrections are complete and all tests pass.** Do not request them again. The revised file was not reuploaded, so the exact new source was not independently inspected.

Crucial concept learned: with `transaction.on_commit(..., robust=False)` (default), if a callback raises, later callbacks are skipped and the exception propagates, **but the database has already committed and cannot be rolled back by catching that callback exception**. With `robust=True`, Django catches/logs ordinary exceptions and continues later callbacks. This was clarified at the end of Phase 2. Do not quiz on this again unless directly relevant.

**PHASE 2 IS COMPLETE. ALL TESTS REPORTED PASSING BY LEARNER.**

## Phase 3: Notification API and Request Diagnostics — NEXT

**Objective:** Expose notifications safely over authenticated HTTP endpoints and learn Django's request-response lifecycle, including middleware, sessions, CSRF, and (later in this phase) sync/async views.

Suggested incremental progression, not an obligation to assign all at once:

1. **Exercise 3.1: First authenticated read-only notification endpoint.** Implement a basic Django view and URL that returns the current logged-in user's notifications (e.g. JSON with ID, message, type, `created_at`, `is_read`). Require authentication, filter by `request.user`, and test that an authenticated user sees only their own notifications while an anonymous request is rejected or redirected according to the chosen auth approach. Keep design minimal: built-in Django views / `JsonResponse` are sufficient, do not introduce Django REST Framework unless the learner requests it.
2. **Exercise 3.2: Notification state update endpoint.** Add mark-as-read behavior, verify ownership, require an appropriate HTTP method, and cover CSRF/session implications and denial for other users' notifications.
3. **Exercise 3.3: Request/response middleware.** Implement focused diagnostic middleware and test behavior for normal responses and exceptions from views.
4. **Exercise 3.4: Sync and async request handling.** Introduce the main distinction and a small applicable test, without preemptively building Channels.
5. **Exercise 3.5: Short integration review.** Verify authenticated requests, response contents, unauthorized access, CSRF where relevant, and middleware diagnostics; conclude Phase 3.

Keep this flexible. Adapt to existing project URLs, user preferences, and code submissions. Do not introduce pagination, serializers, permissions frameworks, performance benchmarks, advanced auth design, or frontend work unless needed for the current objective.

### Immediate next response expected

Begin **Exercise 3.1 only**. Briefly explain that a Django view receives a request and returns an HTTP response. Ask the learner to add one authenticated endpoint for listing **only the logged-in user's** notifications using the existing `for_user()` QuerySet and to write two or three focused tests (own notifications, isolation from another user, anonymous access). Mention URL routing and `JsonResponse` as relevant APIs. Let the learner choose the implementation; do **not** supply a finished view. Ask for the view, URL mapping, and tests when ready. Do not ask for Phase 2 work or recap completed exercises beyond a one-sentence transition.

## Review and mentoring contract

- The user prefers **minimal context, plain correction, no fluff**, and has explicitly asked that the new agent **not spiral**.
- Advance one exercise at a time. Be concise, concrete, and practical; avoid exploratory chains of tangential questions.
- Review uploaded code carefully, distinguish confirmed code from learner-reported test results, and point out only material correctness failures.
- Do not make a completed task contingent on nonessential polish, extra questions, or hypothetical production concerns.
- No full code solutions unless requested. Small API examples or targeted corrections are acceptable.
- Prefer deterministic pytest tests; use existing signal marker/fixture configuration rather than recreating it.
- If a needed source file is not available, ask for that specific file; do not claim you inspected unseen revisions.
