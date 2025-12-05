import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# ==============================================================================
#                     GESTOR DE RUIDO Y SIMULACIÓN
# ==============================================================================

def obtener_simulador(tipo_escenario, nivel_ruido=0.0):

    if tipo_escenario == 'Canal Seguro (Ideal)':
        # Simulación ideal, se espera violación máxima de Bell (S ~ 2.82) [cite: 19]
        return AerSimulator()
    else:
        # Canal inseguro: La perturbación de Eve destruye el entrelazamiento [cite: 21]
        noise_model = NoiseModel()
        
        # Error en 1 qubit (Afecta bases de BB84)
        error_1q = depolarizing_error(nivel_ruido, 1)
        # Error en 2 qubits (Afecta la compuerta CX del entrelazamiento E91)
        error_2q = depolarizing_error(nivel_ruido, 2)
        
        noise_model.add_all_qubit_quantum_error(error_1q, ['x', 'h', 'measure', 'ry'])
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
        
        return AerSimulator(noise_model=noise_model)

# ==============================================================================
#              PROTOCOLO E91 (Desigualdad de Bell - CHSH)
# ==============================================================================

def circuito_chsh_e91(base_alice, base_bob):

    qc = QuantumCircuit(2, 2)
    
    # Generación de entrelazamiento (Estado de Bell)
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    
    # Configuración de Bases para el Test de Bell
    if base_alice == 1: 
        qc.h(0) 
    
    # Rotaciones de Bob para maximizar violación CHSH
    if base_bob == 0: 
        qc.ry(-np.pi/4, 1)
    elif base_bob == 1: 
        qc.ry(np.pi/4, 1)
        
    qc.measure([0, 1], [0, 1])
    return qc

def calcular_valor_S(simulador, shots):

    combinaciones = [(0, 0), (0, 1), (1, 0), (1, 1)]
    circuitos = [circuito_chsh_e91(a, b) for a, b in combinaciones]
    
    job = simulador.run(transpile(circuitos, simulador), shots=shots)
    res = job.result()
    
    E_values = []
    for i in range(4):
        counts = res.get_counts(i)
        total = sum(counts.values())
        P00 = counts.get('00', 0) / total
        P11 = counts.get('11', 0) / total
        P01 = counts.get('01', 0) / total
        P10 = counts.get('10', 0) / total
        
        # Correlación: (Coincidencias) - (Discrepancias)
        E = (P00 + P11) - (P01 + P10)
        E_values.append(E)
    
    # Fórmula CHSH
    S = E_values[0] + E_values[1] + E_values[2] - E_values[3]
    return abs(S)

# ==============================================================================
#                       PROTOCOLO BB84 (Polarización)
# ==============================================================================

def ejecutar_bb84(simulador, n_bits):

    alice_bits = np.random.randint(2, size=n_bits)
    alice_bases = np.random.randint(2, size=n_bits)
    bob_bases = np.random.randint(2, size=n_bits)
    
    circuitos = []
    for i in range(n_bits):
        qc = QuantumCircuit(1, 1)
        
        # Preparación Alice
        if alice_bits[i] == 1: qc.x(0)
        if alice_bases[i] == 1: qc.h(0)
        
        qc.barrier() # Canal susceptible a ruido
        
        # Medición Bob
        if bob_bases[i] == 1: qc.h(0)
        qc.measure(0, 0)
        circuitos.append(qc)
        
    job = simulador.run(transpile(circuitos, simulador), shots=1, memory=True)
    memorias = job.result().get_memory()
    
    errores = 0
    coincidencias = 0
    
    # Proceso de Cribado (Sifting)
    bits_clave_final = []
    for i in range(n_bits):
        if alice_bases[i] == bob_bases[i]:
            bit_medido = int(memorias[i][0])
            coincidencias += 1
            bits_clave_final.append(bit_medido)
            if bit_medido != alice_bits[i]:
                errores += 1
                
    qber = (errores / coincidencias * 100) if coincidencias > 0 else 0
    return qber, coincidencias, bits_clave_final