/**
 * Функционал для работы с избранными захоронениями
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация списка избранных
    initFavoritesList();
});

/**
 * Инициализация списка избранных захоронений
 */
function initFavoritesList() {
    const favoritesList = document.getElementById('favorites-list');
    if (!favoritesList) return;
    
    // Загрузка списка избранных захоронений
    loadFavorites();
    
    // Инициализация кнопки удаления из избранного
    document.querySelectorAll('.remove-favorite-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const graveId = this.dataset.graveId;
            removeFavorite(graveId);
        });
    });
}

/**
 * Загрузка списка избранных захоронений
 */
function loadFavorites() {
    if (!checkAuthStatus()) {
        return;
    }
    
    fetch('/api/favorites/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при загрузке избранных захоронений');
            }
            return response.json();
        })
        .then(data => {
            displayFavorites(data);
        })
        .catch(error => {
            console.error('Ошибка при загрузке избранных захоронений:', error);
            showNotification('Ошибка при загрузке избранных захоронений', 'error');
        });
}

/**
 * Отображение списка избранных захоронений
 */
function displayFavorites(favorites) {
    const favoritesList = document.getElementById('favorites-list');
    if (!favoritesList) return;
    
    if (favorites.length === 0) {
        favoritesList.innerHTML = '<p class="text-center">У вас пока нет избранных захоронений</p>';
        return;
    }
    
    let html = '';
    favorites.forEach(favorite => {
        const grave = favorite.grave_detail;
        
        let dates = '';
        if (grave.birth_date && grave.death_date) {
            dates = `${formatDate(grave.birth_date)} - ${formatDate(grave.death_date)}`;
        } else if (grave.birth_date) {
            dates = `Родился: ${formatDate(grave.birth_date)}`;
        } else if (grave.death_date) {
            dates = `Умер: ${formatDate(grave.death_date)}`;
        }
        
        html += `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">${grave.full_name}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">${dates}</h6>
                    <p class="card-text">${grave.description || 'Описание отсутствует'}</p>
                    <div class="d-flex justify-content-between">
                        <a href="/graves/map/?grave_id=${grave.id}" class="btn btn-sm btn-primary">Показать на карте</a>
                        <button data-grave-id="${grave.id}" class="btn btn-sm btn-outline-danger remove-favorite-btn">
                            Удалить из избранного
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    favoritesList.innerHTML = html;
    
    // Повторно добавляем обработчики кнопок после обновления DOM
    document.querySelectorAll('.remove-favorite-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const graveId = this.dataset.graveId;
            removeFavorite(graveId);
        });
    });
}

/**
 * Удаление захоронения из избранного
 */
function removeFavorite(graveId) {
    if (!checkAuthStatus()) {
        showNotification('Необходимо авторизоваться', 'warning');
        return;
    }
    
    fetch(`/api/favorites/${graveId}/remove/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка при удалении из избранного');
        }
        
        // Обновляем список избранных
        loadFavorites();
        
        showNotification('Захоронение удалено из избранного', 'success');
    })
    .catch(error => {
        console.error('Ошибка при удалении из избранного:', error);
        showNotification('Ошибка при удалении из избранного', 'error');
    });
}

/**
 * Добавление захоронения в избранное
 */
function addToFavorites(graveId) {
    if (!checkAuthStatus()) {
        showNotification('Необходимо авторизоваться', 'warning');
        return;
    }
    
    fetch('/api/favorites/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            grave: graveId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка при добавлении в избранное');
        }
        return response.json();
    })
    .then(data => {
        showNotification('Захоронение добавлено в избранное', 'success');
    })
    .catch(error => {
        console.error('Ошибка при добавлении в избранное:', error);
        showNotification('Ошибка при добавлении в избранное', 'error');
    });
}

/**
 * Форматирование даты в локальный формат
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

/**
 * Проверка статуса аутентификации пользователя
 */
function checkAuthStatus() {
    // Если в DOM есть элемент с data-attribute userAuthenticated
    const authStatus = document.body.dataset.userAuthenticated;
    return authStatus === 'true';
}

/**
 * Получение CSRF-токена для защищенных запросов
 */
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

/**
 * Отображение уведомления
 */
function showNotification(message, type = 'info') {
    // Проверяем, существует ли контейнер для уведомлений
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // Создаем контейнер для уведомлений
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = message;
    notification.style.marginBottom = '10px';
    
    // Добавляем кнопку закрытия
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'close';
    closeButton.innerHTML = '&times;';
    closeButton.style.marginLeft = '10px';
    closeButton.addEventListener('click', function() {
        notificationContainer.removeChild(notification);
    });
    
    notification.appendChild(closeButton);
    
    // Добавляем уведомление в контейнер
    notificationContainer.appendChild(notification);
    
    // Автоматически удаляем уведомление через 5 секунд
    setTimeout(function() {
        if (notification && notification.parentNode === notificationContainer) {
            notificationContainer.removeChild(notification);
        }
    }, 5000);
}
