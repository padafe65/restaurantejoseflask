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

    # Cargamos el archivo SVG de Erwin
    foto_erwin = cargar_imagen_local("avaErwin.svg")
    # Aquí podrías cargar las fotos de tus compañeros si las tienes:
    # foto_comp2 = cargar_imagen_local("foto_comp2.jpg")
    
    tab_doc, tab_est = st.tabs(["👨‍🏫 Docentes", "🎓 Estudiantes"])

    with tab_doc:
        st.markdown('<div class="section-title-custom">Cátedra Ingeniería</div>', unsafe_allow_html=True)
        col1_d, col2_d = st.columns(2)
        with col1_d:
            st.markdown("""
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front">
                        <div class="avatar-rect">JO</div>
                        <h3>Juan Otálora</h3>
                    </div>
                    <div class="flip-card-back">
                        <h3>Docente ACM UD - Python de 0 a 100 UD - 2026</h3>
                        <p class="info-line">Ingeniería de Sistemas</p>
                        <p class="info-line">Universidad Distrital</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with col2_d:
                st.markdown("""
                <div class="flip-card">
                    <div class="flip-card-inner">
                        <div class="flip-card-front">
                            <div class="avatar-rect">JB</div>
                            <h3>Johan Bermeo</h3>
                        </div>
                        <div class="flip-card-back">
                            <h3>Docente ACM UD - Python de 0 a 100 UD - 2026</h3>
                            <p class="info-line">Ingeniería de Sistemas</p>
                            <p class="info-line">Universidad Distrital</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        # Aquí podrías añadir al profesor Jaiber en la col2_d

    with tab_est:
        st.markdown('<div class="section-title-custom">Estudiantes Curso ACM UD - Python de 0 a 100 UD - 2026</div>', unsafe_allow_html=True)
        
        # --- DEFINIMOS LAS 3 COLUMNAS PARA LOS 3 COMPAÑEROS ---
        col1, col2, col3 = st.columns(3)

        # COMPAÑERO 1: Erwin
        with col1:
            st.markdown(f"""
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front">
                        <div class="avatar-rect">DMP</div>
                        <h4 style="margin:0;">Diana Marcela Pulido Diaz</h4>
                    </div>
                    <div class="flip-card-back">
                        <h4 style="margin:0;">Perfil</h4>
                        <p class="info-line">Estudiante ACM UD Python de 0 a 100 UD</p>
                        <p class="info-line">Desarrolladora - 2026</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
        # COMPAÑERO 2
        with col2:
            avatar_erwin = f'<img src="{foto_erwin}" class="avatar-rect">' if foto_erwin else '<div class="avatar-rect">EF</div>'
            st.markdown(f"""
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front">
                        {avatar_erwin}
                        <h4 style="margin:0;">Erwin Ferreira Rojas</h4>
                    </div>
                    <div class="flip-card-back">
                        <h4 style="margin:0;">Perfil</h4>
                        <p style="font-size:0.8rem; line-height:1.1;">Ing. Petróleos UIS / Docente Matemáticas UPN</p>
                        <p class="info-line">ADSO - SENA</p>
                        <p class="info-line">Proyecto Don José</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


        # COMPAÑERO 3
        with col3:
            st.markdown(f"""
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front">
                        <div class="avatar-rect">JPS</div>
                        <h4 style="margin:0;">Juan Pablo Sánchez</h4>
                    </div>
                    <div class="flip-card-back">
                        <h4 style="margin:0;">Perfil</h4>
                        <p class="info-line">Licenciado en Física de la universidad Distrital</p>
                        <p class="info-line">Estudiante ACM UD - Python de 0 a 100 UD</p>
                        <p class="info-line">Desarrollador - 2026</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)