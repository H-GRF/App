import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# --- Configuration et Imports de votre Projet ---
# Si 'config.py' est dans le répertoire parent, ajoutez le chemin:
# Le script Streamlit doit être exécuté depuis la racine de Frost_App
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

try:
    import config as c
    # sys.path.append('./frost') n'est pas nécessaire si l'import ci-dessus est correct 
    # et que vous importez ensuite directement 'frost.func'.
    import frost.func as f 
except ImportError as e:
    st.error(f"Erreur d'importation: {e}")
    st.warning("Assurez-vous que 'config.py' et 'frost/func.py' existent et sont correctement structurés.")
    st.stop()
    
# --- Mise en cache de la fonction de chargement ---
# Streamlit met en cache le DataFrame pour éviter de re-télécharger les données 
# à chaque interaction de l'utilisateur.
@st.cache_data
def load_data(dept_code):
    """Charge les données météo en utilisant la fonction process_weather_data de func.py."""
    try:
        # CORRECTION: Utiliser la fonction process_weather_data, qui est la fonction réelle dans frost.func
        df = f.process_weather_data(dept=dept_code)
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame() # Retourne un DataFrame vide en cas d'erreur


# --- Logique des Visualisations (Adaptée à Streamlit) ---
def plot_visualizations(df: pd.DataFrame, dept_code: str):
    """
    Crée et affiche les trois visualisations en utilisant st.pyplot().
    """
    
    # 1. Préparation des données: Renommer et convertir les colonnes pour la visualisation
    # NOTE: Les noms de colonnes dans le DataFrame 'df' chargé depuis process_weather_data 
    # sont en minuscules (tmin, latitude, longitude, alti).
    # Nous devons les renommer/convertir ici pour correspondre aux noms utilisés dans les graphiques.
    df = df.rename(columns={
        'tmin': 'TN_float',
        'latitude': 'LAT_float',
        'longitude': 'LON_float',
        'alti': 'ALTI_float',
        'station_id': 'NUM_POSTE',
        'station_name': 'NOM_USUEL',
        'date': 'AAAAMMJJ' # Ajouter cette ligne si la colonne 'date' est utilisée dans la logique
    })

    # Assurer la présence des colonnes nécessaires
    if 'AAAAMMJJ' in df.columns and pd.api.types.is_datetime64_any_dtype(df['AAAAMMJJ']):
        df['Year'] = df['AAAAMMJJ'].dt.year
    else:
        st.error("Colonne 'AAAAMMJJ' (date) manquante ou format incorrect.")
        return


    # --- Visualisation 1: Évolution Temporelle de la Température Minimale (TN) ---
    st.header("1. Évolution Temporelle de la Température Minimale (TN) 📈")
    
    try:
        # Utiliser 'NUM_POSTE' (anciennement 'station_id')
        top_station_id = df['NUM_POSTE'].mode()[0] 
        df_station = df[df['NUM_POSTE'] == top_station_id].copy()
        df_annual = df_station.groupby('Year')['TN_float'].mean().reset_index()

        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df_annual['Year'], df_annual['TN_float'], marker='o', linestyle='-', color='skyblue')
        ax1.set_title(f'Température Minimale Moyenne Annuelle pour la station {top_station_id}')
        ax1.set_xlabel('Année')
        ax1.set_ylabel('Température Minimale Moyenne (°C)')
        ax1.grid(True, axis='y')
        st.pyplot(fig1)
        st.markdown(f"Cette courbe montre la tendance annuelle de la température minimale pour la station la plus fréquente ({top_station_id}).")
        plt.close(fig1) # Ferme la figure pour libérer la mémoire
    except IndexError:
        st.warning("Pas assez de données pour l'évolution temporelle.")
    except KeyError as e:
        st.error(f"Erreur de colonne pour la Visualisation 1: {e}. Vérifiez le renommage des colonnes.")


    # --- Visualisation 2: Distribution Spatiale des Stations Météo ---
    st.header("2. Distribution Spatiale des Stations Météo 🗺️")
    
    # Utiliser les colonnes renommées
    stations_map = df[['NUM_POSTE', 'NOM_USUEL', 'LAT_float', 'LON_float', 'ALTI_float']].drop_duplicates().dropna(subset=['LAT_float', 'LON_float'])

    if not stations_map.empty:
        # Utilisation de st.map pour une visualisation cartographique simple et interactive
        st.subheader("Carte Interactive des Stations")
        st.map(stations_map[['LAT_float', 'LON_float']].rename(columns={'LAT_float': 'lat', 'LON_float': 'lon'}))
        
        # Affichage du scatter plot Matplotlib avec l'altitude
        st.subheader("Scatter Plot (Couleur par Altitude)")
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        scatter = ax2.scatter(
            stations_map['LON_float'], 
            stations_map['LAT_float'], 
            alpha=0.7, 
            c=stations_map['ALTI_float'], 
            cmap='plasma', 
            s=50 
        )
        cbar = fig2.colorbar(scatter, label='Altitude (m)')
        ax2.set_title('Localisation des Stations Météo du Département')
        ax2.set_xlabel('Longitude')
        ax2.set_ylabel('Latitude')
        ax2.grid(True)
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.warning("Impossible d'afficher la carte : données de Latitude/Longitude manquantes.")


    # --- Visualisation 3: Distribution des Températures (Box Plot par Année) ---
    st.header("3. Distribution des Températures (Box Plot par Année) 🧊")
    
    try:
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        # Utiliser 'TN_float' et 'Year' qui existent après le renommage/calcul
        df.boxplot(column='TN_float', by='Year', ax=ax3, grid=False)
        ax3.set_title('Distribution de la Température Minimale (TN) par Année')
        # Supprime le titre automatique Boxplot of TN_float by Year
        fig3.suptitle('') 
        ax3.set_xlabel('Année')
        ax3.set_ylabel('Température Minimale (°C)')
        st.pyplot(fig3)
        st.markdown("Chaque boîte représente la répartition des températures minimales pour une année donnée.")
        plt.close(fig3)
    except KeyError as e:
        st.error(f"Erreur de colonne pour la Visualisation 3: {e}. Vérifiez le renommage des colonnes.")


# --- Application Streamlit Principale ---
def main():
    st.set_page_config(layout="wide")
    st.title("❄️ Analyse des Données Météo - Département 04")
    
    # Sidebar pour les sélections
    st.sidebar.header("Paramètres")
    dept_code = st.sidebar.text_input("Code du Département (ex: 04)", value="04")
    
    # Chargement des données avec mise en cache
    data_load_state = st.info("Chargement des données en cours...")
    df = load_data(dept_code)
    data_load_state.success("Données chargées!")
    
    if not df.empty:
        st.success(f"Données chargées : {len(df)} lignes et {len(df.columns)} colonnes.")
        # Affichage du DataFrame avec les noms de colonnes d'origine de process_weather_data
        st.dataframe(df.head())
        st.markdown("---")
        
        # Affichage des visualisations
        plot_visualizations(df, dept_code)
    else:
        st.error("Le DataFrame est vide. Veuillez vérifier les logs d'erreur ci-dessus.")

if __name__ == "__main__":
    main()