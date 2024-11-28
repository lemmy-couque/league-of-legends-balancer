import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd
import os


def plot_champion_win_rates(df):
    """
    Génère un graphique séparé pour chaque rôle dans les données fournies, 
    montrant les taux de victoire des champions avec un barplot en filigrane pour les parties jouées.

    Args:
        df (pd.DataFrame): DataFrame contenant les colonnes suivantes :
            - 'role': rôle du champion (str)
            - 'champion_name': nom du champion (str)
            - 'win_rate': taux de victoire du champion (float)
            - 'total_matches': nombre total de parties jouées avec le champion (int)
    """
    # Obtenir les dates pour la période d'observation
    d_day = datetime.now().strftime("%d_%m_%Y")
    current_date = datetime.now().strftime("%d/%m/%Y")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")

    # Obtenir les rôles uniques
    roles = df['role'].unique()

    # Palette de couleurs pour différencier les rôles
    palette = sns.color_palette("Set2", len(roles))

    # Générer un graphique séparé pour chaque rôle
    for role, color in zip(roles, palette):
        # Filtrer les données pour le rôle en cours et les champions joués plus de 20 fois
        role_data = df[(df['role'] == role) & (df['total_matches'] > 20)].sort_values(by='win_rate', ascending=False)

        # Si aucun champion ne correspond, passer au rôle suivant
        if role_data.empty:
            continue

        # Identifier le top 5
        top_5 = role_data.iloc[:5]
        others = role_data.iloc[5:]

        # Créer une nouvelle figure pour chaque rôle
        plt.figure(figsize=(12, 14))

        # Tracer les barres pour le top 5 (couleur spéciale)
        bars_top_5 = plt.barh(
            top_5['champion_name'], 
            top_5['win_rate'], 
            color='gold', 
            edgecolor='black',
            label="Top 5 Champions"
        )

        # Tracer les barres pour les autres champions
        bars_others = plt.barh(
            others['champion_name'], 
            others['win_rate'], 
            color=color, 
            alpha=0.6, 
            edgecolor='black',
            label="Other Champions"
        )

        # Ajouter des barres en filigrane représentant le nombre de parties jouées
        max_matches = df['total_matches'].max()
        scale_factor = max_matches / 100  # Ajuster l'échelle si nécessaire
        for bar, matches in zip(list(bars_top_5) + list(bars_others), 
                                pd.concat([top_5['total_matches'], others['total_matches']])):
            match_bar_width = matches / scale_factor
            plt.barh(
                bar.get_y() + 0.4, 
                match_bar_width, 
                height=bar.get_height(), 
                color='grey', 
                alpha=0.3, 
                edgecolor='black',
                label="Number of games played" if bar == bars_top_5[0] else ""
            )

            # Afficher le nombre de parties jouées sur les barres en filigrane
            plt.text(
                0.5, 
                bar.get_y() + bar.get_height() / 2, 
                f"{matches}", 
                va='center', 
                ha='left', 
                color="grey", 
                fontsize=10, 
                fontweight="bold"
            )

        # Ajouter les annotations pour les win rates
        for bar, win_rate in zip(list(bars_top_5) + list(bars_others), 
                                 pd.concat([top_5['win_rate'], others['win_rate']])):
            plt.text(
                bar.get_width() + 1, 
                bar.get_y() + bar.get_height() / 2, 
                f"{win_rate:.1f}%", 
                va='center', 
                ha='left', 
                fontsize=10
            )

        # Ajouter les titres et labels
        plt.title(f"Win Rates of Champions in Role: {role}", fontsize=16, pad=20)
        plt.xlabel("Win Rate (%)", fontsize=14)
        plt.ylabel("Champions", fontsize=14)
        plt.gca().invert_yaxis()
        plt.xlim(0, max(df['win_rate'].max() + 5, 100))

        # Ajouter une grille
        plt.grid(axis='x', linestyle='--', alpha=0.6)

        # Ajouter une légende
        plt.legend(loc="lower right", fontsize=10)

        # Ajouter une période d'observation
        plt.figtext(
            0.5, -0.02, 
            f"Data observed from {start_date} to {current_date}", 
            wrap=True, 
            horizontalalignment='center', 
            fontsize=12, 
            fontstyle='italic'
        )

        # Ajuster les espacements et afficher le graphique
        plt.tight_layout()
    
        # Générer un nom de fichier basé sur le rôle et la date
        filename = f"{role}_win_rates_{d_day}.png"
        filepath = os.path.join("reports", filename)
        
        # Sauvegarder le graphique
        plt.savefig(filepath, dpi=300)
