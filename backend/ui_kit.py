"""Mobile look-and-feel for CropShield (black-green theme): CSS + tiny HTML helpers."""
import html

import streamlit as st

CSS = """<style>
#MainMenu,footer,header[data-testid="stHeader"],[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none !important}
.stApp{background:#050806}
[data-testid="stMainBlockContainer"],.block-container{max-width:430px !important;margin:0 auto !important;padding:0 16px calc(150px + env(safe-area-inset-bottom,0px)) !important;min-height:100vh;background:#0b100d;box-shadow:0 0 60px rgba(34,197,94,.10);overflow-x:hidden}
.card,.hero,.fact,.row{overflow-wrap:anywhere;min-width:0}
.hero{margin:0 -16px 16px;padding:26px 22px 22px;background:radial-gradient(120% 90% at 0% 0%,#1f7a45 0%,#0f3d24 45%,#06180d 100%);border-radius:0 0 30px 30px;box-shadow:0 10px 28px rgba(34,197,94,.18);color:#fff}
.hero .sub{font-size:.85rem;opacity:.8}
.hero .title{font-size:1.7rem;font-weight:800;line-height:1.15;margin:2px 0 12px}
.hero .loc{font-size:.85rem;opacity:.9;margin-bottom:10px}
.hero .big{font-size:3rem;font-weight:800;line-height:1;color:#4ade80}
.hero .of{font-size:.9rem;opacity:.85;margin-left:8px}
.hero .bar{background:rgba(255,255,255,.16);margin:12px 0}
.hero .bar span{background:linear-gradient(90deg,#4ade80,#22c55e)}
.card{background:#121a15;border:1px solid #1d2b22;border-radius:18px;padding:16px;margin:0 0 14px;box-shadow:0 4px 16px rgba(0,0,0,.35);color:#e6f2ea}
.card.warn{background:#221d0b;border-color:#5c4b0a;color:#fde68a}
.card p{margin:6px 0 0}
.card .head{font-weight:800;font-size:1.05rem}
.muted{color:#8fa597 !important;font-size:.85rem}
.method{font-size:1.2rem;font-weight:800;color:#4ade80;margin:2px 0 4px;line-height:1.25}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.chip{background:rgba(34,197,94,.14);color:#86efac;border-radius:99px;padding:4px 12px;font-size:.8rem;font-weight:600}
.bar{height:10px;border-radius:99px;background:#1d2b22;overflow:hidden}
.bar span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#16a34a,#4ade80)}
.pill{display:inline-block;padding:4px 12px;border-radius:99px;font-size:.8rem;font-weight:700}
.pill.green{background:rgba(34,197,94,.20);color:#4ade80}
.pill.yellow{background:rgba(250,204,21,.18);color:#facc15}
.pill.red{background:rgba(248,113,113,.18);color:#f87171}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.fact{background:#0b100d;border:1px solid #1d2b22;border-radius:12px;padding:10px 12px}
.fact small{display:block;color:#8fa597}
.fact b{font-size:1rem}
.row{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid #1d2b22}
.row:last-child{border:0}
.row .nm{font-weight:700;flex:0 0 auto;max-width:42%}
.row .rt{text-align:right;flex:1 1 0;min-width:0;color:#4ade80;font-weight:600;font-size:.9rem}
.row .rt small{display:block;color:#8fa597;font-weight:500}
.srow{display:grid;grid-template-columns:minmax(0,105px) minmax(0,1fr) 40px;gap:10px;align-items:center;margin:10px 0;font-size:.9rem}
.srow em{font-style:normal;color:#8fa597;text-align:right}
.soon{text-align:center;color:#4b6355;padding:60px 0;font-weight:600}
.stButton>button{width:100%;border-radius:14px;min-height:48px;font-weight:700}
[data-testid="stExpander"]{background:#121a15;border:1px solid #1d2b22 !important;border-radius:18px;box-shadow:0 4px 16px rgba(0,0,0,.35);margin-bottom:14px}
.st-key-bottom_nav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:min(100vw,430px);box-sizing:border-box;z-index:1000;background:#0f1612;border-top:1px solid #1d2b22;border-radius:22px 22px 0 0;box-shadow:0 -8px 24px rgba(0,0,0,.55);padding:8px 8px calc(8px + env(safe-area-inset-bottom,0px))}
.st-key-bottom_nav [role="radiogroup"]{display:flex !important;flex-wrap:nowrap !important;width:100%;gap:4px}
.st-key-bottom_nav label{flex:1 1 0 !important;min-width:0 !important;justify-content:center;margin:0 !important;padding:6px 2px !important;border-radius:14px;cursor:pointer}
.st-key-bottom_nav label>span,.st-key-bottom_nav label>input,.st-key-bottom_nav label>div:not(:has([data-testid="stMarkdownContainer"])){display:none !important}
.st-key-bottom_nav label>div{margin:0 !important;padding:0 !important;width:100%}
.st-key-bottom_nav label p{white-space:pre-line;text-align:center;font-size:.7rem;line-height:1.3;color:#7f9488;margin:0}
.st-key-bottom_nav label p::first-line{font-size:1.4rem}
.st-key-bottom_nav label:has(input:checked){background:rgba(34,197,94,.15)}
.st-key-bottom_nav label:has(input:checked) p{color:#4ade80;font-weight:700}
</style>"""


def esc(x) -> str:
    return html.escape(str(x))


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(sub: str, title: str, body: str = ""):
    st.markdown(f'<div class="hero"><div class="sub">{esc(sub)}</div>'
                f'<div class="title">{esc(title)}</div>{body}</div>', unsafe_allow_html=True)


def card(inner: str, warn: bool = False):
    st.markdown(f'<div class="card{" warn" if warn else ""}">{inner}</div>', unsafe_allow_html=True)


def pill(band: str) -> str:
    return f'<span class="pill {band.split()[0].lower()}">{esc(band)}</span>'


def meter(score: float) -> str:
    return f'<div class="bar"><span style="width:{max(0, min(100, score)):.0f}%"></span></div>'


def facts(items) -> str:
    return '<div class="grid">' + "".join(
        f'<div class="fact"><small>{esc(k)}</small><b>{esc(v)}</b></div>' for k, v in items) + "</div>"


def rows(items) -> str:
    """items: (name, main text, small text) -> wrapping two-line rows that never overflow."""
    return "".join(f'<div class="row"><span class="nm">{esc(a)}</span>'
                   f'<span class="rt">{esc(b)}<small>{esc(c)}</small></span></div>' for a, b, c in items)


def coming_soon():
    st.markdown('<div class="soon">Coming soon</div>', unsafe_allow_html=True)
