import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import base64
import pandas as pd  # Necesario para tablas
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

# ==============================================================================
# ESTILOS CSS
# ==============================================================================
st.markdown(f"""
<style>
    .block-container {{ padding-top: 0rem; margin-top: 1rem; }}
    
    /* Banner */
    .hero-container {{
        background-image: url("data:image/jpg;base64,{img_b64}");
        background-size: cover; background-position: center;
        padding: 80px 20px; border-radius: 15px; margin-bottom: 30px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .hero-overlay {{ background-color: rgba(0, 0, 0, 0.7); padding: 20px 40px; border-radius: 10px; display: inline-block; }}
    .hero-title {{ color: #FFFFFF; font-weight: 800; font-size: 3em; margin: 0; text-shadow: 2px 2px 4px #000; }}

    /* Contenedores */
    .report-container {{
        background-color: #1E1E1E; padding: 25px; border-radius: 12px;
        border: 1px solid #333; font-family: 'Segoe UI', sans-serif; color: #E0E0E0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }}
    
    /* Badges */
    .badge {{ display: inline-block; padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 15px; }}
    .badge-warning {{ background-color: rgba(255, 167, 38, 0.2); color: #FFA726; border: 1px solid #FFA726; }}
    .badge-success {{ background-color: rgba(76, 175, 80, 0.2); color: #4CAF50; border: 1px solid #4CAF50; }}
    
    /* Tablas */
    .result-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
    .result-table th {{ text-align: left; color: #888; border-bottom: 1px solid #444; padding: 8px; }}
    .result-table td {{ padding: 10px 8px; border-bottom: 1px solid #333; color: #DDD; }}
    
    /* Tarjetas Métricas */
    .metric-card {{ background-color: #2D2D2D; padding: 20px; border-radius: 8px; text-align: center; margin-top: 20px; border-left: 5px solid; }}
    .metric-value {{ font-size: 28px; font-weight: 800; margin: 5px 0; }}
    .metric-label {{ font-size: 12px; color: #AAA; text-transform: uppercase; }}
    
    /* Utilidades */
    .highlight {{ color: #64B5F6; font-family: 'Courier New', monospace; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# BANNER
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
        
        # --- E91 (SIMULACIÓN) ---
        if protocolo == 'E91 (Entrelazamiento)':
            st.subheader("🔬 Protocolo E91 (Bell-CHSH)")
            S_valor, E_vals = fn.calcular_bell_e91(sim, recursos)
            
            c_log, c_graf = st.columns([1.5, 1])
            with c_log:
                badge_eve = f'<span class="badge badge-warning">🕵️ EVE ACTIVA: RUIDO {nivel_ruido*100:.0f}%</span>' if nivel_ruido > 0 else '<span class="badge badge-success">✅ CANAL LIMPIO</span>'
                
                if S_valor > 2.0:
                    color_s = "#4CAF50"
                    msg_titulo = "¡CANAL SEGURO!"
                    msg_accion = "Correlación cuántica fuerte. <strong>Es hora de comunicarse.</strong>"
                    icono = "✅"
                else:
                    color_s = "#FF5252"
                    msg_titulo = "¡ALERTA DE SEGURIDAD!"
                    msg_accion = "Comportamiento clásico detectado. <strong>No transmitir secretos.</strong>"
                    icono = "🚨"

                # Tabla Nativa
                st.markdown(badge_eve, unsafe_allow_html=True)
                df_sim = pd.DataFrame({
                    "Configuración": ["00 (A-B)", "01 (A-B)", "10 (A-B)", "11 (A-B)"],
                    "Correlación (E)": [f"{e:.4f}" for e in E_vals]
                })
                st.table(df_sim)
                
                # Tarjeta Acción
                st.metric("Valor S (CHSH)", f"{S_valor:.4f}")
                if S_valor > 2.0:
                    st.success(f"### {icono} {msg_titulo}\n{msg_accion}")
                else:
                    st.error(f"### {icono} {msg_titulo}\n{msg_accion}")
            
            with c_graf:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.bar(['S'], [S_valor], color=color_s)
                ax.axhline(2.0, color='red', linestyle='--', linewidth=2, label='Clásico (2.0)')
                ax.axhline(2.82, color='blue', linestyle=':', linewidth=2, label='Cuántico (2.82)')
                
                # Etiquetas en gráfica
                ax.text(0.55, 2.05, 'Clásico', color='red', fontsize=9, fontweight='bold')
                ax.text(0.55, 2.85, 'Cuántico', color='blue', fontsize=9, fontweight='bold')
                ax.bar_label(ax.containers[0], fmt='%.3f', padding=3, fontweight='bold')
                
                ax.set_ylim(0, 3.5); ax.legend(loc='upper left')
                st.pyplot(fig)

        # --- BB84 (SIMULACIÓN) ---
        elif protocolo == 'BB84 (Polarización)':
            st.subheader("🔐 Protocolo BB84")
            data = fn.ejecutar_bb84(sim, recursos)
            
            c_log, c_graf = st.columns([1.8, 1])
            with c_log:
                def arr_str(arr): return " ".join([str(x) for x in arr])
                eficiencia = (data['len_clave']/data['n_bits']*100)
                
                # Badge Estado
                if data['qber'] == 0:
                    st.success("✅ **CANAL SEGURO (QBER 0%)**")
                    accion = st.success
                    msg_acc = "**Acción:** Proceder con la transmisión cifrada."
                elif data['qber'] < 11:
                    st.warning(f"⚠️ **RUIDO BAJO ({data['qber']:.1f}%)**")
                    accion = st.info
                    msg_acc = "**Acción:** Aplicar corrección de errores y privacidad."
                else:
                    st.error(f"🚨 **EVE DETECTADA ({data['qber']:.1f}%)**")
                    accion = st.error
                    msg_acc = "**Acción:** DESCARTAR CLAVE INMEDIATAMENTE."

                # Reporte Texto
                st.markdown("### 📨 Datos Transmitidos")
                st.text(f"Alice Bits (10): {data['alice_bits'][:10]}")
                st.text(f"Alice Bases (10):{data['alice_bases'][:10]}")
                st.text(f"Bob Bases (10):  {data['bob_bases'][:10]}")
                
                st.markdown("### 🔑 Cribado")
                c1, c2 = st.columns(2)
                c1.metric("Longitud Final", f"{data['len_clave']}")
                c2.metric("Eficiencia", f"{eficiencia:.1f}%")
                
                st.text_area("Muestra Clave (Alice):", str(data['alice_key'][:15]), disabled=True)
                
                # Mensaje Acción
                st.markdown("---")
                accion(f"### Tasa de Error: {data['qber']:.2f}%\n{msg_acc}")

            with c_graf:
                fig, ax = plt.subplots(figsize=(4, 5))
                bar_color = '#FF5252' if data['qber'] > 11 else '#4CAF50'
                bars = ax.bar(['QBER'], [data['qber']], color=bar_color, width=0.6)
                ax.axhline(11, color='red', linestyle='--', linewidth=2)
                ax.text(0.6, 11.5, 'Límite (11%)', color='red')
                ax.bar_label(bars, fmt='%.1f%%', padding=3, fontweight='bold')
                ax.set_ylim(0, 100); ax.set_ylabel("Error (%)")
                st.pyplot(fig)

# ==============================================================================
# MODO 2: HARDWARE REAL IBM
# ==============================================================================
else:
    st.sidebar.markdown("---")
    st.sidebar.header("☁️ Conexión IBM Quantum")
    user_token = st.sidebar.text_input("API Token:", type="password")
    
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
            
            shots = st.number_input("Shots:", 100, 4000, 1024)
            if st.button("⚛️ Enviar Trabajo"):
                try:
                    with st.spinner("Enviando..."):
                        job = fn.ejecutar_e91_real(backend_obj, shots)
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
                            
                            st.info(f"📡 **REPORTE:** {backend_obj.name}")
                            
                            # Tabla Nativa para IBM
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
                            # --- GRÁFICO HARDWARE REAL DETALLADO ---
                            fig, ax = plt.subplots(figsize=(4, 5))
                            
                            # Barra
                            bars = ax.bar(['S Real'], [S_real], color='#9C27B0', width=0.5, edgecolor='black')
                            
                            # Líneas Límite
                            ax.axhline(2.0, color='red', linestyle='--', linewidth=2, label='Clásico')
                            ax.axhline(2.82, color='blue', linestyle=':', linewidth=2, label='Cuántico')
                            
                            # Etiquetas de texto en el gráfico
                            ax.text(0.55, 2.05, 'Clásico (2.0)', color='red', fontsize=9, fontweight='bold')
                            ax.text(0.55, 2.85, 'Cuántico (~2.82)', color='blue', fontsize=9, fontweight='bold')
                            
                            # Valor sobre la barra
                            ax.bar_label(bars, fmt='%.3f', padding=3, fontsize=12, fontweight='bold')
                            
                            ax.set_ylim(0, 3.5)
                            ax.set_title(f"Resultados en {backend_obj.name}", fontsize=12)
                            ax.grid(axis='y', linestyle='--', alpha=0.3)
                            
                            st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No hay backends disponibles.")
    else:
        st.info("👈 Ingresa tu token para conectar.")