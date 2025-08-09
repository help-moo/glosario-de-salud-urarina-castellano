import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata

######### CONFIG #########
st.set_page_config(initial_sidebar_state="collapsed")

def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(text))
        if unicodedata.category(c) != 'Mn'
    )

@st.cache_data
def get_first_letter(word):
    word = word.lstrip("¿").strip()
    word = remove_accents(word)
    return word[0].upper() if word else ""

######### TÍTULO #########
st.title("Glosario de salud castellano-urarina")

##################### Cargar CSV #####################
df = pd.read_csv("corpus_entries.csv", encoding="utf-8")

##################### Función para renderizar contenido de la entrada #####################

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

def render_entry(entry):
    # Audio si existe
    if pd.notna(entry["audio"]):
        audio_path = Path(entry["audio"])
        if audio_path.exists():
            st.audio(str(audio_path), format="audio/wav", autoplay=False)
        else:
            st.warning(f"Archivo de audio no encontrado: {audio_path}")

    # Información
    st.markdown(f"""
    <div style="font-size:16px; font-weight:bold;">Definición:</div>
    <div style="font-size:18px; margin-top:5; margin-bottom:8px;">{entry["mainheadword"]}</div>

    <div style="font-size:16px; font-weight:bold; margin-bottom:4px;">Clase de palabra:</div>
    <div style="font-size:18px; margin-top:5; margin-bottom:8px;">{entry["partofspeech"]}</div>

    <div style="font-size:16px; font-weight:bold; margin-bottom:4px;">Dominio semántico:</div>
    <div style="font-size:18px; margin-top:5; margin-bottom:18px;">{entry["semanticdomain"]}</div>
    """, unsafe_allow_html=True)

##################### Definir el diálogo dinámico #####################
def show_dialog(entry):
    @st.dialog(entry["definitionorgloss"])  # Título del modal = definición
    def _():
        render_entry(entry)
    _()

##################### BUSCADOR #####################
col1, col2 = st.columns([0.8, 0.2], vertical_alignment="bottom")

with col1:
    text_search = st.text_input("Buscar por palabra", value="").strip()

with col2:
    st.page_link('urarina-castellano.py', label="Urarina", use_container_width=True)
    st.page_link('pages/1-castellano-urarina.py', label="Castellano", disabled=True, use_container_width=True)

# Filtrado por búsqueda
df_filtered = df[df["definitionorgloss"].str.contains(text_search, case=False, na=False)].head(20) if text_search else None

##################### Mostrar resultados #####################
with st.container(border=True):
    if df_filtered is not None and not df_filtered.empty:
        st.write(f"Mostrando {len(df_filtered)} resultados:")
        for idx, entry in df_filtered.iterrows():
            label = f'**{entry["definitionorgloss"]}** - {entry["mainheadword"]}'
            if pd.notna(entry["audio"]) and entry["audio"].strip() != "":
                label += " 🔊"
            if st.button(label, key=f"btn_search_{idx}", use_container_width=True):
                show_dialog(entry)

    elif text_search:
        st.info("No se encontraron resultados para la búsqueda.")

    else:
        # Obtener letras que tienen palabras, normalizadas y sin tilde
        letters_with_results = sorted(set(df["definitionorgloss"].dropna().apply(get_first_letter)))

        if letters_with_results:
            for tab, letter in zip(st.tabs(letters_with_results), letters_with_results):
                with tab:
                    df_letter = df[
                        df["definitionorgloss"].apply(lambda w: get_first_letter(w) == letter)
                    ]
                    for idx, entry in df_letter.iterrows():
                        label = f'**{entry["definitionorgloss"]}** - {entry["mainheadword"]}'
                        if pd.notna(entry["audio"]) and entry["audio"].strip() != "":
                            label += " 🔊"
                        if st.button(label, key=f"btn_{letter}_{idx}", use_container_width=True):
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