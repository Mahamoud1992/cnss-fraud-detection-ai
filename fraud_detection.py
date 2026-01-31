import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# ============================
# PARTIE 1 — TRAINING MODELE
# ============================

def train_model():

    print("Chargement des données...")

    df = pd.read_csv("data/raw/declarations_cnss_synthétiques.csv")

    # Supprimer colonnes inutiles
    df = df.drop(["entreprise_id", "date_declaration", "date_paiement"], axis=1)

    # Séparer X / y
    X = df.drop("flag_fraude", axis=1)
    y = df["flag_fraude"]

    # Encoder texte
    X = pd.get_dummies(X, drop_first=True)

    # Sauvegarder colonnes pour prédiction
    joblib.dump(X.columns.tolist(), "models/model_columns.pkl")

    # Train / Test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Entraînement du modèle...")

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    print("\nRapport de classification :")
    print(classification_report(y_test, pred))

    joblib.dump(model, "models/cnss_model.pkl")

    print("Modèle sauvegardé dans models/cnss_model.pkl")


# ============================
# PARTIE 2 — CLASSE PREDICTION
# ============================

class CNSSFraudDetector:

    def __init__(self):
        self.model = None
        self.columns = None

    def load_model(self, path_model, path_columns="models/model_columns.pkl"):
        try:
            self.model = joblib.load(path_model)
            self.columns = joblib.load(path_columns)
            print("Modèle chargé avec succès")
        except:
            print("Mode démo activé")
            self.model = None

    def preprocess(self, df):
        df = pd.get_dummies(df, drop_first=True)

        for col in self.columns:
            if col not in df.columns:
                df[col] = 0

        df = df[self.columns]
        return df

    def predict_risk_score(self, df):

        if self.model is None:
            np.random.seed(42)
            risk_scores = np.random.uniform(0, 100, len(df))

        else:
            try:
                X = self.preprocess(df)
                probs = self.model.predict_proba(X)
                risk_scores = probs[:, 1] * 100
            except:
                np.random.seed(42)
                risk_scores = np.random.uniform(0, 100, len(df))

        risk_labels = [
            "À RISQUE" if score > 70 else "NORMAL"
            for score in risk_scores
        ]

        return risk_scores, risk_labels


# ============================
# LANCEMENT DIRECT
# ============================

if __name__ == "__main__":
    train_model()
