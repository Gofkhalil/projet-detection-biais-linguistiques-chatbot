import pandas as pd
import re

# 1️⃣ Lecture du corpus JSON
df = pd.read_json("messages200.json", encoding="utf-8")

# 2️⃣ Définition des mots/phrases sensibles par type de biais
indicateurs = {
    "ton_rude": [
        "vous devez", "vous auriez dû", "c'est votre faute", 
        "pas notre problème", "impossible", "vous ne comprenez pas",
        "clairement", "évidemment", "anormal", "normal"
    ],
    "generalisation": [
        "toujours", "jamais", "souvent", "normalement"
    ],
    "manque_politesse": [
        "vérifiez", "contactez votre banque", "faites ceci",
        "envoyez une photo", "regardez la politique"
    ],
    "non_inclusif": [
        "monsieur", "madame", "client masculin", "client femme",
        "jeune", "âgé", "dans votre région", "chez vous"
    ],
    "accusation": [
        "vous avez fait une erreur", "vous êtes responsable",
        "vous avez mal", "problème vient de vous"
    ]
}

# 3️⃣ Dictionnaire de reformulation ÉTENDU
reformulation = {
    # Ton rude
    "vous devez": "nous vous invitons à",
    "vous auriez dû": "il serait préférable de",
    "c'est votre faute": "pouvons-nous clarifier la situation ?",
    "vous ne comprenez pas": "permettez-moi de mieux expliquer",
    "pas notre problème": "nous allons vous aider à résoudre cela",
    "impossible": "actuellement non disponible, mais nous cherchons des alternatives",
    "clairement": "pour clarifier",
    "évidemment": "comme vous pouvez le constater",
    "anormal": "inhabituel",
    "normal": "habituel",
    
    # Généralisation
    "toujours": "généralement",
    "jamais": "rarement",
    "souvent": "dans certains cas",
    "normalement": "habituellement",
    
    # Manque de politesse
    "vérifiez": "pourriez-vous vérifier",
    "contactez votre banque": "nous vous suggérons de contacter votre banque",
    "faites ceci": "pourriez-vous faire ceci",
    "envoyez une photo": "pourriez-vous nous envoyer une photo",
    "regardez la politique": "vous pouvez consulter notre politique",
    
    # Non inclusif
    "monsieur": "cher·e client·e",
    "madame": "cher·e client·e",
    "client masculin": "client·e",
    "client femme": "client·e",
    "jeune": "client·e",
    "âgé": "client·e",
    "dans votre région": "dans votre zone géographique",
    "chez vous": "à votre domicile",
    
    # Accusation
    "vous avez fait une erreur": "il semble y avoir un malentendu",
    "vous êtes responsable": "explorons ensemble la situation",
    "vous avez mal": "revoyons ensemble",
    "problème vient de vous": "clarifions ensemble ce point"
}

# 4️⃣ Fonction pour détecter les biais et leur type
def trouver_biais_par_type(texte):
    result = {}
    for type_biais, mots in indicateurs.items():
        trouve = [mot for mot in mots if re.search(rf"\b{re.escape(mot)}\b", texte, re.IGNORECASE)]
        if trouve:
            result[type_biais] = trouve
    return result

# 5️⃣ Appliquer sur les réponses du chatbot
df['biais_detecte'] = df['chatbot'].apply(trouver_biais_par_type)

# 6️⃣ Créer une colonne "nb_biais" pour compter le nombre total de mots détectés
df['nb_biais'] = df['biais_detecte'].apply(lambda d: sum(len(v) for v in d.values()))

# 7️⃣ Générer les suggestions de reformulation (VERSION CORRIGÉE)
def generer_suggestion(biais_dict):
    suggestions = []
    for mots in biais_dict.values():
        for mot_detecte in mots:
            mot_detecte_lower = mot_detecte.lower()
            # Chercher directement dans le dictionnaire de reformulation
            if mot_detecte_lower in reformulation:
                suggestions.append(f"'{mot_detecte}' → '{reformulation[mot_detecte_lower]}'")
    return suggestions

df['suggestion'] = df['biais_detecte'].apply(generer_suggestion)

# 8️⃣ Fonction pour reformuler automatiquement une phrase
def reformuler_phrase(texte, biais_dict):
    texte_reforme = texte
    for mots in biais_dict.values():
        for mot_detecte in mots:
            mot_lower = mot_detecte.lower()
            if mot_lower in reformulation:
                # Remplacer en préservant la casse
                pattern = re.compile(re.escape(mot_detecte), re.IGNORECASE)
                texte_reforme = pattern.sub(reformulation[mot_lower], texte_reforme)
    return texte_reforme

df['chatbot_reforme'] = df.apply(
    lambda row: reformuler_phrase(row['chatbot'], row['biais_detecte']), 
    axis=1
)

# 9️⃣ Top 10 des réponses avec le plus de biais
df_top10 = df.sort_values('nb_biais', ascending=False).head(10)

# 🔟 Affichage détaillé
print("=" * 100)
print("TOP 10 DES RÉPONSES AVEC LE PLUS DE BIAIS")
print("=" * 100)
for idx, row in df_top10.iterrows():
    print(f"\n📌 Message client: {row['client']}")
    print(f"❌ Réponse originale: {row['chatbot']}")
    print(f"🚨 Biais détectés ({row['nb_biais']}): {row['biais_detecte']}")
    print(f"💡 Suggestions: {', '.join(row['suggestion'])}")
    print(f"✅ Réponse reformulée: {row['chatbot_reforme']}")
    print("-" * 100)

# 1️⃣1️⃣ Statistiques globales
print("\n" + "=" * 100)
print("STATISTIQUES GLOBALES")
print("=" * 100)
print(f"Nombre total de messages analysés: {len(df)}")
print(f"Messages avec biais: {len(df[df['nb_biais'] > 0])}")
print(f"Pourcentage de messages biaisés: {len(df[df['nb_biais'] > 0]) / len(df) * 100:.2f}%")

# Statistiques par type de biais
print("\n📊 Répartition des biais par type:")
all_bias_types = {}
for biais_dict in df['biais_detecte']:
    for type_biais, mots in biais_dict.items():
        if type_biais not in all_bias_types:
            all_bias_types[type_biais] = 0
        all_bias_types[type_biais] += len(mots)

for type_biais, count in sorted(all_bias_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {type_biais}: {count} occurrences")

# 1️⃣2️⃣ Export CSV final
df.to_csv("result_complet2.csv", index=False, encoding='utf-8-sig')
print("\n✅ Fichier 'result_complet.csv' généré avec succès!")

# 1️⃣3️⃣ Export du top 10 pour présentation
df_top10[['client', 'chatbot', 'biais_detecte', 'nb_biais', 'suggestion', 'chatbot_reforme']].to_csv(
    "top10_biais.csv", 
    index=False, 
    encoding='utf-8-sig'
)
print("✅ Fichier 'top10_biais.csv' généré avec succès!")