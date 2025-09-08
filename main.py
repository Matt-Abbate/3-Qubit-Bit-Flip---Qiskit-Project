# qec_bitflip_demo.py
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.visualization import plot_histogram
import numpy as np
import matplotlib.pyplot as plt

# --- helpers to build circuits ---

def encode_bitflip(msg_qubit_index=0):
    """
    Build a 3-qubit repetition (bit-flip) encoding circuit.
    Input: a single logical qubit is assumed prepared in qubit 0 of a 3-qubit register.
    Output: circuit which copies logical qubit into qubits 1 and 2 via CNOTs.
    """
    qc = QuantumCircuit(3, name="encode")
    # assume state prepared on qubit 0; copy to 1 and 2
    qc.cx(0, 1)
    qc.cx(0, 2)
    return qc

def decode_bitflip():
    """
    The decoding (and simple syndrome extraction via majority) for the 3-qubit bit-flip code.
    We'll decode by performing the same CNOTs and then a Toffoli-style correction isn't required
    for demonstration — instead we'll measure and majority-vote classically.
    """
    qc = QuantumCircuit(3, name="decode")
    # To decode back into qubit 0 we can do CNOTs again (this reverses encode)
    qc.cx(0, 2)
    qc.cx(0, 1)
    return qc

def make_circuit_with_error(state_prep='plus', error_on=1):
    """
    Build a full circuit:
      - prepare logical state on qubit 0 (|0>, |1>, |+> supported)
      - encode to 3 qubits
      - apply X error to one physical qubit (error_on index)
      - decode
      - measure all three physical qubits
    Returns a QuantumCircuit.
    """
    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(3, 'c')
    qc = QuantumCircuit(qr, cr, name="3q_bitflip_demo")

    # --- prepare logical qubit on q[0] ---
    if state_prep == 'zero':
        pass  # default is |0>
    elif state_prep == 'one':
        qc.x(0)
    elif state_prep == 'plus':
        qc.h(0)
    else:
        raise ValueError("state_prep not in ['zero','one','plus']")

    # encode
    qc.append(encode_bitflip().to_instruction(), [0,1,2])

    # inject a bit-flip error (X) on a chosen physical qubit
    qc.x(error_on)

    # decode (reverse of encode)
    qc.append(decode_bitflip().to_instruction(), [0,1,2])

    # measure all physical qubits
    qc.measure([0,1,2], [0,1,2])
    return qc

# --- run demo ---

def run_demo(shots=4096):
    backend = Aer.get_backend('qasm_simulator')

    # Try three logical inputs to see how the code protects them:
    states = ['zero', 'one', 'plus']
    histograms = {}
    for s in states:
        # inject error on physical qubit 1 (middle qubit)
        circ = make_circuit_with_error(state_prep=s, error_on=1)
        job = execute(circ, backend=backend, shots=shots)
        result = job.result()
        counts = result.get_counts()
        # counts keys are strings like 'c2 c1 c0' (bit order may vary)
        histograms[s] = counts

    # plot histograms
    fig, axs = plt.subplots(1, 3, figsize=(12,3))
    for ax, s in zip(axs, states):
        plot_histogram(histograms[s], ax=ax)
        ax.set_title(f"Input |{s}> with X on qubit 1")
    plt.tight_layout()
    plt.show()

    # For the |+> input, measure how often the decoded logical qubit is correct:
    counts_plus = histograms['plus']
    # in this demo, the logical measurement is majority vote of the three measured bits
    def majority_from_key(key):
        bits = [int(b) for b in key[::-1]]  # Qiskit ordering: c0 is lower index -> reverse
        maj = 1 if sum(bits) >= 2 else 0
        return maj

    total = sum(counts_plus.values())
    correct = 0
    for key, n in counts_plus.items():
        # logical |+> is in X-basis; but we measured in Z-basis — so for a proper fidelity
        # we should have prepared |+> and not injected phase flips; here this demonstrates
        # how measurement outcome distribution looks. For simplicity, treat |+> as "superposition"
        # and just show raw counts. (See larger project for fidelity measurement.)
        pass

    print("Raw counts for |+> (Z-basis measurement):")
    print(counts_plus)

if __name__ == "__main__":
    run_demo()