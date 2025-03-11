document.addEventListener('DOMContentLoaded', function() {
    // Загрузка SVG из файла
    fetch('/static/media/main_map.svg')
      .then(response => response.text())
      .then(svgContent => {
        // Вставляем SVG в контейнер
        document.getElementById('svg-map').innerHTML = svgContent;
        
        // Инициализация SVG-Pan-Zoom после того, как SVG загружен
        const svgElement = document.querySelector('#svg-map svg');
        if (svgElement) {
          // Добавляем атрибуты для корректной работы
          svgElement.setAttribute('width', '100%');
          svgElement.setAttribute('height', '100%');
          svgElement.setAttribute('preserveAspectRatio', 'xMidYMid meet');
          
          // Инициализируем pan-zoom
          const panZoom = svgPanZoom(svgElement, {
            zoomEnabled: true,
            controlIconsEnabled: true,
            fit: true,
            center: true,
            minZoom: 0.5,
            maxZoom: 10,
            zoomScaleSensitivity: 0.3,
            beforePan: function() {
              return {x: true, y: true}; // Разрешаем панорамирование по обеим осям
            }
          });
  
          // Обработка события resize окна
          window.addEventListener('resize', function() {
            panZoom.resize();
            panZoom.fit();
            panZoom.center();
          });
          
          // Привязываем кнопку "Показать всю карту" к функции сброса зума
          document.getElementById('reset-view').addEventListener('click', function(e) {
            e.preventDefault();
            panZoom.reset();
          });
          
          // Находим все интерактивные элементы в SVG
          const interactiveElements = svgElement.querySelectorAll('path, rect, circle, polygon, g');
          
          // Добавляем класс для интерактивности
          interactiveElements.forEach(element => {
            element.classList.add('interactive');
            
            // Добавляем обработчик клика
            element.addEventListener('click', function(event) {
              // Предотвращаем распространение события, чтобы не сработал клик на родительских элементах
              event.stopPropagation();
              
              // Удаляем класс active у всех элементов
              interactiveElements.forEach(el => {
                el.classList.remove('active');
              });
              
              // Добавляем класс active текущему элементу
              this.classList.add('active');
              
              // Получаем информацию об элементе
              const elementId = this.id || 'unknown';
              const elementType = this.tagName;
              const elementTitle = this.getAttribute('title') || this.getAttribute('data-title') || 'Без названия';
              
              // Показываем название карты в правой панели
              document.querySelector('.map-title').textContent = elementTitle;
            });
          });
        }
      })
      .catch(error => {
        console.error('Ошибка загрузки SVG:', error);
        document.getElementById('svg-map').innerHTML = '<p style="padding: 20px; color: red;">Ошибка загрузки карты</p>';
      });
      
    // Обработчик для кнопки "Скрыть всё"
    document.getElementById('hide-all').addEventListener('click', function(e) {
      e.preventDefault();
      // Здесь можно реализовать логику скрытия всех слоев
      const checkboxes = document.querySelectorAll('.layers-list input[type="checkbox"]');
      checkboxes.forEach(checkbox => {
        checkbox.checked = false;
      });
      // В реальном приложении здесь нужно будет еще скрыть соответствующие слои на карте
    });
});