"""
Utilitaires de géocodage
"""
import requests
from flask import current_app


def geocode_address(address):
    """
    Géocode une adresse avec Nominatim (OpenStreetMap)
    Retourne {'lat': float, 'lng': float} ou None
    """
    try:
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'fr'
        }
        headers = {
            'User-Agent': 'Dermo-CRM/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data and len(data) > 0:
            return {
                'lat': float(data[0]['lat']),
                'lng': float(data[0]['lon'])
            }
    except Exception as e:
        current_app.logger.error(f'Geocoding error: {e}')
    
    return None


def reverse_geocode(lat, lng):
    """
    Reverse geocoding : coordonnées -> adresse
    """
    try:
        url = 'https://nominatim.openstreetmap.org/reverse'
        params = {
            'lat': lat,
            'lon': lng,
            'format': 'json'
        }
        headers = {
            'User-Agent': 'Dermo-CRM/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data:
            return {
                'address': data.get('display_name', ''),
                'city': data.get('address', {}).get('city', ''),
                'postcode': data.get('address', {}).get('postcode', '')
            }
    except Exception as e:
        current_app.logger.error(f'Reverse geocoding error: {e}')
    
    return None
