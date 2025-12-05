import sys
import os

# Agrega la carpeta donde está este archivo al sistema de búsqueda de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import matplotlib.pyplot as plt
import Funciones as bq  # Ahora sí debería encontrarlo

# ==========================================
# CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(page_title="Ciberseguridad Cuántica", page_icon="⚛️", layout="wide")

st.title("🛡️ Proyecto: Ciberseguridad Cuántica")
st.markdown("""
**Simulación y Análisis de Detección de Espionaje mediante Protocolos E91 y BB84** Este aplicativo permite explorar la intersección entre la mecánica cuántica (no-localidad) y la ciberseguridad[cite: 10].
""")

# ==========================================
# MENÚ LATERAL (INPUTS)
# ==========================================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selección de Protocolo
    protocolo = st.selectbox(
        "Seleccione Protocolo:",
        ('E91 (Entrelazamiento)', 'BB84 (Polarización)', 'COMPARACIÓN (Ambos)')
    )
    
    # Selección de Escenario (Ideal vs Inseguro)
    escenario = st.selectbox(
        "Estado del Canal:",
        ('Canal Seguro (Ideal)', 'Canal Inseguro (Espía/Ruido)')
    )
    
    # Configuración de Ruido (Solo si es inseguro)
    ruido = 0.0
    if escenario == 'Canal Inseguro (Espía/Ruido)':
        st.warning("⚠️ Eve (la espía) está activa.")
        st.markdown("_El ruido simula la decoherencia o interceptación [cite: 20]_")
        ruido = st.slider("Nivel de Interceptación:", 0.0, 1.0, 0.2, 0.05)
    
    # Recursos
    recursos = st.slider("Cantidad de Qubits/Fotones:", 100, 5000, 1000, 100)
    
    btn_correr = st.button("🚀 Ejecutar Simulación", type="primary")

# ==========================================
# LÓGICA DE EJECUCIÓN
# ==========================================
if btn_correr:
    # 1. Llamamos a la función del backend para obtener el simulador configurado
    sim = bq.obtener_simulador(escenario, ruido)
    
    col1, col2 = st.columns(2)
    
    # --- ANÁLISIS E91 ---
    if protocolo == 'E91 (Entrelazamiento)' or protocolo == 'COMPARACIÓN (Ambos)':
        # Llamamos a la lógica matemática del backend
        val_S = bq.calcular_valor_S(sim, recursos)
        
        with col1:
            st.subheader("🔬 Protocolo E91 (Test de Bell)")
            st.metric(label="Valor S (Correlación)", value=f"{val_S:.4f}")
            
            # Visualización Gráfica
            fig, ax = plt.subplots(figsize=(6,1.5))
            # Si S > 2, es cuántico (verde). Si S <= 2, es clásico/interceptado (rojo) [cite: 16]
            color_barra = '#4CAF50' if val_S > 2.0 else '#FF5252'
            
            ax.barh([0], [val_S], color=color_barra)
            ax.set_xlim(0, 3)
            ax.axvline(2.0, color='black', linestyle='--', label='Límite Clásico (2.0)')
            ax.axvline(2.82, color='blue', linestyle=':', label='Límite Cuántico (2.82)')
            ax.set_yticks([])
            ax.set_title("Violación de Desigualdad CHSH")
            ax.legend(loc='upper right', fontsize='x-small')
            st.pyplot(fig)

            if val_S > 2.0:
                st.success("✅ **CANAL SEGURO:** Se mantienen las correlaciones cuánticas (S > 2).")
            else:
                st.error("🚨 **INTRUSIÓN DETECTADA:** El entrelazamiento ha colapsado (S ≤ 2).")

    # --- ANÁLISIS BB84 ---
    if protocolo == 'BB84 (Polarización)' or protocolo == 'COMPARACIÓN (Ambos)':
        # Llamamos a la lógica matemática del backend
        qber, bits_utiles, muestra_clave = bq.ejecutar_bb84(sim, recursos)
        
        target_col = col2 if protocolo == 'COMPARACIÓN (Ambos)' else col1
        
        with target_col:
            st.subheader("🔐 Protocolo BB84")
            st.metric(label="QBER (Tasa de Error)", value=f"{qber:.2f}%")
            st.caption(f"Bits generados para la clave: {bits_utiles}")
            
            # Visualización Gráfica
            fig2, ax2 = plt.subplots(figsize=(6,2))
            colores = ['#FF5252' if qber > 11 else '#4CAF50', 'lightgray']
            ax2.bar(['Error', 'Correctos'], [qber, 100-qber], color=colores)
            ax2.set_ylim(0, 100)
            ax2.set_ylabel("Porcentaje (%)")
            ax2.set_title("Calidad de la Transmisión")
            st.pyplot(fig2)

            if qber < 11: # Umbral teórico aproximado para seguridad
                st.success("✅ **CANAL SEGURO:** QBER bajo. Se puede destilar una clave.")
            else:
                st.error("🚨 **INTRUSIÓN DETECTADA:** QBER alto. Eve ha alterado los estados al medir.")

    # --- COMPARACIÓN ---
    if protocolo == 'COMPARACIÓN (Ambos)':
        st.divider()
        st.markdown("### 📊 Conclusiones del Estudio")
        st.info("""
        * **E91:** Detecta al espía mediante la **física fundamental** (violación de desigualdades de Bell). Es inherentemente seguro si $S > 2$.
        * **BB84:** Detecta al espía mediante **estadística** (tasa de error QBER). Requiere comparar un subconjunto de la clave.
        """)

else:
    st.info("👈 Seleccione los parámetros en el menú lateral y presione 'Ejecutar Simulación'.")