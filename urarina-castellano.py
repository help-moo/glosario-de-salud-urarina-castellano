import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata


######### CONFIG #########
st.set_page_config(initial_sidebar_state="collapsed")

######### TITULO #########
st.title("Glosario de salud urarina-castellano")
    
##################### Cargar CSV #####################
df = pd.read_csv("corpus_entries.csv", encoding="utf-8")

##################### Estado para entrada seleccionada #####################
if "selected_entry" not in st.session_state:
    st.session_state.selected_entry = None

##################### Función para quitar tildes #####################
def remove_accents(input_str):
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(input_str))
        if unicodedata.category(c) != 'Mn'
    )

##################### BUSCADOR y FILTRADO #####################
col1, col2 = st.columns([0.8, 0.2], vertical_alignment="bottom")

with col1:
    text_search = st.text_input("Buscar por palabra", value="").strip()

with col2:
    st.page_link('urarina-castellano.py', label="Urarina", use_container_width=True, disabled=True)
    st.page_link('pages/1-castellano-urarina.py', label="Castellano", use_container_width=True)

# Filtrado por búsqueda
df_filtered = df[df["mainheadword"].str.contains(text_search, case=False, na=False)].head(20) if text_search else None

##################### Función para mostrar entrada #####################

##################### inyectar CSS para modificar .dialog ######################
st.markdown("""
<style>
.st-bp.st-em.st-en.st-eo.st-c1.st-ep.st-ef.st-eq.st-er {
    padding: 1.5rem 1.5rem 0rem !important;
}

.st-emotion-cache-2vdko {
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

######################### St.dialog para mostrar entrada #########################

@st.cache_data
def render_entry(entry):
    if pd.notna(entry["audio"]):
        audio_path = Path(entry["audio"])
        if audio_path.exists():
            st.audio(str(audio_path), format="audio/wav", autoplay=False)
        else:
            st.warning(f"Archivo de audio no encontrado: {audio_path}")

    st.markdown(f"""
    <div style="font-size:16px; font-weight:bold;">Definición:</div>
    <div style="font-size:18px; margin-top:0; margin-bottom:8px;">{entry["definitionorgloss"]}</div>

    <div style="font-size:16px; font-weight:bold; margin-bottom:4px;">Clase de palabra:</div>
    <div style="font-size:18px; margin-top:0; margin-bottom:8px;">{entry["partofspeech"]}</div>

    <div style="font-size:16px; font-weight:bold; margin-bottom:4px;">Dominio semántico:</div>
    <div style="font-size:18px; margin-top:0; margin-bottom:18px;">{entry["semanticdomain"]}</div>
    """, unsafe_allow_html=True)


##################### Definir el diálogo #####################
def show_dialog(entry):
    @st.dialog(entry["mainheadword"])  # Usar la palabra como título
    def _():
        render_entry(entry)
    _()

##################### Mostrar resultados #####################
with st.container(border=True):
    if df_filtered is not None and not df_filtered.empty:
        st.write(f"Mostrando {len(df_filtered)} resultados:")
        for _, entry in df_filtered.iterrows():
            label = f'**{entry["mainheadword"]}**'
            if pd.notna(entry["audio"]) and entry["audio"].strip() != "":
                label += " 🔊"
            label += f' - {entry["definitionorgloss"]}'
            if st.button(label, key=entry["mainheadword"], use_container_width=True):
                st.session_state.selected_entry = entry
                show_dialog(entry)
    elif text_search:
        st.info("No se encontraron resultados para la búsqueda.")
    else:
        # Agrupar letras sin acentos
        first_letters = (
            df["mainheadword"]
            .dropna()
            .apply(lambda w: remove_accents(w.strip())[0].upper() if w.strip() else "")
        )
        letters_with_results = sorted(set(first_letters))

        if letters_with_results:
            for tab, letter in zip(st.tabs(letters_with_results), letters_with_results):
                with tab:
                    df_letter = df[
                        df["mainheadword"].apply(
                            lambda w: remove_accents(w.strip()).upper().startswith(letter)
                        )
                    ]
                    for _, entry in df_letter.iterrows():
                        label = f'**{entry["mainheadword"]}**'
                        if pd.notna(entry["audio"]) and entry["audio"].strip() != "":
                            label += " 🔊"
                        label += f' - {entry["definitionorgloss"]}'
                        if st.button(label, key=f"{letter}-{entry['mainheadword']}", use_container_width=True):
                            st.session_state.selected_entry = entry
                            show_dialog(entry)
        else:
            st.info("No hay palabras que empiecen con ninguna letra.")
            
st.markdown("""
<div style="text-align:center; margin-top:10px; font-size:14px; color:#444;">
  <p style="font-size:12px; color:#888;">© 2025 GELCOP</p>  
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/" target="_blank" style="display:inline-block;">
    <img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-nd.png" alt="Licencia CC BY-NC-ND 4.0" height="30" />
  </a>
</div>
""", unsafe_allow_html=True)
