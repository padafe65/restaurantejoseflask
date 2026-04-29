import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from PIL import Image

def render_carrusel():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(BASE_DIR, "imagenes")
    fotos = ["resjose1.jpg", "resjose2.jpg", "resjose3.jpg", "resjose4.jpg", "resjose5.jpg", "resjose6.jpg"]
    
    # Refresco automático cada 5 segundos
    count = st_autorefresh(interval=3000, key="carrusel_counter")
    indice = count % len(fotos)
    
    if os.path.exists(img_dir):
        ruta_foto = os.path.join(img_dir, fotos[indice])
        
        if os.path.exists(ruta_foto):
            try:
                img_original = Image.open(ruta_foto)
                
                # --- PROPORCIÓN DE BANNER (Ancho y corto para que no tape el login) ---
                # Usaremos 600 de ancho por 200 de alto
                TARGET_SIZE = (350, 250) 
                
                # Recorte inteligente (Center Crop)
                w, h = img_original.size
                target_ratio = TARGET_SIZE[0] / TARGET_SIZE[1]
                current_ratio = w / h
                
                if current_ratio > target_ratio:
                    new_width = int(target_ratio * h)
                    left = (w - new_width) / 2
                    img_res = img_original.crop((left, 0, left + new_width, h))
                else:
                    new_height = int(w / target_ratio)
                    top = (h - new_height) / 2
                    img_res = img_original.crop((0, top, w, top + new_height))
                
                # Redimensionar con alta calidad
                img_final = img_res.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # --- DISEÑO DE PANTALLA ---
                # Usamos 5 columnas y ponemos la imagen en la del centro (3) 
                # para que se vea pequeña y centrada
                c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])
                
                with c3:
                    st.image(img_final, use_container_width='stretch')
                    # Estilo para bordes redondeados y sombra suave
                    st.markdown("""
                        <style>
                        [data-testid="stImage"] img {
                            border-radius: 10px;
                            box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error: {e}")