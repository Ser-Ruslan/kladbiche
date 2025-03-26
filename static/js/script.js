ymaps.ready(function () {
    if (window.geoJsonData) {
        // Создаем карту
        var map = new ymaps.Map('map', {
            center: [52.06, 113.52],
            zoom: 15,
            controls: ['zoomControl', 'typeSelector', 'searchControl'],
            behaviors: ['default', 'scrollZoom']
        });

        // Объект для хранения слоев
        var layers = {
            'Граница территории': new ymaps.GeoObjectCollection(),
            'Основные дороги': new ymaps.GeoObjectCollection(),
            'Второстепенные дороги': new ymaps.GeoObjectCollection(),
            'Памятные места': new ymaps.GeoObjectCollection()
        };
        
        // Распределяем объекты по слоям
        window.geoJsonData.features.forEach(function(feature) {
            var geoObject = new ymaps.GeoObject({
                geometry: feature.geometry,
                properties: feature.properties
            }, {
                strokeColor: feature.properties.stroke,
                strokeWidth: feature.properties['stroke-width'],
                strokeOpacity: feature.properties['stroke-opacity'],
                fillColor: feature.properties.fill,
                fillOpacity: feature.properties['fill-opacity'],
                preset: 'islands#blueDotIconWithCaption'
            });

            if (feature.geometry.type === 'Polygon') {
                layers['Граница территории'].add(geoObject);
            } 
            else if (feature.geometry.type === 'LineString') {
                if (feature.properties.stroke === '#ed4543') {
                    layers['Основные дороги'].add(geoObject);
                } else if (feature.properties.stroke === '#ff931e') {
                    layers['Второстепенные дороги'].add(geoObject);
                }
            }
            else if (feature.geometry.type === 'Point') {
                layers['Памятные места'].add(geoObject);
            }
        });

        // Добавляем все слои на карту и создаем элементы управления
        var layersList = document.getElementById('layersList');
        
        Object.keys(layers).forEach(function(layerName) {
            map.geoObjects.add(layers[layerName]);
            
            var layerItem = document.createElement('div');
            layerItem.className = 'layer-item';
            
            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'layer-checkbox';
            checkbox.checked = true;
            
            var label = document.createElement('span');
            label.className = 'layer-name';
            label.textContent = layerName;
            
            layerItem.appendChild(checkbox);
            layerItem.appendChild(label);
            layersList.appendChild(layerItem);
            
            checkbox.addEventListener('change', function(e) {
                if (e.target.checked) {
                    map.geoObjects.add(layers[layerName]);
                } else {
                    map.geoObjects.remove(layers[layerName]);
                }
            });
        });

        // Устанавливаем границы карты
        var bounds = map.geoObjects.getBounds();
        if (bounds) {
            map.setBounds(bounds, {
                checkZoomRange: true,
                zoomMargin: 50
            });

            var extendCoef = 0.2;
            var latDiff = (bounds[1][0] - bounds[0][0]) * extendCoef;
            var lonDiff = (bounds[1][1] - bounds[0][1]) * extendCoef;

            var restrictedBounds = [
                [bounds[0][0] - latDiff, bounds[0][1] - lonDiff],
                [bounds[1][0] + latDiff, bounds[1][1] + lonDiff]
            ];

            map.options.set({
                restrictMapArea: restrictedBounds,
                minZoom: map.getZoom() - 2,
                maxZoom: 19
            });
        }
    } else {
        console.error('GeoJSON data not available');
        var map = new ymaps.Map('map', {
            center: [52.06, 113.52],
            zoom: 15,
            controls: ['zoomControl', 'typeSelector', 'searchControl']
        });
    }
});

function togglePanel() {
    const panel = document.getElementById('rightPanel');
    panel.classList.toggle('active');
}