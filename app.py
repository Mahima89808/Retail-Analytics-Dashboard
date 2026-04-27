import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Cost Optimization Analysis For Businesses", page_icon="💼",
                   layout="wide", initial_sidebar_state="expanded")

# ── session state defaults ────────────────────────────────────────────────────
for k, v in {"dark_mode": True, "trained_model": None, "model_name": None,
             "r2": None, "rmse": None, "mae": None, "y_test": None,
             "y_pred": None, "feat_cols": None, "le_map": None,
             "cat_feats": None, "df_ml": None,
             "uploaded_file_bytes": None, "uploaded_file_name": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

DK = st.session_state.dark_mode

if DK:
    T = dict(bg_app="#080c18", bg_sidebar="#0b1120", bg_card="#0f172a", bg_card2="#162032",
             border="#1e3a5f", border_hi="#2563eb", text_h="#f0f6ff", text_b="#94a3b8",
             text_dim="#3d5068", blue="#3b82f6", green="#10b981", red="#f43f5e",
             amber="#f59e0b", purple="#8b5cf6", cyan="#06b6d4",
             plotly="plotly_dark", plot_bg="#0f172a", paper_bg="#0f172a",
             grid="#1e3a5f", insight_bg="#0c1e36", rec_bg="#09200f", warn_bg="#211205",
             pred_pos_bg="#05160c", pred_neg_bg="#190508",
             shadow="0 4px 32px rgba(0,0,0,0.6)", card_shadow="0 2px 16px rgba(0,0,0,0.5)",
             glow_blue="0 0 0 1px #2563eb, 0 4px 20px rgba(37,99,235,0.25)")
else:
    T = dict(bg_app="#f1f5fb", bg_sidebar="#1e293b", bg_card="#ffffff", bg_card2="#f8fafd",
             border="#dce3ef", border_hi="#3b82f6", text_h="#0f172a", text_b="#475569",
             text_dim="#94a3b8", blue="#2563eb", green="#059669", red="#e11d48",
             amber="#d97706", purple="#7c3aed", cyan="#0891b2",
             plotly="plotly_white", plot_bg="#ffffff", paper_bg="#ffffff",
             grid="#e2e8f0", insight_bg="#eff6ff", rec_bg="#f0fdf4", warn_bg="#fffbeb",
             pred_pos_bg="#f0fdf4", pred_neg_bg="#fff1f2",
             shadow="0 2px 16px rgba(0,0,0,0.08)", card_shadow="0 1px 8px rgba(0,0,0,0.06)",
             glow_blue="0 0 0 2px #bfdbfe, 0 4px 20px rgba(37,99,235,0.1)")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{{box-sizing:border-box}}
html,body,[class*="css"]{{font-family:'Plus Jakarta Sans',sans-serif!important;-webkit-font-smoothing:antialiased;}}
.stApp{{background-color:{T['bg_app']}!important}}
.block-container{{padding:1.6rem 2.4rem 4rem!important;max-width:100%!important}}
[data-testid="stSidebar"]{{background:{T['bg_sidebar']}!important;border-right:1px solid {"rgba(30,58,95,0.8)" if DK else "rgba(203,213,225,0.4)"}}}
[data-testid="stSidebar"]>div{{padding:1rem 1rem 2rem!important}}
[data-testid="stSidebar"] *{{color:#e2e8f0!important}}
[data-testid="stSidebar"] .stSelectbox label{{font-size:0.7rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:0.09em!important;color:#64748b!important}}
[data-testid="stVerticalBlockBorderWrapper"]>div{{background:{T['bg_card']}!important;border:1px solid {T['border']}!important;border-radius:16px!important;box-shadow:{T['card_shadow']}!important;overflow:hidden;transition:box-shadow 0.2s,border-color 0.2s}}
[data-testid="stVerticalBlockBorderWrapper"]>div:hover{{border-color:{T['border_hi']}!important;box-shadow:{T['glow_blue']}!important}}
h1,h2,h3,h4{{color:{T['text_h']}!important;letter-spacing:-0.025em!important}}
[data-testid="stMetricValue"]{{font-family:'JetBrains Mono',monospace!important;font-size:1.7rem!important;font-weight:700!important;color:{T['text_h']}!important}}
[data-testid="stMetricLabel"]{{font-size:0.72rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:0.07em!important;color:{T['text_b']}!important}}
.stButton>button{{background:linear-gradient(135deg,{T['blue']},{T['purple']})!important;color:#fff!important;border:none!important;border-radius:10px!important;font-weight:700!important;font-size:0.85rem!important;padding:0.55rem 1.5rem!important;box-shadow:0 4px 14px rgba(59,130,246,0.4)!important;transition:opacity 0.18s,transform 0.18s!important}}
.stButton>button:hover{{opacity:0.86!important;transform:translateY(-1px)!important}}
[data-testid="stExpander"]{{border:1px solid {T['border']}!important;border-radius:12px!important;background:{T['bg_card']}!important}}
[data-testid="stDataFrame"]{{border:1px solid {T['border']}!important;border-radius:12px!important;overflow:hidden!important}}
::-webkit-scrollbar{{width:5px;height:5px}}
::-webkit-scrollbar-thumb{{background:{T['border']};border-radius:4px}}
[data-testid="stSidebar"] [data-baseweb="tag"]{{background:{"rgba(37,99,235,0.25)" if DK else "#dbeafe"}!important;border:1px solid {"rgba(37,99,235,0.5)" if DK else "#93c5fd"}!important;border-radius:6px!important;}}
[data-testid="stSidebar"] [data-baseweb="tag"] span{{color:{"#93c5fd" if DK else "#1d4ed8"}!important;font-size:0.7rem!important;font-weight:600!important;}}
[data-testid="stSidebar"] [data-baseweb="tag"] [role="button"]{{color:{"#93c5fd" if DK else "#1d4ed8"}!important;}}
[data-testid="stSidebar"] [data-baseweb="select"]>div{{background:{"rgba(15,23,42,0.6)" if DK else "#f8fafd"}!important;border-color:{"#1e3a5f" if DK else "#dce3ef"}!important;border-radius:8px!important;}}
</style>
""", unsafe_allow_html=True)

# ── helpers ──────────────────────────────────────────────────────────────────
def brand_header():
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:0 0 1.4rem;border-bottom:1px solid {T['border']};margin-bottom:1.6rem;">
      <div>
        <h1 style="margin:0;font-size:1.75rem;font-weight:800;
                   background:linear-gradient(135deg,{T['blue']},{T['purple']});
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          💼 Cost Optimization Analysis for Businesses </h1>
        <p style="margin:4px 0 0;font-size:0.79rem;color:{T['text_b']};">
          Business Cost Optimization &amp; Profitability Intelligence</p>
      </div>
      <div style="display:flex;gap:0.4rem;align-items:center;">
        <span style="background:{"rgba(16,185,129,0.12)" if DK else "#d1fae5"};color:{T['green']};
                     border:1px solid {"rgba(16,185,129,0.3)" if DK else "#6ee7b7"};
                     border-radius:20px;padding:3px 12px;font-size:0.68rem;font-weight:700;letter-spacing:0.06em;">● LIVE</span>
        <span style="background:{"rgba(59,130,246,0.1)" if DK else "#dbeafe"};color:{T['blue']};
                     border:1px solid {"rgba(59,130,246,0.25)" if DK else "#93c5fd"};
                     border-radius:20px;padding:3px 12px;font-size:0.68rem;font-weight:700;letter-spacing:0.06em;">v3.0</span>
      </div>
    </div>""", unsafe_allow_html=True)

def slabel(icon, title, sub=""):
    s = f"<p style='margin:2px 0 0.7rem;font-size:0.74rem;color:{T['text_b']};'>{sub}</p>" if sub else "<div style='height:0.65rem'></div>"
    st.markdown(f"<h3 style='margin:0;font-size:0.95rem;font-weight:800;color:{T['text_h']};'>{icon} {title}</h3>{s}", unsafe_allow_html=True)

def vbox(label, value, icon, accent, sub="", up=None):
    if up is True:  badge=f"<span style='font-size:0.67rem;font-weight:700;color:{T['green']};background:{'rgba(16,185,129,0.12)' if DK else '#d1fae5'};padding:2px 8px;border-radius:12px;'>▲ {sub}</span>"
    elif up is False: badge=f"<span style='font-size:0.67rem;font-weight:700;color:{T['red']};background:{'rgba(244,63,94,0.12)' if DK else '#ffe4e6'};padding:2px 8px;border-radius:12px;'>▼ {sub}</span>"
    else: badge=f"<span style='font-size:0.67rem;color:{T['text_b']};'>{sub}</span>"
    st.markdown(f"""
    <div style="background:{T['bg_card2']};border:1px solid {T['border']};border-left:3px solid {accent};
                border-radius:14px;padding:1.1rem 1.2rem;box-shadow:{T['card_shadow']};position:relative;overflow:hidden;">
      <div style="position:absolute;right:1rem;top:0.9rem;font-size:1.8rem;opacity:0.1;">{icon}</div>
      <p style="margin:0 0 0.15rem;font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:{T['text_b']};">{label}</p>
      <p style="margin:0 0 0.3rem;font-size:1.6rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:{T['text_h']};line-height:1;">{value}</p>
      {badge}
      <div style="height:3px;border-radius:3px;margin-top:0.55rem;background:{accent};opacity:0.75;"></div>
    </div>""", unsafe_allow_html=True)

def ibox(text, kind="info"):
    cols={"info":T['blue'],"success":T['green'],"warn":T['amber'],"error":T['red']}
    bgs ={"info":T['insight_bg'],"success":T['rec_bg'],"warn":T['warn_bg'],"error":T['pred_neg_bg']}
    ics ={"info":"💡","success":"✅","warn":"⚠️","error":"🚨"}
    st.markdown(f"<div style='background:{bgs[kind]};border-left:3px solid {cols[kind]};border-radius:0 10px 10px 0;padding:0.65rem 1rem;margin:0.4rem 0;font-size:0.82rem;color:{T['text_h']};line-height:1.55;'><b>{ics[kind]}</b> {text}</div>", unsafe_allow_html=True)

def pred_box(val, mname, r2):
    pos=val>=0; col=T['green'] if pos else T['red']; bg=T['pred_pos_bg'] if pos else T['pred_neg_bg']
    st.markdown(f"""
    <div style="background:{bg};border:2px solid {col};border-radius:16px;padding:1.8rem;text-align:center;
                margin-top:0.6rem;box-shadow:0 0 30px {"rgba(16,185,129,0.15)" if pos else "rgba(244,63,94,0.15)"};">
      <p style="margin:0 0 0.25rem;font-size:0.73rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:{T['text_b']};">Predicted Profit</p>
      <p style="margin:0;font-size:3.2rem;font-weight:800;color:{col};font-family:'JetBrains Mono',monospace;line-height:1.1;">${val:,.2f}</p>
      <p style="margin:0.35rem 0 0;font-size:0.78rem;color:{col};font-weight:600;">{"▲ Profitable" if pos else "▼ Loss-Making"}</p>
      <p style="margin:0.5rem 0 0;font-size:0.69rem;color:{T['text_dim']};">{mname} &nbsp;·&nbsp; R² = {r2:.4f}</p>
    </div>""", unsafe_allow_html=True)

def plo(fig, h=350):
    fig.update_layout(template=T['plotly'], paper_bgcolor=T['paper_bg'], plot_bgcolor=T['plot_bg'],
                      font_family="Plus Jakarta Sans", font_color=T['text_b'], height=h,
                      margin=dict(t=12,b=12,l=0,r=0),
                      legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11,orientation="h",
                                  yanchor="bottom",y=1.02,xanchor="right",x=1))
    fig.update_xaxes(gridcolor=T['grid'],zerolinecolor=T['grid'],linecolor=T['grid'])
    fig.update_yaxes(gridcolor=T['grid'],zerolinecolor=T['grid'],linecolor=T['grid'])
    return fig

def divider():
    st.markdown(f"<hr style='border:none;border-top:1px solid {T['border']};margin:0.9rem 0;'>", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_df_from_bytes(file_bytes, file_name):
    import io
    buf = io.BytesIO(file_bytes)
    df = (pd.read_excel(buf) if file_name.lower().endswith(("xlsx","xls")) else pd.read_csv(buf))
    df.drop_duplicates(inplace=True); df.columns=df.columns.str.strip()
    for c in ["Category","Sub-Category","Region","Segment","Ship Mode","State","City","Country"]:
        if c in df.columns: df[c]=df[c].astype(str).str.strip()
    for c in ["Sales","Profit","Discount","Quantity"]:
        if c in df.columns: df[c]=pd.to_numeric(df[c],errors="coerce")
    df.fillna(0,inplace=True)
    if {"Sales","Profit"}<=set(df.columns):
        df["Profit Margin %"]=np.where(df["Sales"]!=0,df["Profit"]/df["Sales"]*100,0)
    return df

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""<div style="padding:0.2rem 0 1rem;margin-bottom:0.7rem;border-bottom:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:1.1rem;font-weight:800;color:#f0f6ff;letter-spacing:-0.02em;">💼 Cost Optimization for Businesses </div>
        <div style="font-size:0.67rem;color:#475569;margin-top:2px;">Business Optimization Suite</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin-bottom:0.3rem;'>⚙️ Appearance</p>", unsafe_allow_html=True)
    _ndm = st.toggle("Dark Mode", value=st.session_state.dark_mode, key="_dm")
    if _ndm != st.session_state.dark_mode:
        st.session_state.dark_mode = _ndm
        st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin:0.3rem 0;'>🗂 Pages</p>", unsafe_allow_html=True)
    page = st.radio("_nav",[
        "🏠  Overview","🏷️  Category Analysis","🌍  Geographic View",
        "👥  Segment Analysis","🔗  Correlation & KPIs","🤖  ML Predictor"],
        label_visibility="collapsed")

    divider()
    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin-bottom:0.3rem;'>📂 Data Source</p>", unsafe_allow_html=True)

    # Show current file info in sidebar if already loaded, but uploader stays in center
    if st.session_state.uploaded_file_bytes is not None:
        st.markdown(f"<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:0.5rem 0.75rem;font-size:0.75rem;color:#10b981;'>"
                    f"✅ <b>{st.session_state.uploaded_file_name}</b><br>"
                    f"<span style='font-size:0.65rem;color:#475569;'>Dataset loaded — theme switches won't reset this.</span></div>",
                    unsafe_allow_html=True)
        if st.button("🗑 Remove Dataset", key="remove_ds"):
            st.session_state.uploaded_file_bytes = None
            st.session_state.uploaded_file_name = None
            st.rerun()
    else:
        st.markdown(f"<div style='font-size:0.74rem;color:#475569;'>No dataset loaded yet.<br>Upload from the main screen.</div>", unsafe_allow_html=True)

    divider()

    f_reg_slot = st.empty(); f_cat_slot = st.empty()
    f_seg_slot = st.empty(); f_shp_slot = st.empty()
    divider()
    ins_panel  = st.empty()
    divider()

    with st.expander("📖 User Manual"):
        st.markdown(f"""<div style='font-size:0.75rem;color:#94a3b8;line-height:1.65;'>

**How to use Cost Optimization Analysis for Businesses:**

• Upload your `.xlsx` or `.csv` from the main screen — it persists across theme switches.

• **Filters are dependent** — choosing a Region limits Categories to that Region's data only.

• 🚨 **Sidebar Signals** show live loss alerts. Act on red items first.

• **What-If Predictor** — use sliders to stress-test scenarios before committing.

• Dark Mode toggle persists — sliders/filters won't reset when you switch theme.
</div>""")

# ── load data — persist across theme toggles ──────────────────────────────────
# Check if a new file was uploaded via the center uploader (handled below via key)
_center_upload_key = "center_file_uploader"

# If no data loaded yet — show center upload screen
if st.session_state.uploaded_file_bytes is None:
    # Center upload widget
    st.markdown(f"""<div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;min-height:60vh;text-align:center;gap:1rem;">
        <div style="font-size:5rem;line-height:1;">💼</div>
        <h1 style="font-size:1.9rem;font-weight:800;margin:0;
                   background:linear-gradient(135deg,{T['blue']},{T['purple']});
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Cost Optimization for Businesses</h1>
        <p style="color:{T['text_b']};font-size:0.88rem;max-width:400px;line-height:1.7;margin:0;">
            Upload your <b>dataset</b> (.xlsx or .csv) below to unlock
            analytics, maps, ML prediction, and live cost-saving signals.</p>
    </div>""", unsafe_allow_html=True)

    # Center the file uploader
    _uc1, _uc2, _uc3 = st.columns([1, 2, 1])
    with _uc2:
        center_file = st.file_uploader(
            "Drop your dataset here (.xlsx or .csv)",
            type=["xlsx", "xls", "csv"],
            key=_center_upload_key,
            label_visibility="visible"
        )
        if center_file is not None:
            st.session_state.uploaded_file_bytes = center_file.read()
            st.session_state.uploaded_file_name  = center_file.name
            st.rerun()
    st.stop()

# Data is loaded — parse it
df_raw = load_df_from_bytes(
    st.session_state.uploaded_file_bytes,
    st.session_state.uploaded_file_name
)

# ── dependent multi-select filters ───────────────────────────────────────────
# Helper: empty list = "All" (no filter applied)
with f_reg_slot:
    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin:0.6rem 0 0.2rem;'>🌍 Region</p>", unsafe_allow_html=True)
    _reg_opts = sorted(df_raw["Region"].unique().tolist())
    sel_reg = st.multiselect("Region", _reg_opts, placeholder="All regions", key="f_reg", label_visibility="collapsed")
_dr = df_raw if not sel_reg else df_raw[df_raw["Region"].isin(sel_reg)]

with f_cat_slot:
    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin:0.4rem 0 0.2rem;'>🏷️ Category</p>", unsafe_allow_html=True)
    _cat_opts = sorted(_dr["Category"].unique().tolist())
    sel_cat = st.multiselect("Category", _cat_opts, placeholder="All categories", key="f_cat", label_visibility="collapsed")
_dc = _dr if not sel_cat else _dr[_dr["Category"].isin(sel_cat)]

with f_seg_slot:
    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin:0.4rem 0 0.2rem;'>👥 Segment</p>", unsafe_allow_html=True)
    _seg_opts = sorted(_dc["Segment"].unique().tolist())
    sel_seg = st.multiselect("Segment", _seg_opts, placeholder="All segments", key="f_seg", label_visibility="collapsed")
_ds = _dc if not sel_seg else _dc[_dc["Segment"].isin(sel_seg)]

with f_shp_slot:
    if "Ship Mode" in df_raw.columns:
        st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin:0.4rem 0 0.2rem;'>🚚 Ship Mode</p>", unsafe_allow_html=True)
        _shp_opts = sorted(_ds["Ship Mode"].unique().tolist())
        sel_shp = st.multiselect("Ship Mode", _shp_opts, placeholder="All ship modes", key="f_shp", label_visibility="collapsed")
    else:
        sel_shp = []

df = _ds.copy()
if sel_shp and "Ship Mode" in df.columns:
    df = df[df["Ship Mode"].isin(sel_shp)]

# Active filter summary badge
_active = []
if sel_reg: _active.append(f"**Region:** {', '.join(sel_reg)}")
if sel_cat: _active.append(f"**Cat:** {', '.join(sel_cat)}")
if sel_seg: _active.append(f"**Seg:** {', '.join(sel_seg)}")
if sel_shp: _active.append(f"**Ship:** {', '.join(sel_shp)}")
if df.empty:
    st.warning("No data matches current filters. Adjust selections.")
    st.stop()

# ── active filter badge ───────────────────────────────────────────────────────
if _active:
    _badge_bg  = "rgba(37,99,235,0.1)"  if DK else "#dbeafe"
    _badge_bdr = "rgba(37,99,235,0.3)"  if DK else "#93c5fd"
    st.markdown(
        f"<div style='background:{_badge_bg};border:1px solid {_badge_bdr};"
        f"border-radius:10px;padding:0.45rem 1rem;margin-bottom:0.6rem;"
        f"font-size:0.75rem;color:{T['blue']};line-height:1.7;'>"
        f"🔍 <b>Active filters:</b> &nbsp;" + " &nbsp;·&nbsp; ".join(_active) + "</div>",
        unsafe_allow_html=True)

# ── live signal panel ─────────────────────────────────────────────────────────
with ins_panel.container():
    st.markdown("<p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#475569;margin:0 0 0.45rem;'>📡 Live Signals</p>", unsafe_allow_html=True)
    for _cat, _pval in df.groupby("Category")["Profit"].sum().items():
        (st.error if _pval<0 else st.success)(f"{'🚨' if _pval<0 else '✅'} **{_cat}**: ${_pval:,.0f}")
    _ad=df["Discount"].mean()*100
    if _ad>25: st.warning(f"⚠️ High avg discount: {_ad:.1f}%")
    _wsub=df.groupby("Sub-Category")["Profit"].sum().idxmin()
    _wsv =df.groupby("Sub-Category")["Profit"].sum().min()
    if _wsv<0: st.error(f"🚨 **{_wsub}**: ${_wsv:,.0f}")
    st.info(f"💡 Best region: **{df.groupby('Region')['Profit'].sum().idxmax()}**")

# ── shared KPIs ───────────────────────────────────────────────────────────────
tot_s=df["Sales"].sum(); tot_p=df["Profit"].sum()
tot_q=int(df["Quantity"].sum()); avg_m=df["Profit Margin %"].mean()
avg_d=df["Discount"].mean()*100; n_ord=len(df)

# ═══════════════════ PAGE: OVERVIEW ══════════════════════════════════════════
if "Overview" in page:
    brand_header()

    k1,k2,k3,k4 = st.columns(4, gap="medium")
    with k1:
        with st.container(border=True):
            vbox("Total Sales",f"${tot_s:,.0f}","💰",T['blue'],f"{n_ord:,} orders")
    with k2:
        with st.container(border=True):
            vbox("Total Profit",f"${tot_p:,.0f}","📈",T['green'] if tot_p>0 else T['red'],"gain" if tot_p>0 else "loss",up=tot_p>0)
    with k3:
        with st.container(border=True):
            vbox("Avg Profit Margin",f"{avg_m:.1f}%","🎯",T['green'] if avg_m>0 else T['red'],"positive" if avg_m>0 else "negative",up=avg_m>0)
    with k4:
        with st.container(border=True):
            vbox("Avg Discount",f"{avg_d:.1f}%","🏷️",T['amber'] if avg_d>20 else T['green'],"high — review" if avg_d>20 else "healthy",up=avg_d<=20)

    st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        _show=st.checkbox("📋 Show Raw Data Table", key="raw_chk")
        if _show:
            st.dataframe(df, use_container_width=True, height=255)

    ch1,ch2 = st.columns(2, gap="medium")
    with ch1:
        with st.container(border=True):
            slabel("📊","Profit by Category")
            cg=df.groupby("Category").agg(Sales=("Sales","sum"),Profit=("Profit","sum")).reset_index()
            fig=go.Figure()
            fig.add_bar(name="Sales",x=cg["Category"],y=cg["Sales"],marker_color=T['blue'],opacity=0.88,
                        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>")
            fig.add_bar(name="Profit",x=cg["Category"],y=cg["Profit"],opacity=0.88,
                        marker_color=[T['green'] if v>=0 else T['red'] for v in cg["Profit"]],
                        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>")
            fig.update_layout(barmode="group")
            plo(fig,350); st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    with ch2:
        with st.container(border=True):
            slabel("📉","Discount vs Profit","With linear trend line")
            samp=df.sample(min(1500,len(df)),random_state=42)
            fig2=go.Figure()
            for i,cat in enumerate(sorted(samp["Category"].unique())):
                d=samp[samp["Category"]==cat]
                fig2.add_scatter(x=d["Discount"],y=d["Profit"],mode="markers",name=cat,
                                 marker=dict(color=[T['blue'],T['amber'],T['purple']][i%3],size=5,opacity=0.6),
                                 hovertemplate=f"<b>{cat}</b><br>Disc: %{{x:.0%}}<br>Profit: $%{{y:,.0f}}<extra></extra>")
            xv=samp["Discount"].values; yv=samp["Profit"].values; ok=np.isfinite(xv)&np.isfinite(yv)
            if ok.sum()>1:
                m,b=np.polyfit(xv[ok],yv[ok],1); xr=np.linspace(xv[ok].min(),xv[ok].max(),120)
                fig2.add_scatter(x=xr,y=m*xr+b,mode="lines",name="Trend",
                                 line=dict(color=T['red'],width=2.5,dash="dash"),hoverinfo="skip")
            plo(fig2,350); st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("🔍","Profit by Sub-Category","Worst → Best")
        sg=df.groupby("Sub-Category")["Profit"].sum().reset_index().sort_values("Profit")
        fig3=go.Figure(go.Bar(x=sg["Profit"],y=sg["Sub-Category"],orientation="h",
                              marker_color=[T['red'] if v<0 else T['green'] for v in sg["Profit"]],
                              opacity=0.88,text=sg["Profit"].apply(lambda v:f"${v:,.0f}"),textposition="outside",textfont_size=10,
                              hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"))
        plo(fig3,380); st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("💡","Insights & Recommendations")
        wc=df.groupby("Category")["Profit"].sum().idxmin()
        bs=df.groupby("Segment")["Profit"].sum().idxmax()
        ibox(f"<b>{wc}</b> is the least profitable category — audit pricing and COGS urgently.","warn")
        ibox(f"<b>{bs}</b> drives the highest profit — protect margins and grow volume.","info")
        ibox("Higher discounts consistently erode profits. Implement tiered discount governance.","warn")
        ibox("Focus marketing on high-margin sub-categories to maximise ROI.","success")

    with st.expander("📖 User Manual — How to Interpret This Dashboard"):
        st.markdown(f"<div style='color:{T['text_b']};font-size:0.82rem;line-height:1.7;'>"
                    "• <b>Red bars</b> = loss-making. Investigate discount depth and COGS.<br>"
                    "• <b>Trend line</b> — downward slope confirms discounts destroy margin.<br>"
                    "• <b>KPI badge ▲/▼</b> — green healthy, red requires intervention.<br>"
                    "• <b>Sidebar Signals</b> auto-update with live loss alerts as filters change.<br>"
                    "• <b>Dependent filters</b>: choosing a Region narrows available Categories.</div>")

# ═══════════════════ PAGE: CATEGORY ══════════════════════════════════════════
elif "Category" in page:
    brand_header()
    st.markdown(f"<h2 style='font-size:1.3rem;font-weight:800;color:{T['text_h']};margin:0 0 1.2rem;'>🏷️ Category & Sub-Category Analysis</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        fc_col,_ = st.columns([2,5])
        with fc_col: focus=st.selectbox("Focus Category",["All"]+sorted(df["Category"].unique().tolist()))
    dfc = df if focus=="All" else df[df["Category"]==focus]

    ca1,ca2=st.columns(2,gap="medium")
    with ca1:
        with st.container(border=True):
            slabel("💰","Profit by Category")
            cg2=df.groupby("Category").agg(Profit=("Profit","sum"),Sales=("Sales","sum")).reset_index()
            cg2["Margin"]=cg2["Profit"]/cg2["Sales"]*100
            fig=px.bar(cg2.sort_values("Profit"),x="Profit",y="Category",orientation="h",color="Profit",
                       text=cg2.sort_values("Profit")["Profit"].apply(lambda v:f"${v:,.0f}"),
                       color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
            fig.update_traces(textposition="outside",hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>")
            plo(fig,350); st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with ca2:
        with st.container(border=True):
            slabel("📐","Profit Margin % by Category")
            fig2=go.Figure(go.Bar(x=cg2["Category"],y=cg2["Margin"],
                                  marker_color=[T['green'] if v>=0 else T['red'] for v in cg2["Margin"]],
                                  text=[f"{v:.1f}%" for v in cg2["Margin"]],textposition="outside",
                                  hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"))
            plo(fig2,350); st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("🔍","Sub-Category Deep Dive")
        sub2=dfc.groupby(["Category","Sub-Category"]).agg(Sales=("Sales","sum"),Profit=("Profit","sum")).reset_index().sort_values("Profit")
        fig3=px.bar(sub2,x="Profit",y="Sub-Category",orientation="h",color="Profit",
                    facet_col="Category" if focus=="All" else None,
                    color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
        plo(fig3,430); st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("🌳","Sales Treemap — colored by Profit")
        fig4=px.treemap(sub2,path=["Category","Sub-Category"],values="Sales",color="Profit",
                        color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
        plo(fig4,420); fig4.update_layout(margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig4,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("💡","Insights & Recommendations")
        ws=sub2.iloc[0]["Sub-Category"]; bs2=sub2.iloc[-1]["Sub-Category"]
        ibox(f"<b>{ws}</b> is the biggest loss-maker — high discounts or low demand.","error")
        ibox(f"<b>{bs2}</b> is the top performer — protect and scale this sub-category.","success")
        ibox("Use treemap: big red tiles = high revenue but negative margin = urgent repricing.","warn")

# ═══════════════════ PAGE: GEOGRAPHIC ════════════════════════════════════════
elif "Geographic" in page:
    brand_header()
    st.markdown(f"<h2 style='font-size:1.3rem;font-weight:800;color:{T['text_h']};margin:0 0 1.2rem;'>🌍 Geographic Profitability</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        slabel("🗺️","World Profit Map")
        cntry=df.groupby("Country").agg(Profit=("Profit","sum"),Sales=("Sales","sum")).reset_index()
        fg1=px.choropleth(cntry,locations="Country",locationmode="country names",color="Profit",
                          hover_name="Country",hover_data={"Sales":":.0f","Profit":":.0f"},
                          color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
        plo(fg1,430); fg1.update_layout(geo=dict(bgcolor=T['plot_bg'],showframe=False,
                                                  landcolor=T['bg_card2'],showocean=True,oceancolor=T['bg_app']))
        st.plotly_chart(fg1,use_container_width=True,config={"displayModeBar":False})

    if "State" in df.columns:
        with st.container(border=True):
            _mc,_ = st.columns([2,5])
            with _mc: mm=st.selectbox("Colour States By",["Profit","Sales","Quantity"])
            slabel("🇺🇸",f"US State Map — {mm}")
            stg=df.groupby("State").agg(Profit=("Profit","sum"),Sales=("Sales","sum"),Quantity=("Quantity","sum")).reset_index()
            fg2=px.choropleth(stg,locations="State",locationmode="USA-states",color=mm,
                              hover_name="State",scope="usa",
                              color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
            plo(fg2,440); fg2.update_layout(geo=dict(bgcolor=T['plot_bg'],showframe=False,
                                                      landcolor=T['bg_card2'],showlakes=True,lakecolor=T['bg_app']))
            st.plotly_chart(fg2,use_container_width=True,config={"displayModeBar":False})

        g1,g2=st.columns(2,gap="medium")
        with g1:
            with st.container(border=True):
                slabel("🏆","Top 10 States by Profit")
                t10=stg.nlargest(10,"Profit")
                fg3=px.bar(t10,x="Profit",y="State",orientation="h",color="Profit",
                           text=t10["Profit"].apply(lambda v:f"${v:,.0f}"),
                           color_continuous_scale=[[0,T['cyan']],[1,T['green']]])
                fg3.update_traces(textposition="outside")
                plo(fg3,350); st.plotly_chart(fg3,use_container_width=True,config={"displayModeBar":False})
        with g2:
            with st.container(border=True):
                slabel("📉","Bottom 10 States by Profit")
                b10=stg.nsmallest(10,"Profit")
                fg4=px.bar(b10,x="Profit",y="State",orientation="h",color="Profit",
                           text=b10["Profit"].apply(lambda v:f"${v:,.0f}"),
                           color_continuous_scale=[[0,T['red']],[1,T['amber']]])
                fg4.update_traces(textposition="outside")
                plo(fg4,350); st.plotly_chart(fg4,use_container_width=True,config={"displayModeBar":False})

        bss=stg.nlargest(1,"Profit")["State"].values[0]
        wss=stg.nsmallest(1,"Profit")["State"].values[0]
        with st.container(border=True):
            slabel("💡","Insights & Recommendations")
            ibox(f"<b>{bss}</b> is the top-profit state — replicate its model in neighbouring states.","success")
            ibox(f"<b>{wss}</b> has the deepest losses — investigate logistics and product mix.","error")
            ibox("States with high sales but low profit signal discount abuse — check that map layer.","warn")

# ═══════════════════ PAGE: SEGMENT ═══════════════════════════════════════════
elif "Segment" in page:
    brand_header()
    st.markdown(f"<h2 style='font-size:1.3rem;font-weight:800;color:{T['text_h']};margin:0 0 1.2rem;'>👥 Customer Segment Analysis</h2>", unsafe_allow_html=True)

    sg2=df.groupby("Segment").agg(Sales=("Sales","sum"),Profit=("Profit","sum"),
                                   Quantity=("Quantity","sum"),AvgDisc=("Discount","mean")).reset_index()
    sg2["Margin %"]=sg2["Profit"]/sg2["Sales"]*100

    scols=st.columns(len(sg2),gap="medium")
    for i,(_,row) in enumerate(sg2.iterrows()):
        with scols[i]:
            with st.container(border=True):
                vbox(row["Segment"],f"${row['Profit']:,.0f}","👤",
                     T['green'] if row["Margin %"]>=0 else T['red'],
                     f"Margin {row['Margin %']:.1f}%",up=row["Margin %"]>=0)

    sc1,sc2=st.columns(2,gap="medium")
    with sc1:
        with st.container(border=True):
            slabel("📊","Segment Performance Comparison")
            fs1=px.bar(sg2,x="Segment",y=["Sales","Profit","Quantity"],barmode="group",
                       color_discrete_sequence=[T['blue'],T['green'],T['amber']])
            plo(fs1,350); st.plotly_chart(fs1,use_container_width=True,config={"displayModeBar":False})
    with sc2:
        with st.container(border=True):
            slabel("🌡️","Segment × Category Heatmap")
            pvd=df.groupby(["Segment","Category"])["Profit"].sum().reset_index()
            pvt=pvd.pivot(index="Segment",columns="Category",values="Profit")
            fs2=px.imshow(pvt,text_auto=".0f",color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
            plo(fs2,350); st.plotly_chart(fs2,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("💡","Insights & Recommendations")
        bsg=sg2.nlargest(1,"Profit")["Segment"].values[0]
        wsg=sg2.nsmallest(1,"Profit")["Segment"].values[0]
        ibox(f"<b>{bsg}</b> is the primary profit driver — prioritise loyalty and retention.","success")
        ibox(f"<b>{wsg}</b> underperforms — explore volume pricing or dedicated account management.","warn")
        ibox("Heatmap reveals which (Segment, Category) combos destroy the most value — fix those first.","info")

# ═══════════════════ PAGE: CORRELATION ═══════════════════════════════════════
elif "Correlation" in page:
    brand_header()
    st.markdown(f"<h2 style='font-size:1.3rem;font-weight:800;color:{T['text_h']};margin:0 0 1.2rem;'>🔗 Correlation & KPI Analysis</h2>", unsafe_allow_html=True)

    nums=[c for c in ["Sales","Profit","Discount","Quantity","Profit Margin %"] if c in df.columns]
    cm=df[nums].corr()

    cc1,cc2=st.columns(2,gap="medium")
    with cc1:
        with st.container(border=True):
            slabel("🧊","Correlation Heatmap")
            fk1=px.imshow(cm,text_auto=".2f",color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['blue']]])
            plo(fk1,350); st.plotly_chart(fk1,use_container_width=True,config={"displayModeBar":False})
    with cc2:
        with st.container(border=True):
            slabel("📉","Discount vs Profit — Linear Trend")
            s3=df.sample(min(2000,len(df)),random_state=77)
            fk2=go.Figure()
            for i,cat in enumerate(sorted(s3["Category"].unique())):
                d3=s3[s3["Category"]==cat]
                fk2.add_scatter(x=d3["Discount"],y=d3["Profit"],mode="markers",name=cat,
                                marker=dict(color=[T['blue'],T['amber'],T['purple']][i%3],size=5,opacity=0.5),
                                hovertemplate=f"<b>{cat}</b><br>Disc: %{{x:.0%}}<br>$%{{y:,.0f}}<extra></extra>")
            xv3=s3["Discount"].values; yv3=s3["Profit"].values; ok3=np.isfinite(xv3)&np.isfinite(yv3)
            if ok3.sum()>1:
                m3,b3=np.polyfit(xv3[ok3],yv3[ok3],1); xr3=np.linspace(xv3[ok3].min(),xv3[ok3].max(),120)
                fk2.add_scatter(x=xr3,y=m3*xr3+b3,mode="lines",name="Trend",
                                line=dict(color=T['red'],width=2.5,dash="dash"),hoverinfo="skip")
            plo(fk2,350); st.plotly_chart(fk2,use_container_width=True,config={"displayModeBar":False})

    with st.container(border=True):
        slabel("🫧","Sub-Category — Sales vs Profit Bubble")
        sk2=df.groupby("Sub-Category").agg(Sales=("Sales","sum"),Profit=("Profit","sum"),Quantity=("Quantity","sum")).reset_index()
        fk3=px.scatter(sk2,x="Sales",y="Profit",size="Quantity",text="Sub-Category",color="Profit",
                       size_max=52,color_continuous_scale=[[0,T['red']],[0.5,T['amber']],[1,T['green']]])
        fk3.update_traces(textposition="top center",textfont_size=9,
                          hovertemplate="<b>%{text}</b><br>Sales:$%{x:,.0f}<br>Profit:$%{y:,.0f}<extra></extra>")
        plo(fk3,420); st.plotly_chart(fk3,use_container_width=True,config={"displayModeBar":False})

    dc=cm.loc["Discount","Profit"]
    with st.container(border=True):
        slabel("💡","Insights & Recommendations")
        ibox(f"Discount–Profit r = <b>{dc:.3f}</b>. Every extra % discount directly shrinks profit.","error" if dc<-0.1 else "warn")
        ibox("Bottom-left bubble quadrant (low sales, negative profit) = discontinuation candidates.","warn")
        ibox("Implement tiered discount caps: 10% standard · 20% clearance · 30% absolute ceiling.","success")

# ═══════════════════ PAGE: ML PREDICTOR ══════════════════════════════════════
elif "ML" in page or "Predictor" in page:
    brand_header()
    st.markdown(f"<h2 style='font-size:1.3rem;font-weight:800;color:{T['text_h']};margin:0 0 1.2rem;'>🤖 What-If Profit Predictor</h2>", unsafe_allow_html=True)

    _dfm=df.copy(); _lm={}
    _cfs=["Category","Sub-Category","Region","Segment","Ship Mode","State","City"]
    for _c in _cfs:
        if _c in _dfm.columns:
            _le=LabelEncoder(); _dfm[_c+"_enc"]=_le.fit_transform(_dfm[_c].astype(str)); _lm[_c]=_le
    _fc=["Sales","Discount","Quantity"]+[_c+"_enc" for _c in _cfs if _c in _dfm.columns]
    _X=_dfm[_fc]; _y=_dfm["Profit"]

    with st.container(border=True):
        slabel("⚙️","Model Configuration")
        mc1,mc2,mc3=st.columns([2,2,3])
        with mc1: mch=st.selectbox("Algorithm",["Linear Regression","Random Forest","Gradient Boosting"])
        with mc2: tsp=st.selectbox("Test Split",["20%","25%","30%"]); ts=int(tsp.replace("%",""))/100
        with mc3:
            st.markdown("<div style='padding-top:1.55rem'></div>", unsafe_allow_html=True)
            tb=st.button("🚀 Train Model",type="primary")

    if tb:
        Xtr,Xte,ytr,yte=train_test_split(_X,_y,test_size=ts,random_state=42)
        with st.spinner("Training…"):
            if mch=="Linear Regression": mdl=LinearRegression()
            elif mch=="Random Forest":   mdl=RandomForestRegressor(n_estimators=130,random_state=42,n_jobs=-1)
            else:                         mdl=GradientBoostingRegressor(n_estimators=130,random_state=42)
            mdl.fit(Xtr,ytr); yp=mdl.predict(Xte)
        st.session_state.trained_model=mdl; st.session_state.model_name=mch
        st.session_state.r2=r2_score(yte,yp); st.session_state.rmse=float(np.sqrt(mean_squared_error(yte,yp)))
        st.session_state.mae=float(np.mean(np.abs(yte.values-yp)))
        st.session_state.y_test=yte; st.session_state.y_pred=yp
        st.session_state.feat_cols=_fc; st.session_state.le_map=_lm
        st.session_state.cat_feats=_cfs; st.session_state.df_ml=_dfm

    if st.session_state.trained_model is not None:
        pk1,pk2,pk3=st.columns(3,gap="medium")
        with pk1:
            with st.container(border=True):
                vbox("R² Score",f"{st.session_state.r2:.4f}","🎯",T['green'] if st.session_state.r2>0.7 else T['amber'])
        with pk2:
            with st.container(border=True):
                vbox("RMSE",f"${st.session_state.rmse:,.2f}","📐",T['amber'])
        with pk3:
            with st.container(border=True):
                vbox("MAE",f"${st.session_state.mae:,.2f}","📏",T['purple'])

        pc1,pc2=st.columns(2,gap="medium")
        with pc1:
            with st.container(border=True):
                slabel("🎯","Actual vs Predicted")
                res=pd.DataFrame({"Actual":st.session_state.y_test.values[:300],"Predicted":st.session_state.y_pred[:300]})
                fp1=go.Figure()
                fp1.add_scatter(x=res["Actual"],y=res["Predicted"],mode="markers",name="Predictions",
                                marker=dict(color=T['blue'],size=5,opacity=0.6),
                                hovertemplate="Actual:$%{x:,.0f}<br>Pred:$%{y:,.0f}<extra></extra>")
                mn2=float(min(res["Actual"].min(),res["Predicted"].min()))
                mx2=float(max(res["Actual"].max(),res["Predicted"].max()))
                fp1.add_scatter(x=[mn2,mx2],y=[mn2,mx2],mode="lines",name="Perfect Fit",
                                line=dict(color=T['green'],dash="dash",width=2))
                plo(fp1,350); st.plotly_chart(fp1,use_container_width=True,config={"displayModeBar":False})
        with pc2:
            with st.container(border=True):
                if st.session_state.model_name!="Linear Regression":
                    slabel("🏋️","Feature Importances")
                    fi=pd.DataFrame({"Feature":_fc,"Importance":st.session_state.trained_model.feature_importances_}).sort_values("Importance")
                    fp2=px.bar(fi,x="Importance",y="Feature",orientation="h",color="Importance",
                               color_continuous_scale=[[0,T['blue']],[1,T['purple']]])
                    plo(fp2,350); st.plotly_chart(fp2,use_container_width=True,config={"displayModeBar":False})
                else:
                    slabel("📈","Residuals Distribution")
                    resid=st.session_state.y_test.values-st.session_state.y_pred
                    fp2=px.histogram(resid,nbins=50,color_discrete_sequence=[T['blue']],labels={"value":"Residual"})
                    plo(fp2,350); st.plotly_chart(fp2,use_container_width=True,config={"displayModeBar":False})

        # ── What-If box ───────────────────────────────────────────────────────
        with st.container(border=True):
            slabel("🔮","What-If Analysis Simulator","Drag sliders · select options · click Predict")
            wa1,wa2=st.columns([3,2],gap="large")
            with wa1:
                s_in=st.slider("💰 Sales ($)",    0.0,10000.0,500.0,10.0)
                d_in=st.slider("🏷️ Discount",    0.0,0.8,    0.2,  0.01,format="%.2f")
                q_in=st.slider("📦 Quantity",     1,  100,    3,    1)
                wc1,wc2=st.columns(2)
                with wc1:
                    r_in=st.selectbox("Region",  sorted(df_raw["Region"].unique()),  key="wa_r")
                    c_in=st.selectbox("Category",sorted(df_raw["Category"].unique()),key="wa_c")
                with wc2:
                    g_in=st.selectbox("Segment", sorted(df_raw["Segment"].unique()), key="wa_g")
                    if "Ship Mode" in df_raw.columns:
                        sh_in=st.selectbox("Ship Mode",sorted(df_raw["Ship Mode"].unique()),key="wa_sh")
                    else: sh_in="Standard"
            with wa2:
                st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
                pb=st.button("🔮 Run Prediction",type="primary")
                if pb:
                    _row={"Sales":s_in,"Discount":d_in,"Quantity":q_in,"Category":c_in,
                          "Sub-Category":df_raw["Sub-Category"].iloc[0],
                          "Region":r_in,"Segment":g_in,"Ship Mode":sh_in,
                          "State":df_raw["State"].iloc[0] if "State" in df_raw.columns else "CA",
                          "City": df_raw["City"].iloc[0]  if "City"  in df_raw.columns else "NY"}
                    _rdf=pd.DataFrame([_row])
                    for _cx in st.session_state.cat_feats:
                        if _cx in _rdf.columns and _cx in st.session_state.le_map:
                            _kn=list(st.session_state.le_map[_cx].classes_)
                            _vl=str(_rdf[_cx].iloc[0])
                            _rdf[_cx+"_enc"]=st.session_state.le_map[_cx].transform([_vl])[0] if _vl in _kn else 0
                    _Xn=_rdf[st.session_state.feat_cols]
                    _pv=st.session_state.trained_model.predict(_Xn)[0]
                    pred_box(_pv,st.session_state.model_name,st.session_state.r2)
                    if _pv<0: st.error("🚨 Loss-making scenario. Reduce discount or increase volume.")
                    elif _pv<50: st.warning("⚠️ Marginal profit. Consider adjusting pricing.")
                    else: st.success("✅ Healthy profit scenario. Consider scaling this combination.")

        with st.container(border=True):
            slabel("💡","Insights & Recommendations")
            ibox(f"Model: <b>{st.session_state.model_name}</b> | R² = <b>{st.session_state.r2:.3f}</b> — {'strong' if st.session_state.r2>0.7 else 'moderate'} predictive power.","info")
            ibox("Sliders let you stress-test: reducing Discount 30%→10% typically recovers $50–200 profit per order.","success")
            ibox("Re-train monthly with fresh data to keep predictions aligned with market dynamics.","warn")
    else:
        st.markdown(f"<div style='text-align:center;padding:4rem;color:{T['text_b']};'><div style='font-size:3.5rem;margin-bottom:1rem;'>🤖</div><p>Configure above and click <b style='color:{T['blue']};'>Train Model</b> to begin.</p></div>", unsafe_allow_html=True)
