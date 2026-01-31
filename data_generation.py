import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_cnss_data(n_enterprises=500, n_months=24):
    """Génère des données synthétiques réalistes pour la CNSS Djibouti"""
    
    # Secteurs économiques de Djibouti
    sectors = [
        'TRANSPORT_LOGISTIQUE', 'BATIMENT_TRAVAUX_PUBLICS', 'COMMERCE',
        'HOTELLERIE_RESTAURATION', 'TELECOM', 'BANQUE_ASSURANCE',
        'ADMINISTRATION_PUBLIQUE', 'SANTE', 'EDUCATION'
    ]
    
    # Tailles d'entreprises
    sizes = ['TPE (1-9)', 'PME (10-49)', 'ETI (50-249)', 'GE (250+)']
    
    # Localisations à Djibouti
    locations = ['DJIBOUTI-VILLE', 'ALI-SABIEH', 'TADJOURA', 'OBOCK', 'DIKHIL', 'ARTA']
    
    data = []
    enterprise_ids = []
    
    # Créer les entreprises
    for i in range(n_enterprises):
        ent_id = f'ENT_{str(i+1).zfill(4)}'
        enterprise_ids.append(ent_id)
        
        sector = np.random.choice(sectors, p=[0.25, 0.15, 0.20, 0.10, 0.05, 0.05, 0.10, 0.05, 0.05])
        size = np.random.choice(sizes, p=[0.40, 0.35, 0.20, 0.05])  # Plus de petites entreprises
        location = np.random.choice(locations, p=[0.70, 0.05, 0.05, 0.05, 0.10, 0.05])
        
        # Caractéristiques de base
        base_employees = {
            'TPE (1-9)': np.random.randint(3, 10),
            'PME (10-49)': np.random.randint(10, 50),
            'ETI (50-249)': np.random.randint(50, 150),
            'GE (250+)': np.random.randint(250, 1000)
        }[size]
        
        # Salaire moyen par secteur (en francs DJ)
        avg_salary = {
            'TRANSPORT_LOGISTIQUE': 150000,
            'BATIMENT_TRAVAUX_PUBLICS': 120000,
            'COMMERCE': 90000,
            'HOTELLERIE_RESTAURATION': 80000,
            'TELECOM': 300000,
            'BANQUE_ASSURANCE': 350000,
            'ADMINISTRATION_PUBLIQUE': 200000,
            'SANTE': 180000,
            'EDUCATION': 140000
        }[sector]
        
        # Créer les déclarations mensuelles
        current_date = datetime(2022, 1, 1)
        
        for month in range(n_months):
            # Variations naturelles
            month_variation = np.random.uniform(0.9, 1.1)
            employees_this_month = max(1, int(base_employees * np.random.uniform(0.95, 1.05)))
            
            # Salaire déclaré (avec risque de sous-déclaration)
            if np.random.random() < 0.15:  # 15% des entreprises sous-déclarent
                underdeclaration_rate = np.random.uniform(0.6, 0.9)  # Déclare 60-90% du vrai salaire
            else:
                underdeclaration_rate = 1.0
            
            declared_avg_salary = avg_salary * underdeclaration_rate * month_variation
            
            # Masse salariale déclarée
            declared_mass = employees_this_month * declared_avg_salary
            
            # Cotisations CNSS (23% patronal + 6% salarial en moyenne)
            cotisations = declared_mass * 0.29
            
            # Retard de paiement (certaines entreprises payent en retard)
            if np.random.random() < 0.20:  # 20% ont des retards
                days_late = int(np.random.choice([15, 30, 45, 60, 90], p=[0.4, 0.3, 0.15, 0.1, 0.05]))

            else:
                days_late = 0
            
            # Date de paiement
            payment_date = current_date + timedelta(days=10 + days_late)
            
            # Anomalie flag (pour l'entraînement supervisé plus tard)
            is_fraud = 1 if underdeclaration_rate < 0.85 else 0
            is_late = 1 if days_late > 30 else 0
            
            data.append({
                'entreprise_id': ent_id,
                'date_declaration': current_date.strftime('%Y-%m-%d'),
                'secteur': sector,
                'taille': size,
                'localisation': location,
                'nb_salaries_declares': employees_this_month,
                'salaire_moyen_declare': round(declared_avg_salary),
                'masse_salariale_declaree': round(declared_mass),
                'cotisations_dues': round(cotisations),
                'date_paiement': payment_date.strftime('%Y-%m-%d'),
                'jours_retard': days_late,
                'montant_paye': round(cotisations * (0.7 if np.random.random() < 0.05 else 1.0)),
                'sous_declaration_taux': round(underdeclaration_rate, 2),
                'flag_fraude': is_fraud,
                'flag_retard_grave': is_late,
                'annee': current_date.year,
                'mois': current_date.month
            })
            
            current_date += timedelta(days=30)  # Mois suivant
    
    return pd.DataFrame(data)

# Génération et sauvegarde
print("Génération des données synthétiques CNSS...")
df = generate_cnss_data(n_enterprises=300, n_months=24)
df.to_csv('data/raw/declarations_cnss_synthétiques.csv', index=False, encoding='utf-8')
print(f"Données générées : {len(df)} lignes, {len(df['entreprise_id'].unique())} entreprises")
print("Colonnes:", df.columns.tolist())