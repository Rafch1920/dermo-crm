# -*- coding: utf-8 -*-
import os

# Chemin du dossier templates
template_dir = r"C:\Users\USER\Desktop\dermo-crm\app\templates\pharmacies"

# Contenu de create.html (sans accents)
create_html = '''{% extends 'base.html' %}

{% block title %}Nouvelle Pharmacie - Dermo-CRM{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-4">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-plus-circle"></i> Nouvelle Pharmacie</h4>
                </div>
                <div class="card-body">
                    <form method="POST" id="pharmacyForm">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        
                        <div class="mb-3">
                            <label for="name" class="form-label">Nom *</label>
                            <input type="text" class="form-control" id="name" name="name" required>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="type" class="form-label">Type</label>
                                <select class="form-select" id="type" name="type">
                                    <option value="pharmacie">Pharmacie</option>
                                    <option value="parapharmacie">Parapharmacie</option>
                                    <option value="hopital">Hopital</option>
                                    <option value="clinique">Clinique</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="referent_id" class="form-label">Referent</label>
                                <select class="form-select" id="referent_id" name="referent_id">
                                    <option value="">-- Selectionner --</option>
                                    {% for referent in referents %}
                                    <option value="{{ referent.id }}">{{ referent.name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="address" class="form-label">Adresse</label>
                            <input type="text" class="form-control" id="address" name="address" placeholder="Cliquez sur la carte">
                        </div>
                        
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label for="postal_code" class="form-label">Code Postal</label>
                                <input type="text" class="form-control" id="postal_code" name="postal_code">
                            </div>
                            <div class="col-md-4 mb-3">
                                <label for="city" class="form-label">Ville</label>
                                <input type="text" class="form-control" id="city" name="city">
                            </div>
                            <div class="col-md-4 mb-3">
                                <label for="region" class="form-label">Region</label>
                                <input type="text" class="form-control" id="region" name="region">
                            </div>
                        </div>
                        
                        <input type="hidden" id="latitude" name="latitude">
                        <input type="hidden" id="longitude" name="longitude">
                        
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> 
                            <strong>Localisation :</strong> Utilisez la carte
                        </div>
                        
                        <div class="mb-3">
                            <label for="phone" class="form-label">Telephone</label>
                            <input type="tel" class="form-control" id="phone" name="phone">
                        </div>
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email">
                        </div>
                        
                        <div class="mb-3">
                            <label for="notes" class="form-label">Notes</label>
                            <textarea class="form-control" id="notes" name="notes" rows="2"></textarea>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Creer
                            </button>
                            <a href="{{ url_for('pharmacies.index') }}" class="btn btn-outline-secondary">
                                <i class="fas fa-times"></i> Annuler
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-map-marked-alt"></i> Selection sur la carte</h5>
                    <button type="button" class="btn btn-sm btn-light" onclick="locateMe()">
                        <i class="fas fa-crosshairs"></i> Ma position
                    </button>
                </div>
                <div class="card-body p-0 position-relative" style="height: 600px;">
                    <div class="position-absolute top-0 start-0 end-0 p-2" style="z-index: 1000;">
                        <div class="input-group shadow-sm">
                            <span class="input-group-text bg-white">
                                <i class="fas fa-search text-muted"></i>
                            </span>
                            <input type="text" class="form-control" id="search-input" 
                                   placeholder="Rechercher une adresse..." autocomplete="off">
                            <button class="btn btn-primary" type="button" onclick="searchAddress()">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                        <div id="search-results" class="list-group shadow mt-1" style="display: none; max-height: 200px; overflow-y: auto;"></div>
                    </div>
                    
                    <div id="map" style="width: 100%; height: 100%;"></div>
                    
                    <div class="position-absolute bottom-0 start-0 m-3 p-2 bg-white rounded shadow" style="z-index: 1000;">
                        <small class="text-muted">
                            <i class="fas fa-mouse-pointer text-primary"></i> 
                            Cliquez sur la carte pour placer le marqueur
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
    #map { height: 100%; width: 100%; }
    .search-result-item { cursor: pointer; }
    .search-result-item:hover { background-color: #f8f9fa; }
</style>
{% endblock %}

{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    let map, marker, searchTimeout;

    function initMap() {
        map = L.map('map').setView([46.2276, 2.2137], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        map.on('click', function(e) {
            placeMarker(e.latlng);
        });
    }

    function placeMarker(latlng) {
        if (marker) map.removeLayer(marker);
        marker = L.marker(latlng, {draggable: true}).addTo(map);
        document.getElementById('latitude').value = latlng.lat.toFixed(6);
        document.getElementById('longitude').value = latlng.lng.toFixed(6);
        marker.bindPopup('Position selectionnee').openPopup();
        
        marker.on('dragend', function(e) {
            const pos = marker.getLatLng();
            document.getElementById('latitude').value = pos.lat.toFixed(6);
            document.getElementById('longitude').value = pos.lng.toFixed(6);
        });
    }

    function searchAddress() {
        const q = document.getElementById('search-input').value.trim();
        if (!q) return;
        
        fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(q) + '&limit=5')
            .then(r => r.json())
            .then(data => {
                const container = document.getElementById('search-results');
                container.innerHTML = '';
                if (data.length === 0) {
                    container.innerHTML = '<div class="list-group-item">Aucun resultat</div>';
                } else {
                    data.forEach(place => {
                        const div = document.createElement('a');
                        div.className = 'list-group-item list-group-item-action search-result-item';
                        div.innerHTML = '<strong>' + place.display_name.split(',')[0] + '</strong><br><small>' + place.display_name + '</small>';
                        div.onclick = function() {
                            const lat = parseFloat(place.lat);
                            const lng = parseFloat(place.lon);
                            map.setView([lat, lng], 16);
                            placeMarker({lat: lat, lng: lng});
                            container.style.display = 'none';
                            document.getElementById('search-input').value = place.display_name.split(',')[0];
                        };
                        container.appendChild(div);
                    });
                }
                container.style.display = 'block';
            });
    }

    function locateMe() {
        if (!navigator.geolocation) {
            alert('Geolocalisation non supportee');
            return;
        }
        navigator.geolocation.getCurrentPosition(
            function(p) {
                const lat = p.coords.latitude;
                const lng = p.coords.longitude;
                map.setView([lat, lng], 15);
                placeMarker({lat: lat, lng: lng});
            },
            function(e) {
                alert('Erreur: ' + e.message);
            }
        );
    }

    document.getElementById('search-input').addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (q.length < 3) {
            document.getElementById('search-results').style.display = 'none';
            return;
        }
        searchTimeout = setTimeout(searchAddress, 500);
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('#search-input') && !e.target.closest('#search-results')) {
            document.getElementById('search-results').style.display = 'none';
        }
    });

    document.addEventListener('DOMContentLoaded', initMap);
</script>
{% endblock %}
'''

# Contenu de edit.html (sans accents)
edit_html = '''{% extends 'base.html' %}

{% block title %}Modifier Pharmacie - Dermo-CRM{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-4">
            <div class="card shadow">
                <div class="card-header bg-warning text-dark">
                    <h4 class="mb-0"><i class="fas fa-edit"></i> Modifier {{ pharmacy.name }}</h4>
                </div>
                <div class="card-body">
                    <form method="POST" id="pharmacyForm">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        
                        <div class="mb-3">
                            <label for="name" class="form-label">Nom *</label>
                            <input type="text" class="form-control" id="name" name="name" value="{{ pharmacy.name }}" required>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="type" class="form-label">Type</label>
                                <select class="form-select" id="type" name="type">
                                    <option value="pharmacie" {% if pharmacy.type == 'pharmacie' %}selected{% endif %}>Pharmacie</option>
                                    <option value="parapharmacie" {% if pharmacy.type == 'parapharmacie' %}selected{% endif %}>Parapharmacie</option>
                                    <option value="hopital" {% if pharmacy.type == 'hopital' %}selected{% endif %}>Hopital</option>
                                    <option value="clinique" {% if pharmacy.type == 'clinique' %}selected{% endif %}>Clinique</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="referent_id" class="form-label">Referent</label>
                                <select class="form-select" id="referent_id" name="referent_id">
                                    <option value="">-- Selectionner --</option>
                                    {% for referent in referents %}
                                    <option value="{{ referent.id }}" {% if pharmacy.referent_id == referent.id %}selected{% endif %}>
                                        {{ referent.name }}
                                    </option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="address" class="form-label">Adresse</label>
                            <input type="text" class="form-control" id="address" name="address" value="{{ pharmacy.address or '' }}">
                        </div>
                        
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label for="postal_code" class="form-label">Code Postal</label>
                                <input type="text" class="form-control" id="postal_code" name="postal_code" value="{{ pharmacy.postal_code or '' }}">
                            </div>
                            <div class="col-md-4 mb-3">
                                <label for="city" class="form-label">Ville</label>
                                <input type="text" class="form-control" id="city" name="city" value="{{ pharmacy.city or '' }}">
                            </div>
                            <div class="col-md-4 mb-3">
                                <label for="region" class="form-label">Region</label>
                                <input type="text" class="form-control" id="region" name="region" value="{{ pharmacy.region or '' }}">
                            </div>
                        </div>
                        
                        <input type="hidden" id="latitude" name="latitude" value="{{ pharmacy.latitude or '' }}">
                        <input type="hidden" id="longitude" name="longitude" value="{{ pharmacy.longitude or '' }}">
                        
                        <div class="alert alert-info">
                            <i class="fas fa-map-marker-alt"></i> 
                            <strong>Position :</strong><br>
                            <small>
                                Lat: <span id="display-lat">{{ pharmacy.latitude or 'Non defini' }}</span><br>
                                Lng: <span id="display-lng">{{ pharmacy.longitude or 'Non defini' }}</span>
                            </small>
                        </div>
                        
                        <div class="mb-3">
                            <label for="phone" class="form-label">Telephone</label>
                            <input type="tel" class="form-control" id="phone" name="phone" value="{{ pharmacy.phone or '' }}">
                        </div>
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" value="{{ pharmacy.email or '' }}">
                        </div>
                        
                        <div class="mb-3">
                            <label for="notes" class="form-label">Notes</label>
                            <textarea class="form-control" id="notes" name="notes" rows="2">{{ pharmacy.notes or '' }}</textarea>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-warning">
                                <i class="fas fa-save"></i> Enregistrer
                            </button>
                            <a href="{{ url_for('pharmacies.index') }}" class="btn btn-outline-secondary">
                                <i class="fas fa-times"></i> Annuler
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-map-marked-alt"></i> Modifier la position</h5>
                    <div>
                        <button type="button" class="btn btn-sm btn-light me-2" onclick="searchAddress()">
                            <i class="fas fa-search"></i> Rechercher
                        </button>
                        <button type="button" class="btn btn-sm btn-light" onclick="locateMe()">
                            <i class="fas fa-crosshairs"></i> Ma position
                        </button>
                    </div>
                </div>
                <div class="card-body p-0 position-relative" style="height: 600px;">
                    <div class="position-absolute top-0 start-0 end-0 p-2" style="z-index: 1000;">
                        <div class="input-group shadow-sm">
                            <span class="input-group-text bg-white">
                                <i class="fas fa-search text-muted"></i>
                            </span>
                            <input type="text" class="form-control" id="search-input" 
                                   placeholder="Rechercher..." autocomplete="off">
                            <button class="btn btn-primary" type="button" onclick="searchAddress()">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                        <div id="search-results" class="list-group shadow mt-1" style="display: none; max-height: 200px; overflow-y: auto;"></div>
                    </div>
                    
                    <div id="map" style="width: 100%; height: 100%;"></div>
                    
                    <div class="position-absolute bottom-0 start-0 m-3 p-2 bg-white rounded shadow" style="z-index: 1000;">
                        <small class="text-muted">
                            <i class="fas fa-mouse-pointer text-primary"></i> 
                            Cliquez ou deplacez le marqueur
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
    #map { height: 100%; width: 100%; }
    .search-result-item { cursor: pointer; }
    .search-result-item:hover { background-color: #f8f9fa; }
</style>
{% endblock %}

{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    let map, marker, searchTimeout;
    const existingLat = {{ pharmacy.latitude | default('null', true) }};
    const existingLng = {{ pharmacy.longitude | default('null', true) }};

    function initMap() {
        const defaultLat = existingLat || 46.2276;
        const defaultLng = existingLng || 2.2137;
        const defaultZoom = existingLat ? 15 : 6;

        map = L.map('map').setView([defaultLat, defaultLng], defaultZoom);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        if (existingLat && existingLng) {
            marker = L.marker([existingLat, existingLng], {draggable: true}).addTo(map);
            marker.bindPopup('Position actuelle').openPopup();
            marker.on('dragend', function() {
                updatePosition(marker.getLatLng());
            });
        }

        map.on('click', function(e) {
            if (marker) map.removeLayer(marker);
            marker = L.marker(e.latlng, {draggable: true}).addTo(map);
            updatePosition(e.latlng);
            marker.on('dragend', function() {
                updatePosition(marker.getLatLng());
            });
        });
    }

    function updatePosition(latlng) {
        document.getElementById('latitude').value = latlng.lat.toFixed(6);
        document.getElementById('longitude').value = latlng.lng.toFixed(6);
        document.getElementById('display-lat').textContent = latlng.lat.toFixed(6);
        document.getElementById('display-lng').textContent = latlng.lng.toFixed(6);
        if (marker) {
            marker.setPopupContent('Nouvelle position').openPopup();
        }
    }

    function searchAddress() {
        const q = document.getElementById('search-input').value.trim();
        if (!q) return;
        
        fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(q) + '&limit=5')
            .then(r => r.json())
            .then(data => {
                const container = document.getElementById('search-results');
                container.innerHTML = '';
                if (data.length === 0) {
                    container.innerHTML = '<div class="list-group-item">Aucun resultat</div>';
                } else {
                    data.forEach(place => {
                        const div = document.createElement('a');
                        div.className = 'list-group-item list-group-item-action search-result-item';
                        div.innerHTML = '<strong>' + place.display_name.split(',')[0] + '</strong><br><small>' + place.display_name + '</small>';
                        div.onclick = function() {
                            const lat = parseFloat(place.lat);
                            const lng = parseFloat(place.lon);
                            map.setView([lat, lng], 16);
                            if (marker) map.removeLayer(marker);
                            marker = L.marker([lat, lng], {draggable: true}).addTo(map);
                            updatePosition({lat: lat, lng: lng});
                            marker.on('dragend', function() {
                                updatePosition(marker.getLatLng());
                            });
                            container.style.display = 'none';
                            document.getElementById('search-input').value = place.display_name.split(',')[0];
                        };
                        container.appendChild(div);
                    });
                }
                container.style.display = 'block';
            });
    }

    function locateMe() {
        if (!navigator.geolocation) {
            alert('Geolocalisation non supportee');
            return;
        }
        navigator.geolocation.getCurrentPosition(
            function(p) {
                const lat = p.coords.latitude;
                const lng = p.coords.longitude;
                map.setView([lat, lng], 15);
                if (marker) map.removeLayer(marker);
                marker = L.marker([lat, lng], {draggable: true}).addTo(map);
                updatePosition({lat: lat, lng: lng});
                marker.on('dragend', function() {
                    updatePosition(marker.getLatLng());
                });
            },
            function(e) {
                alert('Erreur: ' + e.message);
            }
        );
    }

    document.getElementById('search-input').addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (q.length < 3) {
            document.getElementById('search-results').style.display = 'none';
            return;
        }
        searchTimeout = setTimeout(searchAddress, 500);
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('#search-input') && !e.target.closest('#search-results')) {
            document.getElementById('search-results').style.display = 'none';
        }
    });

    document.addEventListener('DOMContentLoaded', initMap);
</script>
{% endblock %}
'''

# Contenu de detail.html (sans accents)
detail_html = '''{% extends 'base.html' %}

{% block title %}{{ pharmacy.name }} - Dermo-CRM{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2><i class="fas fa-clinic-medical text-primary"></i> {{ pharmacy.name }}</h2>
            <p class="text-muted mb-0">
                <i class="fas fa-map-marker-alt"></i> {{ pharmacy.address or 'Adresse non definie' }}, {{ pharmacy.city or '' }}
                {% if pharmacy.referent %}
                <span class="ms-3"><i class="fas fa-user"></i> Referent: {{ pharmacy.referent.name }}</span>
                {% endif %}
            </p>
        </div>
        <div>
            <a href="{{ url_for('pharmacies.edit', id=pharmacy.id) }}" class="btn btn-warning">
                <i class="fas fa-edit"></i> Modifier
            </a>
            <a href="{{ url_for('pharmacies.index') }}" class="btn btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Retour
            </a>
        </div>
    </div>

    <div class="row">
        <div class="col-md-4">
            <div class="card shadow mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="fas fa-info-circle"></i> Informations</h5>
                </div>
                <div class="card-body">
                    <table class="table table-borderless">
                        <tr>
                            <td><i class="fas fa-building text-muted"></i> Type</td>
                            <td class="text-end"><span class="badge bg-secondary">{{ pharmacy.type or 'Non defini' }}</span></td>
                        </tr>
                        <tr>
                            <td><i class="fas fa-phone text-muted"></i> Telephone</td>
                            <td class="text-end">{{ pharmacy.phone or '-' }}</td>
                        </tr>
                        <tr>
                            <td><i class="fas fa-envelope text-muted"></i> Email</td>
                            <td class="text-end">{{ pharmacy.email or '-' }}</td>
                        </tr>
                        <tr>
                            <td><i class="fas fa-map-pin text-muted"></i> Code postal</td>
                            <td class="text-end">{{ pharmacy.postal_code or '-' }}</td>
                        </tr>
                        <tr>
                            <td><i class="fas fa-globe text-muted"></i> Region</td>
                            <td class="text-end">{{ pharmacy.region or '-' }}</td>
                        </tr>
                        {% if pharmacy.latitude and pharmacy.longitude %}
                        <tr>
                            <td><i class="fas fa-location-arrow text-muted"></i> GPS</td>
                            <td class="text-end">
                                <small class="text-muted">{{ pharmacy.latitude }}, {{ pharmacy.longitude }}</small>
                            </td>
                        </tr>
                        {% endif %}
                    </table>
                    
                    {% if pharmacy.notes %}
                    <hr>
                    <h6><i class="fas fa-sticky-note"></i> Notes</h6>
                    <p class="text-muted">{{ pharmacy.notes }}</p>
                    {% endif %}
                </div>
            </div>

            <div class="card shadow mb-4">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0"><i class="fas fa-users"></i> Contacts ({{ contacts|length }})</h5>
                </div>
                <div class="card-body">
                    {% if contacts %}
                        {% for contact in contacts %}
                        <div class="d-flex justify-content-between align-items-start mb-3 {% if not loop.last %}border-bottom pb-2{% endif %}">
                            <div>
                                <h6 class="mb-1">
                                    {{ contact.name }}
                                    {% if contact.is_primary %}
                                    <span class="badge bg-primary badge-sm">Principal</span>
                                    {% endif %}
                                </h6>
                                <small class="text-muted">{{ contact.role or 'Non defini' }}</small><br>
                                {% if contact.phone %}
                                <small><i class="fas fa-phone text-success"></i> {{ contact.phone }}</small><br>
                                {% endif %}
                                {% if contact.email %}
                                <small><i class="fas fa-envelope text-info"></i> {{ contact.email }}</small>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p class="text-muted text-center mb-0">Aucun contact enregistre</p>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="col-md-8">
            {% if pharmacy.latitude and pharmacy.longitude %}
            <div class="card shadow mb-4">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="fas fa-map"></i> Localisation</h5>
                </div>
                <div class="card-body p-0">
                    <div id="map" style="height: 300px; width: 100%;"></div>
                </div>
            </div>
            {% endif %}

            <div class="card shadow">
                <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-calendar-check"></i> Visites ({{ visits|length }})</h5>
                    <a href="{{ url_for('visits.create', pharmacy_id=pharmacy.id) }}" class="btn btn-sm btn-success">
                        <i class="fas fa-plus"></i> Nouvelle visite
                    </a>
                </div>
                <div class="card-body">
                    {% if visits %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Type</th>
                                    <th>Agent</th>
                                    <th>Duree</th>
                                    <th>Score</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for visit in visits %}
                                <tr>
                                    <td>{{ visit.visit_date.strftime('%d/%m/%Y') if visit.visit_date else '-' }}</td>
                                    <td>
                                        <span class="badge bg-{{ 'primary' if visit.visit_type == 'planifiee' else 'info' if visit.visit_type == 'ponctuelle' else 'secondary' }}">
                                            {{ visit.visit_type or 'Non defini' }}
                                        </span>
                                    </td>
                                    <td>{{ visit.user.full_name if visit.user else '-' }}</td>
                                    <td>{{ visit.duration or '-' }} min</td>
                                    <td>
                                        {% if visit.quality_score %}
                                            <span class="badge bg-{{ 'success' if visit.quality_score >= 4 else 'warning' if visit.quality_score >= 3 else 'danger' }}">
                                                {{ visit.quality_score }}/5
                                            </span>
                                        {% else %}
                                            -
                                        {% endif %}
                                    </td>
                                    <td>
                                        <a href="{{ url_for('visits.detail', id=visit.id) }}" class="btn btn-sm btn-outline-primary">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                        <p class="text-muted text-center mb-0">Aucune visite enregistree</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_css %}
{% if pharmacy.latitude and pharmacy.longitude %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
{% endif %}
{% endblock %}

{% block extra_js %}
{% if pharmacy.latitude and pharmacy.longitude %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const lat = {{ pharmacy.latitude }};
        const lng = {{ pharmacy.longitude }};
        
        const map = L.map('map').setView([lat, lng], 15);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'OpenStreetMap contributors'
        }).addTo(map);
        
        L.marker([lat, lng]).addTo(map)
            .bindPopup('<b>{{ pharmacy.name }}</b><br>{{ pharmacy.address or "" }}')
            .openPopup();
    });
</script>
{% endif %}
{% endblock %}
'''

# Supprimer les anciens fichiers et creer les nouveaux
files = {
    'create.html': create_html,
    'edit.html': edit_html,
    'detail.html': detail_html
}

for filename, content in files.items():
    filepath = os.path.join(template_dir, filename)
    # Supprimer l'ancien fichier s'il existe
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Supprime: {filename}")
    
    # Creer le nouveau fichier en UTF-8
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cree: {filename}")

print("\nTous les fichiers ont ete recrees avec succes!")
print("Redemarrez Flask et testez.")