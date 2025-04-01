/**
 * Скрипт для работы с интерактивной картой кладбища
 * Использует Яндекс Карты API
 */

// Глобальные переменные
let map;
let currentMarker = null;
let burialMarkers = [];
let favoriteMarkerId = null;

// Инициализация карты
function initMap(centerLat, centerLng, apiKey) {
    // Проверяем, загружен ли API
    if (!window.ymaps) {
        console.error('Яндекс Карты API не загружен');
        return;
    }

    ymaps.ready(() => {
        // Создаем экземпляр карты
        map = new ymaps.Map('map', {
            center: [centerLat, centerLng],
            zoom: 17,
            controls: ['zoomControl', 'fullscreenControl', 'geolocationControl']
        });
        
        // Сохраняем ссылку на карту в глобальной переменной для доступа из других функций
        window.myMap = map;

        // Добавляем поисковую строку
        const searchControl = new ymaps.control.SearchControl({
            options: {
                provider: 'yandex#search',
                size: 'large'
            }
        });
        map.controls.add(searchControl);

        // Загружаем захоронения
        loadBurials();

        // Добавляем обработчик события клика по карте для админа или при добавлении нового захоронения
        if (document.getElementById('admin-mode') || document.getElementById('add-burial-mode')) {
            map.events.add('click', function (e) {
                // Получаем координаты щелчка
                const coords = e.get('coords');
                placeMarkerOnClick(coords);
            });
        }
    });
}

// Загрузка захоронений с сервера
function loadBurials(cemeteryId = null) {
    let url = '/api/burials/';
    
    // Если указан ID кладбища, добавляем параметр фильтрации
    if (cemeteryId) {
        url = `/api/burials/?cemetery_id=${cemeteryId}`;
    } else {
        // Если кладбище не указано, но есть селектор кладбищ, получаем выбранное кладбище
        const cemeterySelector = document.getElementById('cemetery-selector');
        if (cemeterySelector && cemeterySelector.value) {
            url = `/api/burials/?cemetery_id=${cemeterySelector.value}`;
        }
    }
    
    console.log('Загрузка захоронений с URL:', url);
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(`Загружено ${data.length} захоронений`);
            renderBurialsOnMap(data);
        })
        .catch(error => {
            console.error('Ошибка при загрузке захоронений:', error);
        });
}

// Отображение захоронений на карте
function renderBurialsOnMap(burials) {
    // Удаляем старые маркеры
    burialMarkers.forEach(marker => {
        map.geoObjects.remove(marker);
    });
    burialMarkers = [];

    // Добавляем новые маркеры
    burials.forEach(burial => {
        const marker = createBurialMarker(burial);
        map.geoObjects.add(marker);
        burialMarkers.push(marker);
    });
}

// Создание маркера захоронения
function createBurialMarker(burial) {
    const markerColor = burial.is_favorite ? '#f6ad55' : '#4a5568';
    
    const marker = new ymaps.Placemark(
        [burial.latitude, burial.longitude],
        {
            hintContent: burial.full_name,
            balloonContentHeader: burial.full_name,
            balloonContentBody: getBurialInfoHTML(burial),
            burialId: burial.id
        },
        {
            preset: 'islands#circleDotIcon',
            iconColor: markerColor
        }
    );

    marker.events.add('click', function() {
        // Открываем страницу с деталями захоронения
        window.location.href = `/burials/${burial.id}/`;
    });

    return marker;
}

// Формирование HTML для всплывающей подсказки о захоронении
function getBurialInfoHTML(burial) {
    let birthDate = burial.birth_date ? new Date(burial.birth_date).toLocaleDateString('ru-RU') : 'Неизвестно';
    let deathDate = burial.death_date ? new Date(burial.death_date).toLocaleDateString('ru-RU') : 'Неизвестно';
    
    return `
        <div class="burial-balloon">
            <p>Дата рождения: ${birthDate}</p>
            <p>Дата смерти: ${deathDate}</p>
            <a href="/burials/${burial.id}/" class="btn btn-primary btn-sm">Подробнее</a>
        </div>
    `;
}

// Добавление маркера при клике (для админов или при добавлении захоронения)
function placeMarkerOnClick(coords) {
    // Если маркер уже существует, удаляем его
    if (currentMarker) {
        map.geoObjects.remove(currentMarker);
    }

    // Создаем новый маркер
    currentMarker = new ymaps.Placemark(
        coords,
        {
            hintContent: 'Новое место'
        },
        {
            preset: 'islands#redDotIcon',
            draggable: true
        }
    );

    // Добавляем маркер на карту
    map.geoObjects.add(currentMarker);

    // Обновляем координаты в формах (могут быть две формы с разными ID)
    const userLatInput = document.getElementById('latitude');
    if (userLatInput) userLatInput.value = coords[0].toFixed(6);
    
    const userLngInput = document.getElementById('longitude');
    if (userLngInput) userLngInput.value = coords[1].toFixed(6);
    
    const adminLatInput = document.getElementById('admin-latitude');
    if (adminLatInput) adminLatInput.value = coords[0].toFixed(6);
    
    const adminLngInput = document.getElementById('admin-longitude');
    if (adminLngInput) adminLngInput.value = coords[1].toFixed(6);

    // При перетаскивании маркера обновляем координаты
    currentMarker.events.add('dragend', function () {
        const newCoords = currentMarker.geometry.getCoordinates();
        
        // Обновляем координаты в формах
        if (userLatInput) userLatInput.value = newCoords[0].toFixed(6);
        if (userLngInput) userLngInput.value = newCoords[1].toFixed(6);
        if (adminLatInput) adminLatInput.value = newCoords[0].toFixed(6);
        if (adminLngInput) adminLngInput.value = newCoords[1].toFixed(6);
    });
}

// Поиск захоронений
function searchBurials(query, options) {
    let url = `/api/burials/search/?query=${encodeURIComponent(query)}`;
    
    // Добавляем дополнительные параметры поиска
    if (options) {
        if (options.birthDateFrom) url += `&birth_date_from=${options.birthDateFrom}`;
        if (options.birthDateTo) url += `&birth_date_to=${options.birthDateTo}`;
        if (options.deathDateFrom) url += `&death_date_from=${options.deathDateFrom}`;
        if (options.deathDateTo) url += `&death_date_to=${options.deathDateTo}`;
        if (options.favoritesOnly) url += `&favorites_only=true`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Отображаем результаты поиска на карте
            renderBurialsOnMap(data);
            
            // Если есть результаты, центрируем карту на первом результате
            if (data.length > 0) {
                const firstBurial = data[0];
                map.setCenter([firstBurial.latitude, firstBurial.longitude], 18);
            }
            
            // Обновляем список результатов, если есть соответствующий контейнер
            const resultsContainer = document.getElementById('search-results');
            if (resultsContainer) {
                updateSearchResultsList(data, resultsContainer);
            }
        })
        .catch(error => {
            console.error('Ошибка при поиске захоронений:', error);
        });
}

// Обновление списка результатов поиска в DOM
function updateSearchResultsList(burials, container) {
    // Очищаем контейнер
    container.innerHTML = '';
    
    if (burials.length === 0) {
        container.innerHTML = '<p class="text-center">Ничего не найдено</p>';
        return;
    }
    
    // Создаем список результатов
    const ul = document.createElement('ul');
    ul.className = 'burial-list';
    
    burials.forEach(burial => {
        const li = document.createElement('li');
        li.className = 'burial-item';
        
        let birthDate = burial.birth_date ? new Date(burial.birth_date).toLocaleDateString('ru-RU') : 'Неизвестно';
        let deathDate = burial.death_date ? new Date(burial.death_date).toLocaleDateString('ru-RU') : 'Неизвестно';
        
        li.innerHTML = `
            <div>
                <div class="burial-name">${burial.full_name}</div>
                <div class="burial-dates">${birthDate} - ${deathDate}</div>
            </div>
            <a href="/burials/${burial.id}/" class="btn btn-outline btn-sm">Подробнее</a>
        `;
        
        // Добавляем обработчик клика для центрирования карты на захоронении
        li.addEventListener('click', function(e) {
            if (!e.target.closest('a')) {  // Игнорируем клик по кнопке
                map.setCenter([burial.latitude, burial.longitude], 18);
                
                // Находим и открываем соответствующий маркер
                burialMarkers.forEach(marker => {
                    if (marker.properties.get('burialId') === burial.id) {
                        marker.balloon.open();
                    }
                });
            }
        });
        
        ul.appendChild(li);
    });
    
    container.appendChild(ul);
}

// Получение текущего местоположения пользователя
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const coords = [position.coords.latitude, position.coords.longitude];
                
                // Если пользователь добавляет захоронение, ставим маркер
                if (document.getElementById('add-burial-mode')) {
                    placeMarkerOnClick(coords);
                }
                
                // В любом случае центрируем карту на текущем местоположении
                map.setCenter(coords, 18);
            },
            (error) => {
                console.error('Ошибка получения геолокации:', error);
                showNotification('Не удалось получить ваше местоположение', 'danger');
            }
        );
    } else {
        showNotification('Геолокация не поддерживается вашим браузером', 'warning');
    }
}

// Добавляем захоронение в избранное/удаляем из избранного
function toggleFavorite(burialId, btn) {
    fetch(`/burials/${burialId}/favorite/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем иконку на кнопке
            const icon = btn.querySelector('i');
            if (data.is_favorite) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                btn.setAttribute('title', 'Удалить из избранного');
                showNotification('Добавлено в избранное', 'success');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                btn.setAttribute('title', 'Добавить в избранное');
                showNotification('Удалено из избранного', 'info');
            }
            
            // Обновляем маркеры на карте, если она загружена
            if (window.map) {
                favoriteMarkerId = data.is_favorite ? burialId : null;
                loadBurials();
            }
        }
    })
    .catch(error => {
        console.error('Ошибка при изменении статуса избранного:', error);
        showNotification('Произошла ошибка', 'danger');
    });
}

// Сохранение заметки
function saveNote(burialId, form) {
    const formData = new FormData(form);
    
    fetch(`/burials/${burialId}/note/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Заметка сохранена', 'success');
            
            // Обновляем отображаемый текст заметки, если есть соответствующий элемент
            const noteText = document.getElementById('note-text');
            if (noteText) {
                noteText.textContent = data.text;
            }
        } else {
            showNotification('Ошибка при сохранении заметки', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка при сохранении заметки:', error);
        showNotification('Произошла ошибка', 'danger');
    });
    
    // Предотвращаем отправку формы
    return false;
}

// Удаление заметки
function deleteNote(burialId) {
    if (!confirm('Вы уверены, что хотите удалить эту заметку?')) {
        return;
    }
    
    fetch(`/burials/${burialId}/note/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Заметка удалена', 'success');
            
            // Очищаем поле ввода заметки
            document.getElementById('id_text').value = '';
            
            // Обновляем отображаемый текст заметки, если есть соответствующий элемент
            const noteText = document.getElementById('note-text');
            if (noteText) {
                noteText.textContent = '';
            }
        } else {
            showNotification(data.error || 'Ошибка при удалении заметки', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка при удалении заметки:', error);
        showNotification('Произошла ошибка', 'danger');
    });
}

// Обработка запроса на добавление захоронения
function submitBurialRequest(form) {
    const formData = new FormData(form);
    
    // Проверяем, заполнены ли координаты
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;
    
    if (!latitude || !longitude) {
        showNotification('Пожалуйста, отметьте место захоронения на карте', 'warning');
        return false;
    }
    
    fetch('/submit-burial/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Запрос на добавление захоронения отправлен', 'success');
            // Очищаем форму
            form.reset();
            // Удаляем маркер с карты
            if (currentMarker) {
                map.geoObjects.remove(currentMarker);
                currentMarker = null;
            }
            // Закрываем модальное окно, если оно есть
            const modal = document.getElementById('add-burial-modal');
            if (modal) {
                closeModal(modal.id);
            }
        } else {
            showNotification(data.error || 'Ошибка при отправке запроса', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса на добавление захоронения:', error);
        showNotification('Произошла ошибка', 'danger');
    });
    
    // Предотвращаем отправку формы
    return false;
}

// Обработка запроса на добавление захоронения администратором
function addBurial(form) {
    const formData = new FormData(form);
    
    // Проверяем, заполнены ли координаты
    const latitude = document.getElementById('admin-latitude').value;
    const longitude = document.getElementById('admin-longitude').value;
    
    if (!latitude || !longitude) {
        showNotification('Пожалуйста, отметьте место захоронения на карте', 'warning');
        return false;
    }
    
    fetch('/add-burial/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Захоронение успешно добавлено', 'success');
            // Очищаем форму
            form.reset();
            // Удаляем маркер с карты
            if (currentMarker) {
                map.geoObjects.remove(currentMarker);
                currentMarker = null;
            }
            // Обновляем список захоронений на карте
            loadBurials();
            // Закрываем модальное окно, если оно есть
            const modal = document.getElementById('add-burial-modal');
            if (modal) {
                closeModal(modal.id);
            }
        } else {
            showNotification(data.error || 'Ошибка при добавлении захоронения', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка при добавлении захоронения:', error);
        showNotification('Произошла ошибка', 'danger');
    });
    
    // Предотвращаем отправку формы
    return false;
}

// Обработка запроса на модерацию
function processBurialRequest(requestId, action, rejectionReason) {
    const formData = new FormData();
    formData.append('action', action);
    if (rejectionReason) {
        formData.append('rejection_reason', rejectionReason);
    }
    
    fetch(`/process-burial-request/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.status === 'approved') {
                showNotification('Запрос одобрен', 'success');
            } else {
                showNotification('Запрос отклонен', 'info');
            }
            
            // Удаляем обработанный запрос из списка
            const requestElement = document.getElementById(`request-${requestId}`);
            if (requestElement) {
                requestElement.remove();
            }
            
            // Обновляем количество запросов, если есть соответствующий счетчик
            const counter = document.getElementById('pending-requests-count');
            if (counter) {
                const currentCount = parseInt(counter.textContent);
                counter.textContent = currentCount - 1;
            }
            
            // Обновляем список захоронений на карте, если запрос был одобрен
            if (data.status === 'approved') {
                loadBurials();
            }
        } else {
            showNotification(data.error || 'Ошибка при обработке запроса', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка при обработке запроса на добавление захоронения:', error);
        showNotification('Произошла ошибка', 'danger');
    });
}

// Получение CSRF токена из cookies
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Показать уведомление
function showNotification(message, type) {
    // Проверяем, существует ли контейнер для уведомлений
    let notificationContainer = document.getElementById('notification-container');
    
    // Если контейнера нет, создаем его
    if (!notificationContainer) {
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
    notification.className = `alert alert-${type || 'info'}`;
    notification.innerText = message;
    
    // Добавляем кнопку закрытия
    const closeButton = document.createElement('span');
    closeButton.innerHTML = '&times;';
    closeButton.style.float = 'right';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontWeight = 'bold';
    closeButton.addEventListener('click', function() {
        notification.remove();
    });
    
    notification.prepend(closeButton);
    
    // Добавляем уведомление в контейнер
    notificationContainer.appendChild(notification);
    
    // Автоматически скрываем уведомление через 5 секунд
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Открытие модального окна
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

// Закрытие модального окна
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Обработчики событий для закрытия модальных окон при клике вне их содержимого
document.addEventListener('DOMContentLoaded', function() {
    const modals = document.getElementsByClassName('modal');
    
    for (let i = 0; i < modals.length; i++) {
        modals[i].addEventListener('click', function(event) {
            if (event.target === this) {
                this.style.display = 'none';
            }
        });
    }
    
    // Закрытие модальных окон по кнопкам с классом close-modal
    const closeButtons = document.getElementsByClassName('close-modal');
    
    for (let i = 0; i < closeButtons.length; i++) {
        closeButtons[i].addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }
});
