import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Solution aux chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from src.fraud_detection import CNSSFraudDetector
    MODEL_LOADED = True
except ImportError:
    # Mode de secours
    class CNSSFraudDetector:
        def __init__(self):
            pass
        def load_model(self, path):
            st.sidebar.info("🔧 Mode démo - Modèle simulé")
        def predict_risk_score(self, df):
            np.random.seed(42)
            risk_scores = np.random.uniform(0, 100, len(df))
            risk_labels = ['À RISQUE' if score > 70 else 'NORMAL' for score in risk_scores]
            return risk_scores, risk_labels
    MODEL_LOADED = False

# Configuration
st.set_page_config(page_title="CNSS Dashboard", layout="wide")
st.title("📊 CNSS Djibouti - Plateforme d'Intelligence")
st.markdown("**Prototype de démonstration**")

# Chargement des données avec gestion d'erreur
@st.cache_data
def load_data():
    try:
        # Essayer plusieurs chemins possibles
        possible_paths = [
            os.path.join(parent_dir, 'data', 'raw', 'declarations_cnss_synthétiques.csv'),
            'data/raw/declarations_cnss_synthétiques.csv',
            '../data/raw/declarations_cnss_synthétiques.csv'
        ]
        
        df = None
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_csv(path, encoding='utf-8')
                st.sidebar.success(f"✅ Données chargées: {path}")
                break
        
        if df is None:
            st.sidebar.error("❌ Fichier de données non trouvé")
            st.sidebar.info("Génération de données de démonstration...")
            # Générer des données minimales
            df = generate_minimal_data()
        
    except Exception as e:
        st.sidebar.error(f"Erreur de chargement: {e}")
        df = generate_minimal_data()
    
    # Initialiser le détecteur
    detector = CNSSFraudDetector()
    
    # Charger/trainer le modèle
    model_path = os.path.join(parent_dir, 'models', 'cnss_model.pkl')
    detector.load_model(model_path)
    
    # Calculer les scores
    risk_scores, risk_labels = detector.predict_risk_score(df)
    df['risk_score'] = risk_scores
    df['risk_label'] = risk_labels
    
    return df, detector

def generate_minimal_data():
    """Génère des données minimales pour la démo"""
    np.random.seed(42)
    n = 50
    
    data = {
        'entreprise_id': [f'ENT_{i:03d}' for i in range(1, n+1)],
        'secteur': np.random.choice(['TRANSPORT', 'COMMERCE', 'BATIMENT', 'HOTELLERIE'], n),
        'taille': np.random.choice(['TPE', 'PME', 'ETI'], n, p=[0.6, 0.3, 0.1]),
        'jours_retard': np.random.randint(0, 90, n),
        'cotisations_dues': np.random.randint(50000, 500000, n),
        'masse_salariale_declaree': np.random.randint(200000, 2000000, n),
        'date_declaration': pd.date_range('2023-01-01', periods=n, freq='M').strftime('%Y-%m-%d')
    }
    
    return pd.DataFrame(data)

# Interface principale
df, detector = load_data()

# Sidebar
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    # Filtres
    if 'secteur' in df.columns:
        sectors = ['TOUS'] + list(df['secteur'].unique())
        selected_sectors = st.multiselect(
            "Filtrer par secteur",
            options=sectors,
            default=['TOUS']
        )
        
        if 'TOUS' not in selected_sectors:
            df = df[df['secteur'].isin(selected_sectors)]
    
    if 'taille' in df.columns:
        sizes = ['TOUS'] + list(df['taille'].unique())
        selected_sizes = st.multiselect(
            "Filtrer par taille",
            options=sizes,
            default=['TOUS']
        )
        
        if 'TOUS' not in selected_sizes:
            df = df[df['taille'].isin(selected_sizes)]
    
    seuil_risque = st.slider("Seuil d'alerte", 0, 100, 70)
    
    if st.button("🔄 Actualiser"):
        st.rerun()

# KPI
st.subheader("📈 Indicateurs Clés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_cont = df['cotisations_dues'].sum() if 'cotisations_dues' in df.columns else 0
    st.metric("Cotisations dues", f"{total_cont:,.0f} FDJ")

with col2:
    risky = (df['risk_score'] > seuil_risque).sum() if 'risk_score' in df.columns else 0
    st.metric("À risque", f"{risky} ent.")

with col3:
    avg_delay = df['jours_retard'].mean() if 'jours_retard' in df.columns else 0
    st.metric("Retard moyen", f"{avg_delay:.0f} jours")

with col4:
    st.metric("Entreprises", len(df))

# Visualisations
st.subheader("📊 Analyse des Risques")

if 'risk_score' in df.columns:
    fig1 = px.histogram(df, x='risk_score', nbins=20,
                       title='Distribution des scores de risque',
                       labels={'risk_score': 'Score de risque'})
    st.plotly_chart(fig1, use_container_width=True)

# Table des entreprises à risque
st.subheader("🎯 Entreprises prioritaires")

if 'risk_score' in df.columns:
    high_risk = df[df['risk_score'] > seuil_risque]
    
    if not high_risk.empty:
        cols_to_show = ['entreprise_id', 'secteur', 'taille', 
                       'risk_score', 'jours_retard', 'cotisations_dues']
        cols_to_show = [c for c in cols_to_show if c in high_risk.columns]
        
        st.dataframe(
            high_risk[cols_to_show].sort_values('risk_score', ascending=False),
            use_container_width=True
        )
    else:
        st.success("✅ Aucune entreprise à haut risque détectée")

# Pied de page
st.divider()
st.caption(f"📅 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.caption("Prototype de démonstration - Données synthétiques")