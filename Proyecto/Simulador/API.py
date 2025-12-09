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

    /* Badges */
    .badge {{ display: inline-block; padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 15px; }}
    .badge-warning {{ background-color: rgba(255, 167, 38, 0.2); color: #FFA726; border: 1px solid #FFA726; }}
    .badge-success {{ background-color: rgba(76, 175, 80, 0.2); color: #4CAF50; border: 1px solid #4CAF50; }}
    
    /* Tablas */
    .result-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
    .result-table th {{ text-align: left; color: #888; border-bottom: 1px solid #444; padding: 8px; }}
    .result-table td {{ padding: 10px 8px; border-bottom: 1px solid #333; color: #DDD; }}
</style>
""", unsafe_allow_html=True)

# BANNER PRINCIPAL
if img_b64:
    st.markdown(f'<div class="hero-container"><div class="hero-overlay"><h1 class="hero-title"> Comprobación de Ciberseguridad Cuántica</h1></div></div>', unsafe_allow_html=True)
else:
    st.title("Comprobación de Ciberseguridad Cuántica")

# SIDEBAR DE CONFIGURACIÓN
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
        
        # ----------------------------------------------------------------------
        # LÓGICA PROTOCOLO E91
        # ----------------------------------------------------------------------
        if protocolo == 'E91 (Entrelazamiento)':
            st.subheader("🔬 Protocolo E91 (Bell-CHSH)")
            S_valor, E_vals = fn.calcular_bell_e91(sim, recursos)
            
            c_log, c_graf = st.columns([1.5, 1])
            with c_log:
                # Badge de estado de Eve
                badge_eve = f'<span class="badge badge-warning">🕵️ EVE ACTIVA: RUIDO {nivel_ruido*100:.0f}%</span>' if nivel_ruido > 0 else '<span class="badge badge-success">✅ CANAL LIMPIO</span>'
                st.markdown(badge_eve, unsafe_allow_html=True)

                if S_valor > 2.0:
                    color_s = "#4CAF50" # Verde
                    msg_titulo = "¡CANAL SEGURO!"
                    msg_accion = "Correlación cuántica fuerte. <strong>Es hora de comunicarse.</strong>"
                    icono = "✅"
                else:
                    color_s = "#FF5252" # Rojo
                    msg_titulo = "¡ALERTA DE SEGURIDAD!"
                    msg_accion = "Comportamiento clásico detectado. <strong>No transmitir secretos.</strong>"
                    icono = "🚨"

                # Tabla de Correlaciones
                df_sim = pd.DataFrame({
                    "Configuración": ["00 (A-B)", "01 (A-B)", "10 (A-B)", "11 (A-B)"],
                    "Correlación (E)": [f"{e:.4f}" for e in E_vals]
                })
                st.table(df_sim)
                
                # Tarjeta de resultado S
                st.metric("Valor S (CHSH)", f"{S_valor:.4f}")
                if S_valor > 2.0:
                    st.success(f"### {icono} {msg_titulo}\n{msg_accion}")
                else:
                    st.error(f"### {icono} {msg_titulo}\n{msg_accion}")
            
            with c_graf:
                # Gráfico E91
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.bar(['S'], [S_valor], color=color_s)
                ax.axhline(2.0, color='red', linestyle='--', linewidth=2, label='Clásico (2.0)')
                ax.axhline(2.82, color='blue', linestyle=':', linewidth=2, label='Cuántico (2.82)')
                
                ax.text(0.55, 2.05, 'Clásico', color='red', fontsize=9, fontweight='bold')
                ax.text(0.55, 2.85, 'Cuántico', color='blue', fontsize=9, fontweight='bold')
                ax.bar_label(ax.containers[0], fmt='%.3f', padding=3, fontweight='bold')
                
                ax.set_ylim(0, 3.5); ax.legend(loc='upper left')
                st.pyplot(fig)

        # ----------------------------------------------------------------------
        # LÓGICA PROTOCOLO BB84 (ACTUALIZADO AL ESTILO CONSOLA)
        # ----------------------------------------------------------------------
        elif protocolo == 'BB84 (Polarización)':
            st.subheader("🔐 Protocolo BB84")
            
            # Ejecutamos la lógica
            data = fn.ejecutar_bb84(sim, recursos)
            
            # Función auxiliar para formatear arrays: [0 1 0 1]
            def formato_array(arr, limite=15):
                items = " ".join([str(x) for x in arr[:limite]])
                return f"[{items}...]"

            c_log, c_graf = st.columns([1.8, 1])
            
            with c_log:
                eficiencia = (data['len_clave'] / data['n_bits'] * 100)
                qber = data['qber']

                # 1. ESTADO DEL CANAL (Badge grande)
                if qber == 0:
                    st.success(f"✅ CANAL SEGURO (QBER {qber:.2f}%)")
                    msg_color = "#4CAF50" # Verde
                    msg_accion = "Proceder con la transmisión cifrada."
                elif qber < 11:
                    st.warning(f"⚠️ RUIDO DETECTADO (QBER {qber:.2f}%)")
                    msg_color = "#FFA726" # Naranja
                    msg_accion = "Aplicar corrección de errores y privacidad."
                else:
                    st.error(f"🚨 EVE DETECTADA (QBER {qber:.2f}%)")
                    msg_color = "#F44336" # Rojo
                    msg_accion = "DESCARTAR CLAVE INMEDIATAMENTE."

                # 2. DATOS TRANSMITIDOS (Visualización Alineada tipo Consola)
                st.markdown("### 📨 Datos Transmitidos")
                st.code(f"""
Alice Bits : {formato_array(data['alice_bits'], 20)}
Alice Bases: {formato_array(data['alice_bases'], 20)}
Bob Bases  : {formato_array(data['bob_bases'], 20)}
""", language="text")

                # 3. CRIBADO (Métricas)
                st.markdown("### 🔑 Cribado")
                c1, c2, c3 = st.columns(3)
                c1.metric("Bits Totales", f"{data['n_bits']}")
                c2.metric("Longitud Llave", f"{data['len_clave']}")
                c3.metric("Eficiencia", f"{eficiencia:.1f}%")
                
                # Muestra de la llave
                st.caption("Muestra de la Clave Final (Alice):")
                st.code(formato_array(data['alice_key'], 40), language="text")

                # 4. TARJETA DE ACCIÓN HTML
                st.markdown("---")
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px; border-left: 5px solid {msg_color}; background-color: rgba(255,255,255,0.05);">
                    <h4 style="margin:0; color:{msg_color};">Tasa de Error: {qber:.2f}%</h4>
                    <p style="margin-top:5px; color: #DDD;"><strong>Acción:</strong> {msg_accion}</p>
                </div>
                """, unsafe_allow_html=True)

            # GRÁFICA BB84
            with c_graf:
                fig, ax = plt.subplots(figsize=(4, 5))
                # Color dinámico de la barra
                if qber == 0: color_bar = '#4CAF50' 
                elif qber < 11: color_bar = '#FF9800'
                else: color_bar = '#F44336'
                
                bars = ax.bar(['QBER'], [qber], color=color_bar, width=0.6, edgecolor='black')
                
                # Línea de límite teórico (11%)
                ax.axhline(11, color='red', linestyle='--', linewidth=2)
                ax.text(0.55, 11.5, 'Límite (11%)', color='red', fontsize=10, fontweight='bold')
                
                # Etiqueta
                ax.bar_label(bars, fmt='%.1f%%', padding=3, fontweight='bold', fontsize=12)
                
                ax.set_ylim(0, 50)
                ax.set_ylabel("Error de Bit (%)")
                ax.set_title("Calidad del Canal")
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
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