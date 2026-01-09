import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Détection de biais chatbot", layout="wide")
st.title("🔍 Détection et reformulation des biais linguistiques du chatbot")

# ---------------------------
# Charger les données
# ---------------------------
df = pd.read_json("messages200.json", encoding="utf-8")

# ---------------------------
# Définition des indicateurs et reformulations
# ---------------------------
indicateurs = {
    "ton_rude": ["vous devez","vous auriez dû","c'est votre faute","pas notre problème","impossible","vous ne comprenez pas","clairement","évidemment","anormal","normal"],
    "generalisation": ["toujours","jamais","souvent","normalement"],
    "manque_politesse": ["vérifiez","contactez votre banque","faites ceci","envoyez une photo","regardez la politique"],
    "non_inclusif": ["monsieur","madame","client masculin","client femme","jeune","âgé","dans votre région","chez vous"],
    "accusation": ["vous avez fait une erreur","vous êtes responsable","vous avez mal","problème vient de vous"]
}

reformulation = {
    "vous devez":"nous vous invitons à","vous auriez dû":"il serait préférable de",
    "c'est votre faute":"pouvons-nous clarifier la situation ?","vous ne comprenez pas":"permettez-moi de mieux expliquer",
    "pas notre problème":"nous allons vous aider à résoudre cela","impossible":"actuellement non disponible, mais nous cherchons des alternatives",
    "clairement":"pour clarifier","évidemment":"comme vous pouvez le constater","anormal":"inhabituel","normal":"habituel",
    "toujours":"généralement","jamais":"rarement","souvent":"dans certains cas","normalement":"habituellement",
    "vérifiez":"pourriez-vous vérifier","contactez votre banque":"nous vous suggérons de contacter votre banque",
    "faites ceci":"pourriez-vous faire ceci","envoyez une photo":"pourriez-vous nous envoyer une photo",
    "regardez la politique":"vous pouvez consulter notre politique",
    "monsieur":"cher·e client·e","madame":"cher·e client·e","client masculin":"client·e",
    "client femme":"client·e","jeune":"client·e","âgé":"client·e",
    "dans votre région":"dans votre zone géographique","chez vous":"à votre domicile",
    "vous avez fait une erreur":"il semble y avoir un malentendu",
    "vous êtes responsable":"explorons ensemble la situation",
    "vous avez mal":"revoyons ensemble","problème vient de vous":"clarifions ensemble ce point"
}

# ---------------------------
# Fonctions
# ---------------------------
def trouver_biais_par_type(texte):
    result = {}
    for type_biais, mots in indicateurs.items():
        trouve = [mot for mot in mots if re.search(rf"\b{re.escape(mot)}\b", texte, re.IGNORECASE)]
        if trouve:
            result[type_biais] = trouve
    return result

def generer_suggestion(biais_dict):
    suggestions = []
    for mots in biais_dict.values():
        for mot_detecte in mots:
            mot_detecte_lower = mot_detecte.lower()
            if mot_detecte_lower in reformulation:
                suggestions.append(f"'{mot_detecte}' → '{reformulation[mot_detecte_lower]}'")
    return suggestions

def reformuler_phrase(texte, biais_dict):
    texte_reforme = texte
    for mots in biais_dict.values():
        for mot_detecte in mots:
            mot_lower = mot_detecte.lower()
            if mot_lower in reformulation:
                pattern = re.compile(re.escape(mot_detecte), re.IGNORECASE)
                texte_reforme = pattern.sub(reformulation[mot_lower], texte_reforme)
    return texte_reforme

# ---------------------------
# Interface utilisateur
# ---------------------------
st.subheader("📥 Entrez un message du chatbot à analyser")
texte_input = st.text_area("Message du chatbot", "Bonjour monsieur, vous devez vérifier vos informations immédiatement.")

if st.button("Analyser"):
    biais_detecte = trouver_biais_par_type(texte_input)
    nb_biais = sum(len(v) for v in biais_detecte.values())
    suggestions = generer_suggestion(biais_detecte)
    texte_reforme = reformuler_phrase(texte_input, biais_detecte)

    st.write(f"**Nombre de biais détectés :** {nb_biais}")
    st.write("**Biais détectés :**", biais_detecte if biais_detecte else "Aucun biais détecté")
    st.write("**Suggestions de reformulation :**", ", ".join(suggestions) if suggestions else "Aucune suggestion")
    st.write("**Phrase reformulée :**", texte_reforme)

st.markdown("---")
st.subheader("📊 Statistiques globales du dataset")
st.write(f"Nombre total de messages analysés : {len(df)}")
st.write(f"Messages avec biais : {len(df[df['chatbot'].apply(trouver_biais_par_type).map(lambda d: sum(len(v) for v in d.values())) > 0])}")
