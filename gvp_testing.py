import numpy as np

def gvp_binarization(X):
    """
    Calcula R según GVP estándar (1 = mejor)
    Devuelve R calculado y B calculado.
    """
    
    X = np.array(X)
    D = len(X)
    # Paso 1 y 2: Calcular R estándar (1=mejor/más alto, D=peor/más bajo)
    sorted_indices = np.argsort(-X)
    R_calc = np.zeros(D, dtype=int)
    R_calc[sorted_indices] = np.arange(1, D + 1)

    # Paso 3: Calcular B usando los R calculados
    
    B_calc_inverted = np.array([
        1 if R_calc[j] > R_calc[(j + 1) % D] else 0
        for j in range(D)
    ], dtype=int)
    return R_calc, B_calc_inverted

# ==============================================================================
# Probando el ejemplo (X, I, B)
# ==============================================================================
print("--- Probando el ejemplo (X, I, B) ---")
print("--- Usando: Lógica Invertida R[j] > R[j+1] ---")

# Datos del último ejemplo proporcionado por el usuario
test_case = {
    "id": "Corrected_Example",
    "X": [6.2, 7.3, 2.4, 7.8, 9.1, 2.5, 6.9, 5],
    "expected_R": [5, 3, 8, 2, 1, 7, 4, 6], # Rangos 'I' proporcionados
    "expected_B": [1, 0, 1, 1, 0, 1, 0, 1]  # Target 'B' proporcionado
}

# Extraer datos del caso de prueba
X_input = np.array(test_case["X"])
expected_R = np.array(test_case["expected_R"])
expected_B = np.array(test_case["expected_B"])

print(f"\n--- Caso de Prueba {test_case['id']} ---")
print(f"Entrada X          = {X_input}")
print(f"Rango Esperado (I) = {expected_R}")
print(f"Binario Esperado (B)= {expected_B}")

# Ejecutar la función: gvp_binarization
calculated_R, calculated_B = gvp_binarization(X_input)

# --- Verificaciones ---

# Verificar R (Rangos)
print(f"\nRango Calculado (GVP Estándar) = {calculated_R}")
r_match = np.array_equal(calculated_R, expected_R)
print(f"¿Rango calculado coincide con Rango esperado (I)? {'Sí' if r_match else 'No'}")

# Verificar B (Binario)
print(f"\nBinario Calculado (con R[j] > R[j+1]) = {calculated_B}")
b_match = np.array_equal(calculated_B, expected_B)

print(f"¿Binario calculado coincide con Binario esperado (B)? {'Sí' if b_match else 'No'}")

# --- Resultado Final ---

print("\nResultado de la Verificación:")
if r_match and b_match:
    print(">>> ¡ÉXITO! La implementación actual (con R[j] > R[j+1]) replica correctamente este ejemplo.")
elif not r_match:
    # Esto no debería pasar en este caso porque ya verificamos que los rangos coinciden
    print(">>> FALLÓ: El cálculo de rangos estándar no coincide con los rangos 'I' proporcionados.")
elif not b_match:
    print(">>> FALLÓ: El binario calculado con la lógica invertida '>' no coincide con el binario 'B' esperado.")

print("\n--- Fin de la Prueba ---")