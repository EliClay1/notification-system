from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_POST

from notifications.models import NotificationModel


def serialized_notification(notification: NotificationModel):
    return {
        "id": notification.pk,
        "message": notification.message,
        "type": notification.type,
        "created_at": notification.created_at,
        "is_read": notification.is_read,
    }


@login_required
def authenticated_user_notifications(request: HttpRequest) -> JsonResponse:

    all_data = []
    for notification in NotificationModel.objects.for_user(request.user):
        notification: NotificationModel

        data = {
            "id": notification.pk,
            "message": notification.message,
            "type": notification.type,
            "created_at": notification.created_at,
            "is_read": notification.is_read,
        }
        all_data.append(data)
    return JsonResponse(all_data, safe=False)


@require_POST
@login_required
def mark_notification_read(request: HttpRequest, id: int) -> HttpResponse:
    notification = (
        NotificationModel.objects.for_user(request.user).filter(pk=id).first()
    )
    if notification is None:
        return HttpResponseNotFound(
            f"Notification {id} for user {request.user.get_username()} doesn't exist.",
            content_type="application/json",
        )

    assert isinstance(notification, NotificationModel)

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    return JsonResponse(
        {"success": True, "notification": serialized_notification(notification)}
    )


@sync_to_async
@login_required
def get_unread_notifications(request: HttpRequest) -> HttpResponse:
    count = NotificationModel.objects.for_user(request.user).unread().count()
    return JsonResponse({"success": True, "count": count})
