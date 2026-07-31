import streamlit as st
import breeding_engine

# --- Configuration de la page ---
st.set_page_config(
    page_title="Palworld Breeder Pro",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Styles CSS personnalisés ---
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-family: 'Inter', sans-serif;
        color: #2e7d32;
        margin-bottom: -10px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 30px;
    }
    .breeding-step-card {
        background-color: #f8f9fa;
        border-left: 5px solid #2e7d32;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .step-number {
        font-size: 0.9rem;
        color: #ce8800;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .breed-formula {
        font-size: 1.25rem;
        margin-top: 8px;
        color: #333;
        font-weight: 500;
    }
    .highlight {
        color: #2e7d32;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 class='main-title'>🧬 Palworld Breeder Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Trouvez le chemin de reproduction optimal (Patch 1.0)</p>", unsafe_allow_html=True)

# Récupération et tri des Pals pour l'affichage
pal_list = breeding_engine.get_all_pal_names()
pal_dict = {display_name: internal_name for internal_name, display_name in pal_list}
display_names = sorted(list(pal_dict.keys()))

# --- Section Paramètres ---
st.write("### ⚙️ Paramètres de Recherche")
col1, col2 = st.columns(2)

with col1:
    source_name = st.selectbox("🐣 Pal de départ (Source) :", display_names, index=display_names.index("Lamball") if "Lamball" in display_names else 0)

with col2:
    target_name = st.selectbox("🎯 Pal cible (Objectif) :", display_names, index=display_names.index("Anubis") if "Anubis" in display_names else len(display_names)-1)

st.markdown("<hr/>", unsafe_allow_html=True)

# --- Logique de Calcul ---
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
if btn_col2.button("🚀 Calculer le chemin optimal", use_container_width=True):
    source_id = pal_dict[source_name]
    target_id = pal_dict[target_name]
    
    with st.spinner("Analyse de la base de données..."):
        paths = breeding_engine.bfs_shortest_path(source_id, target_id)
        
    if paths is None or len(paths) == 0:
        st.error("⚠️ Aucun chemin de reproduction trouvé entre ces deux Pals.")
    elif len(paths[0]) == 0:
        st.info("✨ Le Pal de départ est déjà identique au Pal cible.")
    else:
        st.write(f"### 🎉 Succès ! {len(paths)} chemin(s) optimal(s) trouvé(s) en {len(paths[0])} étape(s)")
        
        for i, path in enumerate(paths, 1):
            with st.expander(f"🗺️ Voir l'Option #{i}", expanded=(i == 1)):
                for step_num, (parent_a, parent_b, child) in enumerate(path, 1):
                    name_a = breeding_engine.get_pal_name(parent_a)
                    name_b = breeding_engine.get_pal_name(parent_b)
                    name_child = breeding_engine.get_pal_name(child)
                    
                    img_a = breeding_engine.get_pal_image_url(parent_a)
                    img_b = breeding_engine.get_pal_image_url(parent_b)
                    img_child = breeding_engine.get_pal_image_url(child)
                    
                    st.markdown(f"""
                    <div class="breeding-step-card">
                        <div class="step-number">Génération {step_num}</div>
                        <div class="breed-formula" style="display: flex; align-items: center; gap: 8px;">
                            <img src="{img_a}" width="32" height="32" style="border-radius:50%; object-fit: cover;" onerror="this.src='https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/items/common-egg.png'">
                            <span>{name_a}</span>
                            <span style="color: #888; font-size: 0.9em; margin: 0 4px;">+</span>
                            <img src="{img_b}" width="32" height="32" style="border-radius:50%; object-fit: cover;" onerror="this.src='https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/items/common-egg.png'">
                            <span>{name_b}</span>
                            <span style="color: #2e7d32; font-size: 1.2em; font-weight: bold; margin: 0 8px;">➜</span>
                            <img src="{img_child}" width="40" height="40" style="border-radius:50%; object-fit: cover; box-shadow: 0 0 5px rgba(46,125,50,0.5);" onerror="this.src='https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/items/common-egg.png'">
                            <span class="highlight">{name_child}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)