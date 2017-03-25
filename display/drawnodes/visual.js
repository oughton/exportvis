$(document).ready(function() {
    var _render = function(origin, path, ports) {
        map = _createMap(origin);

        node_lookup = {};

        for (var i = 0; i < path.length; i++) {
            node = path[i];
            //_drawNode(map, node);
            node_lookup[node.node] = node;
        };

        for (var i = 0; i < path.length; i++) {
            var from_node = path[i];

            for (var j = 0; j < from_node.edges.length; j++) {
                var edge = from_node.edges[j];
                var to_node = node_lookup[edge]

                if (to_node)
                    _drawLine(map, from_node, to_node);
            };
        };

        for (var i = 0; i < ports.length; i++) {
            var port = ports[i];
            _drawNode(map, port);
        }
    };

    var _drawNode = function(map, node) {
        var options = {
            strokeWeight: 0,
            fillColor: '#0000FF',
            fillOpacity: 1,
            map: map,
            center: _toMapLatLng(node.lat, node.lon),
            radius: 150000
        };

        var circle = new google.maps.Circle(options);

        var popup = null;

        circle.addListener('mouseover', function(event) {
            popup = new google.maps.InfoWindow({
                content: node.name + ': ' + _formatValue(node.value),
                map: map,
                position: event.latLng
            });

            popup.open(map, this);
        });

        circle.addListener('mouseout', function(event) {
            if (popup)
                popup.close();
        });
    };

    var _drawLine = function(map, from_node, to_node) {
        var coords = [
            { lat: from_node.lat, lng: from_node.lon },
            { lat: to_node.lat, lng: to_node.lon }
        ];

        var path = new google.maps.Polyline({
            path: coords,
            //geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: to_node.weight * 50
        });

        path.setMap(map);

        var popup = null;

        path.addListener('mouseover', function(event) {
            popup = new google.maps.InfoWindow({
                content: _formatValue(to_node.value),
                map: map,
                position: event.latLng
            });

            popup.open(map, this);
        });

        path.addListener('mouseout', function(event) {
            if (popup)
                popup.close();
        });
    };

    var _circleContains = function(circle, latLng) {
        return circle.getBounds().contains(latLng)
            && google.maps.geometry.spherical.computeDistanceBetween(circle.getCenter(), latLng) <= circle.getRadius();
    }

    var _formatValue = function(value) {
        var result = value;
        var unit;

        if (result >= 1000000000) {
            result = result / 1000000000.0;
            unit = 'billion';
        } else if (result >= 1000000) {
            result = result / 1000000.0;
            unit = 'million';
        } else {
            result = result;
            unit = '';
        }

        result = result.toFixed(2)
        return '$' + result + ' ' + unit;
    }

    var _createMap = function(mapLatLon) {
        var mapOptions = {
            center: mapLatLon,
            zoom: 2
        };

        elem = document.getElementById('map-canvas')
        var map = new google.maps.Map(elem, mapOptions);

        var bounds = new google.maps.LatLngBounds();
        bounds.extend(mapLatLon);

        return map;
    };

    var _toMapLatLng = function(lat, lon) {
        return new google.maps.LatLng(lat, lon);
    };

    var _run = function(path, ports) {
    	origin = _toMapLatLng(-41.291212, 174.781897)
    	_render(origin, path, ports)
    }

    //var path = 'shippingroutes.json';
    var path = 'paths.json'
    var ports = 'ports.json'

    $.getJSON(path, function(path_data) {
        $.getJSON(ports, function(port_data) {
            _run(path_data.nodes, port_data.ports);
        }.bind(this));
    }.bind(this));
});