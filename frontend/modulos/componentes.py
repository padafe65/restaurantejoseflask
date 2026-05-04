import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from PIL import Image

def render_carrusel():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(BASE_DIR, "imagenes")
    fotos = ["resjose1.jpg", "resjose2.jpg", "resjose3.jpg", "resjose4.jpg", "resjose5.jpg", "resjose6.jpg"]
    
    # Refresco automático cada 7 segundos
    count = st_autorefresh(interval=7000, key="carrusel_counter")
    indice = count % len(fotos)
    
    if os.path.exists(img_dir):
        ruta_foto = os.path.join(img_dir, fotos[indice])
        
        if os.path.exists(ruta_foto):
            try:
                img_original = Image.open(ruta_foto)
                
                # --- NUEVA PROPORCIÓN MÁS NATURAL (4:3 o 16:9) ---
                # Al aumentar el alto (300 en lugar de 200), la imagen no se ve tan "aplastada"
                TARGET_SIZE = (1200, 600) 
                
                # Recorte inteligente (Mantenemos el aspecto pero con más nitidez)
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
                
                # Redimensionar con LANCZOS (el mejor filtro para nitidez)
                img_final = img_res.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # --- DISEÑO DE PANTALLA ---
                # Usamos columnas laterales más anchas para que la imagen central sea más pequeña
                # El ratio [1.5, 2, 1.5] centra la imagen y le da un tamaño de tarjeta elegante
                c1, c2, c3 = st.columns([1.5, 1, 1.5])
                
                with c2:
                    st.image(img_final, width=400)
                    # CSS mejorado: Sombra más profunda y borde sutil
                    st.markdown("""
                        <style>
                        [data-testid="stImage"] img {
                            border-radius: 15px;
                            box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
                            border: 1px solid #f0f2f6;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error al cargar imagen: {e}")