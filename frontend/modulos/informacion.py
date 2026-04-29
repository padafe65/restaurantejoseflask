import streamlit as st
import os
import base64
from modulos.estilos_ud import CSS_INSTITUCIONAL

def cargar_imagen_local(nombre_archivo):
    """Convierte imagen local (incluyendo SVG) a base64."""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_img = os.path.join(BASE_DIR, "imagenes", nombre_archivo)
    
    if os.path.exists(ruta_img):
        extension = nombre_archivo.split('.')[-1].lower()
        mime_type = f"image/{extension}"
        if extension == "svg":
            mime_type = "image/svg+xml"
            
        with open(ruta_img, "rb") as f:
            data = f.read()
        return f"data:{mime_type};base64,{base64.b64encode(data).decode()}"
    return None

def render_info_institucional():
    st.markdown(CSS_INSTITUCIONAL, unsafe_allow_html=True)

    # Cargamos el archivo SVG exacto que tienes en tu carpeta
    foto_erwin = cargar_imagen_local("avaErwin.svg")
    
    tab_doc, tab_est = st.tabs(["👨‍🏫 Docentes", "🎓 Estudiantes"])

    with tab_doc:
        st.markdown('<div class="section-title-custom">Cátedra Ingeniería</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front">
                        <div class="avatar-rect">JL</div>
                        <h3>Juan Diego Lozada</h3>
                    </div>
                    <div class="flip-card-back">
                        <h3>Docente</h3>
                        <p class="info-line">Ingeniería de Sistemas</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_est:
        st.markdown('<div class="section-title-custom">Desarrollador</div>', unsafe_allow_html=True)
        
        # Elegimos si mostrar el rectángulo con imagen o con iniciales
        if foto_erwin:
            avatar_html = f'<img src="{foto_erwin}" class="avatar-rect">'
        else:
            avatar_html = '<div class="avatar-rect">EF</div>'

        st.markdown(f"""
        <div class="flip-card" style="max-width: 350px; margin: auto;">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    {avatar_html}
                    <h3>Erwin Ferreira Rojas</h3>
                </div>
                <div class="flip-card-back">
                    <h3>Perfil</h3>
                    <p class="info-line">ADSO - SENA</p>
                    <p class="info-line">Proyecto Restaurante</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)