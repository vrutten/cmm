import numpy as np
from numpy.random import randn, uniform, seed
from scipy.linalg import eigh, svd
from scipy.sparse.linalg import svds
from timeit import timeit

# test parameters
n, k = 2800, 750
n_timing_runs = 10

seed(0)
A = randn(n, k) + 1j * randn(n, k)


def multiply_and_eigh(A):
    M = A.conj().T @ A
    return eigh(M, subset_by_index=[k - 1, k - 1])


def scipy_svds(A):
    _, s, Vh = svds(A, k=1)
    return s ** 2, Vh.conj().T


def full_svd_and_take_first(A):
    _, s, Vh = svd(A, full_matrices=False)
    return s[0] ** 2, Vh[0].conj().reshape(-1, 1)


# code adapted from https://github.com/TheAlgorithms/Python/blob/master/linear_algebra/src/power_iteration.py
# Copyright (c) 2016-2022 TheAlgorithms and contributors
def custom_power_iteration(A):
    error_tol = 1e-12
    max_iterations = 1000
    converged = False
    lambda_previous = 0
    iterations = 0

    v = uniform(size=(A.shape[1],))
    v /= np.linalg.norm(v)
    while not converged:
        w = np.dot(A, v)
        alpha = np.linalg.norm(w)
        v = np.dot(A.conj().T, w)
        beta = np.linalg.norm(v)

        v /= beta
        lambda_ = (beta / alpha) ** 2

        error = np.abs(lambda_ - lambda_previous) / lambda_
        lambda_previous = lambda_
        iterations += 1

        if error <= error_tol or iterations >= max_iterations:
            converged = True

    return lambda_, v.reshape(-1,1)


def unify_sign(vector_map):
    for v in vector_map.values():
        if np.iscomplex(v[0]):
            v *= np.exp(-1j * np.angle(v[0]))
        else:
            v *= np.sign(v[0])
    return vector_map


def print_differing_elements(elements: dict):
    reference_name, reference_val = list(elements.items())[0]
    not_identical = [(name, err) for name, val in elements.items() if (err := np.linalg.norm(reference_val - val)) > 1e-7]
    if not_identical:
        print(f"The following elements differ (reference = '{reference_name})':")
        for name, err in not_identical:
            print(f"\t{name} (error = {err:.2e})")
    else:
        print("\tAll values identical!")


functions = [
    multiply_and_eigh,
    scipy_svds,
    full_svd_and_take_first,
    custom_power_iteration,
]

eigvals = {}
eigvecs = {}
for func in functions:
    s, v = func(A)
    execution = lambda: func(A)
    timer = timeit(stmt=execution, setup=execution, number=n_timing_runs)
    print(f"Function '{func.__name__}' ({n_timing_runs} iterations) took {timer}s.")
    eigvals[func.__name__] = s
    eigvecs[func.__name__] = v

print("\nEigenvalues:")
print_differing_elements(eigvals)

eigvecs = unify_sign(eigvecs)
print("\nEigenvectors:")
print_differing_elements(eigvecs)
