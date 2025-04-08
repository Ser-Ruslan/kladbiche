from django.utils.translation import gettext as _
from .models import Notification


def notify_user(user, notification_type, message, related_id=None):
    """
    Отправить уведомление пользователю
    
    Args:
        user: Объект пользователя, которому отправляется уведомление
        notification_type: Тип уведомления (system, edit_proposal, proposal_status)
        message: Текст уведомления
        related_id: ID связанной сущности (например, ID предложения редактирования)
    
    Returns:
        Созданное уведомление
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        related_id=related_id
    )
    
    return notification


def notify_user_about_proposal_status(proposal, approved=False):
    """
    Отправить уведомление пользователю о статусе его предложения редактирования
    
    Args:
        proposal: Объект предложения редактирования
        approved: Флаг, указывающий, одобрено ли предложение
    
    Returns:
        Созданное уведомление
    """
    if approved:
        message = _(f'Ваше предложение по редактированию описания захоронения "{proposal.grave.full_name}" было одобрено.')
    else:
        message = _(f'Ваше предложение по редактированию описания захоронения "{proposal.grave.full_name}" было отклонено.')
        if proposal.rejection_reason:
            message += _(' Причина: {0}').format(proposal.rejection_reason)
    
    return notify_user(
        user=proposal.user,
        notification_type='proposal_status',
        message=message,
        related_id=proposal.id
    )