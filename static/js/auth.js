/**
 * Функционал для аутентификации пользователей
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация форм аутентификации
    initLoginForm();
    initRegisterForm();
    initPasswordResetForm();
});

/**
 * Инициализация формы входа
 */
function initLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', function(e) {
        const emailInput = document.getElementById('id_username');
        const passwordInput = document.getElementById('id_password');
        
        // Базовая валидация
        if (!emailInput.value.trim()) {
            e.preventDefault();
            showFormError(emailInput, 'Пожалуйста, введите email');
            return;
        }
        
        if (!passwordInput.value.trim()) {
            e.preventDefault();
            showFormError(passwordInput, 'Пожалуйста, введите пароль');
            return;
        }
    });
}

/**
 * Инициализация формы регистрации
 */
function initRegisterForm() {
    const registerForm = document.getElementById('register-form');
    if (!registerForm) return;
    
    registerForm.addEventListener('submit', function(e) {
        const emailInput = document.getElementById('id_email');
        const usernameInput = document.getElementById('id_username');
        const password1Input = document.getElementById('id_password1');
        const password2Input = document.getElementById('id_password2');
        
        // Базовая валидация
        if (!emailInput.value.trim()) {
            e.preventDefault();
            showFormError(emailInput, 'Пожалуйста, введите email');
            return;
        }
        
        if (!validateEmail(emailInput.value.trim())) {
            e.preventDefault();
            showFormError(emailInput, 'Пожалуйста, введите корректный email');
            return;
        }
        
        if (!usernameInput.value.trim()) {
            e.preventDefault();
            showFormError(usernameInput, 'Пожалуйста, введите имя пользователя');
            return;
        }
        
        if (!password1Input.value.trim()) {
            e.preventDefault();
            showFormError(password1Input, 'Пожалуйста, введите пароль');
            return;
        }
        
        if (password1Input.value.trim().length < 8) {
            e.preventDefault();
            showFormError(password1Input, 'Пароль должен содержать не менее 8 символов');
            return;
        }
        
        if (!password2Input.value.trim()) {
            e.preventDefault();
            showFormError(password2Input, 'Пожалуйста, подтвердите пароль');
            return;
        }
        
        if (password1Input.value.trim() !== password2Input.value.trim()) {
            e.preventDefault();
            showFormError(password2Input, 'Пароли не совпадают');
            return;
        }
    });
}

/**
 * Инициализация формы сброса пароля
 */
function initPasswordResetForm() {
    const resetForm = document.getElementById('password-reset-form');
    if (!resetForm) return;
    
    resetForm.addEventListener('submit', function(e) {
        const emailInput = document.getElementById('id_email');
        
        // Базовая валидация
        if (!emailInput.value.trim()) {
            e.preventDefault();
            showFormError(emailInput, 'Пожалуйста, введите email');
            return;
        }
        
        if (!validateEmail(emailInput.value.trim())) {
            e.preventDefault();
            showFormError(emailInput, 'Пожалуйста, введите корректный email');
            return;
        }
    });
}

/**
 * Отображение ошибки валидации формы
 */
function showFormError(inputElement, errorMessage) {
    // Удаляем существующие сообщения об ошибках
    const existingError = inputElement.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Добавляем стиль ошибки к полю ввода
    inputElement.classList.add('is-invalid');
    
    // Создаем и добавляем сообщение об ошибке
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message text-danger';
    errorElement.textContent = errorMessage;
    
    inputElement.parentNode.appendChild(errorElement);
    
    // Удаляем ошибку при фокусе на поле
    inputElement.addEventListener('focus', function() {
        inputElement.classList.remove('is-invalid');
        const error = inputElement.parentNode.querySelector('.error-message');
        if (error) {
            error.remove();
        }
    });
}

/**
 * Валидация формата email
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
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
 * Получение URL для аутентификации пользователя
 */
function getLoginUrl() {
    return '/users/login/';
}

/**
 * Перенаправление на страницу входа с возвратом на текущую страницу
 */
function redirectToLogin() {
    const currentUrl = encodeURIComponent(window.location.href);
    window.location = `${getLoginUrl()}?next=${currentUrl}`;
}

/**
 * Выход пользователя из системы
 */
function logout() {
    window.location = '/users/logout/';
}
