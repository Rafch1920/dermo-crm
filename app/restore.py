# -*- coding: utf-8 -*-
import os

base_dir = r"C:\Users\USER\Desktop\dermo-crm\app\templates"

# Sauvegarde les fichiers existants avant modification
import shutil
from datetime import datetime

backup_dir = os.path.join(base_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
os.makedirs(backup_dir, exist_ok=True)

# Liste des fichiers à vérifier/réparer
files_to_check = {
    'pharmacies/create.html': '''{% extends 'base.html' %}

{% block title %}Nouvelle Pharmacie - Dermo-CRM{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Formulaire -->
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
                            <input type="text" class="form-control" id="address" name="address">
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
                            <i class="fas fa-info-circle"></i> Cliquez sur la carte pour positionner
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
                                Annuler
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- Carte -->
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-map-marked-alt"></i> Selection sur la carte</h5>
                    <button type="button" class="btn btn-sm btn-light" onclick="locateMe()">
                        <i class="fas fa-crosshairs"></i> Ma position
                    </button>
                </div>
                <div class="card-body p-0 position-relative" style="height: 600px;">
                    <!-- Barre de recherche -->
                    <div class="position-absolute top-0 start-0 end-0 p-2" style="z-index: 1000;">
                        <div class="input-group shadow-sm">
                            <span class="input-group-text bg-white"><i class="fas fa-search text-muted"></i></span>
                            <input type="text" class="form-control" id="search-input" placeholder="Rechercher une adresse..." autocomplete="off">
                            <button class="btn btn-primary" type="button" onclick="searchAddress()">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                        <div id="search-results" class="list-group shadow mt-1" style="display: none; max-height: 200px; overflow-y: auto;"></div>
                    </div>
                    
                    <div id="map" style="width: 100%; height: 100%;"></div>
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
            attribution: 'OSM',
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
        
        marker.on('dragend', function() {
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
                        div.onclick = () => {
                            const lat = parseFloat(place.lat), lng = parseFloat(place.lon);
                            map.setView([lat, lng], 16);
                            placeMarker({lat, lng});
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
            (p) => {
                const lat = p.coords.latitude, lng = p.coords.longitude;
                map.setView([lat, lng], 15);
                placeMarker({lat, lng});
            },
            (e) => alert('Erreur: ' + e.message)
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
{% endblock %}'''
}

# Fonction pour sauvegarder et ecrire
def safe_write(filepath, content):
    full_path = os.path.join(base_dir, filepath)
    folder = os.path.dirname(full_path)
    os.makedirs(folder, exist_ok=True)
    
    # Sauvegarde si existe
    if os.path.exists(full_path):
        backup_path = os.path.join(backup_dir, filepath.replace('/', '_'))
        shutil.copy2(full_path, backup_path)
        print(f"Sauvegarde: {filepath} -> backup/")
    
    # Ecriture
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Ecrit: {filepath}")

# Executer
for filepath, content in files_to_check.items():
    safe_write(filepath, content)

print(f"\nSauvegardes dans: {backup_dir}")
print("Redemarrez Flask.")