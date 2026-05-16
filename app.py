import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import date, datetime
from io import BytesIO, StringIO
import plotly.graph_objects as go

st.set_page_config(
    page_title="Monitor de Formação · Bootcamp Afya",
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
WPP_LINK    = "https://chat.whatsapp.com/Cf2CicuO1Al1jVoYFe5i0l"

BOOTCAMP_END   = date(2026, 7, 12)
STORAGE_PATH   = os.path.join(os.path.dirname(__file__), "data", "history.json")
GRAD_THRESHOLD = 0.70

TIER_COLORS = {
    "Formado":         {"bg": "#1a4d2e", "text": "#4ecb71", "icon": "✅"},
    "No Caminho":      {"bg": "#0d3d4d", "text": "#5bc8e0", "icon": "🟢"},
    "Alta Prioridade": {"bg": "#4a1050", "text": "#eddc11", "icon": "🎯"},
    "Atenção":         {"bg": "#4d3a00", "text": "#f5c842", "icon": "🟡"},
    "Estagnado":       {"bg": "#4d1a1a", "text": "#e24b4a", "icon": "🔴"},
    "Abandono":        {"bg": "#2a2a2a", "text": "#9a8fa5", "icon": "⚫"},
}

TIER_CRITERIA = {
    "Alta Prioridade": "Está progredindo semana a semana. Projeção até jul/26 entre 40% e 69%. Um empurrão pode converter.",
    "Atenção":         "Progredindo, mas em ritmo lento. Projeção abaixo de 40%. Check-in para identificar barreiras.",
    "No Caminho":      "Projeção ≥ 70%. No ritmo atual, vai se formar. Mensagem de celebração.",
    "Estagnado":       "Sem progresso há 2 ou mais semanas consecutivas. Máximo 1 contato.",
    "Formado":         "Graduado(a) = Sim no relatório da DIO. Convidar para depoimento.",
    "Abandono":        "Nunca progrediu desde a semana 1. Não contatar.",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', sans-serif !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 0 !important; max-width: 1280px; }}

.pda-header {{
    background: {DARK_BG}; margin: -1rem -1rem 2rem -1rem;
    padding: 22px 40px; display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 12px;
    border-bottom: 2px solid {YELLOW};
}}
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
.hero-sub {{ font-size:12px; color:{GRAY}; line-height:1.4; }}
.hero-alert {{ background:#4d1a00; border:1px solid {ORANGE}; border-radius:8px; padding:10px 14px; font-size:12px; color:#f5c842; margin-top:12px; }}

.prog-labels {{ display:flex; justify-content:space-between; font-size:11px; color:{GRAY}; margin:12px 0 5px 0; }}
.prog-track {{ background:{CARD_BORDER}; border-radius:6px; height:10px; overflow:hidden; }}
.prog-fill {{ height:100%; border-radius:6px; background:linear-gradient(90deg,{GREEN},#7de89a); }}

.kpi-card {{ background:{CARD_BG}; border-radius:12px; padding:18px; border:1px solid {CARD_BORDER}; text-align:left; }}
.kpi-label {{ font-size:10px; font-weight:600; color:{GRAY}; text-transform:uppercase; letter-spacing:.6px; margin-bottom:6px; }}
.kpi-value {{ font-family:'Dela Gothic One',sans-serif !important; font-size:32px; color:{YELLOW}; line-height:1; margin-bottom:4px; }}
.kpi-value.green {{ color:{GREEN}; }}
.kpi-value.red {{ color:{RED}; }}
.kpi-sub {{ font-size:11px; color:#7a6f85; }}

.section-title {{ font-family:'Dela Gothic One',sans-serif !important; color:{YELLOW}; font-size:16px; margin:0 0 2px 0; }}
.section-sub {{ font-size:11px; color:{GRAY}; margin:0 0 14px 0; }}

.tier-badge {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600; white-space:nowrap; }}

.contact-card {{
    background:#270028; border-radius:10px; border:1px solid #4a0050;
    padding:16px 18px; margin-bottom:10px;
}}
.contact-name {{ font-weight:600; font-size:13px; color:{WHITE}; }}
.contact-meta {{ font-size:11px; color:#7a6f85; margin-top:2px; }}
.pbar-wrap {{ display:flex; align-items:center; gap:8px; }}
.pbar {{ width:70px; height:5px; background:{CARD_BORDER}; border-radius:3px; overflow:hidden; display:inline-block; }}
.pfill {{ height:100%; border-radius:3px; }}
.adv-badge {{ background:#1a4d2e; color:{GREEN}; font-size:11px; font-weight:600; padding:3px 10px; border-radius:6px; white-space:nowrap; }}

.msg-box {{ background:{DARK_BG}; border-radius:8px; border:1px solid #3a003d; padding:14px 16px; font-size:12px; color:#c0b4d8; line-height:1.8; margin-top:12px; white-space:pre-wrap; }}

.full-table {{ width:100%; border-collapse:collapse; font-size:12px; }}
.full-table thead th {{ background:{DARK_BG}; padding:10px 12px; text-align:left; font-size:10px; font-weight:600; color:{GRAY}; text-transform:uppercase; letter-spacing:.5px; border-bottom:1px solid {CARD_BORDER}; white-space:nowrap; }}
.full-table tbody tr {{ border-bottom:1px solid #4a0050; }}
.full-table tbody tr:hover {{ background:#4a0050; }}
.full-table tbody td {{ padding:10px 12px; vertical-align:top; color:{WHITE}; }}
.td-meta {{ font-size:11px; color:#7a6f85; }}
.td-msg {{ font-size:11px; color:#9a8fa5; line-height:1.5; max-width:280px; }}

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

# ── FILE PARSING ──────────────────────────────────────────────────────────────
def extract_date_from_name(name: str) -> str | None:
    m = re.search(r"(\d{4}-\d{2}-\d{2})T", name)
    if m: return m.group(1)
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

# ── DATA PROCESSING ───────────────────────────────────────────────────────────
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

    last_date  = datetime.strptime(sorted_dates[-1], "%Y-%m-%d").date()
    weeks_left = max(0.0, (BOOTCAMP_END - last_date).days / 7)

    result = []
    for p in people.values():
        hist   = sorted(p["historico"], key=lambda h: h["semana"])
        progs  = [h["progresso"] for h in hist]
        deltas = [progs[i] - progs[i-1] for i in range(1, len(progs))]

        p["progresso_atual"] = progs[-1] if progs else 0.0
        recent = deltas[-3:] if deltas else []
        p["velocidade"]   = sum(recent) / len(recent) if recent else 0.0
        p["delta_ultimo"] = deltas[-1] if deltas else None
        p["delta_penult"] = deltas[-2] if len(deltas) >= 2 else None

        stagnado = 0
        for d in reversed(deltas):
            if d < 0.005: stagnado += 1
            else: break
        p["semanas_estagnado"] = stagnado
        p["nunca_progrediu"]   = bool(deltas) and all(d < 0.005 for d in deltas)

        vel_pos = max(0.0, p["velocidade"])
        p["projetado"] = min(1.0, p["progresso_atual"] + vel_pos * weeks_left)
        gap = max(0.0, GRAD_THRESHOLD - p["projetado"])
        p["score"] = p["velocidade"] * (1 - gap) * 100 if p["velocidade"] > 0 else 0.0

        if p["graduado"]:                                            tier = "Formado"
        elif p["nunca_progrediu"] and p["semanas_estagnado"] >= 2:  tier = "Abandono"
        elif p["semanas_estagnado"] >= 2:                           tier = "Estagnado"
        elif p["projetado"] >= GRAD_THRESHOLD:                      tier = "No Caminho"
        elif p["velocidade"] > 0 and p["projetado"] >= 0.40:        tier = "Alta Prioridade"
        else:                                                        tier = "Atenção"
        p["tier"] = tier
        result.append(p)
    return result

# ── MESSAGE GENERATION ────────────────────────────────────────────────────────
def generate_message(p: dict) -> str:
    nome = p["nome"].split()[0] if p["nome"] else "você"
    tier = p["tier"]
    if tier == "Alta Prioridade":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Você está na reta final do Bootcamp DIOxAfyaxPdA e tem tudo para garantir sua certificação em "
            f"Automação de Dados com IA antes do encerramento em 12 de julho. Não para agora!📆\n\n"
            f"Você não precisa chegar lá sozinho(a). A PdA oferece monitorias síncronas de todo o conteúdo "
            f"do bootcamp. Acesse o grupo do WhatsApp e participe quando quiser: {WPP_LINK}\n\n"
            f"A PdA está aqui para qualificar e empoderar pessoas negras e indígenas a construíremcarreira no mercado da tecnologia. Você já "
            f"está mostrando que tem o que precisa para chegar lá. Vai até o fim! 🚀"
        )
    elif tier == "Atenção":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Você está no Bootcamp DIOxAfyaxPdA e ainda tem tempo de garantir sua certificação em "
            f"Automação de Dados com IA. O encerramento é em 12 de julho e cada semana conta.📆\n\n"
            f"Sabia que a PdA oferece monitorias síncronas de todo o conteúdo? Se tiver dúvida em algum "
            f"módulo ou quiser avançar mais rápido, acesse o grupo do WhatsApp: {WPP_LINK}\n\n"
            f"Somos uma comunidade que acelera pessoas negras e indígenas no mercado de tecnologia, "
            f"e você faz parte disso. Vai em frente! 💪"
        )
    elif tier == "No Caminho":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Você está indo muito bem no Bootcamp DIOxAfyaxPdA, parabéns pela dedicação!\n\n"
            f"Continue nesse ritmo e a certificação em Automação de Dados com IA é sua até 12 de julho. "
            f"Se quiser acelerar ainda mais, a PdA tem monitorias síncronas para você: {WPP_LINK}\n\n"
            f"A PdA está aqui para qualificar e empoderar pessoas negras e indígenas a construíremcarreira no mercado da tecnologia. "
            f"Você está chegando lá! 🌟"
        )
    elif tier == "Estagnado":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Passamos para dar um alô e lembrar que o Bootcamp DIOxAfyaxPdA ainda está aberto até 12 de julho.\n\n"
            f"A gente sabe que aprender sozinho(a) é difícil, por isso a PdA oferece monitorias síncronas para te apoiar onde precisar, viu? "
            f"Acesse o grupo do WhatsApp: {WPP_LINK}\n\n"
            f"Estamos torcendo por você! 💜"
        )
    elif tier == "Formado":
        return (
            f"Oi, {nome}! 👋\n\n"
            f"Parabéns pela conquista, você concluiu o Bootcamp Afya! 🎉\n\n"
            f"A PdA adoraria contar sua história para inspirar outras pessoas negras e indígenas no "
            f"mercado de tecnologia. Topa compartilhar um depoimento? Entre no nosso grupo: {WPP_LINK}\n\n"
            f"Você é prova de que é possível. Obrigada por fazer parte da nossa comunidade! 💛"
        )
    return ""

# ── HELPERS ───────────────────────────────────────────────────────────────────
def pct(v: float) -> str:
    return f"{v * 100:.0f}%"

def prog_color(v: float) -> str:
    if v >= 0.70: return GREEN
    if v >= 0.40: return ORANGE
    return RED

def fmt_wpp(num: str) -> str:
    s = re.sub(r"\D", "", str(num))
    if not s: return ""
    return s if s.startswith("55") else "55" + s

def tier_badge_html(tier: str) -> str:
    c = TIER_COLORS.get(tier, {"bg": "#333", "text": "#fff", "icon": ""})
    return f'<span class="tier-badge" style="background:{c["bg"]};color:{c["text"]}">{c["icon"]} {tier}</span>'

def delta_qualitative(p: dict) -> str:
    d = p.get("delta_ultimo")
    if d is None: return '<span style="color:#7a6f85">—</span>'
    if d > 0.005: return f'<span style="color:{GREEN};font-weight:600">↑ avançou</span>'
    if d < -0.005: return f'<span style="color:{RED};font-weight:600">↓ recuou</span>'
    return f'<span style="color:{GRAY}">→ estável</span>'

def build_export_list(ppl: list[dict], last_date_str: str) -> list[dict]:
    out = []
    for p in ppl:
        msg = generate_message(p)
        if not msg: continue
        out.append({
            "nome":                p["nome"],
            "email":               p["email"],
            "whatsapp":            fmt_wpp(p["whatsapp"]),
            "tier":                p["tier"],
            "progresso_atual_pct": round(p["progresso_atual"] * 100, 1),
            "projecao_pct":        round(p["projetado"] * 100, 1),
            "score_conversao":     round(p["score"], 2),
            "avancou_semana":      (p["delta_ultimo"] or 0) > 0.005,
            "mensagem":            msg,
            "semana_referencia":   last_date_str,
        })
    out.sort(key=lambda x: -x["score_conversao"])
    return out

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
history      = load_history()
sorted_dates = sorted(history.keys())
last_date_str = sorted_dates[-1] if sorted_dates else None
badge_text = (
    f"Atualizado em {datetime.strptime(last_date_str, '%Y-%m-%d').strftime('%d/%m/%Y')}"
    if last_date_str else "Nenhum dado carregado"
)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="pda-header">
  <div>
    <h1>Bootcamp Afya — Monitor de Formação</h1>
    <p>Programadores do Amanhã · Meta: 10% do grupo de diversidade formado até 12/07/2026</p>
  </div>
  <span class="header-badge">{badge_text}</span>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<p style="font-family:\'Dela Gothic One\',sans-serif;color:{YELLOW};font-size:15px;margin-bottom:4px">Histórico carregado</p>', unsafe_allow_html=True)
    if history:
        st.caption(f"**{len(sorted_dates)} semana(s):**")
        for d in sorted_dates:
            st.caption(f"• {datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m/%Y')} — {len(history[d])} pessoas")
        st.divider()
        if st.button("🗑️ Limpar todos os dados", use_container_width=True):
            if st.checkbox("Confirmar limpeza"):
                history = {}
                save_history(history)
                st.rerun()
    else:
        st.caption("Nenhum dado carregado ainda.")

# ── UPLOAD ────────────────────────────────────────────────────────────────────
def process_uploads(files):
    msgs = []
    for f in files:
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
                msgs.append(f"⚠️ {f.name}: nenhuma linha válida.")
                continue
            history[week_date] = rows
            msgs.append(f"✅ {f.name} → {week_date} ({len(rows)} pessoas)")
        except Exception as e:
            msgs.append(f"❌ {f.name}: {e}")
    if msgs:
        save_history(history)
        for m in msgs: st.write(m)
        st.rerun()

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
people    = build_people(history)
div_ppl   = [p for p in people if p["diversidade"]]
all_ppl   = people

total     = len(people)
div_total = len(div_ppl)
meta      = max(1, -(-div_total // 10))
formados  = sum(1 for p in div_ppl if p["graduado"])
pct_meta  = min(1.0, formados / meta) if meta else 0.0

last_date  = datetime.strptime(sorted_dates[-1], "%Y-%m-%d").date()
weeks_left = max(0.0, (BOOTCAMP_END - last_date).days / 7)

# Projeção: quantos do grupo diversidade chegariam a GRAD_THRESHOLD
proj_form = sum(1 for p in div_ppl if p["projetado"] >= GRAD_THRESHOLD or p["graduado"])
gap_meta  = max(0, meta - proj_form)

# Velocidades e momentum
def mean(lst): return sum(lst)/len(lst) if lst else 0.0

div_vels  = [p["velocidade"] for p in div_ppl]
all_vels  = [p["velocidade"] for p in all_ppl]
div_vel   = mean(div_vels)
all_vel   = mean(all_vels)

div_prog  = mean([p["progresso_atual"] for p in div_ppl])
all_prog  = mean([p["progresso_atual"] for p in all_ppl])

div_accel = sum(1 for p in div_ppl
                if p["delta_ultimo"] is not None and p["delta_penult"] is not None
                and p["delta_ultimo"] > p["delta_penult"])
div_decel = sum(1 for p in div_ppl
                if p["delta_ultimo"] is not None and p["delta_penult"] is not None
                and p["delta_ultimo"] < p["delta_penult"])
all_accel = sum(1 for p in all_ppl
                if p["delta_ultimo"] is not None and p["delta_penult"] is not None
                and p["delta_ultimo"] > p["delta_penult"])
all_decel = sum(1 for p in all_ppl
                if p["delta_ultimo"] is not None and p["delta_penult"] is not None
                and p["delta_ultimo"] < p["delta_penult"])

tier_counts = {}
for t in TIER_COLORS:
    tier_counts[t] = sum(1 for p in div_ppl if p["tier"] == t)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 1 — SITUAÇÃO DA META
# ═══════════════════════════════════════════════════════════════════
weeks_int = int(round(weeks_left))
fill_pct  = int(pct_meta * 100)
alert_html = ""
if proj_form < meta:
    alert_html = f'<div class="hero-alert">⚠️ No ritmo atual, a meta <strong>não será atingida</strong>. Faltam <strong>{gap_meta}</strong> pessoas. Intensifique os contatos de Alta Prioridade.</div>'
else:
    alert_html = f'<div style="background:#1a4d2e;border:1px solid {GREEN};border-radius:8px;padding:10px 14px;font-size:12px;color:{GREEN};margin-top:12px">✅ No ritmo atual, a meta <strong>será atingida</strong>! Continue monitorando.</div>'

st.markdown(f"""
<div class="hero-card">
  <div class="hero-grid">
    <div class="hero-block">
      <div class="hero-eye">⏳ Semanas restantes</div>
      <div class="hero-num">{weeks_int}</div>
      <div class="hero-sub">até 12/07/2026<br>Tempo para agir é agora</div>
    </div>
    <div class="hero-block">
      <div class="hero-eye">🎯 Progresso da meta</div>
      <div class="hero-num">{formados} <span style="font-size:20px;color:#7a6f85">/ {meta}</span></div>
      <div class="hero-sub">formados do grupo de diversidade</div>
      <div class="prog-labels"><span>Atual: {fill_pct}%</span><span>Meta: {meta} pessoas (10%)</span></div>
      <div class="prog-track"><div class="prog-fill" style="width:{fill_pct}%"></div></div>
    </div>
    <div class="hero-block">
      <div class="hero-eye">📈 Projeção no ritmo atual</div>
      <div class="hero-num {'green' if proj_form >= meta else 'red'}">{proj_form}</div>
      <div class="hero-sub">formados projetados até jul/26<br>
        <span style="color:{'#e24b4a' if proj_form < meta else '#4ecb71'};font-weight:600">
          {'Faltam ' + str(gap_meta) + ' para a meta' if proj_form < meta else 'Meta atingida no ritmo atual'}
        </span>
      </div>
      {alert_html}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 2 — DISTRIBUIÇÃO + MOMENTUM
# ═══════════════════════════════════════════════════════════════════
col_donut, col_momentum = st.columns([1, 1.6])

with col_donut:
    st.markdown(f'<p class="section-title">Distribuição do Grupo</p><p class="section-sub">{div_total} pessoas · grupo de diversidade</p>', unsafe_allow_html=True)

    donut_labels = list(TIER_COLORS.keys())
    donut_values = [tier_counts.get(t, 0) for t in donut_labels]
    donut_colors = ["#eddc11","#f5c842","#5bc8e0","#e24b4a","#4ecb71","#555555"]

    fig_donut = go.Figure(go.Pie(
        labels=donut_labels, values=donut_values,
        hole=0.65, marker_colors=donut_colors,
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} pessoas<br>%{percent}<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{div_total}</b><br><span style='font-size:11px'>total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color=WHITE, family="IBM Plex Sans"),
    )
    fig_donut.update_layout(
        height=260, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    # Legenda com critérios
    for tier, color in zip(donut_labels, donut_colors):
        count = tier_counts.get(tier, 0)
        pct_t = round(count / div_total * 100) if div_total else 0
        icon  = TIER_COLORS[tier]["icon"]
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:4px 6px;border-radius:6px;font-size:12px;margin-bottom:2px">'
            f'<span><span style="background:{color};width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:6px"></span>{icon} {tier}</span>'
            f'<span style="color:{YELLOW};font-weight:600">{count}</span>'
            f'<span style="color:{GRAY};font-size:11px;margin-left:4px">{pct_t}%</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    with st.expander("ℹ️ Ver critérios de classificação"):
        for tier, criterio in TIER_CRITERIA.items():
            c = TIER_COLORS[tier]
            st.markdown(
                f'<div style="background:{c["bg"]};color:{c["text"]};padding:8px 12px;border-radius:8px;font-size:12px;margin-bottom:6px">'
                f'<strong>{c["icon"]} {tier}:</strong> {criterio}</div>',
                unsafe_allow_html=True
            )

with col_momentum:
    st.markdown(f'<p class="section-title">Momentum do Grupo</p><p class="section-sub">Velocidade e tendência — grupo de diversidade</p>', unsafe_allow_html=True)

    vel_trend  = "▲ acelerando" if div_vel >= all_vel else "▼ abaixo da média"
    vel_color  = GREEN if div_vel >= all_vel else RED
    prog_color_txt = GREEN if div_prog >= all_prog else ORANGE

    m1, m2, m3, m4 = st.columns(4)
    for col, label, val, sub, val_color in [
        (m1, "Velocidade média/sem", f"+{div_vel*100:.1f}%", f'<span style="color:{vel_color};font-size:11px;font-weight:600">{vel_trend}</span>', YELLOW),
        (m2, "Progresso médio", f"{div_prog*100:.0f}%", "grupo de diversidade", YELLOW),
        (m3, "Aceleraram esta sem.", str(div_accel), "delta > semana anterior", GREEN),
        (m4, "Desaceleraram esta sem.", str(div_decel), "delta < semana anterior", RED),
    ]:
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">{label}</div>'
                f'<div class="kpi-value" style="color:{val_color}">{val}</div>'
                f'<div class="kpi-sub">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with st.expander("↔ Comparar com grupo geral (sem diversidade)"):
        c1, c2, c3, c4 = st.columns(4)
        all_div_ratio = sum(1 for p in all_ppl
                            if p.get("delta_ultimo") is not None and p.get("delta_penult") is not None
                            and p["delta_ultimo"] > p["delta_penult"])
        for col, label, div_v, all_v in [
            (c1, "Velocidade/sem", f"+{div_vel*100:.1f}%", f"+{all_vel*100:.1f}%"),
            (c2, "Progresso médio", f"{div_prog*100:.0f}%", f"{all_prog*100:.0f}%"),
            (c3, "Aceleraram", str(div_accel), str(all_accel)),
            (c4, "Desaceleraram", str(div_decel), str(all_decel)),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:#1a0020;border-radius:8px;padding:10px;font-size:12px">'
                    f'<div style="color:#7a6f85;font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">{label}</div>'
                    f'<div style="color:{YELLOW};font-weight:600">🎯 Div: {div_v}</div>'
                    f'<div style="color:{GRAY}">👥 Geral: {all_v}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # Mini gráfico de linha no momentum
    if len(sorted_dates) >= 2:
        def avg_prog_week(d, filter_fn):
            rows = [r for r in history[d] if filter_fn(r)]
            return mean([r["progresso"] for r in rows]) * 100

        xlabels = [datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m") for d in sorted_dates]
        div_avgs = [avg_prog_week(d, lambda r: r["diversidade_negro"] or r["diversidade_indig"]) for d in sorted_dates]
        all_avgs = [avg_prog_week(d, lambda r: True) for d in sorted_dates]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=xlabels, y=[round(v,1) for v in div_avgs], name="Diversidade",
            line=dict(color=YELLOW, width=2.5), marker=dict(size=6, color=YELLOW),
            fill="tozeroy", fillcolor="rgba(237,220,17,0.06)",
        ))
        fig_line.add_trace(go.Scatter(
            x=xlabels, y=[round(v,1) for v in all_avgs], name="Geral",
            line=dict(color=GRAY, width=1.5, dash="dot"), marker=dict(size=4, color=GRAY),
        ))
        fig_line.update_layout(
            height=160, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Sans", size=11, color=WHITE),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10, color=GRAY)),
            yaxis=dict(ticksuffix="%", gridcolor=CARD_BORDER, tickfont=dict(color=GRAY)),
            xaxis=dict(gridcolor=CARD_BORDER, tickfont=dict(color=GRAY)),
        )
        st.plotly_chart(fig_line, use_container_width=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 3 — CONTATOS DESTA SEMANA
# ═══════════════════════════════════════════════════════════════════
alta_prio = [p for p in div_ppl if p["tier"] == "Alta Prioridade"]
alta_prio.sort(key=lambda p: (-p["score"], -p["projetado"]))

export_alta = build_export_list(alta_prio, last_date_str)
export_json = json.dumps(export_alta, ensure_ascii=False, indent=2)

hdr1, hdr2 = st.columns([3, 1])
with hdr1:
    st.markdown(f'<p class="section-title">🎯 Contatos desta semana</p><p class="section-sub">Alta Prioridade · mensagem gerada automaticamente · exporte o JSON para o n8n enviar via WhatsApp</p>', unsafe_allow_html=True)
with hdr2:
    st.download_button(
        label=f"⬇ Exportar {len(alta_prio)} contatos (n8n)",
        data=export_json,
        file_name=f"contatos_alta_prioridade_{last_date_str}.json",
        mime="application/json",
        use_container_width=True,
    )

if not alta_prio:
    st.info("Nenhuma pessoa em Alta Prioridade nesta semana.")
else:
    show_n = st.slider("Quantas pessoas exibir:", 5, min(50, len(alta_prio)), min(10, len(alta_prio)), key="show_slider")
    for p in alta_prio[:show_n]:
        pc    = prog_color(p["progresso_atual"])
        adv   = (p["delta_ultimo"] or 0) > 0.005
        wpp   = fmt_wpp(p["whatsapp"])
        msg   = generate_message(p)

        st.markdown(f"""
        <div class="contact-card">
          <div style="display:grid;grid-template-columns:1fr auto auto;gap:14px;align-items:start;margin-bottom:10px">
            <div>
              <div class="contact-name">{p['nome']}</div>
              <div class="contact-meta">{p['email']} · {wpp or '—'}</div>
            </div>
            <div style="min-width:130px">
              <div class="pbar-wrap">
                <div class="pbar"><div class="pfill" style="width:{pct(p['progresso_atual'])};background:{pc}"></div></div>
                <span style="font-size:12px;font-weight:600;color:{pc}">{pct(p['progresso_atual'])}</span>
                <span style="font-size:11px;color:#7a6f85">→ {pct(p['projetado'])} proj.</span>
              </div>
            </div>
            {'<span class="adv-badge">↑ avançou</span>' if adv else '<span style="color:#7a6f85;font-size:11px">→ estável</span>'}
          </div>
          <div class="msg-box">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 4 — EVOLUÇÃO SEMANAL
# ═══════════════════════════════════════════════════════════════════
st.markdown(f'<p class="section-title">Evolução Semanal</p><p class="section-sub">O que esse gráfico revela: o grupo de diversidade está ganhando ou perdendo velocidade em relação ao total? Se a linha amarela sobe mais rápido que a cinza, estamos fechando a brecha histórica de desigualdade de acesso.</p>', unsafe_allow_html=True)

if len(sorted_dates) >= 2:
    def avg_prog_all(d, key):
        if key == "div":
            rows = [r for r in history[d] if r["diversidade_negro"] or r["diversidade_indig"]]
        else:
            rows = history[d]
        return mean([r["progresso"] for r in rows]) * 100

    xlabels  = [datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m") for d in sorted_dates]
    div_avgs2 = [round(avg_prog_all(d,"div"),1) for d in sorted_dates]
    all_avgs2 = [round(avg_prog_all(d,"all"),1) for d in sorted_dates]

    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(
        x=xlabels, y=div_avgs2, name="Grupo Diversidade",
        line=dict(color=YELLOW, width=3), marker=dict(size=8, color=YELLOW),
        fill="tozeroy", fillcolor="rgba(237,220,17,0.06)",
    ))
    fig_evol.add_trace(go.Scatter(
        x=xlabels, y=all_avgs2, name="Total geral",
        line=dict(color=GRAY, width=2, dash="dot"), marker=dict(size=5, color=GRAY),
    ))
    fig_evol.add_hline(y=70, line_dash="dash", line_color=GREEN,
        annotation_text="Meta de conclusão (70%)",
        annotation_position="top left",
        annotation_font_color=GREEN,
    )
    fig_evol.update_layout(
        height=260, margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=CARD_BG,
        font=dict(family="IBM Plex Sans", size=12, color=WHITE),
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=11, color=GRAY)),
        yaxis=dict(ticksuffix="%", gridcolor=CARD_BORDER, tickfont=dict(color=GRAY), range=[0,max(max(div_avgs2),max(all_avgs2))*1.15 if div_avgs2 else 100]),
        xaxis=dict(gridcolor=CARD_BORDER, tickfont=dict(color=GRAY)),
    )
    st.plotly_chart(fig_evol, use_container_width=True)

    # Leitura automática
    if len(div_avgs2) >= 2:
        delta_div = div_avgs2[-1] - div_avgs2[-2]
        delta_all = all_avgs2[-1] - all_avgs2[-2]
        if delta_div > delta_all:
            insight = f"✅ Diversidade avançou **+{delta_div:.1f} pontos** esta semana, acima do geral (**+{delta_all:.1f} pontos**). Tendência positiva."
        elif delta_div < delta_all:
            insight = f"⚠️ Diversidade avançou **+{delta_div:.1f} pontos** esta semana, abaixo do geral (**+{delta_all:.1f} pontos**). Intensifique os contatos."
        else:
            insight = f"→ Diversidade e grupo geral avançaram igualmente esta semana (+{delta_div:.1f} pontos)."
        st.info(insight)
else:
    st.info("O gráfico aparece a partir de 2 semanas carregadas. Use o painel '📂 Carregar relatório' acima e selecione os arquivos históricos de semanas anteriores junto com o mais recente.")

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BLOCO 5 — LISTA COMPLETA POR GRUPO
# ═══════════════════════════════════════════════════════════════════
st.markdown(f'<p class="section-title">Lista Completa por Grupo</p><p class="section-sub">Dados mais recentes de {datetime.strptime(last_date_str, "%Y-%m-%d").strftime("%d/%m/%Y")} · selecione a aba e exporte para o n8n</p>', unsafe_allow_html=True)

tier_options = ["Alta Prioridade", "Atenção", "No Caminho", "Estagnado", "Formado", "Abandono", "Todos"]
tab_labels   = []
for t in tier_options:
    if t == "Todos":
        tab_labels.append(f"Todos ({div_total})")
    else:
        n = tier_counts.get(t, 0)
        icon = TIER_COLORS[t]["icon"]
        tab_labels.append(f"{icon} {t} ({n})")

tabs = st.tabs(tab_labels)

for tab, tier_key in zip(tabs, tier_options):
    with tab:
        if tier_key == "Todos":
            filtered = list(div_ppl)
        else:
            filtered = [p for p in div_ppl if p["tier"] == tier_key]

        filtered.sort(key=lambda p: (-p["score"], -p["projetado"]))

        col_exp, col_cnt = st.columns([1, 3])
        with col_cnt:
            st.caption(f"{len(filtered)} pessoa(s)")
        with col_exp:
            export_data = build_export_list(filtered, last_date_str)
            fname = f"contatos_{tier_key.lower().replace(' ','_')}_{last_date_str}.json"
            st.download_button(
                label="⬇ Exportar para n8n",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=fname,
                mime="application/json",
                use_container_width=True,
                key=f"exp_{tier_key}",
            )

        if not filtered:
            st.info("Nenhuma pessoa nesta categoria.")
            continue

        rows_html = ""
        for i, p in enumerate(filtered, 1):
            pc    = prog_color(p["progresso_atual"])
            prc   = prog_color(p["projetado"])
            msg   = generate_message(p)
            msg_short = (msg[:120] + "…") if len(msg) > 120 else msg
            rows_html += f"""
            <tr>
              <td style="color:#7a6f85;font-size:11px">{i}</td>
              <td><strong style="font-size:12px;color:{WHITE}">{p['nome']}</strong></td>
              <td class="td-meta">{p['email']}<br>{fmt_wpp(p['whatsapp']) or '—'}</td>
              <td>
                <div style="font-weight:600;color:{pc};font-size:12px">{pct(p['progresso_atual'])}</div>
                <div style="width:60px;height:4px;background:{CARD_BORDER};border-radius:2px;overflow:hidden;margin-top:3px">
                  <div style="width:{pct(p['progresso_atual'])};height:100%;background:{pc};border-radius:2px"></div>
                </div>
              </td>
              <td>{delta_qualitative(p)}</td>
              <td style="font-weight:600;color:{prc};font-size:12px">{pct(p['projetado'])}</td>
              <td>{tier_badge_html(p['tier'])}</td>
              <td class="td-msg">{msg_short.replace(chr(10), ' ')}</td>
            </tr>"""

        st.markdown(f"""
        <table class="full-table">
          <thead>
            <tr><th>#</th><th>Nome</th><th>Contato</th><th>Progresso</th>
            <th>Δ semana</th><th>Projeção 12/07</th><th>Tier</th><th>Mensagem</th></tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f'<div style="text-align:center;padding:40px 0 20px;color:#5a1060;font-size:11px">Programadores do Amanhã · Monitor Bootcamp Afya</div>', unsafe_allow_html=True)
