import pytest
from django.contrib.auth.models import User
from django.db.models import signals

from notifications.signals import on_user_creation


@pytest.fixture(autouse=True)
def disconnect_user_signal(request):
    if request.node.get_closest_marker("keep_user_signal"):
        yield
        return
    signals.post_save.disconnect(
        receiver=on_user_creation,
        sender=User,
    )

    yield

    signals.post_save.connect(
        receiver=on_user_creation,
        sender=User,
    )
