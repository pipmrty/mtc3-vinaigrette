from sage.all import *
import hashlib

def solve_vinaigrette():
    msg = b"Mayonnaise is not an instrument"
    shake = hashlib.shake_256()
    shake.update(msg)
    hash_bytes = shake.digest(38)
    bit_string = ''.join(f'{b:08b}' for b in hash_bytes)
    target_vals = [int(bit_string[i*5 : (i+1)*5], 2) % 31 for i in range(60)]

    F = GF(31)
    T = vector(F, target_vals)
    n = 62
    m = 60
    k = 10

    print("[*] target vector built")

    # read the public key
    elements_per_matrix = (n * (n + 1)) // 2

    with open('public-key.txt', 'r') as f:
        data = f.read().split()

    assert len(data) == m * elements_per_matrix, "public key has the wrong size!"

    matrices = []
    idx = 0
    for _ in range(m):
        M = Matrix(F, n, n)
        for i in range(n):
            for j in range(i, n):
                M[i, j] = F(int(data[idx]))
                idx += 1
        matrices.append(M)

    print("[*] loaded 60 public key matrices")

    # linearization attack
    lams = [5, 2, 1, 1, 0, 0, 0, 0, 0, 0]

    # pick random v_i, retry until the system is solvable
    while True:
        V = [vector(F, [F.random_element() for _ in range(n)]) for _ in range(k)]

        # v = sum(lambda_i * v_i)
        v_sum = sum(lams[i] * V[i] for i in range(k))

        M_rows = []
        C_elements = []

        for j in range(m):
            P = matrices[j]
            # polar form of the quadratic form: A = P + P^T
            A = P + P.transpose()

            # row j of the linear system
            row = v_sum * A
            M_rows.append(row)

            # constant term (target minus the quadratic part from the v_i)
            c_j = T[j] - sum(V[i] * P * V[i] for i in range(k))
            C_elements.append(c_j)

        M_mat = matrix(F, M_rows)
        C_vec = vector(F, C_elements)

        try:
            # solve Mx = C
            x = M_mat.solve_right(C_vec)
            print("[+] linear system solved")
            break
        except ValueError:
            # random v_i gave a bad matrix (not enough rank), try again
            continue

    # build the signature
    signature = []
    for i in range(k):
        s_i = V[i] + lams[i] * x
        signature.extend(list(s_i))

    # output as space-separated numbers
    sig_str = " ".join(str(val) for val in signature)

    print("\n[+] VALID SIGNATURE FOUND (length: 620 numbers):")
    print(sig_str)

    with open("signature.txt", "w") as f:
        f.write(sig_str)
    print("\n[*] signature saved to 'signature.txt'")

# run it
solve_vinaigrette()
