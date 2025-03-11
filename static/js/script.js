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
                // Устанавливаем атрибуты width/height в 100%
                svgElement.setAttribute('width', '100%');
                svgElement.setAttribute('height', '100%');

                // Получаем viewBox SVG
                let viewBox = svgElement.getAttribute('viewBox');
                if (!viewBox) {
                    const bbox = svgElement.getBBox();
                    viewBox = `0 0 ${bbox.width} ${bbox.height}`;
                    svgElement.setAttribute('viewBox', viewBox);
                }

                // Разбираем viewBox для установки границ панорамирования
                const viewBoxValues = viewBox.split(' ').map(Number);
                const viewBoxWidth = viewBoxValues[2];
                const viewBoxHeight = viewBoxValues[3];

                // Инициализация библиотеки
                const panZoom = svgPanZoom(svgElement, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true,
                    minZoom: 1.9,
                    maxZoom: 10,
                    zoomScaleSensitivity: 0.3,
                    // Ограничения панорамирования
                    panLimit: true,
                    boundPadding: 0.1, // отступ от границ
                    // Ограничения перетаскивания
                    restrictPan: true,
                    // Обработчики событий для более точного контроля
                    beforePan: function(oldPan, newPan) {
                        // Ограничиваем перетаскивание границами SVG
                        const sizes = this.getSizes();
                        const restrictedPan = {
                            x: Math.max(Math.min(newPan.x, 0), sizes.width - sizes.viewBox.width * sizes.realZoom),
                            y: Math.max(Math.min(newPan.y, 0), sizes.height - sizes.viewBox.height * sizes.realZoom)
                        };
                        return restrictedPan;
                    },
                    beforeZoom: function(oldScale, newScale) {
                        // Возвращаем true для разрешения зума
                        return true;
                    }
                });

                // Обработчик события колеса мыши для SVG-контейнера
                document.getElementById('svg-map').addEventListener('wheel', function(e) {
                    // Если нажата клавиша Ctrl, блокируем зум SVG и позволяем браузеру масштабировать страницу
                    if (e.ctrlKey) {
                        e.stopPropagation();
                        // Отключаем обработку события библиотекой svg-pan-zoom
                        return true;
                    }
                    // Для обычного скролла (без Ctrl) позволяем svg-pan-zoom обрабатывать событие
                }, { passive: false });

                // Обработчик для блокировки стандартного поведения Ctrl+колесо при наведении на SVG
                svgElement.addEventListener('wheel', function(e) {
                    if (e.ctrlKey) {
                        // Не блокируем стандартное поведение браузера при Ctrl+колесо
                        return true;
                    }
                }, { passive: true });

                // Дополнительный глобальный обработчик для восстановления зума после потери фокуса
                window.addEventListener('focus', function() {
                    if (panZoom) {
                        panZoom.enableZoom();
                    }
                });
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки SVG:', error);
        });
});