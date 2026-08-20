import os
import re
import tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fpdf import FPDF
from data.report_compiler import reconstruct_popt, calculate_mape
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

class UnifiedReportPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, "INFORME GLOBAL DE DIFUSIÓN DE TECNOLOGÍA - ANÁLISIS DE CONSENSO Y RAG", border="B", ln=True, align="R")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        page_str = f"Página {self.page_no()}"
        self.cell(0, 10, page_str, border="T", align="C")


from PIL import Image

def render_latex_to_temp_png(latex_str, dpi=300, fontsize=10.0):
    fig = plt.figure(figsize=(0.1, 0.1))
    clean_latex = latex_str.strip()
    if not (clean_latex.startswith("$") and clean_latex.endswith("$")):
        clean_latex = f"${clean_latex}$"
    
    plt.text(0.5, 0.5, clean_latex, fontsize=fontsize, ha='center', va='center', color='#1e293b')
    plt.axis('off')
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp_path = tmp_file.name
    tmp_file.close()
    
    plt.savefig(tmp_path, bbox_inches='tight', pad_inches=0.04, dpi=dpi, transparent=True)
    plt.close(fig)

    with Image.open(tmp_path) as img:
        w_px, h_px = img.size

    w_mm = (w_px / dpi) * 25.4
    h_mm = (h_px / dpi) * 25.4

    return tmp_path, w_mm, h_mm


def clean_txt_only(txt):
    if not txt:
        return ""
    txt = txt.replace("**", "").replace("*", "").replace("`", "")
    txt = re.sub(r'\(Paper ID:[^\)]+\)', '', txt)
    txt = re.sub(r'\(Ladrón-de-Guevara & Putsis, 2011, Eq\.\s*\d+\)', '(Eq.)', txt)
    txt = re.sub(r'\s+:', ':', txt)
    # Strip non-latin1 emojis and symbols for FPDF compatibility
    txt = txt.encode('latin-1', 'ignore').decode('latin-1')
    return txt.strip()

def flush_table_buffer(pdf, rows):
    if not rows:
        return
    headers = rows[0]
    data_rows = rows[1:]
    col_count = len(headers)
    
    ABBREV_MAP = {
        "modelo de bass clásico (1969)": "Bass",
        "modelo de dos mercados independientes - roset & canals (2011)": "Dual Mkt",
        "modelo de innovación pura de fourt & woodlock (1960)": "Fourt-W",
        "modelo asimétrico de gompertz": "Gompertz",
        "modelo de bass generalizado (gbm)": "GBM",
        "modelo con boca a boca variable de horsky & simon": "Horsky-S",
        "modelo de difusión multietapa de muller & yogev": "Muller-Y",
        "modelo de aceleración tecnológica de van den bulte & joshi": "VdB-Joshi",
        "modelo logístico de convergencia": "Logístico",
        "modelo de aceleración tecnológica de ladrón-de-guevara & putsis": "Ladrón-P",
        "bass clásico": "Bass",
        "dual market": "Dual Mkt",
        "fourt & woodlock": "Fourt-W",
        "gompertz (asimétrico)": "Gompertz",
        "bass generalizado (gbm)": "GBM",
        "horsky & simon": "Horsky-S",
        "muller & yogev": "Muller-Y",
        "van den bulte & joshi": "VdB-Joshi",
        "ladrón-de-guevara & putsis": "Ladrón-P",
        "adopción real acumulada (m)": "Real (M)",
        "fuente principal / cita de referencia": "Fuente Principal"
    }

    if col_count > 6:
        id_cols = [0]
        if col_count > 1 and ("real" in headers[1].lower() or "adopción" in headers[1].lower()):
            id_cols = [0, 1]
        
        value_cols = [i for i in range(len(headers)) if i not in id_cols]
        chunk_size = 4
        
        for chunk_start in range(0, len(value_cols), chunk_size):
            curr_cols = id_cols + value_cols[chunk_start:chunk_start + chunk_size]
            c_w = min(174.0 / len(curr_cols), 65.0)
            
            pdf.set_font("helvetica", "B", 7.5)
            pdf.set_fill_color(37, 99, 235)
            pdf.set_text_color(255, 255, 255)
            for ci in curr_cols:
                raw_h = clean_txt_only(headers[ci])
                abbr = ABBREV_MAP.get(raw_h.lower(), raw_h[:15])
                pdf.cell(c_w, 6.0, abbr, border=1, align="C", fill=True)
            pdf.ln()
            
            pdf.set_font("helvetica", "", 7.5)
            pdf.set_text_color(50, 50, 50)
            for r in data_rows:
                for ci in curr_cols:
                    val_cell = r[ci] if ci < len(r) else ""
                    pdf.cell(c_w, 5.0, clean_txt_only(val_cell)[:22], border=1, align="C")
                pdf.ln()
            pdf.ln(3)
    else:
        c_w = min(174.0 / col_count, 85.0)
        f_size = 7.5 if col_count > 4 else 8.5
        pdf.set_font("helvetica", "B", f_size)
        pdf.set_fill_color(37, 99, 235)
        pdf.set_text_color(255, 255, 255)
        for h in headers:
            raw_h = clean_txt_only(h)
            abbr = ABBREV_MAP.get(raw_h.lower(), raw_h[:25])
            pdf.cell(c_w, 6.0, abbr, border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("helvetica", "", f_size)
        pdf.set_text_color(50, 50, 50)
        for r in data_rows:
            for val_cell in r:
                pdf.cell(c_w, 5.2, clean_txt_only(val_cell)[:35], border=1, align="C")
            pdf.ln()
        pdf.ln(3)

def print_paragraph_with_formulas(pdf, text):
    if not text:
        return
        
    text = re.sub(r'\s*[\*\-\•]\s+(\*\*[^\*\n]+?\*\*:?)', r'\n\n* \1\n', text)
    text = re.sub(r'([.!?])\s*(\*\*[^\*\n]+?\*\*:?)', r'\1\n\n\2\n', text)
    text = re.sub(r'([^\n])\s*(#{1,4}\s+)', r'\1\n\n\2', text)
    text = re.sub(r'(\*\*[^\*\n]+?\*\*:)\s*([^\n])', r'\1\n\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    lines = text.split("\n")
    table_buffer = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str in ('#', '##', '###', '####'):
            if table_buffer:
                flush_table_buffer(pdf, table_buffer)
                table_buffer = []
            pdf.ln(3.5)
            continue

        if line_str.startswith("|") and line_str.endswith("|"):
            parts = [cell.strip() for cell in line_str.split("|")[1:-1]]
            if parts and not all(re.match(r'^[-:]+$', cell) for cell in parts):
                table_buffer.append(parts)
            continue
        else:
            if table_buffer:
                flush_table_buffer(pdf, table_buffer)
                table_buffer = []

        header_match = re.match(r'^(#{1,4})\s+', line_str)
        bold_subheading_match = re.match(r'^\*\*([^\*]+)\*\*:?$', line_str)
        
        if header_match or bold_subheading_match:
            if header_match:
                prefix_len = len(header_match.group(0))
                clean_title = line_str[prefix_len:].replace("**", "").strip()
            else:
                clean_title = bold_subheading_match.group(1).strip()
                
            clean_title = re.sub(r'^[\d\.\-]+\s+', '', clean_title)
            clean_title = clean_txt_only(clean_title)
            
            title_lower = clean_title.lower()
            if not clean_title or len(clean_title) < 2 or any(kw in title_lower for kw in [
                "análisis cualitativo del mercado", "analisis cualitativo del mercado",
                "reporte de análisis cualitativo", "reporte de analisis cualitativo",
                "introducción y contexto del mercado", "introduccion y contexto del mercado"
            ]):
                continue

            pdf.ln(4.5)
            pdf.subsection_counter = getattr(pdf, "subsection_counter", 0) + 1
            section_num = getattr(pdf, "current_section", 0)
            
            pdf.set_font("helvetica", "B", 10.5)
            pdf.set_text_color(37, 99, 235)
            if section_num > 0:
                pdf.cell(0, 6, f"{section_num}.{pdf.subsection_counter} {clean_title}", ln=True)
            else:
                pdf.cell(0, 6, f"{clean_title}", ln=True)
            pdf.set_text_color(50, 50, 50)
            pdf.ln(3)
            continue

        if line_str.startswith("$$") and line_str.endswith("$$"):
            latex_formula = line_str[2:-2].strip()
            if latex_formula:
                try:
                    img_path, w_mm, h_mm = render_latex_to_temp_png(latex_formula, fontsize=10.0)
                    max_w = pdf.epw - 30.0
                    if w_mm > max_w:
                        scale = max_w / w_mm
                        w_mm *= scale
                        h_mm *= scale
                    x_pos = pdf.l_margin + 15
                    pdf.ln(1.5)
                    pdf.image(img_path, x=x_pos, w=w_mm, h=h_mm)
                    pdf.ln(1.5)
                    os.remove(img_path)
                except Exception:
                    pdf.set_font("helvetica", "I", 8.5)
                    pdf.cell(0, 5, f"  Ecuación: {clean_txt_only(latex_formula)}", ln=True)
            continue

        if re.match(r'^[\*\-\•]\s+', line_str):
            clean_b = re.sub(r'^[\*\-\•]\s+', '', line_str)
            pdf.ln(2.0)
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 5, f"  {chr(149)} {clean_txt_only(clean_b)}")
            pdf.ln(1.0)
            continue

        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, clean_txt_only(line_str))
        pdf.ln(1.5)

    if table_buffer:
        flush_table_buffer(pdf, table_buffer)
        table_buffer = []

def reset_pdf_counters(pdf):
    pdf.current_section = 0
    pdf.subsection_counter = 0

def draw_section_header(pdf, title_text):
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(37, 99, 235) # Solid Royal Blue (#2563eb) - matching reference PDF!
    pdf.set_text_color(255, 255, 255) # White text
    pdf.cell(0, 8.5, f"   {title_text}", ln=True, fill=True)
    pdf.set_text_color(50, 50, 50)

    
    # Extraer el número de sección
    num_match = re.match(r'^(\d+)\.', title_text.strip())
    if num_match:
        pdf.current_section = int(num_match.group(1))
    else:
        pdf.current_section = 0
    pdf.subsection_counter = 0

def extract_consensus_anchor_points(text):
    if not text:
        return []
    anchors = []
    # Buscar patrones como: 2031: 54.45M / 54.45 millones / 2031 (horizonte...): 54.45
    pattern = r'\b(202[6-9]|203[0-9]|2040)\b[^\n]*?:\s*\*?\*?\s*([\d\.,]+)\s*(?:M|millones)?\b'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    seen_years = set()
    for y_str, val_str in matches:
        try:
            year = int(y_str)
            if year in seen_years:
                continue
            val_clean = val_str.replace(' ', '')
            if ',' in val_clean and '.' in val_clean:
                val = float(val_clean.replace('.', '').replace(',', '.'))
            elif ',' in val_clean:
                val = float(val_clean.replace(',', '.'))
            else:
                val = float(val_clean)
            if 2026 <= year <= 2045 and val > 0.0:
                seen_years.add(year)
                anchors.append({'year': year, 'mid': val, 'low': val * 0.93, 'high': val * 1.07})
        except ValueError:
            pass
    return sorted(anchors, key=lambda x: x['year'])

def build_consensus_curve_from_anchors(anchors, last_hist_year, last_hist_val, anios_proj_full):
    if not anchors:
        return None, None, None, None
    
    years = [last_hist_year] + [a['year'] for a in anchors]
    mids = [last_hist_val] + [a['mid'] for a in anchors]
    lows = [last_hist_val] + [a['low'] for a in anchors]
    highs = [last_hist_val] + [a['high'] for a in anchors]
    
    years, unique_idx = np.unique(years, return_index=True)
    mids = np.array(mids)[unique_idx]
    lows = np.array(lows)[unique_idx]
    highs = np.array(highs)[unique_idx]
    
    future_years = [y for y in anios_proj_full if y >= last_hist_year]
    if len(future_years) < 2:
        return None, None, None, None
        
    y_mid_interp = np.interp(future_years, years, mids)
    y_low_interp = np.interp(future_years, years, lows)
    y_high_interp = np.interp(future_years, years, highs)

    # Extrapolación suave logística post-ancla para evitar líneas horizontales planas
    if len(years) >= 2 and max(future_years) > max(years):
        last_y = max(years)
        last_val = mids[-1]
        prev_val = mids[-2] if len(mids) >= 2 else last_hist_val
        growth_rate = max(0.005, (last_val - prev_val) / max(1, (years[-1] - years[-2])))
        m_sat = max(last_val * 1.12, last_val + 5.0)
        
        for idx_fy, fy in enumerate(future_years):
            if fy > last_y:
                dt = fy - last_y
                y_extrap = m_sat - (m_sat - last_val) * np.exp(-0.15 * dt)
                y_mid_interp[idx_fy] = min(m_sat, max(last_val, y_extrap))
                y_low_interp[idx_fy] = y_mid_interp[idx_fy] * 0.93
                y_high_interp[idx_fy] = y_mid_interp[idx_fy] * 1.07

    return future_years, y_low_interp, y_mid_interp, y_high_interp

def rank_and_select_best_model(params):
    if not params:
        return None, []
    ranked = sorted(params.keys(), key=lambda k: params[k].get("r_cuadrado", 0), reverse=True)
    return ranked[0], ranked

def compute_weighted_consensus_projection(params, t_proj, ranked_list):
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
    top_models = ranked_list[:3]
    preds = []
    weights = []
    for m_key in top_models:
        p = params[m_key]
        popt = reconstruct_popt(m_key, p)
        if popt and m_key in model_funcs:
            r2 = max(p.get("r_cuadrado", 0.5), 0.5)
            w = r2 ** 4
            y_p = model_funcs[m_key](t_proj, *popt)
            preds.append(y_p)
            weights.append(w)
    if not preds:
        return None
    weights = np.array(weights) / sum(weights)
    consensus_pred = np.zeros_like(preds[0])
    for w, pred in zip(weights, preds):
        consensus_pred += w * pred
    return consensus_pred

def generate_diffusion_plot(tech, df_hist, params, output_path, models_to_plot=None):
    anios_reales = df_hist["anio"].values
    ultimo_anio = int(anios_reales[-1])
    y_true = df_hist["adopcion_acumulada"].values
    
    anios_totales = list(anios_reales) + list(range(ultimo_anio + 1, ultimo_anio + 11))
    t_totales = np.arange(len(anios_totales))
    
    fig = plt.figure(figsize=(8.5, 4.5))
    plt.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
    plt.gca().set_facecolor("#f8fafc")
    
    plt.scatter(anios_reales, y_true, color="#0f172a", s=55, zorder=5, label="Datos Reales")
    
    colors = {
        "Bass_Clasico": "#3b82f6",
        "Dual_Market": "#ef4444",
        "Fourt_Woodlock": "#8b5cf6",
        "Gompertz": "#ec4899",
        "Generalized_Bass": "#f59e0b",
        "Horsky_Simon": "#10b981",
        "Tanny_Derzko": "#06b6d4",
        "Steffens_Murthy": "#6366f1",
        "Muller_Yogev": "#a855f7",
        "VdB_Joshi": "#d97706",
        "Logistic_Diffusion_Convergence": "#0284c7",
        "Ladron_Putsis": "#14b8a6"
    }
    
    model_labels = {
        "Bass_Clasico": "Bass Clásico",
        "Dual_Market": "Dual Market",
        "Fourt_Woodlock": "Fourt & Woodlock",
        "Gompertz": "Gompertz (Asimétrico)",
        "Generalized_Bass": "Bass Generalizado (GBM)",
        "Horsky_Simon": "Horsky & Simon",
        "Tanny_Derzko": "Tanny & Derzko",
        "Steffens_Murthy": "Steffens & Murthy",
        "Muller_Yogev": "Muller & Yogev",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Modelo Logístico de Convergencia",
        "Ladron_Putsis": "Ladrón-de-Guevara & Putsis"
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
    
    for m_key in model_labels.keys():
        if m_key not in params:
            continue
        if models_to_plot is not None and m_key not in models_to_plot:
            continue
        color = colors.get(m_key, "#64748b")
        p = params[m_key]
        popt = reconstruct_popt(m_key, p)
        if not popt:
            continue
        func = model_funcs[m_key]
        y_pred = func(t_totales, *popt)
        
        idx_hist_end = len(anios_reales) - 1
        plt.plot(anios_totales[:idx_hist_end+1], y_pred[:idx_hist_end+1], color=color, linewidth=2, label=model_labels[m_key])
        plt.plot(anios_totales[idx_hist_end:], y_pred[idx_hist_end:], color=color, linewidth=1.5, linestyle=":")
        
    plt.title(f"Curvas de Difusión y Proyecciones: {tech.upper()}", fontsize=11, fontweight="bold", pad=12, color="#1e293b")
    plt.xlabel("Año", fontsize=8, color="#475569")
    plt.ylabel("Adopción Acumulada (Millones)", fontsize=8, color="#475569")
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
    pdf.cell(0, 8, f"INFORME GLOBAL DE ADOPCIÓN: {tech.upper()}", ln=True, align="C")
    pdf.set_font("helvetica", "I", 9.5)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 5, "Estudio Unificado de Modelización Matemática de Difusión y RAG pgvector", ln=True, align="C")
    
    pdf.set_y(45)
    pdf.set_text_color(50, 50, 50)
    
    # 2. SECCIÓN 1: Contexto Cualitativo
    if analisis_cualitativo:
        analisis_cualitativo = re.sub(r'^\s*#+\s*(?:Reporte de\s+)?Análisis Cualitativo del Mercado[^\n]*\n?', '', analisis_cualitativo, flags=re.IGNORECASE | re.MULTILINE)
        analisis_cualitativo = re.sub(r'^\s*#+\s*\d+\.\s*Introducción y Contexto del Mercado[^\n]*\n?', '', analisis_cualitativo, flags=re.IGNORECASE | re.MULTILINE)
        analisis_cualitativo = re.sub(r'^\s*#+\s*Introducción y Contexto del Mercado[^\n]*\n?', '', analisis_cualitativo, flags=re.IGNORECASE | re.MULTILINE)
        analisis_cualitativo = re.sub(r'^\s*#+\s*Análisis Cualitativo[^\n]*\n?', '', analisis_cualitativo, flags=re.IGNORECASE | re.MULTILINE)
        analisis_cualitativo = analisis_cualitativo.strip()
    draw_section_header(pdf, "1. Resumen Ejecutivo y Contexto de Mercado")
    print_paragraph_with_formulas(pdf, analisis_cualitativo)
    
    # 3. SECCIÓN 2: Serie Histórica y Formulación
    draw_section_header(pdf, "2. Datos Históricos y Resumen de Modelos")
    
    from data.loaders import resolve_historical_source

    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(37, 99, 235) # Solid Royal Blue header fill
    pdf.set_text_color(255, 255, 255) # White text
    pdf.cell(28, 7, "Año", border=1, align="C", fill=True)
    pdf.cell(52, 7, "Adopción Real (M)", border=1, align="C", fill=True)
    pdf.cell(94, 7, "Fuente Principal / Referencia de Datos", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 7.5)
    pdf.set_text_color(50, 50, 50)
    for idx, row in df_hist.iterrows():
        year_val = int(row["anio"])
        src_val = resolve_historical_source(tech, year_val, row.get("fuente"))
        pdf.cell(28, 6, str(year_val), border=1, align="C")
        pdf.cell(52, 6, f"{row['adopcion_acumulada']:.2f} M", border=1, align="C")
        pdf.cell(94, 6, clean_txt_only(src_val)[:55], border=1, align="L")
        pdf.ln()

        
    pdf.ln(5)
    
    if isinstance(detalles_modelos, str) and detalles_modelos.strip():
        print_paragraph_with_formulas(pdf, detalles_modelos)
        
    # 4. SECCIÓN 3: Ajuste de Modelos
    draw_section_header(pdf, "3. Resumen de Calidad de Ajuste (Errores de Modelos)")
    
    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(75, 7, "Modelo de Difusión", border=1, fill=True)
    pdf.cell(35, 7, "R²", border=1, align="C", fill=True)
    pdf.cell(45, 7, "MAPE Ajuste", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 8)
    anios_reales = df_hist["anio"].values
    t_hist = np.arange(len(anios_reales))
    y_true = df_hist["adopcion_acumulada"].values
    
    model_labels = {
        "Bass_Clasico": "Bass Clásico",
        "Dual_Market": "Dual Market",
        "Fourt_Woodlock": "Fourt & Woodlock",
        "Gompertz": "Gompertz (Asimétrico)",
        "Generalized_Bass": "Bass Generalizado (GBM)",
        "Horsky_Simon": "Horsky & Simon",
        "Tanny_Derzko": "Tanny & Derzko",
        "Steffens_Murthy": "Steffens & Murthy",
        "Muller_Yogev": "Muller & Yogev",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Modelo Logístico de Convergencia",
        "Ladron_Putsis": "Ladrón-de-Guevara & Putsis"
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
        
        pdf.cell(75, 6, model_labels[m_key], border=1)
        pdf.cell(35, 6, f"{p['r_cuadrado']:.5f}", border=1, align="C")
        pdf.cell(45, 6, f"{mape_val:.2f}%", border=1, align="C")
        pdf.ln()
        
    pdf.ln(5)
    
    # 5. SECCIÓN 4: Proyecciones y Gráficas
    draw_section_header(pdf, "4. Proyecciones Futuras y Gráficas de Difusión")
    
    # 4.1 Gráfica Global (Todos los modelos)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "Comparativa Global de Modelos Matemáticos", ln=True)
    pdf.ln(2)
    
    avail_w = pdf.epw
    img_w = min(155.0, avail_w)
    x_pos = pdf.l_margin + (avail_w - img_w) / 2
    
    try:
        tmp_all = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plot_all_path = tmp_all.name
        tmp_all.close()
        
        generate_diffusion_plot(tech, df_hist, params, plot_all_path, models_to_plot=None)
        pdf.image(plot_all_path, x=x_pos, w=img_w)
        os.remove(plot_all_path)
    except Exception as e:
        pdf.multi_cell(0, 6, f"(Error generando gráfica global: {e})")

    pdf.ln(8)
    
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
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, "Proyección Estratégica: Modelo Recomendado por IA", ln=True)
        else:
            best_statistical = max(params.keys(), key=lambda k: params[k].get("r_cuadrado", 0)) if params else None
            if best_statistical:
                models_to_plot.append(best_statistical)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, "Proyección Matemática: Mejor Ajuste Estadístico", ln=True)
                
        pdf.ln(2)
        generate_diffusion_plot(tech, df_hist, params, plot_rec_path, models_to_plot=models_to_plot)
        pdf.image(plot_rec_path, x=x_pos, w=img_w)
        os.remove(plot_rec_path)
    except Exception as e:
        pdf.multi_cell(0, 6, f"(Error generando gráfica recomendada: {e})")
        
    pdf.ln(6)

    # Tabla de proyecciones (Dividida en bloques de máximo 5 modelos para perfecta legibilidad)
    if active_models:
        pdf.set_font("helvetica", "B", 9.5)
        pdf.cell(0, 6, "Proyecciones Futuras por Modelo (2027 - 2036)", ln=True)
        pdf.ln(2)

        chunk_size = 5
        for chunk_idx in range(0, len(active_models), chunk_size):
            model_chunk = active_models[chunk_idx:chunk_idx + chunk_size]
            
            pdf.set_font("helvetica", "B", 7.5)
            pdf.set_fill_color(235, 238, 245)
            pdf.set_text_color(30, 41, 59)
            
            col_w = (pdf.epw - 18) / len(model_chunk)
            pdf.cell(18, 7, "Año", border=1, align="C", fill=True)
            for m_key in model_chunk:
                pdf.cell(col_w, 7, model_labels[m_key][:22], border=1, align="C", fill=True)
            pdf.ln()

            ultimo_anio = int(anios_reales[-1])
            anios_proj = list(range(ultimo_anio + 1, ultimo_anio + 11))
            t_proj = np.arange(len(anios_reales), len(anios_reales) + 10)

            proj_data = {}
            for m_key in model_chunk:
                p = params[m_key]
                popt = reconstruct_popt(m_key, p)
                func = model_funcs[m_key]
                proj_data[m_key] = func(t_proj, *popt)

            pdf.set_font("helvetica", "", 7.5)
            pdf.set_text_color(50, 50, 50)
            for i, anio in enumerate(anios_proj):
                pdf.cell(18, 6, str(anio), border=1, align="C")
                for m_key in model_chunk:
                    pdf.cell(col_w, 6, f"{proj_data[m_key][i]:.2f} M", border=1, align="C")
                pdf.ln()
            pdf.ln(4)
            
    pdf.ln(4)
    
    # 6. SECCIÓN 5: Pronóstico de Consenso
    draw_section_header(pdf, "5. Pronóstico de Consenso y Estrategia de IA")
    print_paragraph_with_formulas(pdf, consenso_forecast)
    
    # Generar gráfica de consenso
    if consenso_forecast.strip():
        try:
            fig_c = plt.figure(figsize=(8.5, 4.5))
            plt.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
            plt.gca().set_facecolor("#fcfcfc")
            
            anios_reales = df_hist["anio"].values
            y_true = df_hist["adopcion_acumulada"].values
            plt.scatter(anios_reales, y_true, color="#0f172a", s=55, zorder=5, label="Datos Reales")
            
            last_hist_year = int(anios_reales[-1])
            last_hist_val = float(y_true[-1])
            t_proj = np.arange(len(anios_reales) + 15)
            anios_proj_full = [int(anios_reales[0] + i) for i in t_proj]
            
            anchors = extract_consensus_anchor_points(consenso_forecast)
            
            anios_fut_c, y_low_c, y_mid_c, y_high_c = build_consensus_curve_from_anchors(
                anchors, last_hist_year, last_hist_val, anios_proj_full
            )
            
            if anios_fut_c is not None:
                hist_years = list(anios_reales[:-1])
                hist_vals = list(y_true[:-1])
                anios_plot = hist_years + list(anios_fut_c)
                y_plot = hist_vals + list(y_mid_c)
                
                plt.plot(anios_plot, y_plot, color="#d97706", linewidth=2.5, label="Consenso IA (Proyección)")
                if len(y_low_c) > 0:
                    plt.fill_between(anios_fut_c, y_low_c, y_high_c, color="#fef3c7", alpha=0.6, label="Banda de Confianza IA")
                
                for a in anchors:
                    plt.scatter([a['year']], [a['mid']], color='#b45309', s=80, marker='D', zorder=6)
            else:
                best_key, ranked_list = rank_and_select_best_model(params)
                if ranked_list:
                    y_consenso = compute_weighted_consensus_projection(params, t_proj, ranked_list)
                    if y_consenso is not None:
                        plt.plot(anios_proj_full, y_consenso, color="#d97706", linewidth=2.5, label="Consenso Matemático")
            
            plt.title(f"Proyección de Consenso: {tech.upper()}", fontsize=11, fontweight="bold", pad=12, color="#1e293b")
            plt.xlabel("Año", fontsize=8, color="#475569")
            plt.ylabel("Adopción (Millones)", fontsize=8, color="#475569")
            plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#e2e8f0", fontsize=7)
            plt.tight_layout()
            
            tmp_c_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            plot_c_path = tmp_c_file.name
            tmp_c_file.close()
            
            plt.savefig(plot_c_path, dpi=300)
            plt.close(fig_c)
            
            avail_w = pdf.epw
            img_w = min(155.0, avail_w)
            x_pos = pdf.l_margin + (avail_w - img_w) / 2
            
            pdf.ln(5)
            pdf.image(plot_c_path, x=x_pos, w=img_w)
            pdf.ln(4)
            os.remove(plot_c_path)
        except Exception as e:
            pdf.set_font("helvetica", "I", 8.5)
            pdf.cell(0, 6, f"No se pudo insertar la gráfica de consenso: {e}", ln=True)
            pdf.ln(3)
    
    # 7. SECCIÓN 6: RAG
    draw_section_header(pdf, "6. Informe Analítico Científico RAG (pgvector)")
    print_paragraph_with_formulas(pdf, informe_cientifico)
    
    return bytes(pdf.output())
