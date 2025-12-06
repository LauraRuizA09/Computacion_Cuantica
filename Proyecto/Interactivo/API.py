import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import base64
import pandas as pd  # Necesario para tablas bonitas
import Funciones as fn 

st.set_page_config(page_title="Ciberseguridad Cuántica", page_icon="⚛️", layout="wide")

# ==============================================================================
# CARGA DE IMAGEN DE FONDO
# ==============================================================================
def obtener_imagen_base64(ruta_imagen):
    try:
        with open(ruta_imagen, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

img_b64 = obtener_imagen_base64("Portada.jpg")

# CSS Mínimo para el Banner
st.markdown(f"""
<style>
    .block-container {{ padding-top: 0rem; margin-top: 1rem; }}
    .hero-container {{
        background-image: url("data:image/jpg;base64,{img_b64}");
        background-size: cover; background-position: center;
        padding: 80px 20px; border-radius: 15px; margin-bottom: 30px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .hero-overlay {{ background-color: rgba(0, 0, 0, 0.7); padding: 20px 40px; border-radius: 10px; display: inline-block; }}
    .hero-title {{ color: #FFFFFF; font-weight: 800; font-size: 3em; margin: 0; text-shadow: 2px 2px 4px #000; }}
</style>
""", unsafe_allow_html=True)

# MOSTRAR BANNER
if img_b64:
    st.markdown('<div class="hero-container"><div class="hero-overlay"><h1 class="hero-title">🎛️ Comprobación de Ciberseguridad Cuántica</h1></div></div>', unsafe_allow_html=True)
else:
    st.title("Comprobación de Ciberseguridad Cuántica")

modo_ejecucion = st.sidebar.radio("📍 Entorno de Ejecución:", ["Simulación (Local)", "Hardware Real (IBM Quantum)"])

# ==============================================================================
# MODO 1: SIMULACIÓN LOCAL
# ==============================================================================
if modo_ejecucion == "Simulación (Local)":
    
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Configuración Simulación")
        protocolo = st.selectbox("1. Protocolo:", ('E91 (Entrelazamiento)', 'BB84 (Polarización)'))
        escenario = st.selectbox("2. Escenario:", ('Canal Seguro (Ideal)', 'Canal Inseguro (Simulando a Eve)'))
        
        nivel_ruido = 0.0
        if escenario == 'Canal Inseguro (Simulando a Eve)':
            st.warning("🕵️ **Eve Activada**")
            nivel_ruido = st.slider("Intensidad de Espionaje:", 0.0, 1.0, 0.3, 0.05)
        
        recursos = st.slider("3. Recursos (Bits/Shots):", 50, 2000, 1000, 50)
        btn_simular = st.button("🚀 Iniciar Simulación", type="primary")

    if btn_simular:
        sim = fn.obtener_simulador(escenario, nivel_ruido, protocolo)
        
        # --- E91 (DISEÑO NATIVO LIMPIO) ---
        if protocolo == 'E91 (Entrelazamiento)':
            st.subheader("🔬 Protocolo E91 (Bell-CHSH)")
            S_valor, E_vals = fn.calcular_bell_e91(sim, recursos)
            
            c_log, c_graf = st.columns([1.5, 1])
            with c_log:
                # 1. Estado de Eve (Badge Nativo)
                if nivel_ruido > 0:
                    st.warning(f"🕵️ **EVE DETECTADA:** Ruido inyectado al {nivel_ruido*100:.0f}%")
                else:
                    st.success("✅ **CANAL LIMPIO:** Sin interferencias detectadas.")

                st.markdown("### 📊 Resultados de Correlación")
                
                # 2. Tabla de Datos (Usando Pandas para que se vea ordenado)
                df_resultados = pd.DataFrame({
                    "Configuración": ["Alice 0 - Bob 0", "Alice 0 - Bob 1", "Alice 1 - Bob 0", "Alice 1 - Bob 1"],
                    "Correlación (E)": [f"{e:.4f}" for e in E_vals]
                })
                st.table(df_resultados)

                st.markdown("---")

                # 3. Tarjeta de Acción (Usando componentes nativos)
                # Métrica grande
                st.metric(label="Valor S (CHSH) Calculado", value=f"{S_valor:.4f}", delta=f"{S_valor-2.0:.2f} vs Clásico")

                # Mensaje de Acción
                if S_valor > 2.0:
                    st.success("""
                    ### ✅ ¡CANAL SEGURO!
                    **Acción Recomendada:** La violación de la desigualdad es clara. Puede proceder a generar la clave criptográfica.
                    """)
                else:
                    st.error("""
                    ### 🚨 ALERTA DE SEGURIDAD
                    **Acción Recomendada:** El canal se comporta clásicamente. **Detener transmisión y ajustar parámetros.**
                    """)
            
            with c_graf:
                # Gráfico
                fig, ax = plt.subplots(figsize=(4, 4))
                color_s = "#4CAF50" if S_valor > 2.0 else "#FF5252"
                ax.bar(['S'], [S_valor], color=color_s)
                ax.axhline(2.0, color='red', linestyle='--', label='Clásico (2.0)')
                ax.axhline(2.82, color='blue', linestyle=':', label='Cuántico (2.82)')
                ax.set_ylim(0, 3.2); ax.legend()
                st.pyplot(fig)

        # --- BB84 (DISEÑO NATIVO LIMPIO) ---
        elif protocolo == 'BB84 (Polarización)':
            st.subheader("🔐 Protocolo BB84")
            data = fn.ejecutar_bb84(sim, recursos)
            
            c_log, c_graf = st.columns([1.8, 1])
            with c_log:
                # 1. Estado General
                if data['qber'] == 0:
                    st.success("✅ **ÉXITO:** Claves idénticas. Canal seguro.")
                elif data['qber'] < 11:
                    st.warning("⚠️ **ADVERTENCIA:** Ruido bajo detectado. Corregible.")
                else:
                    st.error("🚨 **ALERTA CRÍTICA:** Eve detectada. Canal comprometido.")

                st.markdown("### 📨 Datos Transmitidos")
                
                # Muestras de datos (Texto formateado simple)
                st.text(f"Alice Bits (10):  {data['alice_bits'][:10]}")
                st.text(f"Alice Bases (10): {data['alice_bases'][:10]}")
                st.text(f"Bob Bases (10):   {data['bob_bases'][:10]}")
                
                st.markdown("### 🔑 Generación de Clave")
                col_k1, col_k2 = st.columns(2)
                col_k1.metric("Longitud Original", f"{data['n_bits']}")
                col_k2.metric("Longitud Final", f"{data['len_clave']}")
                
                st.caption(f"Eficiencia del cribado: {(data['len_clave']/data['n_bits']*100):.1f}%")

                st.text_area("Muestra de Clave Alice (15 bits):", str(data['alice_key'][:15]), height=70, disabled=True)
                st.text_area("Muestra de Clave Bob (15 bits):", str(data['bob_key'][:15]), height=70, disabled=True)

                st.markdown("---")
                
                # 2. Acción Final
                st.metric("Tasa de Error (QBER)", f"{data['qber']:.2f}%")
                
                if data['qber'] < 11:
                    st.info("**Acción:** Proceder con corrección de errores y amplificación de privacidad.")
                else:
                    st.error("**Acción:** DESCARTAR CLAVE. La tasa de error es demasiado alta.")

            with c_graf:
                fig, ax = plt.subplots(figsize=(4, 5))
                bar_color = '#FF5252' if data['qber'] > 11 else '#4CAF50'
                ax.bar(['QBER'], [data['qber']], color=bar_color, width=0.6)
                ax.axhline(11, color='red', linestyle='--', linewidth=2, label="Umbral")
                ax.text(0.6, 11.5, 'Límite (11%)', color='red')
                ax.set_ylim(0, 100); ax.set_ylabel("Error (%)")
                st.pyplot(fig)

# ==============================================================================
# MODO 2: HARDWARE REAL IBM
# ==============================================================================
else:
    st.sidebar.markdown("---")
    st.sidebar.header("☁️ Conexión IBM Quantum")
    user_token = st.sidebar.text_input("Ingresa tu API Token:", type="password")
    
    if st.sidebar.button("📡 Conectar"):
        with st.spinner("Conectando..."):
            service, error = fn.conectar_ibm(user_token)
            if service:
                st.session_state['ibm_service'] = service
                st.session_state['backends'] = fn.obtener_backends_ibm(service)
                st.sidebar.success("¡Conectado!")
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
                            
                            st.markdown(f"### 📡 Reporte: {backend_obj.name}")
                            
                            # Tabla Nativa
                            df_real = pd.DataFrame({
                                "Config": ["00", "01", "10", "11"],
                                "Correlación": [f"{e:.4f}" for e in E_vals]
                            })
                            st.table(df_real)
                            
                            st.metric("Valor S Medido", f"{S_real:.4f}", delta=f"-{ruido_est:.3f} Ruido")
                            
                            if S_real > 2.0:
                                st.success("""
                                ### ✅ VIOLACIÓN DE BELL CONFIRMADA
                                **Acción:** El dispositivo muestra comportamiento cuántico real. Es seguro comunicarse.
                                """)
                            else:
                                st.error("""
                                ### 🚨 RUIDO EXCESIVO
                                **Acción:** El ruido ha destruido el entrelazamiento. Cambiar de máquina o aumentar shots.
                                """)

                        with cgraf:
                            fig, ax = plt.subplots(figsize=(4, 5))
                            ax.bar(['S Real'], [S_real], color='#9C27B0')
                            ax.axhline(2.0, color='red', linestyle='--'); ax.axhline(2.82, color='blue', linestyle=':')
                            ax.set_ylim(0, 3.2)
                            st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No hay backends disponibles.")
    else:
        st.info("👈 Ingresa tu token para conectar.")