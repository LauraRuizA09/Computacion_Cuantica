import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ==============================================================================
# 1. GESTOR DE SIMULACIÓN Y RUIDO
# ==============================================================================
def obtener_simulador(tipo_escenario, nivel_ruido, protocolo_seleccionado):
    if tipo_escenario == 'Canal Seguro (Ideal)':
        return AerSimulator()
    else:
        modelo_ruido_eve = NoiseModel()
        
        # Lógica de ruido específica
        if 'E91' in protocolo_seleccionado:
            # E91: Ruido en entrelazamiento (CX)
            error = depolarizing_error(nivel_ruido, 2)
            modelo_ruido_eve.add_all_qubit_quantum_error(error, ['cx'])
            
        elif 'BB84' in protocolo_seleccionado:
            # BB84: Ruido en compuertas de 1 qubit (Medición/Preparación)
            error = depolarizing_error(nivel_ruido, 1)
            modelo_ruido_eve.add_all_qubit_quantum_error(error, ['x', 'h', 'measure'])
            
        return AerSimulator(noise_model=modelo_ruido_eve)

# ==============================================================================
# 2. LÓGICA E91 (Test de Bell)
# ==============================================================================
def crear_circuito_chsh(base_alice, base_bob):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1); qc.barrier()
    if base_alice == 1: qc.h(0)
    if base_bob == 0: qc.ry(-np.pi/4, 1)
    elif base_bob == 1: qc.ry(np.pi/4, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def calcular_bell_e91(simulador, shots):
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
    
    S = E_values[0] + E_values[1] + E_values[2] - E_values[3]
    return abs(S), E_values

# ==============================================================================
# 3. LÓGICA BB84 (QKD)
# ==============================================================================
def ejecutar_bb84(simulador, n_bits):
    # 1. Generación
    alice_bits = np.random.randint(2, size=n_bits)
    alice_bases = np.random.randint(2, size=n_bits)
    bob_bases = np.random.randint(2, size=n_bits)
    mensajes_bob = []

    # 2. Transmisión
    for i in range(n_bits):
        qc = QuantumCircuit(1, 1)
        if alice_bits[i] == 1: qc.x(0)
        if alice_bases[i] == 1: qc.h(0)
        qc.barrier()
        if bob_bases[i] == 1: qc.h(0)
        qc.measure(0, 0)

        compiled_qc = transpile(qc, simulador)
        result = simulador.run(compiled_qc, shots=1, memory=True).result()
        mensajes_bob.append(int(result.get_memory()[0]))

    # 3. Cribado
    alice_key = []
    bob_key = []
    for i in range(n_bits):
        if alice_bases[i] == bob_bases[i]:
            alice_key.append(alice_bits[i])
            bob_key.append(mensajes_bob[i])

    # 4. Cálculo de Errores
    errores = 0
    len_clave = len(alice_key)
    for ba, bb in zip(alice_key, bob_key):
        if ba != bb: errores += 1
            
    qber = (errores / len_clave * 100) if len_clave > 0 else 0
    
    # IMPORTANTE: Retornar diccionario para la visualización nueva
    return {
        'n_bits': n_bits,
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'alice_key': alice_key,
        'bob_key': bob_key,
        'qber': qber,
        'len_clave': len_clave
    }

# ==============================================================================
# 4. LÓGICA HARDWARE REAL (IBM)
# ==============================================================================
def conectar_ibm(api_token):
    try:
        service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)
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
    isa_circuits = transpile(circuitos, backend=backend)
    sampler = Sampler(mode=backend)
    job = sampler.run(isa_circuits, shots=shots)
    return job

def procesar_resultados_e91_real(job):
    result = job.result()
    E_values = []
    for i in range(4):
        data = result[i].data
        bit_array = list(data.values())[0]
        counts = bit_array.get_counts()
        total = sum(counts.values())
        P_coinc = (counts.get('00', 0) + counts.get('11', 0)) / total
        P_disc = (counts.get('01', 0) + counts.get('10', 0)) / total
        E_values.append(P_coinc - P_disc)
    S = E_values[0] + E_values[1] + E_values[2] - E_values[3]
    return abs(S), E_values