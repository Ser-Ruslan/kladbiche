/**
 * Основной JavaScript файл для приложения карты кладбища
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        tooltip.title = tooltip.getAttribute('data-title');
    });

    // Обработчики событий для форм поиска
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const query = document.getElementById('id_query').value;
            const birthDateFrom = document.getElementById('id_birth_date_from').value;
            const birthDateTo = document.getElementById('id_birth_date_to').value;
            const deathDateFrom = document.getElementById('id_death_date_from').value;
            const deathDateTo = document.getElementById('id_death_date_to').value;
            const favoritesOnly = document.getElementById('id_favorites_only').checked;
            
            const searchOptions = {
                birthDateFrom: birthDateFrom,
                birthDateTo: birthDateTo,
                deathDateFrom: deathDateFrom,
                deathDateTo: deathDateTo,
                favoritesOnly: favoritesOnly
            };
            
            searchBurials(query, searchOptions);
        });
    }

    // Обработчики событий для форм добавления захоронений
    const addBurialForm = document.getElementById('add-burial-form');
    if (addBurialForm) {
        addBurialForm.addEventListener('submit', function(event) {
            event.preventDefault();
            submitBurialRequest(this);
        });
    }

    const adminAddBurialForm = document.getElementById('admin-add-burial-form');
    if (adminAddBurialForm) {
        adminAddBurialForm.addEventListener('submit', function(event) {
            event.preventDefault();
            addBurial(this);
        });
    }

    // Обработчик для кнопки получения местоположения
    const locationButton = document.getElementById('get-location');
    if (locationButton) {
        locationButton.addEventListener('click', function() {
            getCurrentLocation();
        });
    }

    // Обработчики для кнопок избранного
    const favoriteButtons = document.querySelectorAll('.favorite-toggle');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const burialId = this.getAttribute('data-burial-id');
            toggleFavorite(burialId, this);
        });
    });

    // Обработчики для форм заметок
    const noteForm = document.getElementById('note-form');
    if (noteForm) {
        noteForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const burialId = this.getAttribute('data-burial-id');
            saveNote(burialId, this);
        });
    }

    // Обработчик для кнопки удаления заметки
    const deleteNoteButton = document.getElementById('delete-note');
    if (deleteNoteButton) {
        deleteNoteButton.addEventListener('click', function() {
            const burialId = this.getAttribute('data-burial-id');
            deleteNote(burialId);
        });
    }

    // Обработчики для модальных окон
    const modalTriggers = document.querySelectorAll('[data-toggle="modal"]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            openModal(target);
        });
    });

    // Обработчики для кнопок обработки запросов на добавление захоронений
    const approveButtons = document.querySelectorAll('.approve-request');
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const requestId = this.getAttribute('data-request-id');
            processBurialRequest(requestId, 'approve');
        });
    });

    const rejectButtons = document.querySelectorAll('.reject-request');
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const requestId = this.getAttribute('data-request-id');
            const reason = prompt('Укажите причину отклонения запроса:');
            if (reason !== null) {
                processBurialRequest(requestId, 'reject', reason);
            }
        });
    });
});

// Функция для проверки формы перед отправкой
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Функция для форматирования даты в российском формате
function formatDate(dateString) {
    if (!dateString) return 'Неизвестно';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}
