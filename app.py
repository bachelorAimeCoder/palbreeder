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
    .tree-step {
        display: flex;
        align-items: center;
        justify-content: space-around;
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .tree-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #ffffff;
        border: 2px solid #2e7d32;
        border-radius: 8px;
        padding: 8px;
        width: 100px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .tree-node img {
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 5px;
    }
    .tree-node span {
        font-weight: 600;
        font-size: 0.85rem;
        color: #333;
        text-align: center;
    }
    .tree-target {
        border-color: #ce8800;
        box-shadow: 0 0 10px rgba(206, 136, 0, 0.4);
        background-color: #fffbf0;
    }
    .tree-target span {
        color: #ce8800;
    }
    .tree-plus {
        font-size: 1.2rem;
        font-weight: bold;
        color: #999;
    }
    .tree-arrow {
        font-size: 1.5rem;
        color: #2e7d32;
    }
    .gen-badge {
        background: #2e7d32;
        color: white;
        padding: 4px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 1px;
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
            with st.expander(f"🗺️ Voir l'Option #{i}", expanded=True):
                for step_num, (parent_a, parent_b, child) in enumerate(path, 1):
                    name_a = breeding_engine.get_pal_name(parent_a)
                    name_b = breeding_engine.get_pal_name(parent_b)
                    name_child = breeding_engine.get_pal_name(child)
                    
                    img_a = breeding_engine.get_pal_image_url(parent_a)
                    img_b = breeding_engine.get_pal_image_url(parent_b)
                    img_child = breeding_engine.get_pal_image_url(child)
                    
                    is_target = (step_num == len(path))
                    target_class = " tree-target" if is_target else ""
                    
                    st.markdown(f"""
<div class="tree-step">
    <div class="gen-badge">GEN {step_num}</div>
    
    <div class="tree-node">
        <img src="{img_a}" width="48" height="48" onerror="this.src='https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/items/common-egg.png'">
        <span>{name_a}</span>
    </div>
    
    <div class="tree-plus">➕</div>
    
    <div class="tree-node">
        <img src="{img_b}" width="48" height="48" onerror="this.src='https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/items/common-egg.png'">
        <span>{name_b}</span>
    </div>
    
    <div class="tree-arrow">➡️</div>
    
    <div class="tree-node{target_class}">
        <img src="{img_child}" width="48" height="48" onerror="this.src='https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/items/common-egg.png'">
        <span>{name_child}</span>
    </div>
</div>
""", unsafe_allow_html=True)