import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_cnss_data():
    print("Génération de données synthétiques CNSS...")
    
    # Créer le dossier si nécessaire
    os.makedirs('data/raw', exist_ok=True)
    
    # Paramètres
    n_enterprises = 200
    n_months = 12
    
    # Données de base
    sectors = ['TRANSPORT_LOGISTIQUE', 'BATIMENT_TRAVAUX_PUBLICS', 'COMMERCE',
               'HOTELLERIE_RESTAURATION', 'TELECOM', 'BANQUE_ASSURANCE',
               'ADMINISTRATION_PUBLIQUE', 'SANTE', 'EDUCATION']
    
    sizes = ['TPE (1-9)', 'PME (10-49)', 'ETI (50-249)', 'GE (250+)']
    locations = ['DJIBOUTI-VILLE', 'ALI-SABIEH', 'TADJOURA', 'OBOCK', 'DIKHIL', 'ARTA']
    
    data = []
    
    for i in range(n_enterprises):
        ent_id = f'ENT_{i+1:04d}'
        sector = np.random.choice(sectors)
        size = np.random.choice(sizes, p=[0.4, 0.35, 0.2, 0.05])
        location = np.random.choice(locations, p=[0.7, 0.05, 0.05, 0.05, 0.1, 0.05])
        
        # Caractéristiques de base
        base_employees = {
            'TPE (1-9)': np.random.randint(3, 10),
            'PME (10-49)': np.random.randint(10, 50),
            'ETI (50-249)': np.random.randint(50, 150),
            'GE (250+)': np.random.randint(250, 500)
        }[size]
        
        # Salaire moyen (FDJ)
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
        
        # Générer les déclarations mensuelles
        current_date = datetime(2023, 1, 1)
        
        for month in range(n_months):
            # Variation mensuelle
            month_variation = np.random.uniform(0.9, 1.1)
            employees = max(1, int(base_employees * np.random.uniform(0.95, 1.05)))
            
            # Sous-déclaration (15% des entreprises)
            if np.random.random() < 0.15:
                underdeclaration = np.random.uniform(0.6, 0.9)
            else:
                underdeclaration = 1.0
            
            declared_salary = avg_salary * underdeclaration * month_variation
            declared_mass = employees * declared_salary
            cotisations = declared_mass * 0.29
            
            # Retard (20% ont des retards)
            if np.random.random() < 0.20:
                days_late = np.random.choice([15, 30, 45, 60], p=[0.5, 0.3, 0.15, 0.05])
            else:
                days_late = 0
            
            data.append({
                'entreprise_id': ent_id,
                'date_declaration': current_date.strftime('%Y-%m-%d'),
                'secteur': sector,
                'taille': size,
                'localisation': location,
                'nb_salaries_declares': employees,
                'salaire_moyen_declare': round(declared_salary),
                'masse_salariale_declaree': round(declared_mass),
                'cotisations_dues': round(cotisations),
                'jours_retard': days_late,
                'montant_paye': round(cotisations * np.random.uniform(0.95, 1.0)),
                'annee': current_date.year,
                'mois': current_date.month
            })
            
            current_date += timedelta(days=30)
    
    df = pd.DataFrame(data)
    
    # Sauvegarder
    file_path = 'data/raw/declarations_cnss_synthétiques.csv'
    df.to_csv(file_path, index=False, encoding='utf-8')
    
    print(f"✅ Données générées: {len(df)} lignes, {n_enterprises} entreprises")
    print(f"📁 Fichier sauvegardé: {file_path}")
    
    # Aperçu
    print("\n📊 Aperçu des données:")
    print(df.head())
    print(f"\n💰 Cotisations totales: {df['cotisations_dues'].sum():,.0f} FDJ")
    print(f"⏱️ Retard moyen: {df['jours_retard'].mean():.1f} jours")
    
    return df

if __name__ == "__main__":
    generate_cnss_data()