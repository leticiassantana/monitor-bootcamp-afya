import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import date, datetime
from io import BytesIO
import plotly.graph_objects as go

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monitor de Formação · Bootcamp Afya",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── BRAND ────────────────────────────────────────────────────────────────────
YELLOW  = "#eddc11"
ROXO    = "#270028"
CARD_BG = "#3a003d"
CARD_BORDER = "#5a1060"
WHITE   = "#f0eaf5"
GREEN   = "#4ecb71"
ORANGE  = "#f5a623"
RED     = "#e24b4a"
GRAY    = "#9a8fa5"
BLUE    = "#2E86AB"

TIER_COLORS = {
    "Formado":         {"bg": "#1a4d2e", "text": "#4ecb71", "icon": "✅"},
    "No Caminho":      {"bg": "#0d3d4d", "text": "#5bc8e0", "icon": "🟢"},
    "Alta Prioridade": {"bg": "#4a1050", "text": "#eddc11", "icon": "🎯"},
    "Atenção":         {"bg": "#4d3a00", "text": "#f5c842", "icon": "🟡"},
    "Estagnado":       {"bg": "#4d1a1a", "text": "#e24b4a", "icon": "🔴"},
    "Abandono":        {"bg": "#2a2a2a", "text": "#9a8fa5", "icon": "⚫"},
}

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif !important;
}}

/* Hide Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 0 !important; max-width: 1280px; }}

/* ── TOP HEADER ── */
.pda-header {{
    background: #1a0020;
    margin: -1rem -1rem 2rem -1rem;
    padding: 28px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 2px solid {YELLOW};
}}
.pda-header h1 {{
    font-family: 'Dela Gothic One', sans-serif !important;
    color: {YELLOW};
    font-size: 22px;
    margin: 0;
    letter-spacing: -0.3px;
}}
.pda-header p {{
    color: rgba(255,255,255,0.5);
    font-size: 12px;
    margin: 4px 0 0 0;
    font-weight: 300;
}}
.header-badge {{
    background: {YELLOW};
    color: {ROXO};
    font-size: 11px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 20px;
}}

/* ── KPI CARDS ── */
.kpi-card {{
    background: {CARD_BG};
    border-radius: 12px;
    padding: 20px;
    border: 1px solid {CARD_BORDER};
    text-align: left;
}}
.kpi-label {{
    font-size: 10px;
    font-weight: 600;
    color: #9a8fa5;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-family: 'Dela Gothic One', sans-serif !important;
    font-size: 36px;
    color: {YELLOW};
    line-height: 1;
    margin-bottom: 4px;
}}
.kpi-value.green {{ color: {GREEN}; }}
.kpi-sub {{
    font-size: 11px;
    color: #7a6f85;
}}

/* ── GOAL BAR ── */
.goal-wrap {{
    background: {CARD_BG};
    border-radius: 12px;
    padding: 18px 24px;
    border: 1px solid {CARD_BORDER};
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 20px;
}}
.goal-label {{
    font-size: 12px;
    font-weight: 600;
    color: {WHITE};
    min-width: 140px;
}}
.goal-track {{
    flex: 1;
    background: #5a1060;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
}}
.goal-fill {{
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, {GREEN}, #7de89a);
}}
.goal-info {{
    font-size: 11px;
    color: #7a6f85;
    margin-top: 5px;
}}
.goal-pct {{
    font-family: 'Dela Gothic One', sans-serif !important;
    font-size: 22px;
    color: {YELLOW};
    min-width: 52px;
    text-align: right;
}}

/* ── SECTION TITLE ── */
.section-title {{
    font-family: 'Dela Gothic One', sans-serif !important;
    color: {YELLOW};
    font-size: 17px;
    margin: 0 0 2px 0;
}}
.section-sub {{
    font-size: 12px;
    color: #7a6f85;
    margin: 0 0 16px 0;
}}

/* ── TIER BADGE ── */
.tier-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}}

/* ── TABLE ── */
.styled-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    background: {CARD_BG};
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid {CARD_BORDER};
}}
.styled-table thead th {{
    background: #1a0020;
    padding: 10px 14px;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
    color: #9a8fa5;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid {CARD_BORDER};
    white-space: nowrap;
}}
.styled-table tbody tr {{
    border-bottom: 1px solid #4a0050;
    transition: background 0.1s;
    color: {WHITE};
}}
.styled-table tbody tr:hover {{ background: #4a0050; }}
.styled-table tbody td {{
    padding: 10px 14px;
    vertical-align: middle;
}}
.prog-bar-wrap {{ display: flex; align-items: center; gap: 8px; }}
.prog-bar {{
    width: 64px; height: 6px;
    background: #5a1060; border-radius: 3px; overflow: hidden;
    display: inline-block;
}}
.prog-fill {{ height: 100%; border-radius: 3px; }}
.delta-pos {{ color: {GREEN}; font-weight: 600; }}
.delta-neg {{ color: {RED};   font-weight: 600; }}
.delta-zero {{ color: {GRAY}; }}
.td-name {{ font-weight: 500; color: {WHITE}; }}
.td-name small {{ display: block; font-size: 11px; color: #7a6f85; font-weight: 400; }}
.wpp {{ font-size: 11px; color: #7a6f85; }}

/* ── UPLOAD AREA ── */
.upload-box {{
    background: {CARD_BG};
    border: 2px dashed {CARD_BORDER};
    border-radius: 12px;
    padding: 32px;
    text-align: center;
    color: #7a6f85;
    font-size: 13px;
}}
.upload-box h3 {{
    font-family: 'Dela Gothic One', sans-serif !important;
    color: {YELLOW};
    margin-bottom: 8px;
}}

/* ── EMPTY STATE ── */
.empty-state {{
    text-align: center;
    padding: 80px 40px;
    background: {CARD_BG};
    border-radius: 16px;
    border: 2px dashed {CARD_BORDER};
}}
.empty-state h2 {{
    font-family: 'Dela Gothic One', sans-serif !important;
    color: {YELLOW};
    font-size: 24px;
    margin-bottom: 12px;
}}
.empty-state p {{ color: #9a8fa5; font-size: 14px; }}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────────────────────
BOOTCAMP_END  = date(2026, 7, 12)
STORAGE_PATH  = os.path.join(os.path.dirname(__file__), "data", "history.json")
GRAD_THRESHOLD = 0.70

# ── PERSISTENCE ──────────────────────────────────────────────────────────────
def load_history() -> dict:
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    if os.path.exists(STORAGE_PATH):
        try:
            with open(STORAGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_history(history: dict):
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ── FILE PARSING ─────────────────────────────────────────────────────────────
def extract_date_from_name(name: str) -> str | None:
    m = re.search(r"(\d{4}-\d{2}-\d{2})T", name)
    if m:
        return m.group(1)
    m2 = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return m2.group(1) if m2 else None

def is_sim(val) -> bool:
    return str(val).strip().lower() == "sim"

def get_col(row: dict, keys: list[str]) -> str:
    for k in keys:
        for rk, rv in row.items():
            if k.lower() in str(rk).lower():
                return str(rv).strip()
    return ""

def normalize_rows(df: pd.DataFrame) -> list[dict]:
    rows = []
    for _, r in df.iterrows():
        row = {k: str(v) for k, v in r.items()}
        prog_str = get_col(row, ["progresso no bootcamp", "progresso"])
        try:
            prog = float(prog_str.replace(",", "."))
        except ValueError:
            prog = 0.0
        prog = min(1.0, max(0.0, prog))
        email = get_col(row, ["email"]).lower()
        if not email or "@" not in email:
            continue
        rows.append({
            "nome":               get_col(row, ["nome"]),
            "email":              email,
            "whatsapp":           get_col(row, ["whatsapp"]),
            "progresso":          prog,
            "diversidade_negro":  is_sim(get_col(row, ["preto ou pardo"])),
            "diversidade_indig":  is_sim(get_col(row, ["ind"])),
            "graduado":           is_sim(get_col(row, ["graduado"])),
        })
    return rows

def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        content = uploaded_file.read().decode("utf-8", errors="replace")
        from io import StringIO
        df = pd.read_csv(StringIO(content), sep=",", dtype=str)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(BytesIO(uploaded_file.read()), dtype=str)
    else:
        raise ValueError("Formato não suportado. Use CSV ou XLSX.")
    return df

# ── DATA PROCESSING ──────────────────────────────────────────────────────────
def build_people(history: dict) -> list[dict]:
    sorted_dates = sorted(history.keys())
    if not sorted_dates:
        return []

    people: dict[str, dict] = {}

    for d in sorted_dates:
        for row in history[d]:
            email = row["email"]
            if email not in people:
                people[email] = {
                    "nome":       row["nome"],
                    "email":      email,
                    "whatsapp":   row["whatsapp"],
                    "diversidade": False,
                    "graduado":   False,
                    "historico":  [],
                }
            p = people[email]
            if row["nome"]:           p["nome"] = row["nome"]
            if row["whatsapp"]:       p["whatsapp"] = row["whatsapp"]
            if row["diversidade_negro"] or row["diversidade_indig"]:
                p["diversidade"] = True
            if row["graduado"]:       p["graduado"] = True
            if not any(h["semana"] == d for h in p["historico"]):
                p["historico"].append({"semana": d, "progresso": row["progresso"]})

    last_date  = datetime.strptime(sorted_dates[-1], "%Y-%m-%d").date()
    weeks_left = max(0.0, (BOOTCAMP_END - last_date).days / 7)

    result = []
    for p in people.values():
        hist  = sorted(p["historico"], key=lambda h: h["semana"])
        progs = [h["progresso"] for h in hist]
        deltas = [progs[i] - progs[i-1] for i in range(1, len(progs))]

        p["progresso_atual"] = progs[-1] if progs else 0.0

        recent = deltas[-3:] if deltas else []
        p["velocidade"]   = sum(recent) / len(recent) if recent else 0.0
        p["delta_ultimo"] = deltas[-1] if deltas else None

        # consecutive stagnant weeks from most recent
        stagnado = 0
        for d in reversed(deltas):
            if d < 0.005:
                stagnado += 1
            else:
                break
        p["semanas_estagnado"] = stagnado
        p["nunca_progrediu"]   = bool(deltas) and all(d < 0.005 for d in deltas)

        vel_pos  = max(0.0, p["velocidade"])
        p["projetado"] = min(1.0, p["progresso_atual"] + vel_pos * weeks_left)

        gap = max(0.0, GRAD_THRESHOLD - p["projetado"])
        p["score"] = p["velocidade"] * (1 - gap) * 100 if p["velocidade"] > 0 else 0.0

        # Tier
        if p["graduado"]:
            tier = "Formado"
        elif p["nunca_progrediu"] and p["semanas_estagnado"] >= 2:
            tier = "Abandono"
        elif p["semanas_estagnado"] >= 2:
            tier = "Estagnado"
        elif p["projetado"] >= GRAD_THRESHOLD:
            tier = "No Caminho"
        elif p["velocidade"] > 0 and p["projetado"] >= 0.40:
            tier = "Alta Prioridade"
        else:
            tier = "Atenção"
        p["tier"] = tier

        estrategias = {
            "Formado":         "Convidar para mentoria reversa ou depoimento",
            "No Caminho":      "Celebrar progresso — compartilhar conquista no grupo",
            "Alta Prioridade": "Contato focado via WhatsApp — um empurrão pode converter",
            "Atenção":         "Check-in amigável — identificar barreiras e oferecer apoio",
            "Estagnado":       "Máx. 1 contato — não insistir se não responder",
            "Abandono":        "Não contatar — reserve recursos para quem está progredindo",
        }
        p["estrategia"] = estrategias[tier]
        result.append(p)

    return result

# ── HELPERS ──────────────────────────────────────────────────────────────────
def pct(v: float) -> str:
    return f"{v * 100:.0f}%"

def prog_bar_html(val: float, color: str = ROXO, width: int = 64) -> str:
    return (
        f'<div class="prog-bar" style="width:{width}px">'
        f'<div class="prog-fill" style="width:{pct(val)};background:{color}"></div>'
        f"</div>"
    )

def tier_badge_html(tier: str) -> str:
    c = TIER_COLORS.get(tier, {"bg": "#eee", "text": "#333", "icon": ""})
    return (
        f'<span class="tier-badge" style="background:{c["bg"]};color:{c["text"]}">'
        f'{c["icon"]} {tier}</span>'
    )

def delta_html(val) -> str:
    if val is None:
        return '<span class="delta-zero">—</span>'
    if val > 0.005:
        return f'<span class="delta-pos">+{pct(val)}</span>'
    if val < -0.005:
        return f'<span class="delta-neg">{pct(val)}</span>'
    return '<span class="delta-zero">+0%</span>'

def prog_color(v: float) -> str:
    if v >= 0.70: return GREEN
    if v >= 0.40: return ORANGE
    return RED

def fmt_wpp(num: str) -> str:
    s = re.sub(r"\D", "", str(num))
    if not s:
        return ""
    return s if s.startswith("55") else "55" + s

# ── HEADER ───────────────────────────────────────────────────────────────────
history = load_history()
sorted_dates = sorted(history.keys())
last_date_str = sorted_dates[-1] if sorted_dates else None
badge_text = (
    f"Atualizado em {datetime.strptime(last_date_str, '%Y-%m-%d').strftime('%d/%m/%Y')}"
    if last_date_str else "Nenhum dado carregado"
)

st.markdown(f"""
<div class="pda-header">
  <div>
    <h1>Bootcamp Afya — Monitor de Formação</h1>
    <p>Programadores do Amanhã · Meta: 10% do grupo de diversidade formado até 12/07/2026</p>
  </div>
  <span class="header-badge">{badge_text}</span>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR: FILE UPLOAD ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <p style="font-family:'Dela Gothic One',sans-serif;color:{YELLOW};font-size:16px;margin-bottom:8px">
    Carregar Relatório
    </p>
    """, unsafe_allow_html=True)
    st.caption("Selecione um ou mais arquivos CSV/XLSX da DIO. A data é detectada automaticamente pelo nome do arquivo.")

    uploaded = st.file_uploader(
        "Arquivos da DIO",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        msgs = []
        for f in uploaded:
            week_date = extract_date_from_name(f.name)
            if not week_date:
                week_date = st.text_input(
                    f"Data para '{f.name}' (AAAA-MM-DD):",
                    key=f"date_{f.name}"
                )
                if not week_date or not re.match(r"\d{4}-\d{2}-\d{2}", week_date):
                    st.warning(f"Informe a data para '{f.name}'")
                    continue
            try:
                df   = parse_uploaded_file(f)
                rows = normalize_rows(df)
                if not rows:
                    msgs.append(f"⚠️ {f.name}: nenhuma linha válida encontrada.")
                    continue
                history[week_date] = rows
                msgs.append(f"✅ {f.name} → {week_date} ({len(rows)} pessoas)")
            except Exception as e:
                msgs.append(f"❌ {f.name}: {e}")

        save_history(history)
        sorted_dates = sorted(history.keys())
        for m in msgs:
            st.write(m)

    st.divider()

    if history:
        st.caption(f"**{len(sorted_dates)} semana(s) carregada(s):**")
        for d in sorted_dates:
            n = len(history[d])
            st.caption(f"• {datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m/%Y')} — {n} pessoas")

        if st.button("🗑️ Limpar todos os dados", use_container_width=True):
            if st.checkbox("Confirmar limpeza"):
                history = {}
                save_history(history)
                st.rerun()

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not history:
    st.markdown(f"""
    <div class="empty-state">
      <h2>👈 Carregue um relatório para começar</h2>
      <p>No <strong style="color:{YELLOW}">painel lateral à esquerda</strong>, clique em <strong>"Browse files"</strong>
      e selecione os arquivos CSV ou XLSX baixados da DIO.<br><br>
      Você pode selecionar múltiplos arquivos de uma vez para carregar o histórico completo.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── BUILD DATA ────────────────────────────────────────────────────────────────
people  = build_people(history)
div_ppl = [p for p in people if p["diversidade"]]

total     = len(people)
div_total = len(div_ppl)
meta      = max(1, -(-div_total // 10))   # ceil(10%)
formados  = sum(1 for p in div_ppl if p["graduado"])
prog_med  = (
    sum(p["progresso_atual"] for p in div_ppl) / div_total
    if div_total else 0.0
)
pct_meta  = min(1.0, formados / meta) if meta else 0.0

# ── KPI ROW ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, "Total inscritos",        f"{total:,}".replace(",", "."), "no bootcamp", ""),
    (c2, "Grupo diversidade",      f"{div_total:,}".replace(",", "."), "Preto/Pardo ou Indígena", ""),
    (c3, "Meta 10%",               str(meta), "pessoas a formar", ""),
    (c4, "Formados (diversidade)", str(formados), "graduados", " green"),
    (c5, "Progresso médio",        pct(prog_med), "grupo diversidade", ""),
]
for col, label, value, sub, cls in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value{cls}">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── GOAL BAR ─────────────────────────────────────────────────────────────────
fill_w = int(pct_meta * 100)
st.markdown(f"""
<div class="goal-wrap">
  <span class="goal-label">Meta de formação</span>
  <div style="flex:1">
    <div class="goal-track">
      <div class="goal-fill" style="width:{fill_w}%"></div>
    </div>
    <div class="goal-info">{formados} formados de {div_total} no grupo de diversidade · Meta: {meta} pessoas (10%)</div>
  </div>
  <span class="goal-pct">{int(pct_meta*100)}%</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── PRIORITY TABLE ────────────────────────────────────────────────────────────
st.markdown(f"""
<p class="section-title">Lista de Contato Prioritário — Diversidade</p>
<p class="section-sub">Ordenada por potencial de conversão · Exporte o JSON para disparar via n8n → WhatsApp</p>
""", unsafe_allow_html=True)

tier_options = ["Alta Prioridade", "Atenção", "No Caminho", "Estagnado", "Formado", "Todos"]
tab_labels   = [f"{TIER_COLORS[t]['icon']} {t}" if t != "Todos" else "Todos" for t in tier_options]

tabs = st.tabs(tab_labels)

for tab, tier_key in zip(tabs, tier_options):
    with tab:
        if tier_key == "Todos":
            filtered = [p for p in div_ppl if p["tier"] != "Abandono"]
        else:
            filtered = [p for p in div_ppl if p["tier"] == tier_key]

        filtered.sort(key=lambda p: (-p["score"], -p["projetado"]))

        col_export, col_count = st.columns([1, 4])
        with col_count:
            st.caption(f"{len(filtered)} pessoa(s) nesta categoria")
        with col_export:
            export_tiers = [tier_key] if tier_key != "Todos" else ["Alta Prioridade", "Atenção"]
            export_list  = [
                {
                    "nome":               p["nome"],
                    "email":              p["email"],
                    "whatsapp":           fmt_wpp(p["whatsapp"]),
                    "tier":               p["tier"],
                    "progresso_atual":    round(p["progresso_atual"] * 100, 1),
                    "progresso_projetado":round(p["projetado"] * 100, 1),
                    "velocidade_semanal": round(p["velocidade"] * 100, 1),
                    "score_conversao":    round(p["score"], 2),
                    "estrategia":         p["estrategia"],
                    "semana_referencia":  last_date_str,
                }
                for p in div_ppl
                if p["tier"] in export_tiers
            ]
            export_list.sort(key=lambda x: -x["score_conversao"])
            fname = f"contatos_n8n_{tier_key.lower().replace(' ', '_')}_{last_date_str}.json"
            st.download_button(
                label="⬇ Exportar para n8n",
                data=json.dumps(export_list, ensure_ascii=False, indent=2),
                file_name=fname,
                mime="application/json",
                use_container_width=True,
            )

        if not filtered:
            st.info("Nenhuma pessoa nesta categoria.")
            continue

        # Build HTML table
        rows_html = ""
        for i, p in enumerate(filtered, 1):
            pc  = prog_color(p["progresso_atual"])
            prc = prog_color(p["projetado"])
            vel_str = (f'+{pct(p["velocidade"])}' if p["velocidade"] > 0 else pct(p["velocidade"]))
            wpp_str = fmt_wpp(p["whatsapp"])

            rows_html += f"""
            <tr>
              <td style="color:#9a9ab0;font-size:12px">{i}</td>
              <td class="td-name">
                {p['nome']}
                <small>{p['email']}</small>
              </td>
              <td>
                <div class="prog-bar-wrap">
                  {prog_bar_html(p['progresso_atual'], pc)}
                  <span style="font-size:12px;font-weight:600;color:{pc}">{pct(p['progresso_atual'])}</span>
                </div>
              </td>
              <td>{delta_html(p['delta_ultimo'])}</td>
              <td style="font-size:12px;color:#9a9ab0">{vel_str}/sem</td>
              <td style="font-weight:600;color:{prc}">{pct(p['projetado'])}</td>
              <td>{tier_badge_html(p['tier'])}</td>
              <td style="font-size:11px;color:#9a9ab0;max-width:180px;line-height:1.4">{p['estrategia']}</td>
              <td class="wpp">📱 {wpp_str if wpp_str else '—'}</td>
            </tr>"""

        st.markdown(f"""
        <table class="styled-table">
          <thead>
            <tr>
              <th>#</th><th>Nome</th><th>Progresso</th><th>Δ semana</th>
              <th>Velocidade</th><th>Projeção 12/07</th><th>Tier</th>
              <th>Estratégia</th><th>WhatsApp</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

# ── CHART ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown(f"""
<p class="section-title">Evolução Semanal</p>
<p class="section-sub">Progresso médio do grupo de diversidade semana a semana</p>
""", unsafe_allow_html=True)

if len(sorted_dates) >= 2:
    labels_chart = [
        datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m") for d in sorted_dates
    ]

    def avg_prog(d, filter_fn):
        rows = [r for r in history[d] if filter_fn(r)]
        return (sum(r["progresso"] for r in rows) / len(rows) * 100) if rows else 0

    div_avgs = [avg_prog(d, lambda r: r["diversidade_negro"] or r["diversidade_indig"]) for d in sorted_dates]
    all_avgs = [avg_prog(d, lambda r: True) for d in sorted_dates]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels_chart, y=[round(v, 1) for v in div_avgs],
        name="Grupo Diversidade",
        line=dict(color=ROXO, width=3),
        marker=dict(size=8, color=ROXO),
        fill="tozeroy",
        fillcolor="rgba(39,0,40,0.07)",
    ))
    fig.add_trace(go.Scatter(
        x=labels_chart, y=[round(v, 1) for v in all_avgs],
        name="Total geral",
        line=dict(color=GRAY, width=2, dash="dot"),
        marker=dict(size=6, color=GRAY),
    ))
    fig.add_hline(
        y=70, line_dash="dash", line_color=GREEN,
        annotation_text="Meta de conclusão (70%)",
        annotation_position="top left",
        annotation_font_color=GREEN,
    )
    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="#3a003d",
        paper_bgcolor="#3a003d",
        font=dict(family="IBM Plex Sans", size=12, color="#f0eaf5"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="#f0eaf5")),
        yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor="#5a1060", tickfont=dict(color="#9a8fa5")),
        xaxis=dict(gridcolor="#5a1060", tickfont=dict(color="#9a8fa5")),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Carregue pelo menos 2 semanas de dados para ver o gráfico de evolução.")

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:40px 0 20px;color:#c0b4d8;font-size:11px">
  Programadores do Amanhã · Monitor Bootcamp Afya
</div>
""", unsafe_allow_html=True)
