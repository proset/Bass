import os
import re
import tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from fpdf import FPDF
from data.loaders import load_historical_data, load_model_parameters, load_qualitative_analysis, load_consenso_forecast
from models.rk4_solver import (
    bass_classic,
    dual_market_bass,
    fourt_woodlock_model,
    gompertz_model,
    generalized_bass_model,
    horsky_simon_model,
    muller_yogev_model,
    vdb_joshi_model,
    logistic_diffusion_convergence,
    ladron_puts_model
)
from models.fit_models import rank_and_select_best_model
from ui.tab_projections import extract_consensus_anchor_points, build_consensus_curve_from_anchors, compute_weighted_consensus_projection

class UnifiedReportPDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Informe Global de Adopcion Tecnologica y Benchmarking Cientifico", border=0, align="R")
        self.ln(12)
        
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Pagina {self.page_no()}", border=0, align="C")

def calculate_mape(y_true, y_pred):
    mask = y_true > 0
    if not np.any(mask):
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0

def reconstruct_popt(m_key, p):
    try:
        if m_key == "Bass_Clasico":
            return [p["param_m1"], p["param_p1"], p["param_q1"]]
        elif m_key == "Dual_Market":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"]]
        elif m_key == "Fourt_Woodlock":
            return [p["param_m1"], p["param_p1"]]
        elif m_key == "Gompertz":
            return [p["param_m1"], p["param_p1"], p["param_q1"]]
        elif m_key == "Generalized_Bass":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"]]
        elif m_key == "Horsky_Simon":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"]]
        elif m_key == "Muller_Yogev":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"]]
        elif m_key == "VdB_Joshi":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"]]
        elif m_key == "Logistic_Diffusion_Convergence":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"]]
        elif m_key == "Ladron_Putsis":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"]]
    except Exception:
        pass
    return None

def clean_latex_formulas(text):
    if not text:
        return ""
    # 1. Resolver fracciones \frac{a}{b} -> (a) / (b) con soporte de llaves anidadas
    pattern_frac = r'\\frac\s*\{((?:[^{}]+|\{[^{}]*\})+)\}\s*\{((?:[^{}]+|\{[^{}]*\})+)\}'
    for _ in range(3):
        text = re.sub(pattern_frac, r'(\1) / (\2)', text)
        
    # 2. Reemplazos de comandos LaTeX comunes
    latex_replacements = [
        (r'\\tilde\{\\gamma\}', 'gamma_tilde'),
        (r'\\hat\{\\gamma\}', 'gamma_hat'),
        (r'\\alpha', 'alpha'),
        (r'\\beta', 'beta'),
        (r'\\gamma', 'gamma'),
        (r'\\theta', 'theta'),
        (r'\\omega', 'w'),
        (r'\\exp', 'exp'),
        (r'\\neq', '!='),
        (r'\\left\s*\[', '['),
        (r'\\right\s*\]', ']'),
        (r'\\left\s*\(', '('),
        (r'\\right\s*\)', ')'),
        (r'\\cdot', '*'),
        (r'\\times', '*'),
        (r'\\approx', '~='),
        (r'\\infty', 'inf'),
        (r'\\sum_\{([^}]+)\}', r'Sum_\1'),
        (r'\\sum', 'Sum'),
        (r'\\frac', ' / '), # Fallback para fracciones no capturadas por el regex
        (r'\\', ''),
        (r'\{', '('),
        (r'\}', ')'),
        (r'\$\$', ''),
        (r'\$', '')
    ]
    for pattern, rep in latex_replacements:
        text = re.sub(pattern, rep, text)
    return text.strip()

def clean_txt_only(text):
    if not text:
        return ""
    text = text.replace("`", "")
    text = text.replace("\r", "")
    text = re.sub(r'```[\s\S]*?```', '', text)
    replacements = {
        "—": "-", "–": "-", "“": '"', "”": '"', "‘": "'", "’": "'",
        "™": "(TM)", "®": "(R)", "©": "(C)"
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    try:
        text = text.encode("latin-1", errors="ignore").decode("latin-1")
    except Exception:
        pass
    return text

def clean_txt(text):
    if not text:
        return "No disponible."
    text = clean_latex_formulas(text)
    text = clean_txt_only(text)
    return text

def render_latex_to_temp_png(latex_str):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp_file.name
    tmp_file.close()
    
    from matplotlib import mathtext
    # math_to_image produce una imagen ajustada exactamente a la fórmula, sin padding excesivo
    mathtext.math_to_image('$' + latex_str + '$', path, dpi=300, format='png')
    
    # Añadir fondo blanco puro con PIL para asegurar compatibilidad con FPDF
    with Image.open(path) as img:
        img_rgba = img.convert("RGBA")
        background = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
        alpha_composite = Image.alpha_composite(background, img_rgba)
        rgb_img = alpha_composite.convert("RGB")
        rgb_img.save(path, 'PNG')
        
    return path

def print_bold_text(pdf, text):
    # Ya no se usa directamente por el nuevo parser lineal
    pass

def print_line_with_math_images(pdf, line):
    import re
    # Forzar espacios alrededor de fórmulas matemáticas si el texto original venía pegado
    line = re.sub(r'([^\s])\$', r'\1 $', line)
    line = re.sub(r'\$([^\s])', r'$ \1', line)
    
    # Unificar delimitadores de fórmulas
    line = line.replace("$$", "$")
    
    tokens = re.split(r'(\$[^$]+\$|\*\*)', line)
    is_bold = False
    
    for token in tokens:
        if not token:
            continue
            
        if token == '**':
            is_bold = not is_bold
        elif token.startswith('$') and token.endswith('$') and len(token) >= 2:
            latex_formula = token[1:-1].strip()
            if latex_formula:
                try:
                    img_path = render_latex_to_temp_png(latex_formula)
                    with Image.open(img_path) as img:
                        w_px, h_px = img.size
                    # Escala constante para alinear el tamaño del texto mathtext (~12pt) al texto del documento (9.5pt)
                    img_h = h_px * 0.07
                    img_w = w_px * 0.07
                    
                    avail_w = pdf.w - pdf.r_margin - pdf.get_x()
                    if img_w + 1.5 > avail_w:
                        pdf.ln(4.8)
                        
                    x = pdf.get_x() + 1.5
                    # Centrar verticalmente aproximado con respecto a la línea de texto
                    y = pdf.get_y() + (4.8 - img_h) / 2.0
                    pdf.image(img_path, x=x, y=y, w=img_w, h=img_h)
                    pdf.set_x(x + img_w + 1.5)
                    import os
                    os.remove(img_path)
                except Exception:
                    pdf.set_font("helvetica", "I", 9.5)
                    pdf.set_x(pdf.get_x() + 1.5)
                    pdf.write(4.8, clean_latex_formulas(latex_formula))
                    pdf.set_x(pdf.get_x() + 1.5)
        else:
            if is_bold:
                pdf.set_font("helvetica", "B", 9)
            else:
                pdf.set_font("helvetica", "", 9)
            pdf.write(4.8, clean_txt_only(token))

def print_paragraph_with_formulas(pdf, text):
    if not text:
        return
        
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2.5) # Salto de línea entre párrafos
            continue
            
        # Detectar cabeceras para convertirlas en subapartados numerados
        header_match = re.match(r'^(#{1,4})\s+', line)
        if header_match:
            prefix_len = len(header_match.group(0))
            pdf.subsection_counter = getattr(pdf, "subsection_counter", 0) + 1
            section_num = getattr(pdf, "current_section", 0)
            
            clean_title = line[prefix_len:].replace("**", "").strip()
            clean_title = re.sub(r'^[\d\.\-]+\s+', '', clean_title) # Quitar numeracion previa manual si la hay
            clean_title = clean_txt_only(clean_title)
            
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(30, 64, 175) # Blue 800
            if section_num > 0:
                pdf.write(5, f"{section_num}.{pdf.subsection_counter} {clean_title}")
            else:
                pdf.write(5, f"{clean_title}")
            pdf.set_text_color(50, 50, 50)
            pdf.ln(6)
            continue
            
        # Detectar ecuaciones bloque $$ ... $$
        if line.startswith("$$") and line.endswith("$$"):
            latex_formula = line[2:-2].strip()
            if latex_formula:
                try:
                    img_path = render_latex_to_temp_png(latex_formula)
                    
                    with Image.open(img_path) as img:
                        w_px, h_px = img.size
                    
                    # Para ecuaciones bloque, las hacemos ligeramente más grandes
                    img_h = h_px * 0.085
                    img_w = w_px * 0.085
                    
                    avail_w = pdf.epw
                    img_w = min(img_w, avail_w)
                    
                    pdf.ln(2)
                    x_pos = pdf.l_margin + (avail_w - img_w) / 2
                    pdf.image(img_path, x=x_pos, w=img_w, h=img_h)
                    pdf.ln(2)
                    
                    os.remove(img_path)
                except Exception:
                    # Fallback a texto si falla el renderizado
                    pdf.set_font("helvetica", "I", 9.5)
                    pdf.write(4.8, f" {clean_latex_formulas(latex_formula)} ")
                    pdf.ln(4.8)
            continue
            
        # Detectar si es viñeta
        is_bullet = False
        if line.startswith("- ") or line.startswith("* "):
            is_bullet = True
            line = line[2:]
            
        if is_bullet:
            pdf.set_x(pdf.l_margin + 5)
            pdf.set_font("helvetica", "B", 9)
            pdf.write(4.8, chr(149) + " ") # Dibujar punto de viñeta •
            
        print_line_with_math_images(pdf, line)
        pdf.ln(4.8)

def draw_section_header(pdf, title_text):
    # Extraer numero de seccion para subsecciones
    match = re.match(r"^(\d+)\.", title_text)
    if match:
        pdf.current_section = int(match.group(1))
        pdf.subsection_counter = 0

    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(37, 99, 235) # Blue 600
    pdf.cell(0, 8, f"   {title_text}", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_text_color(50, 50, 50)

def generate_diffusion_plot(tech, df_hist, params, output_path, models_to_plot=None):
    anios_reales = df_hist["anio"].values
    ultimo_anio = int(anios_reales[-1])
    y_true = df_hist["adopcion_acumulada"].values
    
    anios_totales = list(anios_reales) + list(range(ultimo_anio + 1, ultimo_anio + 11))
    t_totales = np.arange(len(anios_totales))
    
    fig = plt.figure(figsize=(8, 4.2))
    plt.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
    plt.gca().set_facecolor("#f8fafc")
    
    plt.scatter(anios_reales, y_true, color="#0f172a", s=50, zorder=5, label="Datos Reales")
    
    colors = {
        "Bass_Clasico": "#3b82f6",
        "Dual_Market": "#ef4444",
        "Tanny_Derzko": "#10b981",
        "Steffens_Murthy": "#f59e0b",
        "Muller_Yogev": "#8b5cf6",
        "VdB_Joshi": "#ec4899",
        "Logistic_Diffusion_Convergence": "#06b6d4",
        "Ladron_Putsis": "#14b8a6"
    }
    
    model_labels = {
        "Bass_Clasico": "Bass Clasico",
        "Dual_Market": "Dual Market",
        "Fourt_Woodlock": "Fourt & Woodlock",
        "Gompertz": "Gompertz",
        "Generalized_Bass": "Generalized Bass",
        "Horsky_Simon": "Horsky & Simon",
        "Muller_Yogev": "Muller & Yogev",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Logistico R&K",
        "Ladron_Putsis": "Ladron-de-Guevara & Putsis"
    }
    
    model_funcs = {
        "Bass_Clasico": bass_classic,
        "Dual_Market": dual_market_bass,
        "Fourt_Woodlock": fourt_woodlock_model,
        "Gompertz": gompertz_model,
        "Generalized_Bass": generalized_bass_model,
        "Horsky_Simon": horsky_simon_model,
        "Muller_Yogev": muller_yogev_model,
        "VdB_Joshi": vdb_joshi_model,
        "Logistic_Diffusion_Convergence": logistic_diffusion_convergence,
        "Ladron_Putsis": ladron_puts_model
    }
    
    for m_key, color in colors.items():
        if m_key not in params:
            continue
        if models_to_plot is not None and m_key not in models_to_plot:
            continue
        p = params[m_key]
        popt = reconstruct_popt(m_key, p)
        if not popt:
            continue
        func = model_funcs[m_key]
        y_pred = func(t_totales, *popt)
        
        idx_hist_end = len(anios_reales) - 1
        plt.plot(anios_totales[:idx_hist_end+1], y_pred[:idx_hist_end+1], color=color, linewidth=2, label=model_labels[m_key])
        plt.plot(anios_totales[idx_hist_end:], y_pred[idx_hist_end:], color=color, linewidth=1.5, linestyle=":")
        
    plt.title(f"Curvas de Difusion y Proyecciones: {tech.upper()}", fontsize=11, fontweight="bold", pad=12, color="#1e293b")
    plt.xlabel("Ano", fontsize=8, color="#475569")
    plt.ylabel("Adopcion Acumulada (Millones)", fontsize=8, color="#475569")
    plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#e2e8f0", fontsize=7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)

def generar_pdf_informe(tech, df_hist, params, analisis_cualitativo, detalles_modelos, consenso_forecast, informe_cientifico):
    pdf = UnifiedReportPDF()
    pdf.set_margins(left=18, top=15, right=18)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. TÍTULO PRINCIPAL (BANNER PREMIUM)
    pdf.set_fill_color(30, 41, 59) # Slate 800
    pdf.rect(0, 0, 210, 40, "F")
    
    pdf.set_y(12)
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, f"INFORME GLOBAL DE ADOPCION: {tech.upper()}", ln=True, align="C")
    pdf.set_font("helvetica", "I", 9.5)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 5, "Estudio Unificado de Modelizacion Matematica de Difusion y RAG pgvector", ln=True, align="C")
    
    pdf.set_y(45)
    pdf.set_text_color(50, 50, 50)
    
    # 2. SECCIÓN 1: Contexto Cualitativo
    draw_section_header(pdf, "1. Resumen Ejecutivo y Contexto de Mercado")
    print_paragraph_with_formulas(pdf, analisis_cualitativo)
    
    # 3. SECCIÓN 2: Serie Histórica y Formulación
    draw_section_header(pdf, "2. Datos Historicos y Resumen de Modelos")
    
    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(45, 7, "Ano", border=1, align="C", fill=True)
    pdf.cell(85, 7, "Adopcion Acumulada Real (M)", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 8)
    for idx, row in df_hist.iterrows():
        pdf.cell(45, 6, str(int(row["anio"])), border=1, align="C")
        pdf.cell(85, 6, f"{row['adopcion_acumulada']:.2f} M", border=1, align="C")
        pdf.ln()
        
    pdf.ln(5)
    
    # Renderizar la lista de los 8 modelos matemáticos con sus fórmulas
    if detalles_modelos.strip():
        print_paragraph_with_formulas(pdf, detalles_modelos)
        
    # 4. SECCIÓN 3: Ajuste de Modelos
    draw_section_header(pdf, "3. Resumen de Calidad de Ajuste (Errores de Modelos)")
    
    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(65, 7, "Modelo de Difusion", border=1, fill=True)
    pdf.cell(30, 7, "R2", border=1, align="C", fill=True)
    pdf.cell(40, 7, "MAPE Ajuste", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 8)
    anios_reales = df_hist["anio"].values
    t_hist = np.arange(len(anios_reales))
    y_true = df_hist["adopcion_acumulada"].values
    
    model_labels = {
        "Bass_Clasico": "Bass Clasico",
        "Dual_Market": "Dual Market",
        "Fourt_Woodlock": "Fourt & Woodlock",
        "Gompertz": "Gompertz",
        "Generalized_Bass": "Generalized Bass",
        "Horsky_Simon": "Horsky & Simon",
        "Muller_Yogev": "Muller & Yogev",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Difusion Logistica R&K",
        "Ladron_Putsis": "Ladron-de-Guevara & Putsis"
    }
    
    model_funcs = {
        "Bass_Clasico": bass_classic,
        "Dual_Market": dual_market_bass,
        "Fourt_Woodlock": fourt_woodlock_model,
        "Gompertz": gompertz_model,
        "Generalized_Bass": generalized_bass_model,
        "Horsky_Simon": horsky_simon_model,
        "Muller_Yogev": muller_yogev_model,
        "VdB_Joshi": vdb_joshi_model,
        "Logistic_Diffusion_Convergence": logistic_diffusion_convergence,
        "Ladron_Putsis": ladron_puts_model
    }
    
    active_models = []
    for m_key in model_labels.keys():
        if m_key not in params:
            continue
        p = params[m_key]
        popt = reconstruct_popt(m_key, p)
        if not popt:
            continue
        active_models.append(m_key)
        func = model_funcs[m_key]
        y_pred = func(t_hist, *popt)
        mape_val = calculate_mape(y_true, y_pred)
        
        pdf.cell(65, 6, model_labels[m_key], border=1)
        pdf.cell(30, 6, f"{p['r_cuadrado']:.4f}", border=1, align="C")
        pdf.cell(40, 6, f"{mape_val:.2f}%", border=1, align="C")
        pdf.ln()
        
    pdf.ln(5)
    
    # 5. SECCIÓN 4: Proyecciones y Gráficas
    draw_section_header(pdf, "4. Proyecciones Futuras y Graficas de Difusion")
    
    # 4.1 Gráfica Global (Todos los modelos)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "Comparativa Global de Modelos Matematicos", ln=True)
    pdf.ln(2)
    
    avail_w = pdf.epw
    img_w = min(150.0, avail_w)
    x_pos = pdf.l_margin + (avail_w - img_w) / 2
    
    try:
        tmp_all = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plot_all_path = tmp_all.name
        tmp_all.close()
        
        generate_diffusion_plot(tech, df_hist, params, plot_all_path, models_to_plot=None)
        pdf.image(plot_all_path, x=x_pos, w=img_w)
        os.remove(plot_all_path)
    except Exception as e:
        pdf.multi_cell(0, 6, f"(Error generando grafica global: {e})")

    pdf.ln(10)
    
    # 4.2 Gráfica Recomendada
    try:
        tmp_rec = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plot_rec_path = tmp_rec.name
        tmp_rec.close()
        
        from ui.tab_projections import extract_recommended_model_from_consensus
        ia_recommended_model = extract_recommended_model_from_consensus(consenso_forecast)
        
        models_to_plot = []
        if ia_recommended_model and ia_recommended_model in params:
            models_to_plot.append(ia_recommended_model)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Proyeccion Estrategica: Modelo Recomendado por IA", ln=True)
        else:
            best_statistical = max(params.keys(), key=lambda k: params[k].get("r_cuadrado", 0)) if params else None
            if best_statistical:
                models_to_plot.append(best_statistical)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Proyeccion Matematica: Mejor Ajuste Estadistico", ln=True)
                
        pdf.ln(2)
        generate_diffusion_plot(tech, df_hist, params, plot_rec_path, models_to_plot=models_to_plot)
        pdf.image(plot_rec_path, x=x_pos, w=img_w)
        os.remove(plot_rec_path)
    except Exception as e:
        pdf.multi_cell(0, 6, f"(Error generando grafica recomendada: {e})")
        
    # Tabla de proyecciones
    if active_models:
        pdf.set_font("helvetica", "B", 7)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(15, 7, "Ano", border=1, align="C", fill=True)
        col_w = 175 / len(active_models)
        for m_key in active_models:
            pdf.cell(col_w, 7, model_labels[m_key][:16], border=1, align="C", fill=True)
        pdf.ln()
        
        ultimo_anio = int(anios_reales[-1])
        anios_proj = list(range(ultimo_anio + 1, ultimo_anio + 11))
        t_proj = np.arange(len(anios_reales), len(anios_reales) + 10)
        
        proj_data = {}
        for m_key in active_models:
            p = params[m_key]
            popt = reconstruct_popt(m_key, p)
            func = model_funcs[m_key]
            proj_data[m_key] = func(t_proj, *popt)
            
        pdf.set_font("helvetica", "", 7)
        for i, anio in enumerate(anios_proj):
            pdf.cell(15, 6, str(anio), border=1, align="C")
            for m_key in active_models:
                pdf.cell(col_w, 6, f"{proj_data[m_key][i]:.2f}M", border=1, align="C")
            pdf.ln()
            
    pdf.ln(5)
    
    # 6. SECCIÓN 5: Pronóstico de Consenso
    draw_section_header(pdf, "5. Pronostico de Consenso y Estrategia de IA")
    print_paragraph_with_formulas(pdf, consenso_forecast)
    
    # Generar grafica de consenso
    if consenso_forecast.strip():
        try:
            fig_c = plt.figure(figsize=(8, 4.2))
            plt.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
            plt.gca().set_facecolor("#fcfcfc")
            
            anios_reales = df_hist["anio"].values
            y_true = df_hist["adopcion_acumulada"].values
            plt.scatter(anios_reales, y_true, color="#0f172a", s=50, zorder=5, label="Datos Reales")
            
            last_hist_year = int(anios_reales[-1])
            last_hist_val = float(y_true[-1])
            t_proj = np.arange(len(anios_reales) + 15)
            anios_proj_full = [int(anios_reales[0] + i) for i in t_proj]
            
            anchors = extract_consensus_anchor_points(consenso_forecast)
            
            anios_fut_c, y_low_c, y_mid_c, y_high_c = build_consensus_curve_from_anchors(
                anchors, last_hist_year, last_hist_val, anios_proj_full
            )
            
            if anios_fut_c is not None:
                # Merge con el historico para graficar linea continua
                hist_years = list(anios_reales[:-1])
                hist_vals = list(y_true[:-1])
                anios_plot = hist_years + list(anios_fut_c)
                y_plot = hist_vals + list(y_mid_c)
                
                plt.plot(anios_plot, y_plot, color="#d97706", linewidth=2.5, label="Consenso IA (Proyeccion)")
                if len(y_low_c) > 0:
                    plt.fill_between(anios_fut_c, y_low_c, y_high_c, color="#fef3c7", alpha=0.6, label="Banda de Confianza IA")
                
                # Plot anchor points
                for a in anchors:
                    plt.scatter([a['year']], [a['mid']], color='#b45309', s=80, marker='D', zorder=6)
            else:
                # Fallback matematico
                best_key, ranked_list = rank_and_select_best_model(params)
                if ranked_list:
                    y_consenso = compute_weighted_consensus_projection(params, t_proj, ranked_list)
                    if y_consenso is not None:
                        plt.plot(anios_proj_full, y_consenso, color="#d97706", linewidth=2.5, label="Consenso Matematico")
            
            plt.title(f"Proyeccion de Consenso: {tech.upper()}", fontsize=11, fontweight="bold", pad=12, color="#1e293b")
            plt.xlabel("Ano", fontsize=8, color="#475569")
            plt.ylabel("Adopcion (Millones)", fontsize=8, color="#475569")
            plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#e2e8f0", fontsize=7)
            plt.tight_layout()
            
            tmp_c_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            plot_c_path = tmp_c_file.name
            tmp_c_file.close()
            
            plt.savefig(plot_c_path, dpi=300)
            plt.close(fig_c)
            
            avail_w = pdf.epw
            img_w = min(150.0, avail_w)
            x_pos = pdf.l_margin + (avail_w - img_w) / 2
            
            pdf.ln(5)
            pdf.image(plot_c_path, x=x_pos, w=img_w)
            pdf.ln(4)
            os.remove(plot_c_path)
        except Exception as e:
            pdf.set_font("helvetica", "I", 8.5)
            pdf.cell(0, 6, f"No se pudo insertar la grafica de consenso: {e}", ln=True)
            pdf.ln(3)
    
    # 6. SECCIÓN 6: RAG
    draw_section_header(pdf, "6. Informe Analitico Cientifico RAG (pgvector)")
    print_paragraph_with_formulas(pdf, informe_cientifico)
    
    return pdf.output()
