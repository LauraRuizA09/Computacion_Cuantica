import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==============================================================================
#                    Generar el ruido segun el protocolo
# ==============================================================================

def obtener_simulador(tipo_escenario, nivel_ruido, protocolo_seleccionado):

    if tipo_escenario == 'Canal Seguro (Ideal)':
        return AerSimulator()
    else:
        modelo_ruido_eve = NoiseModel()
        
        if 'E91' in protocolo_seleccionado:
            # E91: Ruido en entrelazamiento (CX) esto se agrega en esa compuerta debido a que aqui es donde
            # se entrelazan los fotones enotnces introducimos ruido de tal amnera que hacemos que el entrelazamiento
            # no se perfecto y como es el puente de comunicacion si este se daña o tiene ruido se rompe la comunicación

            error = depolarizing_error(nivel_ruido, 2)
            modelo_ruido_eve.add_all_qubit_quantum_error(error, ['cx'])
            
        elif 'BB84' in protocolo_seleccionado:
            # BB84: Ruido en compuertas de 1 qubit (Medición/Preparación) aplicamos ruido en las compuertas x, h y medicion
            # por que en x y h se prepara el foton y bob usa h y medicion para leerlo y si se prpeara de una manera y se mide de otra
            # estamos colapsando la funcion de onda de una manera haciendo que estemos en el modo clasico.

            error = depolarizing_error(nivel_ruido, 1)
            modelo_ruido_eve.add_all_qubit_quantum_error(error, ['x', 'h', 'measure'])
            
        return AerSimulator(noise_model=modelo_ruido_eve)

# ==============================================================================
#                          Protocolo E91
# ==============================================================================


# ===================================================================
#           Configuración de la Prueba CHSH (Protocolo E91)
# ===================================================================     

def crear_circuito_chsh(base_alice, base_bob):

    #Crea un circuito CHSH basado en las elecciones de base de Alice y Bob.
    qc = QuantumCircuit(2, 2)

    # Alice y Bob comparten un par entrelazado |Phi+>
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()

    # ELECCIÓN DE BASES (Rotaciones antes de medir)
    
    # Rotaciones de Alice
    if base_alice == 1: qc.h(0)

    # Rotaciones de Bob (Para maximizar la violación CHSH)
    # Rota a pi/8 (Base W)
    if base_bob == 0: qc.ry(-np.pi/4, 1)
    # Rota a -pi/8 (Base V)
    elif base_bob == 1: qc.ry(np.pi/4, 1)

    #Medicion
    qc.measure([0, 1], [0, 1])

    return qc

def calcular_bell_e91(simulador, shots):

    # Definimos las 4 combinaciones de bases posibles para calcular S
    # (A1, B1), (A1, B2), (A2, B1), (A2, B2)

    # Pares (Alice, Bob)
    combinaciones = [(0, 0), (0, 1), (1, 0), (1, 1)]

    circuitos = [crear_circuito_chsh(a, b) for a, b in combinaciones]
    circuitos_compilados = transpile(circuitos, simulador)
    job = simulador.run(circuitos_compilados, shots=shots)
    res = job.result()
    
    E_values = []

    for i in range(4):
        counts = res.get_counts(i)
        total = sum(counts.values())
        P_coinc = (counts.get('00', 0) + counts.get('11', 0)) / total
        P_disc = (counts.get('01', 0) + counts.get('10', 0)) / total
        E_values.append(P_coinc - P_disc)
    
    # Fórmula CHSH: S = E(A0,B0) - E(A0,B1) + E(A1,B0) + E(A1,B1)
    # Nota: El signo menos puede variar según la definición exacta de los ángulos,
    # pero buscamos la magnitud |S|

    S = E_values[0] + E_values[1] + E_values[2] - E_values[3]

    return abs(S), E_values

# ==============================================================================
#                               Protocolo BB84
# ==============================================================================

def ejecutar_bb84(simulador, n_bits):

    # Alice genera los bits que quiere enviar (0 o 1) de forma aleatoria.
    alice_bits = np.random.randint(2, size=n_bits)

    # Alice elige aleatoriamente la base para codificar cada bit:
    # 0 = Base Rectilínea/Z (+): Estados |0> y |1>
    # 1 = Base Diagonal/X (x): Estados |+> y |->
    alice_bases = np.random.randint(2, size=n_bits)

    # Bob elige aleatoriamente en qué base va a medir los fotones que reciba.
    bob_bases = np.random.randint(2, size=n_bits)

    # Aquí guardaremos lo que Bob mide
    mensajes_bob = []

    # Transmisión
    circuitos = []
    
    for i in range(n_bits):

        # Un circuito por cada fotón individual
        qc = QuantumCircuit(1, 1)

        # Si el bit es 1, aplicamos la compuerta X para cambiar de |0>
        if alice_bits[i] == 1: qc.x(0)

        # Si la base es 1 (Diagonal), aplicamos Hadamard (H).
        # Esto pone el qubit en superposición (|0> -> |+>, |1> -> |->)
        if alice_bases[i] == 1: qc.h(0)

        # La barrera representa el medio físico (fibra óptica/aire). 
        # Aquí es donde el simulador inyectará ruido si "Eve" está activada
        qc.barrier()

        # Si Bob elige medir en base Diagonal (1), debe aplicar H antes de medir
        # para rotar la base de medición de vuelta al eje Z estándar
        if bob_bases[i] == 1: qc.h(0)

        # Bob realiza la medición final, colapsando el estado a 0 o 1
        qc.measure(0, 0)
        circuitos.append(qc)

    # Ejecutamos todos los circuitos en lote para mayor eficiencia.
    # shots=1 simula que es un solo fotón el que se envía y mide
    compiled_qc = transpile(circuitos, simulador)
    job = simulador.run(compiled_qc, shots=1, memory=True)
    res = job.result()

    # Extraemos los bits medidos por Bob de la memoria del simulador.
    for i in range(n_bits):
        bit_medido = int(res.get_memory(i)[0])
        mensajes_bob.append(bit_medido)

    # Comparación de Bases
    alice_key = []
    bob_key = []

    # Alice y Bob comparan públicamente sus bases (NO sus bits).
    # Solo conservan los bits donde usaron la misma base, ya que ahí la física
    # garantiza una correlación perfecta (en ausencia de ruido)
    for i in range(n_bits):
        if alice_bases[i] == bob_bases[i]:
            alice_key.append(alice_bits[i])
            bob_key.append(mensajes_bob[i])

    # Cálculo de Errores
    errores = 0
    len_clave = len(alice_key)

    # Comparamos las claves resultantes para detectar discrepancias.
    # Si Eve intentó interceptar, el QBER aumentará significativamente
    for ba, bb in zip(alice_key, bob_key):
        if ba != bb: errores += 1
            
    # Quantum Bit Error Rate en porcentaje.
    qber = (errores / len_clave * 100) if len_clave > 0 else 0
    
    return {
        'n_bits': n_bits, 'alice_bits': alice_bits, 'alice_bases': alice_bases,
        'bob_bases': bob_bases, 'alice_key': alice_key, 'bob_key': bob_key,
        'qber': qber, 'len_clave': len_clave
    }

# ==============================================================================
#               Conexion al computador cuantico de IBM
# ==============================================================================

def conectar_ibm(api_token):
    try:
        # CORRECCIÓN AQUÍ: channel="ibm_quantum_platform"
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_token)
        return service, None
    except Exception as e:
        return None, str(e)

def obtener_backends_ibm(service):
    if not service: return []
    backends = service.backends(simulator=False, operational=True)
    return sorted(backends, key=lambda b: b.status().pending_jobs)

def ejecutar_e91_real(backend, shots):
    combinaciones = [(0, 0), (0, 1), (1, 0), (1, 1)]
    circuitos = [crear_circuito_chsh(a, b) for a, b in combinaciones]
    
    # Transpilación optimizada para hardware
    isa_circuits = transpile(circuitos, backend=backend)
    
    # Ejecución con SamplerV2
    sampler = Sampler(mode=backend)
    job = sampler.run(isa_circuits, shots=shots)
    return job

def procesar_resultados_e91_real(job):
    result = job.result()
    E_values = []
    for i in range(4):
        # Extracción de datos compatible con SamplerV2
        data = result[i].data
        # Usualmente el registro clásico se llama 'c' o 'meas'
        # Tomamos el primer registro disponible dinámicamente
        bit_array = list(data.values())[0]
        counts = bit_array.get_counts()
        
        total = sum(counts.values())
        P_coinc = (counts.get('00', 0) + counts.get('11', 0)) / total
        P_disc = (counts.get('01', 0) + counts.get('10', 0)) / total
        E_values.append(P_coinc - P_disc)
        
    S = E_values[0] + E_values[1] + E_values[2] - E_values[3]
    return abs(S), E_values