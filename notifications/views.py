from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse

from notifications.models import NotificationModel


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
