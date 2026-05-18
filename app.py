import streamlit as st
import pandas as pd
import json
import os
import re
import io
from datetime import date, datetime
from io import BytesIO, StringIO
import plotly.graph_objects as go

st.set_page_config(
    page_title="Monitor de Formação · Bootcamp DIOxAfyaxPdA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── BRAND ────────────────────────────────────────────────────────────────────
YELLOW      = "#eddc11"
ROXO        = "#270028"
CARD_BG     = "#3a003d"
CARD_BORDER = "#5a1060"
DARK_BG     = "#1a0020"
WHITE       = "#f0eaf5"
GREEN       = "#4ecb71"
ORANGE      = "#f5a623"
RED         = "#e24b4a"
GRAY        = "#9a8fa5"
BLUE        = "#5bc8e0"
YELLOW2     = "#f5c842"
WPP_LINK    = "https://chat.whatsapp.com/Cf2CicuO1Al1jVoYFe5i0l"
BC_FULL     = "Bootcamp Automação de Dados com IA, uma parceria entre DIOxAfyaxPdA"

BOOTCAMP_END   = date(2026, 7, 12)
STORAGE_PATH   = os.path.join(os.path.dirname(__file__), "data", "history.json")
META_PCT       = 0.10

# Tiers (nova lógica de 6 tiers baseada em buckets)
TIER_COLORS = {
    "Formado":         {"bg": "#1a4d2e", "text": "#4ecb71", "icon": "✅"},
    "Quase lá":        {"bg": "#3d2400", "text": "#f5a623", "icon": "🟠"},
    "Alta Prioridade": {"bg": "#4a1050", "text": "#eddc11", "icon": "🎯"},
    "Atenção":         {"bg": "#4d3a00", "text": "#f5c842", "icon": "🟡"},
    "Estagnado":       {"bg": "#4d1a1a", "text": "#e24b4a", "icon": "🔴"},
    "Recém-chegado":   {"bg": "#2a2a2a", "text": "#9a8fa5", "icon": "🆕"},
}
TIER_ORDER = ["Quase lá", "Alta Prioridade", "Atenção", "Estagnado", "Recém-chegado", "Formado"]

TIER_CRITERIA = {
    "Quase lá":        "Faixa 75–99% do bootcamp e ainda não graduada. Foco máximo, pode fechar a meta até 12/07.",
    "Alta Prioridade": "Avançou de faixa nas últimas semanas. Engajamento ativo, continuar empurrando.",
    "Atenção":         "Faixa 25–49% ou 50–74% sem avanço na janela. Check-in para entender o que travou.",
    "Estagnado":       "Faixa 0–24% com 2+ semanas sem se mexer. Máximo 1 contato.",
    "Recém-chegado":   "Tem só 1 snapshot no histórico. Aguardar mais 1 semana para avaliar.",
    "Formado":         "Graduado(a) = Sim no relatório da DIO. Convidar para depoimento.",
}

# Buckets (faixa categórica do progresso DIO)
BUCKET_INFO = {
    1: {"label": "🆕 Em início",  "range": "0–24%",          "color": "#9a8fa5"},
    2: {"label": "🟡 Engajadas",  "range": "25–49%",         "color": "#f5c842"},
    3: {"label": "🟢 Avançando",  "range": "50–74%",         "color": "#5bc8e0"},
    4: {"label": "🟠 Quase lá",   "range": "75–99%",         "color": "#f5a623"},
    5: {"label": "✅ Concluídas", "range": "100% + graduada","color": "#4ecb71"},
}

# Logo PdA inline (estrela de 8 pontas estilizada) — flat para evitar code-block do markdown
LOGO_SVG = (
    '<svg width="56" height="56" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0">'
    '<g transform="translate(50,50)">'
    f'<rect x="-30" y="-30" width="60" height="60" fill="none" stroke="{YELLOW}" stroke-width="6"/>'
    f'<rect x="-30" y="-30" width="60" height="60" fill="none" stroke="{YELLOW}" stroke-width="6" transform="rotate(45)"/>'
    '<rect x="-12" y="-12" width="24" height="24" fill="none" stroke="#ffffff" stroke-width="3" transform="rotate(45)"/>'
    '<line x1="-6" y1="0" x2="6" y2="0" stroke="#ffffff" stroke-width="3"/>'
    '</g></svg>'
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', sans-serif !important; }}
#MainMenu, footer {{ visibility: hidden; }}
header {{ background: transparent !important; }}
.block-container {{ padding-top: 0 !important; max-width: 1280px; }}

.pda-header {{
    background: {DARK_BG}; margin: -1rem -1rem 2rem -1rem;
    padding: 22px 40px; display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 12px;
    border-bottom: 2px solid {YELLOW};
}}
.pda-header-left {{ display:flex; align-items:center; gap:18px; }}
.pda-header h1 {{ font-family:'Dela Gothic One',sans-serif !important; color:{YELLOW}; font-size:20px; margin:0; }}
.pda-header p {{ color:rgba(255,255,255,0.45); font-size:11px; margin:3px 0 0 0; }}
.header-badge {{ background:{YELLOW}; color:{ROXO}; font-size:11px; font-weight:600; padding:5px 14px; border-radius:20px; }}

.hero-card {{
    background:{CARD_BG}; border-radius:14px; border:1px solid {CARD_BORDER};
    padding:28px; position:relative; overflow:hidden;
}}
.hero-card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,{YELLOW},{ORANGE},{GREEN}); }}
.hero-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; }}
.hero-block {{ padding:0 24px; border-right:1px solid {CARD_BORDER}; }}
.hero-block:first-child {{ padding-left:0; }}
.hero-block:last-child {{ border-right:none; }}
.hero-eye {{ font-size:10px; font-weight:600; color:{GRAY}; text-transform:uppercase; letter-spacing:.7px; margin-bottom:6px; }}
.hero-num {{ font-family:'Dela Gothic One',sans-serif !important; font-size:44px; line-height:1; color:{YELLOW}; margin-bottom:4px; }}
.hero-num.green {{ color:{GREEN}; }}
.hero-num.red {{ color:{RED}; }}
.hero-meta-after {{ font-family:'Dela Gothic One',sans-serif !important; color:{ORANGE}; font-size:22px; }}
.hero-sub {{ font-size:12px; color:{GRAY}; line-height:1.4; }}
.hero-alert {{ background:#4d1a00; border:1px solid {ORANGE}; border-radius:8px; padding:10px 14px; font-size:12px; color:#f5c842; margin-top:12px; }}
.hero-alert.green {{ background:#0d3d1a; border-color:{GREEN}; color:{GREEN}; }}

.prog-labels {{ display:flex; justify-content:space-between; font-size:11px; color:{GRAY}; margin:12px 0 5px 0; }}
.prog-track {{ background:{CARD_BORDER}; border-radius:6px; height:10px; overflow:hidden; }}
.prog-fill {{ height:100%; border-radius:6px; background:linear-gradient(90deg,{GREEN},#7de89a); }}

/* Comparativo Taxa de Graduação */
.comp-grad {{ background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:12px;
    padding:20px 28px; margin-top:14px; margin-bottom:20px;
    display:grid; grid-template-columns:1fr 1fr 1fr; gap:24px; align-items:center; }}
.comp-grad-eye {{ font-size:10px; font-weight:600; color:{GRAY}; text-transform:uppercase; letter-spacing:.7px; margin-bottom:6px; }}
.comp-grad-num {{ font-family:'Dela Gothic One',sans-serif !important; font-size:28px; color:{YELLOW}; }}
.comp-grad-num.gray {{ color:{GRAY}; }}
.comp-grad-sub {{ font-size:11px; color:{GRAY}; margin-top:4px; }}
.comp-grad-verdict {{ padding:10px 14px; border-radius:4px; font-size:12px; font-weight:500; line-height:1.5; }}
.verdict-up {{ background:rgba(78,203,113,.12); border-left:3px solid {GREEN}; color:{GREEN}; }}
.verdict-down {{ background:rgba(226,75,74,.12); border-left:3px solid {RED}; color:{RED}; }}

.kpi-card {{ background:{CARD_BG}; border-radius:12px; padding:18px; border:1px solid {CARD_BORDER}; }}
.kpi-label {{ font-size:10px; font-weight:600; color:{GRAY}; text-transform:uppercase; letter-spacing:.6px; margin-bottom:6px; }}
.kpi-value {{ font-family:'Dela Gothic One',sans-serif !important; font-size:32px; color:{YELLOW}; line-height:1; margin-bottom:4px; }}
.kpi-value.green {{ color:{GREEN}; }}
.kpi-value.red {{ color:{RED}; }}
.kpi-value.orange {{ color:{ORANGE}; }}
.kpi-sub {{ font-size:11px; color:#7a6f85; }}

.section-title {{ font-family:'Dela Gothic One',sans-serif !important; color:{YELLOW}; font-size:16px; margin:0 0 2px 0; }}
.section-sub {{ font-size:11px; color:{GRAY}; margin:0 0 14px 0; }}

.tier-badge {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600; white-space:nowrap; }}

/* Donut legend */
.legend-row {{ display:flex; align-items:center; padding:5px 0; font-size:12px; }}
.legend-dot {{ width:11px; height:11px; border-radius:2px; margin-right:8px; flex-shrink:0; }}
.legend-name {{ flex:1; color:{WHITE}; }}
.legend-num {{ font-weight:600; color:{YELLOW}; min-width:46px; text-align:right; display:inline-block; }}
.legend-pct {{ font-size:11px; color:{GRAY}; min-width:36px; text-align:right; display:inline-block; margin-left:8px; }}

/* Funil */
.funil-row {{ display:flex; align-items:center; gap:10px; margin-bottom:14px; }}
.funil-label {{ width:180px; font-size:13px; color:{WHITE}; font-weight:500; }}
.funil-label small {{ display:block; font-size:10px; color:{GRAY}; margin-top:2px; font-weight:400; }}
.funil-bar {{ flex:1; background:{DARK_BG}; border-radius:6px; height:34px; position:relative; overflow:hidden; }}
.funil-bar > div {{ height:100%; display:flex; align-items:center; padding:0 12px; color:{ROXO}; font-weight:700; font-size:13px; }}
.funil-delta {{ width:100px; text-align:right; font-size:11px; }}
.funil-delta .abs {{ font-weight:600; font-size:13px; display:block; }}
.funil-delta.pos .abs {{ color:{GREEN}; }}
.funil-delta.neg .abs {{ color:{RED}; }}
.funil-delta.zero .abs {{ color:{GRAY}; }}
.funil-delta .pct {{ color:{GRAY}; font-size:10px; }}

/* Comparativo bars */
.cmp-row {{ margin-bottom:18px; }}
.cmp-header {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px; }}
.cmp-label {{ font-size:13px; font-weight:600; color:{WHITE}; }}
.cmp-sublabel {{ font-size:11px; color:{GRAY}; margin-top:2px; }}
.cmp-delta {{ font-size:11px; font-weight:600; }}
.cmp-bar-row {{ display:flex; align-items:center; gap:12px; margin-bottom:6px; }}
.cmp-name {{ width:150px; font-size:11px; font-weight:600; }}
.cmp-name.div {{ color:{YELLOW}; }}
.cmp-name.nao {{ color:{GRAY}; }}
.cmp-bar {{ flex:1; background:{DARK_BG}; border-radius:6px; height:22px; overflow:hidden; }}
.cmp-bar > div {{ height:100%; display:flex; align-items:center; padding:0 10px; color:{ROXO}; font-weight:700; font-size:12px; border-radius:6px; }}

/* Contatos */
.contact-card {{
    background:#270028; border-radius:10px; border:1px solid #4a0050;
    padding:16px 18px; margin-bottom:10px;
}}
.contact-name {{ font-weight:600; font-size:14px; color:{WHITE}; }}
.contact-meta {{ font-size:11px; color:#7a6f85; margin-top:4px; }}
.contact-score {{ font-family:'Dela Gothic One',sans-serif !important; color:{YELLOW}; font-size:22px; text-align:right; }}

.msg-box {{ background:{DARK_BG}; border-radius:8px; border:1px solid #3a003d; padding:14px 16px; font-size:12px; color:#c0b4d8; line-height:1.8; margin-top:12px; white-space:pre-wrap; }}

/* Tabela completa */
.full-table {{ width:100%; border-collapse:collapse; font-size:12px; }}
.full-table thead th {{ background:{DARK_BG}; padding:10px 12px; text-align:left; font-size:10px; font-weight:600; color:{YELLOW}; text-transform:uppercase; letter-spacing:.5px; border-bottom:1px solid {CARD_BORDER}; white-space:nowrap; }}
.full-table tbody tr {{ border-bottom:1px solid #4a0050; }}
.full-table tbody tr:hover {{ background:#4a0050; }}
.full-table tbody td {{ padding:10px 12px; vertical-align:top; color:{WHITE}; }}
.td-meta {{ font-size:11px; color:#7a6f85; }}
.td-msg {{ font-size:11px; color:#9a8fa5; line-height:1.5; max-width:280px; }}
.bucket-pill {{ padding:3px 8px; border-radius:10px; font-size:10px; font-weight:600; white-space:nowrap; }}
.b1 {{ background:#2a2a2a; color:#9a8fa5; }}
.b2 {{ background:#4d3a00; color:#f5c842; }}
.b3 {{ background:#0d3d4d; color:#5bc8e0; }}
.b4 {{ background:#3d2400; color:#f5a623; }}
.b5 {{ background:#1a4d2e; color:#4ecb71; }}

.empty-state {{
    text-align:center; padding:80px 40px; background:{CARD_BG};
    border-radius:16px; border:2px dashed {CARD_BORDER};
}}
.empty-state h2 {{ font-family:'Dela Gothic One',sans-serif !important; color:{YELLOW}; font-size:22px; margin-bottom:12px; }}
.empty-state p {{ color:{GRAY}; font-size:13px; }}
</style>
""", unsafe_allow_html=True)

# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load_history() -> dict:
    if "history" in st.session_state:
        return st.session_state["history"]
    try:
        os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
        if os.path.exists(STORAGE_PATH):
            with open(STORAGE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state["history"] = data
                return data
    except Exception:
        pass
    st.session_state["history"] = {}
    return {}

def save_history(history: dict):
    st.session_state["history"] = history
    try:
        os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
        with open(STORAGE_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ── FILE PARSING ──────────────────────────────────────────────────────────────
def extract_date_from_name(name):
    m = re.search(r"(\d{4}-\d{2}-\d{2})T", name)
    if m: return m.group(1)
    m2 = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return m2.group(1) if m2 else None

def is_sim(val) -> bool:
    return str(val).strip().lower() == "sim"

def get_col(row: dict, keys: list) -> str:
    for k in keys:
        for rk, rv in row.items():
            if k.lower() in str(rk).lower():
                return str(rv).strip()
    return ""

def normalize_rows(df: pd.DataFrame) -> list:
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
            "nome":              get_col(row, ["nome"]),
            "email":             email,
            "whatsapp":          get_col(row, ["whatsapp"]),
            "progresso":         prog,
            "diversidade_negro": is_sim(get_col(row, ["preto ou pardo"])),
            "diversidade_indig": is_sim(get_col(row, ["ind"])),
            "graduado":          is_sim(get_col(row, ["graduado"])),
        })
    return rows

def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        content = uploaded_file.read().decode("utf-8", errors="replace")
        return pd.read_csv(StringIO(content), sep=",", dtype=str)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(uploaded_file.read()), dtype=str)
    raise ValueError("Formato não suportado. Use CSV ou XLSX.")

# ── BUCKETS + TIERS ───────────────────────────────────────────────────────────
def bucket_of(prog: float, graduado: bool) -> int:
    """Coluna progresso da DIO é categórica:
       0,25 = 0-24% · 0,5 = 25-49% · 0,75 = 50-74% · 1 = 75-99% · graduado = 100%"""
    if graduado:
        return 5
    if prog >= 1.0:
        return 4
    if prog >= 0.75:
        return 3
    if prog >= 0.5:
        return 2
    return 1

def build_people(history: dict) -> list:
    sorted_dates = sorted(history.keys())
    if not sorted_dates:
        return []
    people = {}
    for d in sorted_dates:
        for row in history[d]:
            email = row["email"]
            if email not in people:
                people[email] = {
                    "nome": row["nome"], "email": email,
                    "whatsapp": row["whatsapp"],
                    "diversidade": False, "graduado": False, "historico": [],
                }
            p = people[email]
            if row["nome"]:     p["nome"] = row["nome"]
            if row["whatsapp"]: p["whatsapp"] = row["whatsapp"]
            if row["diversidade_negro"] or row["diversidade_indig"]:
                p["diversidade"] = True
            if row["graduado"]: p["graduado"] = True
            if not any(h["semana"] == d for h in p["historico"]):
                p["historico"].append({"semana": d, "progresso": row["progresso"]})

    result = []
    for p in people.values():
        hist = sorted(p["historico"], key=lambda h: h["semana"])
        p["historico"] = hist
        p["progresso_atual"] = hist[-1]["progresso"] if hist else 0.0
        p["bucket_atual"] = bucket_of(p["progresso_atual"], p["graduado"])

        # Subiu de faixa na última semana? (entre o penúltimo e o último snapshot)
        if len(hist) >= 2:
            b_prev = bucket_of(hist[-2]["progresso"], False)
            p["subiu_esta_semana"] = p["bucket_atual"] > b_prev
        else:
            p["subiu_esta_semana"] = False

        # Subiu de faixa na janela? (1º snapshot vs atual)
        if len(hist) >= 2:
            b_ini = bucket_of(hist[0]["progresso"], False)
            p["subiu_4sem"] = p["bucket_atual"] > b_ini
        else:
            p["subiu_4sem"] = False

        # Tier (em cascata)
        if p["graduado"]:
            tier = "Formado"
        elif len(hist) == 1:
            tier = "Recém-chegado"
        elif p["bucket_atual"] == 4:
            tier = "Quase lá"
        elif p["subiu_4sem"]:
            tier = "Alta Prioridade"
        elif p["bucket_atual"] == 1:
            tier = "Estagnado"
        else:
            tier = "Atenção"
        p["tier"] = tier

        # Score (para ordenar Alta Prioridade + Quase lá)
        if p["bucket_atual"] == 4:
            base = 100
        else:
            base = p["bucket_atual"] * 15
        if p["subiu_esta_semana"]: base += 30
        elif p["subiu_4sem"]:      base += 15
        p["score"] = base

        result.append(p)
    return result

# ── MESSAGE GENERATION ────────────────────────────────────────────────────────
def generate_message(p: dict) -> str:
    nome = p["nome"].split()[0] if p["nome"] else "você"
    tier = p["tier"]

    if tier == "Quase lá":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Você está na reta final do {BC_FULL}, falta tão pouco para sua certificação! "
            f"O encerramento é em 12 de julho. 📆\n\n"
            f"A PdA oferece monitorias síncronas gratuitas, se precisar de qualquer apoio, "
            f"acessa: {WPP_LINK}\n\n"
            f"A PdA está aqui para qualificar e empoderar pessoas negras e indígenas a "
            f"construírem carreira no mercado da tecnologia. Vai até o fim, estamos torcendo por você! 🚀"
        )
    if tier == "Alta Prioridade":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Você está avançando no {BC_FULL} e tem tudo pra garantir sua certificação até "
            f"12 de julho. Não para agora! 📆\n\n"
            f"A PdA tem monitorias síncronas gratuitas pra te apoiar onde precisar: {WPP_LINK}\n\n"
            f"A gente está aqui pra qualificar e empoderar pessoas negras e indígenas no mercado tech. "
            f"Você está no caminho! 💪"
        )
    if tier == "Atenção":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Você está no {BC_FULL} e ainda tem tempo de garantir sua certificação. O encerramento "
            f"é em 12 de julho, cada semana conta. 📆\n\n"
            f"Se tiver qualquer dúvida, a PdA tem monitorias síncronas gratuitas: {WPP_LINK}\n\n"
            f"Somos uma comunidade que acelera pessoas negras e indígenas no mercado tech, "
            f"e você faz parte. Vai em frente! 💪"
        )
    if tier == "Estagnado":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Passamos para dar um alô e lembrar que o {BC_FULL} ainda está aberto até 12 de julho. 📆\n\n"
            f"Você se inscreveu no Bootcamp, isso quer dizer que quer dar um passo a mais na sua "
            f"carreira! 🧑🏾‍💻\n\n"
            f"A gente sabe que aprender sozinho(a) é difícil, por isso a PdA oferece monitorias "
            f"síncronas gratuitas para te apoiar onde precisar, viu? 🤗\n"
            f"Acesse nossa comunidade no WhatsApp: {WPP_LINK}\n\n"
            f"Junto a gente vai mais longe! 😉\n"
            f"Estamos torcendo por você! 💜"
        )
    if tier == "Recém-chegado":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Que bom que você está no {BC_FULL}! A PdA está aqui pra te apoiar nessa jornada "
            f"até 12 de julho. 📆\n\n"
            f"Acessa nossa comunidade no WhatsApp e participa das monitorias síncronas gratuitas: "
            f"{WPP_LINK}\n\n"
            f"A gente acelera pessoas negras e indígenas no mercado tech, conta com a gente! 💜"
        )
    if tier == "Formado":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Parabéns pela conquista, você concluiu o {BC_FULL}! 🎉\n\n"
            f"A PdA adoraria contar sua história para inspirar outras pessoas negras e indígenas "
            f"no mercado de tecnologia. Topa compartilhar um depoimento? Entre no nosso grupo: {WPP_LINK}\n\n"
            f"Você é prova de que é possível. Obrigada por fazer parte da nossa comunidade! 💛"
        )
    return ""

# ── HELPERS ───────────────────────────────────────────────────────────────────
def pct(v: float) -> str:
    return f"{v * 100:.0f}%"

def fmt_wpp(num: str) -> str:
    s = re.sub(r"\D", "", str(num))
    if not s: return ""
    return s if s.startswith("55") else "55" + s

def fmt_date_br(d_str: str) -> str:
    return datetime.strptime(d_str, "%Y-%m-%d").strftime("%d/%m/%Y")

def tier_badge_html(tier: str) -> str:
    c = TIER_COLORS.get(tier, {"bg": "#333", "text": "#fff", "icon": ""})
    return f'<span class="tier-badge" style="background:{c["bg"]};color:{c["text"]}">{c["icon"]} {tier}</span>'

def bucket_pill_html(bn: int) -> str:
    b = BUCKET_INFO[bn]
    return f'<span class="bucket-pill b{bn}">{b["label"]} {b["range"]}</span>'

def movimento_qualitativo(p: dict) -> str:
    if p["subiu_esta_semana"]:
        return f'<span style="color:{GREEN};font-weight:600">↑↑ +bucket esta sem</span>'
    if p["subiu_4sem"]:
        return f'<span style="color:{GREEN};font-weight:600">↑ +bucket na janela</span>'
    if len(p["historico"]) == 1:
        return f'<span style="color:{GRAY}">— sem histórico</span>'
    return f'<span style="color:{GRAY}">→ estável</span>'

def build_export_list(ppl: list, last_date_str: str) -> list:
    out = []
    for p in ppl:
        msg = generate_message(p)
        if not msg: continue
        out.append({
            "nome":                p["nome"],
            "email":               p["email"],
            "whatsapp":            fmt_wpp(p["whatsapp"]),
            "tier":                p["tier"],
            "bucket_atual":        p["bucket_atual"],
            "bucket_label":        BUCKET_INFO[p["bucket_atual"]]["range"],
            "subiu_esta_semana":   p["subiu_esta_semana"],
            "subiu_na_janela":     p["subiu_4sem"],
            "score_conversao":     round(p["score"], 2),
            "mensagem":            msg,
            "semana_referencia":   last_date_str,
        })
    out.sort(key=lambda x: -x["score_conversao"])
    return out

def build_xlsx_bytes(ppl: list, last_date_str: str) -> bytes:
    rows = []
    for p in ppl:
        rows.append({
            "Nome":             p["nome"],
            "Email":            p["email"],
            "WhatsApp":         fmt_wpp(p["whatsapp"]),
            "Tier":             p["tier"],
            "Faixa atual":      BUCKET_INFO[p["bucket_atual"]]["range"],
            "Bucket (1-5)":     p["bucket_atual"],
            "Subiu esta sem.":  "Sim" if p["subiu_esta_semana"] else "Não",
            "Subiu na janela":  "Sim" if p["subiu_4sem"] else "Não",
            "Score":            round(p["score"], 2),
            "Mensagem":         generate_message(p),
            "Semana referência": last_date_str,
        })
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Pessoas")
    return buf.getvalue()

# ── UPLOAD ────────────────────────────────────────────────────────────────────
def process_uploads(files):
    if "processed_files" not in st.session_state:
        st.session_state["processed_files"] = set()
    history = load_history()
    msgs, any_new = [], False
    for f in files:
        file_id = f"{f.name}_{f.size}"
        if file_id in st.session_state["processed_files"]:
            continue
        week_date = extract_date_from_name(f.name)
        if not week_date:
            week_date = st.text_input(f"Data para '{f.name}' (AAAA-MM-DD):", key=f"date_{f.name}")
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
            st.session_state["processed_files"].add(file_id)
            msgs.append(f"✅ {f.name} → {week_date} ({len(rows)} pessoas)")
            any_new = True
        except Exception as e:
            msgs.append(f"❌ {f.name}: {e}")
    for m in msgs: st.write(m)
    if any_new:
        save_history(history)
        st.rerun()

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
history       = load_history()
sorted_dates  = sorted(history.keys())
last_date_str = sorted_dates[-1] if sorted_dates else None
badge_text    = (f"Atualizado em {fmt_date_br(last_date_str)}" if last_date_str else "Nenhum dado carregado")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="pda-header">'
    f'<div class="pda-header-left">'
    f'{LOGO_SVG}'
    f'<div>'
    f'<h1>Bootcamp DIOxAfyaxPdA — Monitor de Formação</h1>'
    f'<p>Programadores do Amanhã · Meta: 10% do grupo de diversidade formado até 12/07/2026</p>'
    f'</div>'
    f'</div>'
    f'<span class="header-badge">{badge_text}</span>'
    f'</div>',
    unsafe_allow_html=True
)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<p style="font-family:\'Dela Gothic One\',sans-serif;color:{YELLOW};font-size:15px;margin-bottom:4px">Histórico carregado</p>', unsafe_allow_html=True)
    if history:
        st.caption(f"**{len(sorted_dates)} semana(s):**")
        for d in sorted_dates:
            st.caption(f"• {fmt_date_br(d)} — {len(history[d])} pessoas")
        st.divider()
        if st.button("🗑️ Limpar todos os dados", use_container_width=True):
            st.session_state["confirm_clear"] = True
        if st.session_state.get("confirm_clear"):
            st.warning("Tem certeza? Os dados serão apagados.")
            c1, c2 = st.columns(2)
            if c1.button("Sim, limpar", use_container_width=True, type="primary"):
                save_history({})
                st.session_state.pop("confirm_clear", None)
                st.session_state["processed_files"] = set()
                st.rerun()
            if c2.button("Cancelar", use_container_width=True):
                st.session_state.pop("confirm_clear", None)
                st.rerun()
    else:
        st.caption("Nenhum dado carregado ainda.")

# ── UPLOAD UI ─────────────────────────────────────────────────────────────────
with st.expander("📂 Carregar relatório semanal da DIO", expanded=not bool(history)):
    st.caption("Selecione um ou mais arquivos CSV/XLSX. A data é detectada automaticamente pelo nome do arquivo.")
    uploaded = st.file_uploader(
        "Arquivos da DIO", type=["csv","xlsx","xls"],
        accept_multiple_files=True, label_visibility="collapsed", key="uploader",
    )
    if uploaded:
        process_uploads(uploaded)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not history:
    st.markdown(f"""
    <div class="empty-state">
      <h2>👆 Carregue um relatório para começar</h2>
      <p>Use o painel acima para selecionar os arquivos CSV ou XLSX baixados da DIO.<br>
      Você pode selecionar múltiplos arquivos de uma vez para carregar o histórico completo.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── BUILD DATA ────────────────────────────────────────────────────────────────
people     = build_people(history)
div_ppl    = [p for p in people if p["diversidade"]]
nao_div    = [p for p in people if not p["diversidade"]]
total      = len(people)
total_div  = len(div_ppl)
total_nao  = len(nao_div)
formados_div = sum(1 for p in div_ppl if p["graduado"])
formados_nao = sum(1 for p in nao_div if p["graduado"])
meta       = max(1, -(-total_div // 10))
last_date  = datetime.strptime(last_date_str, "%Y-%m-%d").date()
weeks_left = max(0, int((BOOTCAMP_END - last_date).days / 7))

# Projeção: candidatos com chance realista de fechar até 12/07
#   • Já graduados (definitivos)
#   • Quase lá — bucket 4, faltam só os últimos módulos
#   • Avançando — bucket 3 que está em movimento (subiu de faixa na janela)
proj_form = sum(
    1 for p in div_ppl
    if p["graduado"]
    or p["bucket_atual"] == 4
    or (p["bucket_atual"] == 3 and p["subiu_4sem"])
)
gap_meta  = max(0, meta - proj_form)
hit_meta  = proj_form >= meta

# Taxas de graduação
taxa_div  = (formados_div / total_div * 100) if total_div else 0
taxa_nao  = (formados_nao / total_nao * 100) if total_nao else 0
delta_pp  = taxa_div - taxa_nao

# Tier counts (diversidade)
tier_counts = {t: sum(1 for p in div_ppl if p["tier"] == t) for t in TIER_COLORS}

# Momentum (diversidade)
subiu_semana   = sum(1 for p in div_ppl if p["subiu_esta_semana"])
subiu_4sem     = sum(1 for p in div_ppl if p["subiu_4sem"])
parados_inicio = sum(1 for p in div_ppl
                     if len(p["historico"]) >= 2 and p["bucket_atual"] == 1 and not p["subiu_4sem"])

# Comparativo % Div vs Não-Div (usando apenas quem tem 2+ snapshots para "subiu")
nao_div_multi = [p for p in nao_div if len(p["historico"]) >= 2]
subiu_4sem_nao = sum(1 for p in nao_div_multi if p["subiu_4sem"])
subiu_semana_nao = sum(1 for p in nao_div_multi if p["subiu_esta_semana"])

subiu_4sem_div_pct   = (subiu_4sem / total_div * 100) if total_div else 0
subiu_4sem_nao_pct   = (subiu_4sem_nao / len(nao_div_multi) * 100) if nao_div_multi else 0
subiu_semana_div_pct = (subiu_semana / total_div * 100) if total_div else 0
subiu_semana_nao_pct = (subiu_semana_nao / len(nao_div_multi) * 100) if nao_div_multi else 0

em_inicio_div = sum(1 for p in div_ppl if p["bucket_atual"] == 1)
em_inicio_nao = sum(1 for p in nao_div if p["bucket_atual"] == 1)
em_inicio_div_pct = (em_inicio_div / total_div * 100) if total_div else 0
em_inicio_nao_pct = (em_inicio_nao / total_nao * 100) if total_nao else 0

quasela_ou_mais_div = sum(1 for p in div_ppl if p["bucket_atual"] >= 4)
quasela_ou_mais_nao = sum(1 for p in nao_div if p["bucket_atual"] >= 4)
quasela_ou_mais_div_pct = (quasela_ou_mais_div / total_div * 100) if total_div else 0
quasela_ou_mais_nao_pct = (quasela_ou_mais_nao / total_nao * 100) if total_nao else 0

pct_div_total = round(total_div / total * 100) if total else 0

# ═══════════════════════════════════════════════════════════════════
# BLOCO 1 — HERO (Situação da Meta)
# ═══════════════════════════════════════════════════════════════════
proj_class = "green" if hit_meta else "red"
proj_msg = ("Acima da meta" if hit_meta else f"Faltam {gap_meta} para a meta")
alert_class = "green" if hit_meta else ""
alert_text = ("✅ No ritmo atual, a meta <strong>será atingida</strong>. Continue acompanhando 'Quase lá'."
              if hit_meta else
              f"⚠️ No ritmo atual, a meta <strong>não será atingida</strong>. Faltam {gap_meta} pessoas. "
              f"Foque em 'Quase lá' e 'Alta Prioridade'.")

st.markdown(f"""
<div class="hero-card">
  <div class="hero-grid">
    <div class="hero-block">
      <p class="hero-eye">⏳ Semanas Restantes</p>
      <p class="hero-num">{weeks_left}</p>
      <p class="hero-sub">até 12/07/2026<br>Tempo para agir é agora</p>
    </div>
    <div class="hero-block">
      <p class="hero-eye">🎯 Progresso da Meta</p>
      <p><span class="hero-num">{formados_div}</span><span class="hero-meta-after"> / {meta}</span></p>
      <p class="hero-sub">formados do grupo de diversidade</p>
      <div class="prog-track"><div class="prog-fill" style="width:{min(100, formados_div/meta*100):.1f}%"></div></div>
      <div class="prog-labels"><span>Atual: {taxa_div:.1f}%</span><span>Meta: {meta} pessoas (10%)</span></div>
    </div>
    <div class="hero-block">
      <p class="hero-eye">📈 Projeção no Ritmo Atual</p>
      <p class="hero-num {proj_class}">{proj_form}</p>
      <p class="hero-sub">formados projetados até 12/07<br><strong style="color:{GREEN if hit_meta else RED}">{proj_msg}</strong></p>
      <div class="hero-alert {alert_class}">{alert_text}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# COMPARATIVO TAXA DE GRADUAÇÃO Div vs Não-Div
# ═══════════════════════════════════════════════════════════════════
verdict_class = "verdict-up" if delta_pp >= 0 else "verdict-down"
verdict_icon  = "✅" if delta_pp >= 0 else "⚠️"
verdict_text = (
    f"A taxa de graduação da diversidade está <strong>{abs(delta_pp):.2f} p.p. acima</strong> "
    f"do grupo não-diversidade. Resultado consistente com a missão da PdA."
    if delta_pp >= 0 else
    f"A taxa de graduação da diversidade está <strong>{abs(delta_pp):.2f} p.p. abaixo</strong> "
    f"do grupo não-diversidade. Necessário intensificar engajamento."
)

st.markdown(f"""
<div class="comp-grad">
  <div>
    <p class="comp-grad-eye">Taxa de Graduação — Diversidade</p>
    <p class="comp-grad-num">{taxa_div:.2f}%</p>
    <p class="comp-grad-sub">{formados_div} formados de {total_div} inscritos</p>
  </div>
  <div>
    <p class="comp-grad-eye">Taxa de Graduação — Não-Diversidade</p>
    <p class="comp-grad-num gray">{taxa_nao:.2f}%</p>
    <p class="comp-grad-sub">{formados_nao} formados de {total_nao} inscritos</p>
  </div>
  <div class="comp-grad-verdict {verdict_class}">{verdict_icon} {verdict_text}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 2 — Distribuição + Momentum
# ═══════════════════════════════════════════════════════════════════
st.markdown(f'<p class="section-title">Distribuição do Grupo</p>'
            f'<p class="section-sub">{total_div:,} pessoas · grupo de diversidade · {pct_div_total}% do total de inscritos</p>'.replace(",", "."),
            unsafe_allow_html=True)

col_donut, col_momentum = st.columns([1, 2])

with col_donut:
    # Donut com Plotly
    labels, values, colors = [], [], []
    for t in TIER_ORDER:
        n = tier_counts.get(t, 0)
        if n == 0: continue
        labels.append(f"{TIER_COLORS[t]['icon']} {t}")
        values.append(n)
        colors.append(TIER_COLORS[t]['text'])

    fig_donut = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color=CARD_BG, width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} pessoas<br>%{percent}<extra></extra>",
    ))
    fig_donut.update_layout(
        showlegend=False, height=240, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        annotations=[dict(text=f"<b style='color:{YELLOW};font-size:24px'>{total_div:,}</b><br><span style='color:{GRAY};font-size:11px'>total</span>".replace(",", "."),
                          x=0.5, y=0.5, showarrow=False, font=dict(family="Dela Gothic One"))]
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    # Legend HTML
    legend_html = ""
    for t in TIER_ORDER:
        n = tier_counts.get(t, 0)
        if n == 0: continue
        pct_t = (n / total_div * 100) if total_div else 0
        c = TIER_COLORS[t]
        legend_html += (f'<div class="legend-row">'
                        f'<span class="legend-dot" style="background:{c["text"]}"></span>'
                        f'<span class="legend-name">{c["icon"]} {t}</span>'
                        f'<span class="legend-num">{n:,}</span>'.replace(",", ".") +
                        f'<span class="legend-pct">{pct_t:.0f}%</span></div>')
    st.markdown(legend_html, unsafe_allow_html=True)

    # Critérios de classificação (expander)
    with st.expander("ℹ️ Ver critérios de classificação", expanded=False):
        criteria_html = '<div style="font-size:11.5px;line-height:1.6">'
        for t in TIER_ORDER:
            if tier_counts.get(t, 0) == 0:
                continue
            c = TIER_COLORS[t]
            criteria_html += (
                f'<div style="margin-bottom:10px;padding:8px 12px;background:{DARK_BG};border-left:3px solid {c["text"]};border-radius:4px">'
                f'<div style="color:{c["text"]};font-weight:600;margin-bottom:3px">{c["icon"]} {t}</div>'
                f'<div style="color:{WHITE}">{TIER_CRITERIA[t]}</div>'
                f'</div>'
            )
        criteria_html += '</div>'
        st.markdown(criteria_html, unsafe_allow_html=True)

        # Também mostra os 5 buckets de progresso
        st.markdown(f'<p style="margin-top:14px;margin-bottom:6px;font-weight:600;color:{YELLOW};font-size:12px">Faixas de progresso (coluna DIO)</p>', unsafe_allow_html=True)
        buckets_html = '<div style="font-size:11px;line-height:1.6">'
        for bn, info in BUCKET_INFO.items():
            buckets_html += (
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
                f'<span class="bucket-pill b{bn}">{info["label"]}</span>'
                f'<span style="color:{GRAY}">{info["range"]} do bootcamp</span>'
                f'</div>'
            )
        buckets_html += '</div>'
        st.markdown(buckets_html, unsafe_allow_html=True)

with col_momentum:
    sem_prev = fmt_date_br(sorted_dates[-2]) if len(sorted_dates) >= 2 else "—"
    sem_curr = fmt_date_br(last_date_str)
    sem_ini  = fmt_date_br(sorted_dates[0])

    st.markdown(f"""
    <div style="font-family:'Dela Gothic One',sans-serif;color:{YELLOW};font-size:15px;margin-bottom:4px">Momentum do Grupo</div>
    <div style="font-size:11px;color:{GRAY};margin-bottom:14px">Movimento entre faixas ao longo das {len(sorted_dates)} semanas ({sem_ini} → {sem_curr})</div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">🚀 Subiram esta semana</p>
          <p class="kpi-value orange">{subiu_semana}</p>
          <p class="kpi-sub">pularam de bucket entre {sem_prev} e {sem_curr}</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">📈 Subiram nas {len(sorted_dates)} semanas</p>
          <p class="kpi-value green">{subiu_4sem}</p>
          <p class="kpi-sub">pularam ≥1 bucket desde {sem_ini}</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
          <p class="kpi-label">🔴 Parados em "Em início"</p>
          <p class="kpi-value red">{parados_inicio}</p>
          <p class="kpi-sub">há toda a janela em 0–24% sem se mexer</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# COMPARATIVO Diversidade vs Não-Diversidade
# ═══════════════════════════════════════════════════════════════════
def cmp_row_html(label, sublabel, div_pct, nao_pct, higher_is_better):
    delta = div_pct - nao_pct
    win = (delta > 0) if higher_is_better else (delta < 0)
    if abs(delta) < 1:
        color, icon = GRAY, "≈"
    elif win:
        color, icon = GREEN, "✅"
    else:
        color, icon = RED, "⚠️"
    max_pct = max(div_pct, nao_pct, 10)
    div_w = (div_pct / max_pct) * 100
    nao_w = (nao_pct / max_pct) * 100
    sign = "+" if delta > 0 else ""
    return (
        f'<div class="cmp-row">'
        f'<div class="cmp-header">'
        f'<div><div class="cmp-label">{label}</div><div class="cmp-sublabel">{sublabel}</div></div>'
        f'<div class="cmp-delta" style="color:{color}">{icon} Δ {sign}{delta:.1f} p.p.</div>'
        f'</div>'
        f'<div class="cmp-bar-row">'
        f'<div class="cmp-name div">🎯 Diversidade</div>'
        f'<div class="cmp-bar"><div style="width:{div_w:.1f}%;background:{YELLOW}">{div_pct:.1f}%</div></div>'
        f'</div>'
        f'<div class="cmp-bar-row">'
        f'<div class="cmp-name nao">⚪ Não-Diversidade</div>'
        f'<div class="cmp-bar"><div style="width:{nao_w:.1f}%;background:{GRAY}">{nao_pct:.1f}%</div></div>'
        f'</div>'
        f'</div>'
    )

st.markdown(f'<p class="section-title">⚖️ Diversidade vs Não-Diversidade — Quem está avançando mais rápido?</p>'
            f'<p class="section-sub">Comparativo proporcional (% dentro de cada grupo) das principais métricas de movimento e engajamento</p>',
            unsafe_allow_html=True)

cmp_html = '<div style="background:'+CARD_BG+';border:1px solid '+CARD_BORDER+';border-radius:12px;padding:24px">'
cmp_html += cmp_row_html(
    "Avançaram de faixa nas últimas semanas",
    f"Pulou ≥1 bucket entre {fmt_date_br(sorted_dates[0])} e {fmt_date_br(last_date_str)}",
    subiu_4sem_div_pct, subiu_4sem_nao_pct, higher_is_better=True
)
cmp_html += cmp_row_html(
    "Subiram esta semana",
    f"Pulou de bucket entre {sem_prev} e {fmt_date_br(last_date_str)}",
    subiu_semana_div_pct, subiu_semana_nao_pct, higher_is_better=True
)
cmp_html += cmp_row_html(
    "Já em 'Quase lá' ou Formadas",
    "Pessoas na faixa 75–99% ou já graduadas — base potencial de conversão",
    quasela_ou_mais_div_pct, quasela_ou_mais_nao_pct, higher_is_better=True
)
cmp_html += cmp_row_html(
    "Ainda em 'Em início'",
    "Pessoas na faixa 0–24% — quanto menor, melhor",
    em_inicio_div_pct, em_inicio_nao_pct, higher_is_better=False
)
cmp_html += '</div>'
st.markdown(cmp_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# FUNIL DE PROGRESSÃO (5 buckets exclusivos)
# ═══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f'<p class="section-title">📊 Funil de Progressão — Diversidade</p>'
            f'<p class="section-sub">Cada pessoa está em exatamente uma faixa · comparativo com a semana anterior ({sem_prev})</p>',
            unsafe_allow_html=True)

funnel_curr = [sum(1 for p in div_ppl if p["bucket_atual"] == b) for b in [1, 2, 3, 4, 5]]
funnel_prev = [0, 0, 0, 0, 0]
if len(sorted_dates) >= 2:
    prev_date = sorted_dates[-2]
    for p in div_ppl:
        prog_prev, grad_prev = None, False
        for h in p["historico"]:
            if h["semana"] <= prev_date:
                prog_prev = h["progresso"]
        if prog_prev is not None:
            # Para o snapshot anterior, ainda usamos graduado=True só se já era graduado na época
            # Como não temos "graduado por snapshot", aproximamos: se progresso atingiu 1 antes e está graduado agora, considera graduado prev se já tinha histórico ≥ 1
            b = bucket_of(prog_prev, p["graduado"] and prog_prev >= 1.0)
            funnel_prev[b - 1] += 1

max_funil = max(funnel_curr + funnel_prev + [1])

funnel_html = f'<div style="background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:12px;padding:24px">'
for i in range(5):
    bn = i + 1
    info = BUCKET_INFO[bn]
    curr = funnel_curr[i]
    prev = funnel_prev[i]
    d_abs = curr - prev
    d_pct = (d_abs / prev * 100) if prev > 0 else 0
    w = max((curr / max_funil * 100), 4)
    d_class = "pos" if d_abs > 0 else ("neg" if d_abs < 0 else "zero")
    sign = "+" if d_abs > 0 else ""
    curr_fmt = f"{curr:,}".replace(",", ".")
    funnel_html += (
        f'<div class="funil-row">'
        f'<div class="funil-label">{info["label"]}<small>{info["range"]} do bootcamp</small></div>'
        f'<div class="funil-bar"><div style="width:{w:.1f}%;background:{info["color"]}">{curr_fmt}</div></div>'
        f'<div class="funil-delta {d_class}"><span class="abs">{sign}{d_abs}</span><span class="pct">{d_pct:.1f}% sem ant.</span></div>'
        f'</div>'
    )

funnel_html += (
    f'<div style="margin-top:18px;padding:12px 16px;background:rgba(245,166,35,.12);'
    f'border-left:3px solid {ORANGE};border-radius:6px;font-size:12px;color:{ORANGE}">'
    f'💡 <strong>Foco prioritário:</strong> as {funnel_curr[3]} pessoas em "🟠 Quase lá" '
    f'são as candidatas mais prováveis de fechar a meta até 12/07.'
    f'</div></div>'
)
st.markdown(funnel_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 3 — Contatos da Semana (Quase lá + Alta Prioridade)
# ═══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
prioridades = [p for p in div_ppl if p["tier"] in ("Quase lá", "Alta Prioridade")]
prioridades.sort(key=lambda p: -p["score"])

st.markdown(f'<p class="section-title">📞 Contatos desta semana — Prioridade Máxima</p>'
            f'<p class="section-sub">Pessoas em "Quase lá" + "Alta Prioridade", ordenadas por score de conversão. Mostrando os top 10.</p>',
            unsafe_allow_html=True)

col_info, col_dl1, col_dl2 = st.columns([3, 1, 1])
with col_info:
    st.caption(f"Mostrando {min(10, len(prioridades))} de **{len(prioridades)}** contatos prioritários")
with col_dl1:
    if prioridades:
        export = build_export_list(prioridades, last_date_str)
        st.download_button(
            "⬇️ JSON (n8n)",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name=f"contatos_prioridade_{last_date_str}.json",
            mime="application/json",
            use_container_width=True,
        )
with col_dl2:
    if prioridades:
        st.download_button(
            "⬇️ XLSX",
            data=build_xlsx_bytes(prioridades, last_date_str),
            file_name=f"contatos_prioridade_{last_date_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

for p in prioridades[:10]:
    info = TIER_COLORS[p["tier"]]
    bucket_info = BUCKET_INFO[p["bucket_atual"]]
    if p["subiu_esta_semana"]:
        mov = "↑↑ subiu esta semana"
    elif p["subiu_4sem"]:
        mov = "↑ avançou na janela"
    else:
        mov = "→ estável"

    msg_text = generate_message(p)
    st.markdown(
        f'<div class="contact-card">'
        f'<div style="display:grid;grid-template-columns:1fr 100px;gap:18px;align-items:center">'
        f'<div>'
        f'<div class="contact-name">{p["nome"]} {tier_badge_html(p["tier"])}</div>'
        f'<div class="contact-meta">📧 {p["email"]} · 📱 {fmt_wpp(p["whatsapp"])} · faixa: {bucket_info["range"]} · {mov}</div>'
        f'</div>'
        f'<div>'
        f'<div class="contact-score">{p["score"]}</div>'
        f'<div style="font-size:10px;color:{GRAY};text-align:right">score conversão</div>'
        f'</div>'
        f'</div>'
        f'<details style="margin-top:10px">'
        f'<summary style="cursor:pointer;font-size:11px;color:{GRAY}">📝 ver mensagem sugerida</summary>'
        f'<div class="msg-box">{msg_text}</div>'
        f'</details>'
        f'</div>',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════════════
# BLOCO 4 — Evolução Semanal (Área empilhada 100%)
# ═══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f'<p class="section-title">📈 Evolução Semanal — Distribuição por Faixa</p>'
            f'<p class="section-sub">% de pessoas em cada bucket ao longo das {len(sorted_dates)} semanas · diversidade · mostra se o grupo está migrando das faixas iniciais para as avançadas</p>',
            unsafe_allow_html=True)

# Para cada snapshot, contar pessoas em cada bucket NAQUELA data
evo_data = {b: [] for b in [1, 2, 3, 4, 5]}
evo_dates_fmt = []
evo_totals = []
for d in sorted_dates:
    counts = [0, 0, 0, 0, 0]
    total_d = 0
    for p in div_ppl:
        prog_at = None
        for h in p["historico"]:
            if h["semana"] <= d:
                prog_at = h["progresso"]
        if prog_at is not None:
            grad_at = p["graduado"] and prog_at >= 1.0
            b = bucket_of(prog_at, grad_at)
            counts[b - 1] += 1
            total_d += 1
    for i, c in enumerate(counts):
        pct_val = (c / total_d * 100) if total_d else 0
        evo_data[i + 1].append(pct_val)
    evo_dates_fmt.append(fmt_date_br(d))
    evo_totals.append(total_d)

fig_evo = go.Figure()
# Adiciona de baixo pra cima: bucket 1 (Em início) na base
for b in [1, 2, 3, 4, 5]:
    pcts = evo_data[b]
    # rótulo só se a fatia for grande o suficiente pra ler
    labels = [f"{p:.0f}%" if p >= 4 else "" for p in pcts]
    fig_evo.add_trace(go.Bar(
        x=evo_dates_fmt, y=pcts,
        name=f"{BUCKET_INFO[b]['label']} ({BUCKET_INFO[b]['range']})",
        marker=dict(color=BUCKET_INFO[b]['color'], line=dict(color=CARD_BG, width=1)),
        text=labels, textposition="inside", insidetextanchor="middle",
        textfont=dict(color=ROXO, size=11, family="IBM Plex Sans"),
        hovertemplate=f"<b>{BUCKET_INFO[b]['label']}</b><br>%{{x}}<br>%{{y:.1f}}%<extra></extra>",
    ))

fig_evo.update_layout(
    barmode="stack", bargap=0.35,
    height=420,
    paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
    font=dict(color=WHITE, family="IBM Plex Sans"),
    margin=dict(t=30, b=40, l=60, r=20),
    yaxis=dict(title="% do grupo", ticksuffix="%", range=[0, 100], gridcolor="#5a1060", color=GRAY),
    xaxis=dict(gridcolor="#5a1060", color=GRAY, type="category"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)),
    hovermode="x unified",
)
st.plotly_chart(fig_evo, use_container_width=True, config={"displayModeBar": False})

# Leitura automática
if len(sorted_dates) >= 2:
    ini_pct_b1 = evo_data[1][0]
    last_pct_b1 = evo_data[1][-1]
    ini_pct_b2 = evo_data[2][0]
    last_pct_b2 = evo_data[2][-1]
    delta_b1 = last_pct_b1 - ini_pct_b1
    delta_b2 = last_pct_b2 - ini_pct_b2
    leitura = (f"📊 <strong>Leitura:</strong> a faixa 'Em início' foi de {ini_pct_b1:.1f}% ({evo_dates_fmt[0]}) "
               f"para {last_pct_b1:.1f}% ({evo_dates_fmt[-1]}) — variação de {delta_b1:+.1f} p.p. "
               f"A faixa 'Engajadas' foi de {ini_pct_b2:.1f}% para {last_pct_b2:.1f}% ({delta_b2:+.1f} p.p).")
    st.markdown(f"""
    <div style="padding:12px 16px;background:rgba(78,203,113,.12);border-left:3px solid {GREEN};border-radius:6px;font-size:12px;color:{GREEN};margin-top:14px">
      {leitura}
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 5 — Lista Completa por Tier
# ═══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown(f'<p class="section-title">📋 Lista Completa por Tier</p>'
            f'<p class="section-sub">Pessoas do grupo de diversidade, agrupadas por tier. Cada aba pode ser exportada separadamente em JSON (n8n) e XLSX.</p>',
            unsafe_allow_html=True)

# Abas dinâmicas (mostra só tiers com pessoas + Todos)
tab_labels = []
tab_data = []
for t in TIER_ORDER:
    n = tier_counts.get(t, 0)
    if n == 0: continue
    info = TIER_COLORS[t]
    tab_labels.append(f"{info['icon']} {t} ({n})")
    tab_data.append([p for p in div_ppl if p["tier"] == t])
tab_labels.append(f"Todos ({total_div})")
tab_data.append(list(div_ppl))

tabs = st.tabs(tab_labels)

for i, tab in enumerate(tabs):
    with tab:
        ppl = tab_data[i]
        ppl = sorted(ppl, key=lambda p: (-p["bucket_atual"], p["nome"]))

        # Botões de export
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.caption(f"{len(ppl)} pessoas nessa aba")
        with c2:
            if ppl:
                exp = build_export_list(ppl, last_date_str)
                st.download_button(
                    "⬇️ JSON (n8n)",
                    data=json.dumps(exp, ensure_ascii=False, indent=2),
                    file_name=f"lista_{tab_labels[i].split(' ')[1].lower() if ' ' in tab_labels[i] else 'todos'}_{last_date_str}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"json_{i}",
                )
        with c3:
            if ppl:
                st.download_button(
                    "⬇️ XLSX",
                    data=build_xlsx_bytes(ppl, last_date_str),
                    file_name=f"lista_{tab_labels[i].split(' ')[1].lower() if ' ' in tab_labels[i] else 'todos'}_{last_date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"xlsx_{i}",
                )

        # Tabela
        rows_html = ""
        for idx, p in enumerate(ppl[:200]):
            rows_html += (
                f'<tr>'
                f'<td>{idx+1}</td>'
                f'<td><strong>{p["nome"]}</strong></td>'
                f'<td>{p["email"]}<br><span class="td-meta">{fmt_wpp(p["whatsapp"])}</span></td>'
                f'<td>{bucket_pill_html(p["bucket_atual"])}</td>'
                f'<td>{movimento_qualitativo(p)}</td>'
                f'<td>{tier_badge_html(p["tier"])}</td>'
                f'</tr>'
            )
        if len(ppl) > 200:
            rows_html += (
                f'<tr><td colspan="6" style="text-align:center;color:{GRAY};padding:14px">'
                f'... + {len(ppl) - 200} pessoas (use o download XLSX para a lista completa)</td></tr>'
            )

        table_html = (
            '<table class="full-table">'
            '<thead><tr>'
            '<th>#</th><th>Nome</th><th>Contato</th><th>Faixa atual</th><th>Avanço (janela)</th><th>Tier</th>'
            '</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            '</table>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:32px;padding:24px;background:{DARK_BG};border-radius:8px;text-align:center;font-size:12px;color:{GRAY}">
  💜 Programadores do Amanhã · Bootcamp DIOxAfyaxPdA — Monitor de Formação
</div>
""", unsafe_allow_html=True)
