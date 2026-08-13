import sqlite3
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from scoring import calculate_score, risk_band

st.set_page_config(page_title="ProcureWatch Local", page_icon="🏛️", layout="wide")
st.markdown("""
<style>
.stApp{background:#f6f8fb;color:#182230}
.block-container{max-width:1400px;padding-top:1.5rem}
.hero{background:white;border:1px solid #e5e7eb;border-radius:18px;padding:28px;margin-bottom:18px}
.hero h1{color:#111827;margin:0 0 6px}.hero p{color:#667085}
.badge{display:inline-block;background:#eef4ff;color:#2457d6;padding:6px 10px;border-radius:99px;font-weight:700;font-size:.8rem}
[data-testid="stMetric"]{background:white;border:1px solid #e5e7eb;border-radius:14px;padding:12px}
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{color:#111827!important}
label{color:#273244!important;font-weight:600!important}
div[data-baseweb="input"] input,textarea{color:#111827!important;background:white!important}
</style>
""",unsafe_allow_html=True)

DB="procurewatch.db"
con=sqlite3.connect(DB,check_same_thread=False)
con.execute("""CREATE TABLE IF NOT EXISTS tenders(
id INTEGER PRIMARY KEY AUTOINCREMENT,tender_code TEXT UNIQUE,title TEXT,category TEXT,
buyer TEXT,tender_value REAL,bid_count INTEGER,winning_bid REAL,second_bid REAL,
supplier TEXT,supplier_wins INTEGER,supplier_share REAL,conflict_signal REAL,created_at TEXT)""")
con.commit()

def enrich(df):
    if df.empty:return df
    out=df.copy()
    vals=[calculate_score(r.tender_value,r.bid_count,r.winning_bid,r.second_bid,
                          r.supplier_wins,r.supplier_share,r.conflict_signal)
          for r in out.itertuples()]
    out["risk_score"]=vals
    out["risk_band"]=[risk_band(x) for x in vals]
    out["review_note"]=out.apply(lambda r:
        "Review pricing/competition signals" if r.risk_score>=55 else
        "Routine screening" if r.risk_score<30 else "Consider additional evidence review",axis=1)
    return out

st.markdown("""<div class="hero"><span class="badge">ALL SYSTEMS LOCAL · SQLITE · PANDAS · NUMPY · PLOTLY</span>
<h1>🏛️ ProcureWatch Local</h1><p>Public procurement anomaly screening using transparent operational signals for human review.</p></div>""",unsafe_allow_html=True)
st.info("A screening signal is not proof of fraud, corruption, collusion, bid-rigging, or a conflict of interest. Results require authorized procurement, audit, compliance, and legal review.")

t1,t2,t3,t4=st.tabs(["Tender Register","CSV Analysis","Risk Analytics","Methodology"])
with t1:
    with st.form("register"):
        a,b,c=st.columns(3)
        with a:
            code=st.text_input("Tender code *"); title=st.text_input("Tender title *")
            category=st.selectbox("Category",["Infrastructure","IT & Software","Healthcare","Education","Utilities","Other"])
            buyer=st.text_input("Procuring authority / buyer")
        with b:
            value=st.number_input("Tender value",min_value=0.0,value=1000000.0)
            bids=st.number_input("Number of bids",min_value=1,value=4)
            win=st.number_input("Winning bid",min_value=0.0,value=900000.0)
            second=st.number_input("Second-lowest bid",min_value=0.0,value=950000.0)
        with c:
            supplier=st.text_input("Winning supplier *")
            wins=st.number_input("Supplier wins in review period",min_value=0,value=5)
            share=st.slider("Supplier award concentration (%)",0,100,25)
            conflict=st.slider("Conflict-of-interest review signal",0,100,0)
        submit=st.form_submit_button("Register tender",type="primary")
    if submit:
        if not code.strip() or not title.strip() or not supplier.strip(): st.error("Complete required fields.")
        else:
            try:
                con.execute("INSERT INTO tenders(tender_code,title,category,buyer,tender_value,bid_count,winning_bid,second_bid,supplier,supplier_wins,supplier_share,conflict_signal,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (code,title,category,buyer,value,bids,win,second,supplier,wins,share,conflict,datetime.now().isoformat(timespec="seconds")))
                con.commit(); st.success("Tender registered locally.")
            except sqlite3.IntegrityError: st.error("Tender code already exists.")
    raw=pd.read_sql_query("SELECT * FROM tenders ORDER BY id DESC",con)
    if not raw.empty: st.dataframe(enrich(raw.drop(columns=["id","created_at"])),use_container_width=True,hide_index=True)

with t2:
    sample=pd.read_csv("data/procurewatch_sample.csv")
    st.download_button("Download sample CSV",sample.to_csv(index=False),"procurewatch_sample.csv","text/csv")
    up=st.file_uploader("Upload tender CSV",type="csv")
    if up:
        try:
            df=pd.read_csv(up)
            required=["tender_code","title","category","buyer","tender_value","bid_count","winning_bid","second_bid","supplier","supplier_wins","supplier_share","conflict_signal"]
            missing=[x for x in required if x not in df.columns]
            if missing: st.error("Missing columns: "+", ".join(missing))
            else:
                out=enrich(df); st.dataframe(out,use_container_width=True,hide_index=True)
                st.download_button("Download analyzed CSV",out.to_csv(index=False),"procurewatch_analyzed.csv","text/csv")
        except Exception as e: st.error(f"CSV error: {e}")

with t3:
    raw=pd.read_sql_query("SELECT * FROM tenders",con)
    if raw.empty: st.warning("Register tenders or use CSV Analysis first.")
    else:
        d=enrich(raw); a,b,c,e=st.columns(4)
        a.metric("Tenders reviewed",len(d)); b.metric("High / Critical",int((d.risk_score>=55).sum()))
        c.metric("Average risk",f"{d.risk_score.mean():.1f}"); e.metric("Suppliers",d.supplier.nunique())
        p,q=st.columns(2)
        with p:
            fig=px.histogram(d,x="risk_score",nbins=10,title="Risk-score distribution");fig.update_layout(template="plotly_white");st.plotly_chart(fig,use_container_width=True)
        with q:
            counts=d.risk_band.value_counts().reindex(["Low","Moderate","High","Critical"],fill_value=0).reset_index()
            counts.columns=["risk_band","count"];fig=px.bar(counts,x="risk_band",y="count",title="Screening classification");fig.update_layout(template="plotly_white");st.plotly_chart(fig,use_container_width=True)
        st.dataframe(d.sort_values("risk_score",ascending=False)[["tender_code","title","supplier","risk_score","risk_band","review_note"]],use_container_width=True,hide_index=True)

with t4:
    st.subheader("Transparent screening weights")
    st.dataframe(pd.DataFrame({"Signal":["Pricing deviation","Winning-bid gap","Low competition","Supplier concentration","Repeat wins","Conflict review signal"],
    "Weight":["25%","20%","18%","17%","10%","10%"]}),use_container_width=True,hide_index=True)
    st.write("Bands: Low 0–29.9 · Moderate 30–54.9 · High 55–74.9 · Critical 75–100.")
    st.caption("These are prioritization signals, not findings of misconduct.")
