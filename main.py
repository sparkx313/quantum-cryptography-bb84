import numpy as np
from typing import Tuple, List

class BB84Simulator:
    def __init__(self, n_bits: int = 1000, eve_present: bool = False):
        self.n_bits = n_bits
        self.eve_present = eve_present

    def prepare_qubits(self) -> Tuple[List[int], List[int]]:
        bits = np.random.randint(0, 2, self.n_bits).tolist()
        bases = np.random.randint(0, 2, self.n_bits).tolist()  # 0=Z, 1=X
        return bits, bases

    def measure_qubits(self, bits, alice_bases, bob_bases) -> List[int]:
        results = []
        for i in range(self.n_bits):
            if alice_bases[i] == bob_bases[i]:
                results.append(bits[i])
            else:
                results.append(np.random.randint(0, 2))
        return results

    def eve_intercept(self, bits, alice_bases) -> Tuple[List[int], List[int]]:
        eve_bases = np.random.randint(0, 2, self.n_bits).tolist()
        intercepted = []
        for i in range(self.n_bits):
            if alice_bases[i] == eve_bases[i]:
                intercepted.append(bits[i])
            else:
                intercepted.append(np.random.randint(0, 2))
        return intercepted, eve_bases

    def sift_keys(self, alice_bases, bob_bases, alice_bits, bob_bits):
        alice_key, bob_key, indices = [], [], []
        for i in range(self.n_bits):
            if alice_bases[i] == bob_bases[i]:
                alice_key.append(alice_bits[i])
                bob_key.append(bob_bits[i])
                indices.append(i)
        return alice_key, bob_key, indices

    def estimate_qber(self, alice_key, bob_key, sample_size: int = 100) -> float:
        sample = np.random.choice(len(alice_key), min(sample_size, len(alice_key)), replace=False)
        errors = sum(1 for i in sample if alice_key[i] != bob_key[i])
        return errors / len(sample)

    def run(self):
        alice_bits, alice_bases = self.prepare_qubits()
        transmitted_bits = alice_bits[:]

        if self.eve_present:
            transmitted_bits, eve_bases = self.eve_intercept(alice_bits, alice_bases)
            print("[!] Eve is intercepting the channel!")

        bob_bases = np.random.randint(0, 2, self.n_bits).tolist()
        bob_bits = self.measure_qubits(transmitted_bits, alice_bases, bob_bases)
        alice_key, bob_key, _ = self.sift_keys(alice_bases, bob_bases, alice_bits, bob_bits)
        qber = self.estimate_qber(alice_key, bob_key)

        print(f"Sifted key length : {len(alice_key)} bits")
        print(f"QBER              : {qber:.2%}")
        print(f"Eve detected      : {'YES ⚠️' if qber > 0.11 else 'NO ✅'}")
        return alice_key, bob_key, qber

if __name__ == "__main__":
    print("=== BB84 without Eve ===")
    BB84Simulator(n_bits=2000, eve_present=False).run()
    print()
    print("=== BB84 with Eve ===")
    BB84Simulator(n_bits=2000, eve_present=True).run()
