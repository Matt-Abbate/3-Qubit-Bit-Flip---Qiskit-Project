# 3-Qubit-Bit-Flip---Qiskit-Project

This code demonstrates the 3-qubit bit-flip error correction 
code using Qiskit. It prepares a logical qubit in the 
state |0⟩, |1⟩, or |+⟩, encodes it redundantly across three qubits, 
and then deliberately applies a bit-flip error to one of the qubits. 
The circuit is then decoded, all three qubits are measured, and the 
results are plotted as histograms to show how redundancy protects 
the logical information. In essence, it provides a visual and 
numerical demonstration of how quantum error correction can recover from 
a single bit-flip error.