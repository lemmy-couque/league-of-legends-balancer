import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd
import os


def plot_champion_win_rates(df: pd.DataFrame) -> None:
    """
    Generates separate bar plots for each role, showing champion win rates.
    Includes overlay bars indicating the number of matches played.

    Args:
        df (pd.DataFrame): DataFrame containing the following columns:
            - 'role' (str): Champion role (e.g., Top, Jungle, Mid).
            - 'champion_name' (str): Name of the champion.
            - 'win_rate' (float): Champion win rate (percentage).
            - 'total_matches' (int): Total matches played with the champion.
    """
    # Observation period
    current_date = datetime.now().strftime("%d/%m/%Y")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
    output_date = datetime.now().strftime("%d_%m_%Y")

    # Extract unique roles
    roles = df['role'].unique()

    # Define a color palette for roles
    palette = sns.color_palette("Set2", len(roles))

    # Generate a plot for each role
    for role, color in zip(roles, palette):
        # Filter data for the current role and exclude champions with fewer than 20 matches
        role_data = df[(df['role'] == role) & (df['total_matches'] > 20)].sort_values(by='win_rate', ascending=False)

        if role_data.empty:
            continue  # Skip if no champions meet the criteria

        top_5 = role_data.iloc[:5]
        others = role_data.iloc[5:]

        plt.figure(figsize=(12, 14))

        # Plot top 5 champions with a distinct color
        bars_top_5 = plt.barh(
            top_5['champion_name'], 
            top_5['win_rate'], 
            color='gold', 
            edgecolor='black',
            label="Top 5 Champions"
        )

        # Plot other champions with a role-specific color
        bars_others = plt.barh(
            others['champion_name'], 
            others['win_rate'], 
            color=color, 
            alpha=0.6, 
            edgecolor='black',
            label="Other Champions"
        )

        # Overlay bars for total matches played
        max_matches = df['total_matches'].max()
        scale_factor = max_matches / 100  # Scale factor for overlay bar widths

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

            # Annotate total matches
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

        # Annotate win rates
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

        # Plot titles and labels
        plt.title(f"Win Rates of Champions as {role} from {start_date} to {current_date}", fontsize=16, pad=20)
        plt.xlabel("Win Rate (%)", fontsize=14)
        plt.ylabel("Champions", fontsize=14)
        plt.gca().invert_yaxis()
        plt.xlim(0, max(df['win_rate'].max() + 5, 100))

        # Add grid and legend
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.legend(loc="lower right", fontsize=10)

        # Adjust layout
        plt.tight_layout()

        # Save plot
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{role}_win_rates_{output_date}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()

