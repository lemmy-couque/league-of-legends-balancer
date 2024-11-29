# League of Legends Balancer

## Overview
**League of Legends Balancer** is a data engineering project designed to analyze champion performance, pick and ban rates, and win rates using game data from Riot Games API. The goal is to provide actionable insights into champion balance while building predictive models for future buffs and nerfs.

This project focuses on Challenger-tier data to ensure high-quality insights into the meta and performance trends of top-tier gameplay.

---

## Features
- **Data Collection**: Automated retrieval of player, match, and champion data from Riot Games API.
- **Data Transformation**: Enrichment of raw data with champion names, roles, and detailed match statistics.
- **Win Rate Analysis**: Calculation and visualization of champion win rates by role.
- **Data Visualization**: Graphical representation of win rates to identify performance trends.
- **Extensibility**: Framework for adding predictive modeling and advanced analytics.

---

## Tech Stack
- **Language**: Python 3.11
- **APIs**: Riot Games API and Data Dragon
- **Libraries**:
  - **Data Handling**: Pandas
  - **Visualization**: Matplotlib, Seaborn
  - **Environment Management**: Python-dotenv
- **Future Tools**: Flask (web dashboard), Scikit-learn (predictive modeling)

---

## Table of Contents
1. [Setup](#setup)
2. [Project Structure](#project-structure)
3. [Usage](#usage)
4. [Pipeline Details](#pipeline-details)
5. [Visualization](#visualization)
6. [Future Work](#future-work)
7. [License](#license)

---

## Setup

### Prerequisites
- Python 3.11 or later
- Riot Games API Key
- Git installed on your machine

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/league-of-legends-balancer.git
   cd league-of-legends-balancer
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
3. Set up your .env file with your Riot Games API key:
   ```bash
   RIOT_API_KEY=your-api-key-here

---

## Project Structure
   ```bash
   league-of-legends-balancer/
   │
   ├── datasets/                     # Generated CSV files
   ├── reports/                      # Generated visualizations and reports
   ├── transform/                    # Data transformation scripts
   │   ├── __init__.py
   │   ├── fetch_champion_mapping.py
   │   ├── enrich_match_data.py
   │   ├── calculate_win_rates.py
   │   ├── save_matches_to_dataframe.py
   ├── analysis/                     # Data analysis and visualization scripts
   │   ├── __init__.py
   │   ├── plot_champion_win_rates.py
   ├── main.py                       # Main entry point for the project
   ├── requirements.txt              # Dependencies list
   ├── .env                          # Environment variables
   └── README.md                     # Project documentation

---

## Usage

### 1. Fetch Data
Run the main pipeline to collect match data, enrich it, and save CSV files:


