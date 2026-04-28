import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, time as dt_time
import time as python_time

def sincronizar_estados_mesas(api_url, headers, reservas_raw, mesas_list):
    """Verifica que las mesas con reservas confirmadas no aparezcan como LIBRES."""
    for mesa in mesas_list:
        tiene_reserva_activa = any(
            r['table_id'] == mesa['id'] and r['status'] == 'confirmada' 
            for r in reservas_raw
        )
        if tiene_reserva_activa and mesa['status'] == 'libre':
            requests.patch(f"{api_url}/tables/{mesa['id']}/status", 
                           json={"status": "reservada"}, headers=headers)

def render_reservas(api_url, headers, rol):
    st.header("📅 Gestión de Reservaciones")
    
    # 1. Carga de datos
    res_r = requests.get(f"{api_url}/reservations/", headers=headers)
    res_c = requests.get(f"{api_url}/customers/", headers=headers)
    res_m = requests.get(f"{api_url}/tables/", headers=headers)

    if res_r.status_code == 200 and res_c.status_code == 200 and res_m.status_code == 200:
        reservas_raw = res_r.json()
        clientes = res_c.json()
        mesas = res_m.json()

        sincronizar_estados_mesas(api_url, headers, reservas_raw, mesas)

        # Diccionarios de apoyo
        dict_c_id_nom = {c['id']: c['full_name'] for c in clientes}
        dict_c_nom_id = {f"{c['full_name']} (ID: {c['id']})": c['id'] for c in clientes}
        dict_m_label = {m['id']: f"Mesa {m['number']} | Cap: {m['capacity']}" for m in mesas}
        dict_m_data = {f"Mesa {m['number']} | Cap: {m['capacity']}": m for m in mesas}

        # --- TABLA DE RESERVAS MEJORADA (Con nombres claros) ---
        df = pd.DataFrame(reservas_raw)
        if not df.empty:
            # Creamos la columna con Nombre e ID para que sea fácil identificar
            df['Cliente (ID)'] = df['customer_id'].apply(lambda x: f"{dict_c_id_nom.get(x, 'S/N')} (ID: {x})")
            
            columnas_visibles = {
                'id': 'Reserva #',
                'Cliente (ID)': 'Cliente',
                'table_id': 'ID Mesa',
                'reservation_date': 'Fecha',
                'reservation_time': 'Hora',
                'pax': 'Pax',
                'status': 'Estado'
            }
            # Mostramos el dataframe con los nombres de columna bonitos
            st.dataframe(df[list(columnas_visibles.keys())].rename(columns=columnas_visibles), use_container_width=True)

        st.divider()

        # Selección de reserva
        opciones = {f"Reserva #{r['id']} - {dict_c_id_nom.get(r['customer_id'], 'S/N')}": r for r in reservas_raw}
        sel_res = st.selectbox("🔍 Cargar reserva para editar:", ["-- Nueva Reserva --"] + list(opciones.keys()))
        
        if sel_res == "-- Nueva Reserva --":
            r_sel = {"id": 0, "customer_id": None, "table_id": None, "pax": 1, "status": "confirmada", 
                     "reservation_date": str(datetime.now().date()), "reservation_time": "12:00:00"}
        else:
            r_sel = opciones[sel_res]

        with st.form("form_reservas_final"):
            st.markdown(f"### 📝 Datos de la Reserva")
            col1, col2, col3 = st.columns(3)
            with col1:
                idx_c = list(dict_c_nom_id.values()).index(r_sel['customer_id']) if r_sel['customer_id'] in dict_c_nom_id.values() else 0
                f_cliente = st.selectbox("Cliente", list(dict_c_nom_id.keys()), index=idx_c)
                
                label_mesa_actual = dict_m_label.get(r_sel['table_id'], list(dict_m_data.keys())[0])
                idx_m = list(dict_m_data.keys()).index(label_mesa_actual)
                f_mesa = st.selectbox("Mesa", list(dict_m_data.keys()), index=idx_m)
            with col2:
                f_date = st.date_input("Fecha", value=datetime.strptime(r_sel['reservation_date'], '%Y-%m-%d').date())
                f_time = st.time_input("Hora", value=datetime.strptime(r_sel['reservation_time'], '%H:%M:%S').time())
            with col3:
                f_pax = st.number_input("Pax (Personas)", min_value=1, value=int(r_sel['pax']))
                estados_validos = ['confirmada', 'cancelada', 'finalizada']
                idx_est = estados_validos.index(r_sel['status']) if r_sel['status'] in estados_validos else 0
                f_status = st.selectbox("Estado", estados_validos, index=idx_est)

            if st.form_submit_button("💾 Guardar Reservación"):
                m_sel = dict_m_data[f_mesa]
                
                # --- VALIDACIÓN DE CAPACIDAD ---
                if f_pax > m_sel['capacity']:
                    st.error(f"🚫 Capacidad excedida: La Mesa {m_sel['number']} es para máximo {m_sel['capacity']} personas.")
                    
                    # Buscamos mesas que SI tengan la capacidad necesaria y estén libres
                    sugerencias = [f"Mesa {m['number']} (Cap: {m['capacity']})" for m in mesas 
                                  if m['capacity'] >= f_pax and m['status'] == 'libre']
                    
                    if sugerencias:
                        st.info(f"💡 Mesas recomendadas para {f_pax} personas: " + ", ".join(sugerencias))
                    else:
                        st.warning("No hay mesas libres con capacidad suficiente en este momento.")
                else:
                    # Lógica de choque de horario (Regla de 2 horas)
                    nueva_fh = datetime.combine(f_date, f_time)
                    choque = False
                    for r in reservas_raw:
                        if r['table_id'] == m_sel['id'] and r['id'] != r_sel['id'] and r['status'] == 'confirmada':
                            r_fh = datetime.combine(datetime.strptime(r['reservation_date'], '%Y-%m-%d').date(),
                                                   datetime.strptime(r['reservation_time'], '%H:%M:%S').time())
                            if abs((nueva_fh - r_fh).total_seconds()) < 7200:
                                choque = True; break
                    
                    if choque:
                        st.error("🚫 Conflicto: La mesa ya tiene una reserva en ese horario.")
                    else:
                        payload = {
                            "customer_id": dict_c_nom_id[f_cliente], 
                            "table_id": m_sel['id'], 
                            "reservation_date": str(f_date), 
                            "reservation_time": str(f_time), 
                            "pax": f_pax, 
                            "status": f_status
                        }
                        
                        # Guardado en Backend
                        if r_sel['id'] == 0:
                            res = requests.post(f"{api_url}/reservations/", json=payload, headers=headers)
                        else:
                            res = requests.put(f"{api_url}/reservations/{r_sel['id']}", json=payload, headers=headers)
                        
                        if res.status_code in [200, 201]:
                            nuevo_estado_mesa = "reservada" if f_status == "confirmada" else "libre"
                            requests.patch(f"{api_url}/tables/{m_sel['id']}/status", 
                                           json={"status": nuevo_estado_mesa}, headers=headers)
                            st.success("✅ Sincronizado correctamente.")
                            python_time.sleep(1)
                            st.rerun()

    # --- LIBERACIÓN MANUAL ---
    st.divider()
    st.subheader("🔓 Liberación Manual")
    m_lib = st.selectbox("Mesa a liberar:", list(dict_m_data.keys()), key="lib_manual_res")
    if st.button("Confirmar Liberación"):
        m_obj = dict_m_data[m_lib]
        if any(r['table_id'] == m_obj['id'] and r['status'] == 'confirmada' for r in reservas_raw):
            st.error("🚫 No se puede liberar: Hay una reserva confirmada activa.")
        else:
            requests.patch(f"{api_url}/tables/{m_obj['id']}/release", headers=headers)
            st.success(f"Mesa {m_obj['number']} liberada."); python_time.sleep(1); st.rerun()