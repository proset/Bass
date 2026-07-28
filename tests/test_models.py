import numpy as np
import pytest
from models.rk4_solver import bass_classic, integrate_rk4, logistic_diffusion_convergence, ladron_puts_model
from models.fit_models import calculate_mape, r2_score_manual, fit_all_models

def test_ladron_puts_model_limits():
    """Valida la convergencia y límites del modelo Ladrón-de-Guevara & Putsis."""
    # S = 100.0, alpha = 0.03, beta = 0.38
    # Si theta = 0, no hay retardo de red en el mercado potencial (M(t) = S). Debe converger a S.
    val_inf = ladron_puts_model(1000.0, 100.0, 0.03, 0.38, 0.0, 1.0)
    assert abs(val_inf - 100.0) < 0.1

def test_bass_classic_saturation():
    """Valida que a t->inf, la curva de Bass clásica converja al potencial de mercado m."""
    m, p, q = 100.0, 0.03, 0.38
    # En un t muy lejano (ej. 1000 periodos), la adopción acumulada debe estar en m
    val_inf = bass_classic(1000.0, m, p, q)
    assert abs(val_inf - m) < 0.01

def test_rk4_integration_linear():
    """Valida la exactitud del resolvedor RK4 contra una ecuación diferencial lineal analítica."""
    # dy/dt = 2.0 (constante), y(0) = 5.0
    # La solución analítica es y(t) = 2*t + 5
    def f_linear(t, y):
        return 2.0
        
    t_grid = np.array([0, 1, 2, 3, 4, 5])
    y_rk4 = integrate_rk4(f_linear, 5.0, t_grid, steps_per_unit=20)
    y_analitica = 2.0 * t_grid + 5.0
    
    assert np.allclose(y_rk4, y_analitica, atol=1e-5)

def test_logistic_diffusion_convergence_limits():
    """Valida los límites del modelo logístico de convergencia."""
    # b1 (límite superior) = 200, b0 (límite inferior/inicio) = 10
    b1, b0, k2, t0 = 200.0, 10.0, 0.5, 5.0
    
    # En t=t0, el valor debe ser b1 / (1 + (b1-b0)/b0 * 1) = b1 / (b1/b0) = b0
    val_t0 = logistic_diffusion_convergence(t0, b1, b0, k2, t0)
    assert abs(val_t0 - b0) < 1e-5
    
    # En t muy grande, debe converger a b1
    val_inf = logistic_diffusion_convergence(1000.0, b1, b0, k2, t0)
    assert abs(val_inf - b1) < 0.01

def test_mape_and_r2():
    """Valida el cálculo de métricas de precisión."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([11.0, 19.0, 33.0])
    
    mape = calculate_mape(y_true, y_pred)
    # Errores relativos: 10%, 5%, 10% -> media: 8.33%
    assert abs(mape - 8.3333333333333) < 0.01
    
    # Validar R2 score manual contra si mismo
    r2_perfect = r2_score_manual(y_true, y_true)
    assert abs(r2_perfect - 1.0) < 1e-7

def test_dummy_fitting():
    """Prueba que el proceso de ajuste de todos los modelos se ejecuta correctamente con datos válidos."""
    # Generar una serie monótonamente creciente artificial que siga a Bass
    t_data = np.arange(10)
    n_data = bass_classic(t_data, 150.0, 0.02, 0.25)
    
    # Añadir un poco de ruido
    n_data = n_data + np.random.normal(0, 0.5, size=len(n_data))
    # Asegurar que sea acumulativo (creciente)
    for i in range(1, len(n_data)):
        n_data[i] = max(n_data[i], n_data[i-1])
        
    fits = fit_all_models(t_data, n_data)
    
    # Debería haber podido ajustar al menos Bass Clásico con un buen R2
    assert "Bass_Clasico" in fits
    assert fits["Bass_Clasico"]["r_cuadrado"] > 0.8
