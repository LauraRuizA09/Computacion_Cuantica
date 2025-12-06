import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import base64
import Funciones as fn 

st.set_page_config(page_title="Ciberseguridad Cuántica", page_icon="⚛️", layout="wide")

# ==============================================================================
# FUNCIÓN DE IMAGEN Y CSS
# ==============================================================================
def obtener_imagen_base64(ruta_imagen):
    try:
        with open(ruta_imagen, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_b64 = obtener_imagen_base64("Portada.jpg")

st.markdown(f"""
<style>
    .block-container {{ padding-top: 0rem; margin-top: 1rem; }}
    .hero-container {{
        background-image: url("data:image/jpg;base64,{img_b64}");
        background-size: cover; background-position: center;
        padding: 60px 20px; border-radius: 15px; margin-bottom: 25px;
        text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    .hero-overlay {{ background-color: rgba(0, 0, 0, 0.6); padding: 20px; border-radius: 10px; display: inline-block; }}
    .hero-title {{ color: #FFFFFF; font-weight: 800; font-size: 3em; margin: 0; }}
    .report-container {{
        background-color: #0E1117; padding: 20px; border-radius: 10px; border: 1px solid #303030;
        font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.5; color: #E0E0E0;
    }}
    .highlight {{ color: #64B5F6; }}
    .success-text {{ color: #4CAF50; font-weight: bold; }}
    .danger-text {{ color: #FF5252; font-weight: bold; }}
    .warning-text {{ color: #FFA726; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# TÍTULO PRINCIPAL (BANNER)
if img_b64:
    st.markdown('<div class="hero-container"><div class="hero-overlay"><h1 class="hero-title">🎛️ Comprobación de Ciberseguridad Cuántica</h1></div></div>', unsafe_allow_html=True)
else:
    st.title("🎛️ Comprobación de Ciberseguridad Cuántica")

# SELECCIÓN DE MODO
modo_ejecucion = st.sidebar.radio("📍 Entorno de Ejecución:", ["Simulación (Local)", "Hardware Real (IBM Quantum)"])

# ==============================================================================
# MODO 1: SIMULACIÓN LOCAL
# ==============================================================================
if modo_ejecucion == "Simulación (Local)":
    
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Configuración Simulación")
        # Asegúrate de que las opciones aquí coincidan exactamente con los IF de abajo
        protocolo = st.selectbox("1. Protocolo:", ('E91 (Entrelazamiento)', 'BB84 (Polarización)'))
        escenario = st.selectbox("2. Escenario:", ('Canal Seguro (Ideal)', 'Canal Inseguro (Simulando a Eve)'))
        
        nivel_ruido = 0.0
        if escenario == 'Canal Inseguro (Simulando a Eve)':
            st.warning("🕵️ **Eve Activada**")
            nivel_ruido = st.slider("Intensidad de Espionaje:", 0.0, 1.0, 0.3, 0.05)
        
        recursos = st.slider("3. Recursos (Bits/Shots):", 50, 2000, 1000, 50)
        btn_simular = st.button("🚀 Iniciar Simulación", type="primary")

    # AQUÍ COMIENZA LA LÓGICA DE EJECUCIÓN
    if btn_simular:
        sim = fn.obtener_simulador(escenario, nivel_ruido, protocolo)
        
        # --- BLOQUE E91 ---
        if protocolo == 'E91 (Entrelazamiento)':
            st.subheader("🔬 Protocolo E91 (Bell-CHSH) - Simulación")
            S_valor, E_vals = fn.calcular_bell_e91(sim, recursos)
            
            c_log, c_graf = st.columns([1.5, 1])
            with c_log:
                estado_eve = f"🕵️ EVE ACTIVADA: Ruido al {nivel_ruido*100:.1f}%" if nivel_ruido > 0 else "✅ CANAL SEGURO"
                conclusion = "✅ VIOLACIÓN CUÁNTICA (S > 2.0)" if S_valor > 2.0 else "🚨 COMPROMETIDO (S ≤ 2.0)"
                reporte = f"""
                <div class="report-container">
                    <div class="warning-text">{estado_eve}</div><br>
                    <div><strong>--- RESULTADOS ---</strong></div>
                    <div>A0B0(E): <span class="highlight">{E_vals[0]:.4f}</span> | A0B1(E): <span class="highlight">{E_vals[1]:.4f}</span></div>
                    <div>A1B0(E): <span class="highlight">{E_vals[2]:.4f}</span> | A1B1(E): <span class="highlight">{E_vals[3]:.4f}</span></div>
                    <br>
                    <div>Valor S: <strong>{S_valor:.4f}</strong></div>
                    <div class="{'success-text' if S_valor > 2 else 'danger-text'}">{conclusion}</div>
                </div>
                """
                st.markdown(reporte, unsafe_allow_html=True)
            
            with c_graf:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.bar(['S'], [S_valor], color='#4CAF50' if S_valor > 2 else '#FF5252')
                ax.axhline(2.0, color='red', linestyle='--'); ax.axhline(2.82, color='blue', linestyle=':')
                ax.set_ylim(0, 3.2); ax.set_title("Test de Bell")
                st.pyplot(fig)

        # --- BLOQUE BB84 (CORREGIDO Y ALINEADO) ---
        elif protocolo == 'BB84 (Polarización)':
            st.subheader("🔐 Protocolo BB84 - Simulación")
            # Llamamos a la función que ahora devuelve un DICCIONARIO
            data = fn.ejecutar_bb84(sim, recursos)
            
            c_log, c_graf = st.columns([1.8, 1])
            with c_log:
                def arr_str(arr): return " ".join([str(x) for x in arr])
                eficiencia = (data['len_clave']/data['n_bits']*100)
                msg = '<span class="success-text">ÉXITO: Canal Seguro.</span>' if data['qber'] == 0 else '<span class="danger-text">ALERTA: Eve detectada.</span>'
                if 0 < data['qber'] < 11: msg = '<span class="warning-text">ADVERTENCIA: Ruido bajo.</span>'
                
                # HTML EXACTO QUE PEDISTE
                reporte = f"""
                <div class="report-container">
                    <div><strong>--- Iniciando Protocolo BB84 con {data['n_bits']} qubits ---</strong></div>
                    <div>Alice Bits (10): <span class="highlight">{arr_str(data['alice_bits'][:10])}</span></div>
                    <div>Alice Bases (10): <span class="highlight">{arr_str(data['alice_bases'][:10])}</span> (0=Z, 1=X)</div>
                    <div>Bob Bases   (10): <span class="highlight">{arr_str(data['bob_bases'][:10])}</span> (0=Z, 1=X)</div>
                    <br>
                    <div><em>Transmitiendo... Cribando...</em></div>
                    <br>
                    <div><strong>--- RESULTADOS ---</strong></div>
                    <div>Longitud original: {data['n_bits']}</div>
                    <div>Longitud clave final: {data['len_clave']}</div>
                    <div>Eficiencia: {eficiencia:.1f}% (Teórico ~50%)</div>
                    <br>
                    <div>Clave Alice (15): <span class="highlight">{arr_str(data['alice_key'][:15])}</span></div>
                    <div>Clave Bob   (15): <span class="highlight">{arr_str(data['bob_key'][:15])}</span></div>
                    <br>
                    <div><strong>Tasa de Error (QBER): {data['qber']:.2f}%</strong></div>
                    <div>{msg}</div>
                </div>
                """
                st.markdown(reporte, unsafe_allow_html=True)
            
            with c_graf:
                # Gráfico Simplificado a la derecha
                fig, ax = plt.subplots(figsize=(4, 5))
                bar_color = '#FF5252' if data['qber'] > 11 else '#4CAF50'
                ax.bar(['QBER'], [data['qber']], color=bar_color, width=0.6)
                ax.axhline(11, color='red', linestyle='--', linewidth=2)
                ax.text(0.6, 11.5, 'Umbral (11%)', color='red')
                ax.set_ylim(0, 100); ax.set_ylabel("Error (%)")
                ax.text(0, data['qber'] + 2, f"{data['qber']:.1f}%", ha='center', fontweight='bold')
                st.pyplot(fig)

# ==============================================================================
# MODO 2: HARDWARE REAL IBM (SIN CAMBIOS)
# ==============================================================================
else:
    st.sidebar.markdown("---")
    st.sidebar.header("☁️ Conexión IBM Quantum")
    user_token = st.sidebar.text_input("Ingresa tu API Token:", type="password")
    
    if st.sidebar.button("📡 Conectar"):
        with st.spinner("Autenticando..."):
            service, error = fn.conectar_ibm(user_token)
            if service:
                st.session_state['ibm_service'] = service
                st.session_state['backends'] = fn.obtener_backends_ibm(service)
                st.sidebar.success("Conectado!")
            else:
                st.sidebar.error(f"Error: {error}")

    if 'ibm_service' in st.session_state:
        backends = st.session_state['backends']
        if backends:
            st.subheader("🖥️ Ejecución en Hardware Real")
            opciones = [f"{b.name} (Q: {b.num_qubits}, Cola: {b.status().pending_jobs})" for b in backends]
            seleccion = st.selectbox("Selecciona Computador:", opciones)
            backend_obj = next(b for b in backends if b.name == seleccion.split(" ")[0])
            
            col1, col2 = st.columns([1, 2])
            shots_real = col1.number_input("Shots:", 100, 4000, 1024)
            if col2.button("⚛️ Enviar Trabajo"):
                try:
                    with st.spinner("Enviando..."):
                        job = fn.ejecutar_e91_real(backend_obj, shots_real)
                        
                        # Polling
                        bar = st.progress(0)
                        while not job.in_final_state():
                            status = job.status()
                            msg = status if isinstance(status, str) else status.name
                            st.toast(f"Estado: {msg}")
                            time.sleep(3)
                            bar.progress(50)
                        bar.progress(100)
                        
                        S_real, E_vals = fn.procesar_resultados_e91_real(job)
                        
                        clog, cgraf = st.columns([1.5, 1])
                        with clog:
                            ruido_est = 2.828 - S_real
                            html_real = f"""
                            <div class="report-container">
                                <div class="header-text">📡 REPORTE: {backend_obj.name}</div><br>
                                <div><strong>--- CORRELACIONES ---</strong></div>
                                <div>E(0,0): {E_vals[0]:.4f} | E(0,1): {E_vals[1]:.4f}</div>
                                <div>E(1,0): {E_vals[2]:.4f} | E(1,1): {E_vals[3]:.4f}</div>
                                <br>
                                <div>Valor S: <strong>{S_real:.4f}</strong></div>
                                <div>Desviación (Ruido): {ruido_est:.4f}</div>
                                <br>
                                <div class="{'header-text' if S_real > 2 else 'danger-text'}">
                                    {'✅ VIOLACIÓN DE BELL' if S_real > 2 else '🚨 RUIDO ALTO'}
                                </div>
                            </div>
                            """
                            st.markdown(html_real, unsafe_allow_html=True)
                        with cgraf:
                            fig, ax = plt.subplots(figsize=(4, 5))
                            ax.bar(['S Real'], [S_real], color='#9C27B0')
                            ax.axhline(2.0, color='red', linestyle='--'); ax.axhline(2.82, color='blue', linestyle=':')
                            ax.set_ylim(0, 3.2); ax.legend()
                            ax.text(0, S_real+0.05, f"{S_real:.3f}", ha='center', fontweight='bold')
                            st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No hay backends disponibles.")
    else:
        st.info("👈 Ingresa tu token para conectar.")