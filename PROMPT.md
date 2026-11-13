# System Prompt
Answer explanation questions in no more than three clear, focused paragraphs. Start with the main idea, then explain how the relevant parts work and lead to the result. Define technical terms in context and connect the explanation to the details the user provided. Adjust the depth to the request; avoid unrelated background, unnecessary analogies, and code unless requested. If the topic needs more explanation, break it into stages and continue in follow-up replies.

# Project Prompt
I'd recommend building the Real-Time Notification System in stages, with each stage introducing a different Django internal and requiring you to write tests that verify its behavior.
The goal shouldn't just be to get notifications working. It should be to understand how Django handles requests, database transactions, asynchronous execution, and application events.
Stack: Django, PostgreSQL, Django Channels, Redis, React, pytest-django
Estimated time: 15–25 hours
```
Django Templates
       |
       +-- React Notification Component
                    |
                    | WebSocket
                    v
              Django Channels
                    |
               Redis Layer
                    |
              Django Backend
                    |
              PostgreSQL
```
I'd split this into six phases.

Phase

Implementation

Django concepts

1

Notification models and services

ORM, managers, QuerySets

2

Notification event handling

Signals, transactions, on_commit()

3

Notification API

Middleware, authentication, async views

4

Real-time delivery

ASGI, Channels, WebSockets, Redis

5

React notification interface

Django templates, static assets, CSRF

6

Advanced testing

Async tests, transaction tests, mocking
Start by implementing a notification model with:
- A recipient
- A notification type
- A message
- A timestamp
- A read/unread status
Then create a custom QuerySet and manager to support operations such as:
```scss
Notification.objects.unread()
Notification.objects.for_user(user)
Notification.objects.recent()
```
Learning objectives:
Understand lazy QuerySet evaluation, database query construction, custom managers, indexes, and the differences between select_related() and prefetch_related().
Testing challenge: Verify that retrieving 100 notifications doesn't result in 100 additional database queries.
Introduce events that generate notifications.
For example, creating a comment on a project should generate a notification for the project's owner.
Implement this first using Django signals, then refactor it into an explicit service function.
Compare the approaches.
Learning objectives:
- How Django registers and dispatches signals
- Why signals can create hidden dependencies
- How transaction.atomic() works
- How transaction.on_commit() prevents external side effects from occurring before a transaction commits
Testing challenge: Verify that a rolled-back transaction does not publish a notification event.
Implement an API that retrieves and updates notifications.
Add custom middleware that measures request execution time and records diagnostic information.
Learning objectives:
- Django's request-response lifecycle
- Middleware execution order
- Authentication and session handling
- Sync versus async views
- CSRF protection
Testing challenge: Verify middleware behavior when a view raises an exception.
This is where the project becomes particularly interesting.
Implement WebSocket connections that deliver notifications immediately.
Learning objectives:
- Differences between WSGI and ASGI
- How Django Channels routes WebSocket connections
- Async consumers
- Redis channel layers
- Sync-to-async database access
- WebSocket authentication and authorization
Testing challenge: Verify that a notification intended for User A cannot be received by User B.
Also test disconnects, reconnects, and unauthorized connections.
Create a Django-rendered dashboard containing a React notification component.
React will handle:
- Establishing the WebSocket connection
- Displaying notifications
- Tracking unread counts
- Marking notifications as read
- Reconnecting after connection failures
Django will handle page routing, authentication, templates, and the notification API.
This will teach you how to integrate React into an existing Django application without turning the entire frontend into a single-page application.
Once the application works, concentrate on understanding the behavior of the framework.
Write tests covering:

Test

What it teaches

Query count assertions

ORM performance

Transaction rollback

Database atomicity

Signal dispatch

Django event handling

Middleware execution

Request lifecycle

Async consumer tests

Event loop behavior

WebSocket authorization

Security boundaries

Concurrent notification updates

Race conditions
For the concurrency tests, explore F() expressions, select_for_update(), and database locking.
Rather than providing you with a complete implementation, I'd suggest working through the project as a series of exercises.
For each phase:
1. Concept: Explain the Django internals involved.
2. Challenge: Give you a concrete feature to implement without providing the solution.
3. Tests: Define the expected behavior and edge cases.
4. Review: Examine your implementation and identify potential improvements.
5. Deep dive: Explore what Django is doing internally and why.
This would give you experience reading Django's source code, debugging framework behavior, and writing meaningful tests rather than simply following a tutorial.
I'd begin with a small Django project containing a notifications application.
Your first challenge would be to design the notification model, implement custom QuerySet methods, and write tests for their behavior.
Before introducing Channels or React, I'd want you to understand exactly when Django executes database queries and how to detect inefficient ORM usage.
One recommendation: Use PostgreSQL from the beginning rather than SQLite. It will make the later transaction, concurrency, and locking exercises more meaningful.
We can start with Phase 1, Exercise 1: Designing the notification data model, where I'll give you requirements and test cases but leave the implementation to you.