document.addEventListener('DOMContentLoaded', function() {
    // Загрузка SVG из файла
    fetch('/static/media/main_map.svg')
        .then(response => response.text())
        .then(svgContent => {
            // Вставляем SVG в контейнер
            document.getElementById('svg-map').innerHTML = svgContent;
            
            // Инициализация SVG-Pan-Zoom
            const svgElement = document.querySelector('#svg-map svg');
            if (svgElement) {
                // Добавляем атрибуты для корректной работы
                svgElement.setAttribute('width', '100%');
                svgElement.setAttribute('height', '100%');
                svgElement.setAttribute('preserveAspectRatio', 'xMidYMid meet');
                
                // Получаем viewBox SVG, если он есть
                let viewBox = svgElement.getAttribute('viewBox');
                if (!viewBox) {
                    // Если viewBox не определен, устанавливаем его на основе размеров SVG
                    const bbox = svgElement.getBBox();
                    viewBox = `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`;
                    svgElement.setAttribute('viewBox', viewBox);
                }
                
                // Инициализируем pan-zoom
                const panZoom = svgPanZoom(svgElement, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true,
                    minZoom: 0.5,
                    maxZoom: 10,
                    beforePan: function(oldPan, newPan) {
                        // Получаем текущие размеры и масштаб
                        const sizes = this.getSizes();
                        
                        // Размер SVG с учетом масштаба
                        const scaledWidth = sizes.viewBox.width * sizes.realZoom;
                        const scaledHeight = sizes.viewBox.height * sizes.realZoom;
                        
                        // Размер контейнера
                        const containerWidth = sizes.width;
                        const containerHeight = sizes.height;
                        
                        // Рассчитываем границы для перемещения
                        // Левый предел: не позволяет увидеть пустое пространство справа от SVG
                        const leftLimit = Math.min(0, containerWidth - scaledWidth);
                        // Правый предел: не позволяет увидеть пустое пространство слева от SVG
                        const rightLimit = 0;
                        
                        // Верхний предел: не позволяет увидеть пустое пространство снизу от SVG
                        const topLimit = Math.min(0, containerHeight - scaledHeight);
                        // Нижний предел: не позволяет увидеть пустое пространство сверху от SVG
                        const bottomLimit = 0;
                        
                        // Применяем ограничения
                        const customPan = {};
                        customPan.x = Math.max(leftLimit, Math.min(rightLimit, newPan.x));
                        customPan.y = Math.max(topLimit, Math.min(bottomLimit, newPan.y));
                        
                        return customPan;
                    }
                });
                
                // Обработка изменения размера окна
                window.addEventListener('resize', function() {
                    panZoom.resize();
                    panZoom.fit();
                    panZoom.center();
                });
            } else {
                console.error('SVG элемент не найден');
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки SVG:', error);
            document.getElementById('svg-map').innerHTML = '<p>Ошибка загрузки карты</p>';
        });
});