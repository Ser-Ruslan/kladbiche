/**
 * Интерактивная карта кладбища
 * Использует Яндекс Карты API для отображения захоронений
 */

// Объект с глобальными переменными карты
const mapApp = {
    map: null,
    graves: [], // Список всех захоронений
    selectedGraveId: null, // ID выбранного захоронения
    favoriteGraves: [], // ID избранных захоронений
    objectManager: null, // Менеджер объектов Яндекс Карт
    searchResults: [], // Результаты поиска
    isAdmin: false, // Флаг администратора
    drawingMode: false, // Режим рисования полигона
    drawingPolygon: null, // Объект создаваемого полигона
    cemeteryCoordinates: {
        central: {
            center: [52.059841124947, 113.51869776876853],
            zoom: 17
        },
        smolenskoe: {
            center: [52.155789125323786, 113.51357141191197],
            zoom: 17
        }
    }
};

/**
 * Получение параметров из URL
 */
function getUrlParams() {
    const params = {};
    const queryString = window.location.search.substring(1);
    const pairs = queryString.split('&');

    for (let i = 0; i < pairs.length; i++) {
        if (pairs[i] === '') continue;

        const pair = pairs[i].split('=');
        params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }

    return params;
}

/**
 * Центрирование карты на указанном захоронении
 */
function centerMapOnGrave(graveId) {
    console.log('Вызов centerMapOnGrave с ID:', graveId);

    // Проверяем, инициализирована ли карта и объекты
    if (!mapApp.map || !mapApp.objectManager) {
        console.log('Карта или менеджер объектов еще не инициализированы');
        console.log('map:', mapApp.map);
        console.log('objectManager:', mapApp.objectManager);
        return;
    }

    // Проверим состояние объектного менеджера
    console.log('Количество загруженных объектов:', mapApp.objectManager.objects.getLength());
    console.log('Все доступные ID объектов:', mapApp.objectManager.objects.getAll().map(obj => obj.id));

    // Получаем объект захоронения из объектного менеджера
    const grave = mapApp.objectManager.objects.getById(graveId);
    console.log('Найденное захоронение в ObjectManager:', grave);

    if (!grave) {
        console.log('Захоронение не найдено в ObjectManager, ищем в graves:', graveId);

        // Попробуем найти в массиве graves
        const graveFromArray = mapApp.graves.find(g => g.id === graveId);

        if (graveFromArray) {
            console.log('Захоронение найдено в массиве graves:', graveFromArray);

            // Парсим координаты полигона
            const polygon = JSON.parse(graveFromArray.polygon_coordinates);

            // Рассчитываем центр полигона
            let sumLat = 0, sumLng = 0;
            polygon[0].forEach(point => {
                sumLat += point[0];
                sumLng += point[1];
            });
            const centerLat = sumLat / polygon[0].length;
            const centerLng = sumLng / polygon[0].length;

            console.log('Рассчитанный центр полигона:', [centerLat, centerLng]);

            // Устанавливаем новый центр карты и приближаем
            mapApp.map.setCenter([centerLat, centerLng], 19, {
                duration: 500
            });

            // Выделяем захоронение
            selectGrave(graveId);

            console.log('Карта центрирована на захоронении ID (из массива):', graveId);
            return;
        }

        console.log('Захоронение не найдено ни в ObjectManager, ни в массиве graves:', graveId);
        return;
    }

    // Получаем координаты захоронения
    const coords = grave.geometry.coordinates;
    if (!coords || !coords.length) {
        console.log('Координаты захоронения не найдены');
        return;
    }

    console.log('Координаты захоронения:', coords);

    // Вычисляем центр полигона
    const center = getCenterOfPolygon(coords);
    console.log('Рассчитанный центр полигона:', center);

    // Устанавливаем новый центр карты и приближаем
    mapApp.map.setCenter(center, 19, {
        duration: 500
    });

    // Выделяем захоронение
    selectGrave(graveId);

    console.log('Карта центрирована на захоронении ID:', graveId);
}

/**
 * Вычисление центра полигона
 */
function getCenterOfPolygon(coordinates) {
    if (!coordinates || !coordinates.length || !coordinates[0].length) return [0, 0];

    let sumLat = 0;
    let sumLng = 0;
    const points = coordinates[0]; // Первый контур полигона

    for (let i = 0; i < points.length; i++) {
        sumLat += points[i][0];
        sumLng += points[i][1];
    }

    return [sumLat / points.length, sumLng / points.length];
}

// Инициализация карты при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {

    // Cemetery selector handling
    const cemeterySelector = document.getElementById('cemetery-selector');
    if (cemeterySelector) {
        cemeterySelector.addEventListener('change', function() {
            const selectedCemetery = this.value;
            
            if (mapApp.map && mapApp.cemeteryCoordinates[selectedCemetery]) {
                // Устанавливаем новый центр карты и зум
                mapApp.map.setCenter(
                    mapApp.cemeteryCoordinates[selectedCemetery].center,
                    mapApp.cemeteryCoordinates[selectedCemetery].zoom,
                    { duration: 800 }
                );
                
                console.log(`Карта перемещена на кладбище: ${selectedCemetery}`);
            } else {
                console.error(`Координаты для кладбища "${selectedCemetery}" не найдены или карта не инициализирована`);
            }
        });
    }

    // Cemetery filter handling
    const cemeteryFilter = document.getElementById('cemetery-filter');
    if (cemeteryFilter) {
        cemeteryFilter.addEventListener('change', function() {
            const selectedCemeteryId = this.value;
            const graves = window.gravesCollection.getGeoObjects();

            graves.forEach(grave => {
                const graveData = grave.properties.get('graveData');
                if (selectedCemeteryId === 'all' || graveData.cemetery_id === parseInt(selectedCemeteryId)) {
                    grave.options.set('visible', true);
                } else {
                    grave.options.set('visible', false);
                }
            });
        });
    }
    // Проверка, авторизован ли пользователь и является ли администратором
    if (document.body.dataset.userAuthenticated === 'true') {
        mapApp.isUserAuthenticated = true;

        if (document.body.dataset.userIsAdmin === 'true') {
            mapApp.isAdmin = true;
        }

        // Получаем список ID избранных захоронений из data-атрибута
        const favoriteGravesString = document.body.dataset.favoriteGraves || '[]';
        mapApp.favoriteGraves = JSON.parse(favoriteGravesString);
    }

    // Инициализация Яндекс Карты
    initMap();

    // Инициализация поиска
    initSearch();

    // Инициализация кнопки сайдбара для мобильных устройств
    initSidebarToggle();

    // Инициализация панели администратора (если пользователь админ)
    if (mapApp.isAdmin) {
        initAdminPanel();
    }

    // Обработка параметров URL перенесена в функцию loadAllGraves
    // для корректной последовательности загрузки
});

/**
 * Инициализация Яндекс Карты
 */
function initMap() {
    // Получаем API ключ и центр карты из data-атрибутов
    const apiKey = document.getElementById('map-container').dataset.apiKey;

    // Логируем данные для отладки
    console.log("Data attributes:", {
        apiKey: document.getElementById('map-container').dataset.apiKey,
        centerLat: document.getElementById('map-container').dataset.centerLat,
        centerLng: document.getElementById('map-container').dataset.centerLng,
        zoom: document.getElementById('map-container').dataset.zoom
    });

    // Устанавливаем жестко заданные координаты для теста
    const centerLat = 52.059841124947;
    const centerLng = 113.51869776876853;
    const zoom = 17;

    // Создаем карту
    ymaps.ready(function() {
        // Инициализация карты
        mapApp.map = new ymaps.Map('map', {
            center: [centerLat, centerLng],
            zoom: zoom,
            controls: ['zoomControl', 'searchControl', 'typeSelector']
        });

        // Создаем и добавляем менеджер объектов для эффективной работы с большим количеством объектов
        mapApp.objectManager = new ymaps.ObjectManager({
            clusterize: false,
            geoObjectOpenBalloonOnClick: false
        });

        // Стилизация полигонов захоронений
        mapApp.objectManager.objects.options.set({
            fillColor: '#b3b3b3',
            strokeColor: '#999999',
            strokeWidth: 1,
            opacity: 0.6,
            cursor: 'pointer',
            interactive: true
        });

        // Обработчик клика по полигону захоронения
        mapApp.objectManager.objects.events.add('click', function(e) {
            const objectId = e.get('objectId');
            selectGrave(objectId);
        });

        mapApp.map.geoObjects.add(mapApp.objectManager);

        // Загружаем все захоронения
        loadAllGraves();
    });
}

/**
 * Загрузка всех захоронений с сервера
 */
function loadAllGraves() {
    return new Promise((resolve, reject) => {
        fetch('/api/graves/')
            .then(response => response.json())
            .then(data => {
                console.log('Загружено захоронений:', data.length);
                mapApp.graves = data;

                // Преобразуем данные в формат для ObjectManager
                const features = data.map(grave => {
                    // Парсим координаты полигона из JSON строки
                    const polygon = JSON.parse(grave.polygon_coordinates);

                    // Определяем цвет заполнения - избранные захоронения выделяются другим цветом
                    const fillColor = mapApp.favoriteGraves.includes(grave.id) ? '#ff9999' : '#b3b3b3';

                    return {
                        type: 'Feature',
                        id: grave.id,
                        geometry: {
                            type: 'Polygon',
                            coordinates: polygon
                        },
                        properties: {
                            graveId: grave.id,
                            name: grave.full_name,
                            isFavorite: mapApp.favoriteGraves.includes(grave.id),
                            cemetery_id: grave.cemetery_id // Add cemetery_id to properties
                        },
                        options: {
                            fillColor: fillColor,
                            strokeColor: '#999999',
                            strokeWidth: 1,
                            opacity: 0.6
                        }
                    };
                });

                // Добавляем объекты на карту
                mapApp.objectManager.add({
                    type: 'FeatureCollection',
                    features: features
                });

                console.log('Объекты добавлены на карту');

                // После загрузки захоронений, проверяем URL параметры
                const urlParams = getUrlParams();
                console.log('URL параметры (после загрузки):', urlParams);

                if (urlParams.grave_id) {
                    const graveId = parseInt(urlParams.grave_id);
                    console.log('Найден grave_id в URL (после загрузки):', graveId);

                    // Небольшая задержка, чтобы дать время карте отрисовать объекты
                    setTimeout(() => {
                        console.log('Запуск таймера для центрирования карты на захоронении:', graveId);
                        // Попытка центрировать карту на захоронении по ID из URL
                        centerMapOnGrave(graveId);
                    }, 500);
                }

                resolve(data);
            })
            .catch(error => {
                console.error('Ошибка при загрузке захоронений:', error);
                showNotification('Ошибка при загрузке данных захоронений', 'error');
                reject(error);
            });
    });
}

/**
 * Выбор захоронения и отображение информации в сайдбаре
 */
function selectGrave(graveId) {
    // Если уже выбрано это захоронение, ничего не делаем
    if (mapApp.selectedGraveId === graveId) return;

    mapApp.selectedGraveId = graveId;

    // Подсветка выбранного захоронения
    mapApp.objectManager.objects.setObjectOptions(graveId, {
        strokeColor: '#007bff',
        strokeWidth: 2,
        opacity: 0.8
    });

    // Сбрасываем стиль для ранее выбранного захоронения
    if (mapApp.prevSelectedGraveId && mapApp.prevSelectedGraveId !== graveId) {
        const prevObject = mapApp.objectManager.objects.getById(mapApp.prevSelectedGraveId);
        if (prevObject) {
            const fillColor = prevObject.properties.isFavorite ? '#ff9999' : '#b3b3b3';
            mapApp.objectManager.objects.setObjectOptions(mapApp.prevSelectedGraveId, {
                strokeColor: '#999999',
                strokeWidth: 1,
                opacity: 0.6,
                fillColor: fillColor
            });
        }
    }

    mapApp.prevSelectedGraveId = graveId;

    // Загружаем информацию о захоронении в сайдбар
    loadGraveDetails(graveId);
}

/**
 * Загрузка подробной информации о захоронении в сайдбар
 */
function loadGraveDetails(graveId) {
    // Показываем индикатор загрузки
    document.getElementById('sidebar-content').innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
        </div>
    `;

    // Запрашиваем данные с сервера
    fetch(`/graves/grave/${graveId}/`)
        .then(response => response.text())
        .then(html => {
            // Обновляем содержимое сайдбара
            document.getElementById('sidebar-content').innerHTML = html;

            // Инициализация обработчиков кнопок в сайдбаре
            initSidebarButtons();
        })
        .catch(error => {
            console.error('Ошибка при загрузке информации о захоронении:', error);
            document.getElementById('sidebar-content').innerHTML = `
                <div class="alert alert-danger">
                    Ошибка при загрузке информации о захоронении. Пожалуйста, попробуйте еще раз.
                </div>
            `;
        });
}

/**
 * Инициализация обработчиков кнопок в сайдбаре
 */
function initSidebarButtons() {
    // Кнопка добавления/удаления из избранного
    const favoriteButton = document.getElementById('favorite-button');
    if (favoriteButton) {
        favoriteButton.addEventListener('click', function() {
            toggleFavorite(mapApp.selectedGraveId);
        });
    }

    // Форма добавления личной заметки
    const noteForm = document.getElementById('note-form');
    if (noteForm) {
        noteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            savePersonalNote(mapApp.selectedGraveId);
        });
    }

    // Форма предложения редактирования
    const editProposalForm = document.getElementById('edit-proposal-form');
    if (editProposalForm) {
        editProposalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitEditProposal(mapApp.selectedGraveId);
        });
    }

    // Кнопки администратора (если есть)
    const adminEditBtn = document.getElementById('admin-edit-grave');
    if (adminEditBtn) {
        adminEditBtn.addEventListener('click', function() {
            openAdminEditForm(mapApp.selectedGraveId);
        });
    }

    const adminDeleteBtn = document.getElementById('admin-delete-grave');
    if (adminDeleteBtn) {
        adminDeleteBtn.addEventListener('click', function() {
            confirmDeleteGrave(mapApp.selectedGraveId);
        });
    }
}

/**
 * Инициализация поиска захоронений
 */
function initSearch() {
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            searchGraves();
        });
    }
}

/**
 * Поиск захоронений по параметрам
 */
function searchGraves() {
    try {
        const searchMode = document.getElementById('search-mode')?.value || 'search';
        const query = document.getElementById('search-query')?.value || '';
        const birthDate = document.getElementById('search-birth-date')?.value || '';
        const deathDate = document.getElementById('search-death-date')?.value || '';
        const cemeteryId = document.getElementById('search-cemetery')?.value || '';
        const favoritesOnly = document.getElementById('favorites-only')?.checked || false;

        if (searchMode === 'filter') {
            // Режим фильтра - делаем запрос на сервер
            const params = new URLSearchParams();
            if (cemeteryId && cemeteryId !== 'all') {
                params.append('cemetery_id', cemeteryId);
            }
            if (favoritesOnly) {
                params.append('favorites_only', 'true');
            }

            fetch(`/graves/search/?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    // Получаем ID найденных захоронений
                    const foundGraveIds = new Set(data.graves.map(grave => grave.id));

                    // Обновляем видимость полигонов
                    mapApp.objectManager.objects.each((object) => {
                        const isVisible = foundGraveIds.has(object.id);
                        mapApp.objectManager.objects.setObjectOptions(object.id, {
                            fillColor: '#b3b3b3',
                            strokeColor: '#999999',
                            strokeWidth: 1,
                            opacity: isVisible ? 0.6 : 0,
                            visible: isVisible
                        });
                    });
                })
                .catch(error => {
                    console.error('Ошибка при фильтрации захоронений:', error);
                    showNotification('Ошибка при фильтрации захоронений', 'error');
                });

            // Очищаем результаты поиска
            document.getElementById('search-results').innerHTML = '';
            return;
        }

        // Режим поиска - отправляем запрос на сервер
        const params = new URLSearchParams();
        if (query) params.append('query', query);
        if (birthDate) params.append('birth_date', birthDate);
        if (deathDate) params.append('death_date', deathDate);
        if (cemeteryId && cemeteryId !== 'all') params.append('cemetery_id', cemeteryId);
        if (favoritesOnly) params.append('favorites_only', 'true');

        const url = `/graves/search/?${params.toString()}`;

        // Показываем индикатор загрузки
        document.getElementById('search-results').innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
            </div>
        `;

        // Запрашиваем результаты поиска
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mapApp.searchResults = data.graves;

                // Получаем ID найденных захоронений
                const foundGraveIds = new Set(data.graves.map(grave => grave.id));

                // Скрываем/показываем полигоны на карте
                mapApp.objectManager.objects.each(object => {
                    const isVisible = foundGraveIds.has(object.id);
                    mapApp.objectManager.objects.setObjectOptions(object.id, {
                        visible: isVisible
                    });
                });

                displaySearchResults(data.graves);
            })
            .catch(error => {
                console.error('Ошибка при поиске захоронений:', error);
                document.getElementById('search-results').innerHTML = `
                    <div class="alert alert-danger">
                        Ошибка при поиске. Пожалуйста, попробуйте еще раз.
                    </div>
                `;
            });
    } catch (error) {
        console.error('Ошибка в функции searchGraves:', error);
        showNotification('Ошибка при поиске захоронений', 'error');
    }
}

/**
 * Отображение результатов поиска в сайдбаре
 */
function displaySearchResults(graves) {
    const resultsContainer = document.getElementById('search-results');

    if (graves.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                Захоронения не найдены
            </div>
        `;
        return;
    }

    let html = '';
    graves.forEach(grave => {
        let dates = '';
        if (grave.birth_date && grave.death_date) {
            dates = `${grave.birth_date} - ${grave.death_date}`;
        } else if (grave.birth_date) {
            dates = `Родился: ${grave.birth_date}`;
        } else if (grave.death_date) {
            dates = `Умер: ${grave.death_date}`;
        }

        html += `
            <div class="search-result-item" data-grave-id="${grave.id}">
                <div class="search-result-name">${grave.full_name}</div>
                <div class="search-result-dates">${dates}</div>
            </div>
        `;
    });

    resultsContainer.innerHTML = html;

    // Добавляем обработчики клика для результатов поиска
    document.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', function() {
            const graveId = parseInt(this.dataset.graveId);

            // Находим координаты захоронения для центрирования карты
            const grave = mapApp.graves.find(g => g.id === graveId);
            if (grave) {
                // Центрируем карту на захоронении
                const polygon = JSON.parse(grave.polygon_coordinates);
                // Рассчитываем центр полигона
                let sumLat = 0, sumLng = 0;
                polygon[0].forEach(point => {
                    sumLat += point[0];
                    sumLng += point[1];
                });
                const centerLat = sumLat / polygon[0].length;
                const centerLng = sumLng / polygon[0].length;

                mapApp.map.setCenter([centerLat, centerLng], 19);

                // Выбираем захоронение
                selectGrave(graveId);
            }
        });
    });
}

/**
 * Добавление/удаление захоронения из избранного
 */
function toggleFavorite(graveId) {
    if (!mapApp.isUserAuthenticated) {
        showNotification('Для добавления в избранное необходимо авторизоваться', 'warning');
        return;
    }

    fetch(`/graves/grave/${graveId}/toggle-favorite/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        const favoriteButton = document.getElementById('favorite-button');

        if (data.is_favorite) {
            // Добавлено в избранное
            favoriteButton.classList.add('active');
            favoriteButton.innerHTML = '<i class="fas fa-heart"></i> В избранном';

            // Обновляем список избранных
            if (!mapApp.favoriteGraves.includes(graveId)) {
                mapApp.favoriteGraves.push(graveId);
            }

            // Обновляем стиль полигона
            mapApp.objectManager.objects.setObjectOptions(graveId, {
                fillColor: '#ff9999'
            });

            // Обновляем свойства объекта
            const feature = mapApp.objectManager.objects.getById(graveId);
            if (feature) {
                feature.properties.isFavorite = true;
            }

            showNotification('Захоронение добавлено в избранное', 'success');
        } else {
            // Удалено из избранного
            favoriteButton.classList.remove('active');
            favoriteButton.innerHTML = '<i class="far fa-heart"></i> В избранное';

            // Обновляем список избранных
            const index = mapApp.favoriteGraves.indexOf(graveId);
            if (index !== -1) {
                mapApp.favoriteGraves.splice(index, 1);
            }

            // Обновляем стиль полигона
            mapApp.objectManager.objects.setObjectOptions(graveId, {
                fillColor: '#b3b3b3'
            });

            // Обновляем свойства объекта
            const feature = mapApp.objectManager.objects.getById(graveId);
            if (feature) {
                feature.properties.isFavorite = false;
            }

            showNotification('Захоронение удалено из избранного', 'success');
        }
    })
    .catch(error => {
        console.error('Ошибка при обновлении избранного:', error);
        showNotification('Ошибка при обновлении избранного', 'error');
    });
}

/**
 * Сохранение личной заметки к захоронению
 */
function savePersonalNote(graveId) {
    if (!mapApp.isUserAuthenticated) {
        showNotification('Для добавления заметок необходимо авторизоваться', 'warning');
        return;
    }

    const noteText = document.getElementById('note-text').value.trim();

    fetch(`/graves/grave/${graveId}/save-note/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `note_text=${encodeURIComponent(noteText)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем отображение заметки
            const noteContainer = document.getElementById('personal-note-container');
            if (noteText) {
                noteContainer.innerHTML = `
                    <div class="personal-note-text">${noteText}</div>
                `;
            } else {
                noteContainer.innerHTML = '';
            }

            document.getElementById('note-text').value = '';

            showNotification('Заметка сохранена', 'success');
        }
    })
    .catch(error => {
        console.error('Ошибка при сохранении заметки:', error);
        showNotification('Ошибка при сохранении заметки', 'error');
    });
}

/**
 * Отправка предложения по редактированию описания захоронения
 */
function submitEditProposal(graveId) {
    if (!mapApp.isUserAuthenticated) {
        showNotification('Для предложения редактирования необходимо авторизоваться', 'warning');
        return;
    }

    const proposedDescription = document.getElementById('edit-proposal-text').value.trim();
    console.log('Отправка предложения:', proposedDescription);

    if (!proposedDescription) {
        showNotification('Пожалуйста, введите предлагаемое описание', 'warning');
        return;
    }

    // Создаем FormData, это более надежный способ отправки данных
    const formData = new FormData();
    formData.append('proposed_description', proposedDescription);

    // Отображаем данные для отладки
    console.log('Данные FormData:');
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }

    fetch(`/graves/grave/${graveId}/submit-edit/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
            // Не устанавливаем Content-Type при использовании FormData, браузер сделает это автоматически
        },
        body: formData
    })
    .then(response => {
        console.log('Ответ сервера:', response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Данные ответа:', data);
        if (data.success) {
            document.getElementById('edit-proposal-text').value = '';
            document.getElementById('edit-proposal-form').style.display = 'none';
            document.getElementById('edit-proposal-success').style.display = 'block';

            showNotification('Ваше предложение отправлено на рассмотрение', 'success');
        } else {
            console.error('Ошибка в ответе:', data);
            showNotification('Ошибка при отправке предложения', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке предложения:', error);
        showNotification('Ошибка при отправке предложения: ' + error.message, 'error');
    });
}

/**
 * Инициализация панели администратора
 */
function initAdminPanel() {
    const adminPanel = document.getElementById('admin-panel');
    if (!adminPanel) return;

    // Инициализация кнопки добавления нового захоронения
    const addGraveBtn = document.getElementById('admin-add-grave');
    if (addGraveBtn) {
        addGraveBtn.addEventListener('click', function() {
            startDrawingMode();
        });
    }
}

/**
 * Запуск режима рисования нового полигона захоронения
 */
function startDrawingMode() {
    if (mapApp.drawingMode) return;

    // Включаем режим рисования
    mapApp.drawingMode = true;

    // Отображаем сообщение для пользователя
    document.getElementById('sidebar-content').innerHTML = `
        <div class="sidebar-header">
            <h2>Добавление захоронения</h2>
        </div>
        <div class="sidebar-body">
            <div class="alert alert-info">
                <strong>Режим рисования:</strong> Щелкните по карте, чтобы добавить точки полигона захоронения. 
                После создания замкнутого контура, используйте контекстное меню для дальнейших действий.
            </div>
            <div class="drawing-controls mt-3">
                <button id="complete-polygon" class="btn btn-primary mb-2">Завершить рисование</button>
                <button id="add-inner-ring" class="btn btn-warning mb-2">Добавить внутренний контур</button>
                <button id="continue-drawing" class="btn btn-info mb-2">Продолжить рисование</button>
                <button id="cancel-drawing" class="btn btn-secondary">Отменить</button>
            </div>
        </div>
    `;

    // Обработчики кнопок управления рисованием
    document.getElementById('complete-polygon').addEventListener('click', function() {
        const coordinates = mapApp.drawingPolygon.geometry.getCoordinates();
        finishDrawingPolygon(coordinates);
    });

    document.getElementById('add-inner-ring').addEventListener('click', function() {
        if (mapApp.drawingPolygon && mapApp.drawingPolygon.editor) {
            mapApp.drawingPolygon.editor.startDrawing('inner');
        }
    });

    document.getElementById('continue-drawing').addEventListener('click', function() {
        if (mapApp.drawingPolygon && mapApp.drawingPolygon.editor) {
            mapApp.drawingPolygon.editor.startDrawing();
        }
    });

    document.getElementById('cancel-drawing').addEventListener('click', function() {
        cancelDrawingMode();
    });

    // Создаем полигон для рисования
    mapApp.drawingPolygon = new ymaps.Polygon([
        // Внешний контур
        [],
        // Внутренние контуры (дырки)
    ], {
        hintContent: 'Новое захоронение'
    }, {
        editorDrawingCursor: 'crosshair',
        fillColor: '#00FF00',
        strokeColor: '#0000FF',
        strokeWidth: 2,
        opacity: 0.5
    });

    // Добавляем полигон на карту
    mapApp.map.geoObjects.add(mapApp.drawingPolygon);

    // Включаем редактор для полигона
    mapApp.drawingPolygon.editor.startDrawing();
}

/**
 * Завершение рисования полигона и открытие формы добавления захоронения
 */
function finishDrawingPolygon(coordinates) {
    try {
        // Проверяем существование полигона и его редактора
        if (!mapApp.drawingPolygon || !mapApp.drawingPolygon.editor) {
            throw new Error('Полигон не инициализирован');
        }

        // Отключаем режим рисования
        mapApp.drawingMode = false;
        mapApp.drawingPolygon.editor.stopEditing();

        console.log('Завершение рисования полигона с координатами:', coordinates);

        // Проверяем валидность координат
        if (!coordinates || !Array.isArray(coordinates) || !coordinates[0] || coordinates[0].length < 3) {
            throw new Error('Некорректные координаты полигона');
        }

        // Преобразуем координаты в строку JSON
        const coordinatesJSON = JSON.stringify(coordinates);
        console.log('Координаты в формате JSON:', coordinatesJSON);

        // Отображаем форму для ввода данных захоронения
        document.getElementById('sidebar-content').innerHTML = `
            <div class="sidebar-header">
                <h2>Добавление захоронения</h2>
            </div>
            <div class="sidebar-body">
                <form id="add-grave-form">
                    <div class="form-group">
                        <label for="full-name">ФИО погребенного *</label>
                        <input type="text" class="form-control" id="full-name" required>
                    </div>
                    <div class="form-group">
                        <label for="birth-date">Дата рождения</label>
                        <input type="date" class="form-control" id="birth-date">
                    </div>
                    <div class="form-group">
                        <label for="death-date">Дата смерти</label>
                        <input type="date" class="form-control" id="death-date">
                    </div>
                    <div class="form-group">
                        <label for="description">Описание</label>
                        <textarea class="form-control" id="description" rows="4"></textarea>
                    </div>
                    <input type="hidden" id="polygon-coordinates" value='${coordinatesJSON}'>
                    <button type="submit" class="btn btn-primary">Сохранить</button>
                    <button type="button" id="cancel-add-grave" class="btn btn-secondary">Отмена</button>
                </form>
            </div>
        `;

        // Обработчик отправки формы
        document.getElementById('add-grave-form').addEventListener('submit', function(e) {
            e.preventDefault();
            saveNewGrave();
        });

        // Обработчик отмены
        document.getElementById('cancel-add-grave').addEventListener('click', function() {
            mapApp.map.geoObjects.remove(mapApp.drawingPolygon);
            mapApp.drawingPolygon = null;
            document.getElementById('sidebar-content').innerHTML = '';
        });
    } catch (error) {
        console.error('Ошибка при завершении рисования:', error);
        showNotification('Ошибка при создании полигона. Пожалуйста, попробуйте еще раз.', 'error');
        cancelDrawingMode();
    }
}

/**
 * Сохранение нового захоронения
 */
function saveNewGrave() {
    const fullName = document.getElementById('full-name').value.trim();
    const birthDate = document.getElementById('birth-date').value;
    const deathDate = document.getElementById('death-date').value;
    const description = document.getElementById('description').value.trim();
    const polygonCoordinates = document.getElementById('polygon-coordinates').value;

    console.log('Попытка сохранения нового захоронения:');
    console.log('ФИО:', fullName);
    console.log('Координаты полигона:', polygonCoordinates);

    const requestData = {
        full_name: fullName,
        birth_date: birthDate || null,
        death_date: deathDate || null,
        description: description,
        polygon_coordinates: polygonCoordinates
    };

    console.log('Отправляемые данные:', JSON.stringify(requestData));

    fetch('/api/graves/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        console.log('Статус ответа:', response.status);
        if (!response.ok) {
            return response.json().then(data => {
                console.error('Ошибка в ответе API:', data);
                throw new Error(JSON.stringify(data));
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Успешный ответ API:', data);

        // Удаляем временный полигон
        mapApp.map.geoObjects.remove(mapApp.drawingPolygon);
        mapApp.drawingPolygon = null;

        // Обновляем список захоронений
        loadAllGraves();

        // Отображаем сообщение об успехе
        showNotification('Захоронение успешно добавлено', 'success');

        // Очищаем сайдбар
        document.getElementById('sidebar-content').innerHTML = '';
    })
    .catch(error => {
        console.error('Ошибка при сохранении захоронения:', error);
        showNotification('Ошибка при сохранении захоронения', 'error');
    });
}

/**
 * Отмена режима рисования
 */
function cancelDrawingMode() {
    if (!mapApp.drawingMode) return;

    // Отключаем режим рисования
    mapApp.drawingMode = false;

    // Удаляем полигон с карты
    if (mapApp.drawingPolygon) {
        mapApp.drawingPolygon.editor.stopEditing();
        mapApp.map.geoObjects.remove(mapApp.drawingPolygon);
        mapApp.drawingPolygon = null;
    }

    // Очищаем сайдбар
    document.getElementById('sidebar-content').innerHTML = '';
}

/**
 * Открытие формы редактирования захоронения (для администраторов)
 */
function openAdminEditForm(graveId) {
    // Запрашиваем данные о захоронении
    fetch(`/api/graves/${graveId}/`)
        .then(response => response.json())
        .then(grave => {
            // Заполняем форму редактирования
            document.getElementById('sidebar-content').innerHTML = `
                <div class="sidebar-header">
                    <h2>Редактирование захоронения</h2>
                </div>
                <div class="sidebar-body">
                    <form id="edit-grave-form">
                        <div class="form-group">
                            <label for="edit-full-name">ФИО погребенного *</label>
                            <input type="text" class="form-control" id="edit-full-name" value="${grave.full_name}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-birth-date">Дата рождения</label>
                            <input type="date" class="form-control" id="edit-birth-date" value="${grave.birth_date || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-death-date">Дата смерти</label>
                            <input type="date" class="form-control" id="edit-death-date" value="${grave.death_date || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-description">Описание</label>
                            <textarea class="form-control" id="edit-description" rows="4">${grave.description || ''}</textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Сохранить</button>
                        <button type="button" class="btn btn-secondary" id="edit-cancel">Отмена</button>
                    </form>
                </div>
            `;

            // Обработчик отправки формы
            document.getElementById('edit-grave-form').addEventListener('submit', function(e) {
                e.preventDefault();
                updateGrave(graveId);
            });

            // Обработчик отмены
            document.getElementById('edit-cancel').addEventListener('click', function() {
                loadGraveDetails(graveId);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных захоронения:', error);
            showNotification('Ошибка при загрузке данных захоронения', 'error');
        });
}

/**
 * Обновление информации о захоронении
 */
function updateGrave(graveId) {
    const fullName = document.getElementById('edit-full-name').value.trim();
    const birthDate = document.getElementById('edit-birth-date').value;
    const deathDate = document.getElementById('edit-death-date').value;
    const description = document.getElementById('edit-description').value.trim();

    fetch(`/api/graves/${graveId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            full_name: fullName,
            birth_date: birthDate || null,
            death_date: deathDate || null,
            description: description
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(JSON.stringify(data));
            });
        }
        return response.json();
    })
    .then(data => {
        // Обновляем список захоронений
        loadAllGraves();

        // Отображаем обновленную информацию
        loadGraveDetails(graveId);

        // Отображаем сообщение об успехе
        showNotification('Захоронение успешно обновлено', 'success');
    })
    .catch(error => {
        console.error('Ошибка при обновлении захоронения:', error);
        showNotification('Ошибка при обновлении захоронения', 'error');
    });
}

/**
 * Подтверждение удаления захоронения
 */
function confirmDeleteGrave(graveId) {
    if (confirm('Вы уверены, что хотите удалить это захоронение? Это действие нельзя отменить.')) {
        deleteGrave(graveId);
    }
}

/**
 * Удаление захоронения
 */
function deleteGrave(graveId) {
    fetch(`/api/graves/${graveId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка при удалении захоронения');
        }

        // Удаляем объект с карты
        mapApp.objectManager.objects.remove(graveId);

        // Очищаем сайдбар
        document.getElementById('sidebar-content').innerHTML = '';

        // Отображаем сообщение об успехе
        showNotification('Захоронение успешно удалено', 'success');
    })
    .catch(error => {
        console.error('Ошибка при удалении захоронения:', error);
        showNotification('Ошибка при удалении захоронения', 'error');
    });
}

/**
 * Инициализация кнопки сайдбара для мобильных устройств
 */
function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
}

/**
 * Получение CSRF-токена из cookies для защищенных запросов
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

// Обработчики в модальном окне редактирования
    const editGraveModal = document.getElementById('editGraveModal');
    if (editGraveModal) {
        editGraveModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const grave = getCurrentGrave();

            // Заполняем поля формы текущими данными
            const form = editGraveModal.querySelector('form');
            form.querySelector('#graveName').value = grave.name;
            form.querySelector('#graveDescription').value = grave.description || '';
            form.querySelector('#graveCemetery').value = grave.cemetery_id || '';
            form.querySelector('#polygon-coordinates').value = JSON.stringify(grave.polygon);

            // Отображаем текущее фото, если оно есть
            const currentPhotoContainer = form.querySelector('.current-photo');
            if (currentPhotoContainer && grave.photo_url) {
                const img = currentPhotoContainer.querySelector('img');
                if (img) {
                    img.src = grave.photo_url;
                }
            }
        });
    }