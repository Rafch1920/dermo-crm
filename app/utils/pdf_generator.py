"""
Générateur de rapports PDF avec ReportLab
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image, PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


def generate_visit_report(visits, start_date=None, end_date=None):
    """Génère un rapport de visites"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    story.append(Paragraph('Rapport de Visites', title_style))
    
    # Période
    if start_date and end_date:
        period = f"Période : {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    else:
        period = f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    story.append(Paragraph(period, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Résumé
    story.append(Paragraph('Résumé', styles['Heading2']))
    summary_data = [
        ['Nombre total de visites', str(len(visits))],
    ]
    
    if visits:
        total_duration = sum(v.duration or 0 for v in visits)
        avg_quality = sum(v.quality_score or 0 for v in visits) / len(visits) if any(v.quality_score for v in visits) else 0
        summary_data.extend([
            ['Durée totale', f'{total_duration} min'],
            ['Qualité moyenne', f'{avg_quality:.1f}/10'],
        ])
    
    summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Tableau des visites
    story.append(Paragraph('Détail des visites', styles['Heading2']))
    
    if visits:
        visit_data = [['Date', 'Pharmacie', 'Durée', 'Qualité', 'Objectif']]
        for v in visits:
            visit_data.append([
                v.visit_date.strftime('%d/%m/%Y'),
                v.pharmacy.name if v.pharmacy else '-',
                f'{v.duration} min' if v.duration else '-',
                str(v.quality_score) if v.quality_score else '-',
                (v.objective[:50] + '...') if v.objective and len(v.objective) > 50 else (v.objective or '-')
            ])
        
        visit_table = Table(visit_data, colWidths=[2.5*cm, 4*cm, 2*cm, 2*cm, 5.5*cm])
        visit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(visit_table)
    else:
        story.append(Paragraph('Aucune visite trouvée.', styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph('Dermo-CRM - Rapport généré automatiquement', footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_campaign_report(campaign):
    """Génère un rapport de campagne"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER
    )
    story.append(Paragraph(f'Rapport Campagne', title_style))
    story.append(Spacer(1, 10))
    
    # Nom campagne
    story.append(Paragraph(campaign.name, styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Infos
    story.append(Paragraph(f'<b>Période :</b> {campaign.start_date.strftime("%d/%m/%Y")} au {campaign.end_date.strftime("%d/%m/%Y")}', styles['Normal']))
    story.append(Paragraph(f'<b>Objectifs :</b> {campaign.objectives or "Non définis"}', styles['Normal']))
    story.append(Paragraph(f'<b>Avancement :</b> {campaign.get_progress()}%', styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph('Dermo-CRM - Rapport généré automatiquement', styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_zone_report(region, pharmacies):
    """Génère un rapport par zone"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    story.append(Paragraph(f'Rapport Zone : {region}', styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Stats
    story.append(Paragraph(f'<b>Nombre de pharmacies :</b> {len(pharmacies)}', styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Liste pharmacies
    if pharmacies:
        story.append(Paragraph('Pharmacies', styles['Heading2']))
        for p in pharmacies:
            story.append(Paragraph(f'• {p.name} - {p.city}', styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
