# -*- coding: utf-8 -*-
"""
Service de gestion des rendez-vous des campagnes
"""
from datetime import datetime, date, timedelta
from app import db
from app.models import Campaign, PharmacyCampaign, Pharmacy


class AppointmentService:
    """Service pour recuperer les rendez-vous des campagnes actives"""
    
    @staticmethod
    def get_upcoming_appointments(days_ahead=7):
        """
        Recupere tous les rendez-vous programmes dans les prochains jours
        depuis les campagnes actives
        
        Returns:
            list: Liste des rendez-vous avec infos de couleur
        """
        today = date.today()
        seven_days_later = today + timedelta(days=days_ahead)
        
        appointments = []
        
        # Recuperer les campagnes actives
        active_campaigns = Campaign.query.filter(
            Campaign.status == 'active',
            Campaign.start_date <= today,
            Campaign.end_date >= today
        ).all()
        
        for campaign in active_campaigns:
            # Chercher les pharmacies programmees (scheduled) dans cette campagne
            scheduled_links = PharmacyCampaign.query.filter_by(
                campaign_id=campaign.id,
                status='scheduled'
            ).all()
            
            for link in scheduled_links:
                if link.scheduled_date:
                    # Convertir en date si c'est un datetime
                    if isinstance(link.scheduled_date, datetime):
                        visit_date = link.scheduled_date.date()
                        visit_datetime = link.scheduled_date
                    else:
                        visit_date = link.scheduled_date
                        visit_datetime = link.scheduled_date
                    
                    # Verifier si c'est dans la periode demandee
                    if today <= visit_date <= seven_days_later:
                        days_until = (visit_date - today).days
                        
                        # Determiner la couleur selon l'urgence
                        if days_until >= 7:
                            color_class = 'appointment-green'
                        elif days_until >= 3:
                            color_class = 'appointment-orange'
                        else:
                            color_class = 'appointment-red'
                        
                        # Recuperer le nom de la pharmacie
                        pharmacy_name = "Pharmacie inconnue"
                        if link.pharmacy_obj:
                            pharmacy_name = link.pharmacy_obj.name
                        elif link.pharmacy_id:
                            pharmacy = Pharmacy.query.get(link.pharmacy_id)
                            if pharmacy:
                                pharmacy_name = pharmacy.name
                        
                        appointments.append({
                            'date': visit_datetime,
                            'pharmacy_name': pharmacy_name,
                            'campaign_name': campaign.name,
                            'days_until': days_until,
                            'color_class': color_class
                        })
        
        # Trier par date croissante
        appointments.sort(key=lambda x: x['date'])
        
        return appointments[:10]  # Limiter a 10 resultats