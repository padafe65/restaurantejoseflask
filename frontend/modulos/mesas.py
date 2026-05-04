import streamlit as st
import requests
import pandas as pd
import time as python_time

# --- CONFIGURACIÓN INICIAL ---

def mesas(API_URL, headers,rol):
    if rol in ["admin", "mesero"]:
        st.header("🪑 Estado de las Mesas")
        res_t = requests.get(f"{API_URL}/tables/", headers=headers)
        res_r_check = requests.get(f"{API_URL}/reservations/", headers=headers)
        
        if res_t.status_code == 200:
            mesas_list = res_t.json()
            reservas_raw = res_r_check.json() if res_r_check.status_code == 200 else []
            
            for m in mesas_list:
                tiene_reserva = any(r['table_id'] == m['id'] and r['status'] == 'confirmada' for r in reservas_raw)
                if tiene_reserva and m['status'] == 'libre':
                    requests.put(f"{API_URL}/tables/{m['id']}", json={"status": "reservada"}, headers=headers)
                    m['status'] = 'reservada'
                elif not tiene_reserva and m['status'] == 'reservada':
                    requests.patch(f"{API_URL}/tables/{m['id']}/release", headers=headers)
                    m['status'] = 'libre'
                
                m['Confirmadas'] = sum(1 for r in reservas_raw if r['table_id'] == m['id'] and r['status'] == 'confirmada')

            cols = st.columns(4) 
            for i, mesa in enumerate(mesas_list):
                with cols[i % 4]:
                    emoji = "🔴" if mesa['status'] == 'ocupada' else "🟡" if mesa['status'] == 'reservada' or mesa['status'] == 'confirmada' else "🟢"
                    st.metric(label=f"Mesa {mesa['number']}", value=mesa['status'].upper(), delta=emoji)
                    if mesa['status'] in ['ocupada', 'reservada']:
                        if st.button(f"🔓 Liberar #{mesa['number']}", key=f"btn_lib_{mesa['id']}"):
                            if mesa.get('Confirmadas', 0) > 0:
                                st.error("Acción bloqueada: Hay reserva activa.")
                            else:
                                requests.patch(f"{API_URL}/tables/{mesa['id']}/release", headers=headers)
                                st.rerun()

            st.divider()
            
            if rol == "admin":
                with st.expander("➕ Agregar Nueva Mesa"):
                    with st.form("new_table"):
                        n_num = st.number_input("Número", min_value=1)
                        n_cap = st.number_input("Capacidad", min_value=1)
                        if st.form_submit_button("Guardar Mesa"):
                            datos=requests.post(f"{API_URL}/tables/", json={"number":n_num, "capacity":n_cap}, headers=headers)
                            if datos.status_code == 201: # 201 es 'Created' según tu backend
                                st.success(f"✅ Mesa {n_num} creada exitosamente")
                                print("Exitoso - Datos de la mesa:", datos.json())
                                python_time.sleep(1) # Pequeña pausa para que el usuario vea el mensaje
                                st.rerun()
                            elif datos.status_code == 400: # Error controlado (ya existe)
                                error_msg = datos.json().get('detail', 'Error al crear la mesa')
                                st.error(f"❌ {error_msg}")
                            else:
                                st.error(f"📡 Error inesperado: {datos.status_code}")
                                st.rerun()           
                st.dataframe(pd.DataFrame(mesas_list), width="stretch", hide_index=True)
            
