from .models import Notification

def create_notification(user, message, notification_type='system', related_id=None):
    """
    Создание нового уведомления для пользователя
    
    Args:
        user: Пользователь, которому предназначено уведомление
        message: Текст уведомления
        notification_type: Тип уведомления (system, edit_proposal, proposal_status)
        related_id: ID связанной сущности (например, ID предложения редактирования)
    
    Returns:
        Созданное уведомление
    """
    notification = Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        related_id=related_id
    )
    return notification


def create_proposal_status_notification(user, proposal, status):
    """
    Создание уведомления о статусе предложения редактирования
    
    Args:
        user: Пользователь, которому предназначено уведомление
        proposal: Предложение редактирования
        status: Статус предложения (approved/rejected)
    
    Returns:
        Созданное уведомление
    """
    grave_name = proposal.grave.full_name
    
    if status == 'approved':
        message = f'Ваше предложение по редактированию описания захоронения "{grave_name}" было одобрено.'
    else:
        message = f'Ваше предложение по редактированию описания захоронения "{grave_name}" было отклонено.'
        if proposal.rejection_reason:
            message += f' Причина: {proposal.rejection_reason}'
    
    return create_notification(
        user=user,
        message=message,
        notification_type='proposal_status',
        related_id=proposal.id
    )
