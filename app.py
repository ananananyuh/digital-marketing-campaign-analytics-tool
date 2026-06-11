import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# THEME & STYLING
# =====================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #161b27 !important; border-right: 1px solid #2a2f3e; }
.block-container { padding: 1.5rem 2rem 2rem; }
[data-testid="stMetric"] { background: #1a1f2e; border: 1px solid #2a2f3e; border-radius: 12px; padding: 1rem 1.2rem; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; color: #7c8db0 !important; }
[data-testid="stMetricValue"] { font-size: 1.55rem !important; font-weight: 700 !important; color: #e8eaf6 !important; }
[data-testid="stMetricDelta"] { font-size: 0.75rem !important; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: #161b27; padding: 6px; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 6px 18px; font-size: 0.82rem; color: #7c8db0; background: transparent; }
.stTabs [aria-selected="true"] { background: #252b3b !important; color: #e8eaf6 !important; font-weight: 600; }
.sec-header { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #4f5b7c; margin: 0 0 0.5rem; font-weight: 600; }
.alert-box { background: #1a2744; border-left: 3px solid #3d7eff; border-radius: 0 8px 8px 0; padding: 0.7rem 1rem; margin: 0.5rem 0; font-size: 0.85rem; color: #b0c4de; }
.alert-success { background: #142b1e; border-left-color: #4caf50; color: #a5d6a7; }
.alert-warn { background: #2b2010; border-left-color: #ff9800; color: #ffcc80; }
hr { border-color: #2a2f3e; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONSTANTS
# =====================================================
PLATFORM_COLORS = {
    "Google":    "#3d7eff",
    "Facebook":  "#a78bfa",
    "Instagram": "#f472b6",
}
CHART_BG   = "#1a1f2e"
GRID_COLOR = "#2a2f3e"
FONT_COLOR = "#c9d1e9"
PLOT_LAYOUT = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor=CHART_BG,
    font=dict(color=FONT_COLOR, family="Inter, sans-serif", size=12),
    margin=dict(l=12, r=12, t=40, b=12),
    xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(size=10)),
    yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(size=10)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_COLOR, font=dict(size=11)),
)

# =====================================================
# DATA
# =====================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    google    = pd.read_csv("data/google_ads.csv")
    facebook  = pd.read_csv("data/facebook_ads.csv")
    instagram = pd.read_csv("data/instagram_ads.csv")
    google["Platform"]    = "Google"
    facebook["Platform"]  = "Facebook"
    instagram["Platform"] = "Instagram"
    df = pd.concat([google, facebook, instagram], ignore_index=True)
    df["CTR"]             = (df["Clicks"] / df["Impressions"]) * 100
    df["Conversion Rate"] = (df["Conversions"] / df["Clicks"]) * 100
    df["CPC"]             = df["Cost"] / df["Clicks"]
    df["CPL"]             = df["Cost"] / df["Conversions"]
    df["ROI"]             = ((df["Revenue"] - df["Cost"]) / df["Cost"]) * 100
    df["ROAS"]            = df["Revenue"] / df["Cost"]
    df["Profit"]          = df["Revenue"] - df["Cost"]
    return df

df = load_data()

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("### 🎛️ Controls")
    st.markdown("---")
    platforms = st.multiselect(
        "Platforms",
        options=sorted(df["Platform"].unique()),
        default=sorted(df["Platform"].unique()),
    )
    avail_campaigns = sorted(
        df[df["Platform"].isin(platforms)]["Campaign"].unique()
    )
    campaigns = st.multiselect(
        "Campaigns",
        options=avail_campaigns,
        default=avail_campaigns,
    )
    st.markdown("---")
    rank_by = st.selectbox(
        "Rank campaigns by",
        ["ROI", "ROAS", "Revenue", "Profit", "CTR", "Conversion Rate"],
    )
    show_annotations = st.toggle("Show chart annotations", value=True)
    show_insights    = st.toggle("Show insights panel", value=True)
    st.markdown("---")
    st.caption("📅 Data period: Q2 2026")

# =====================================================
# FILTER
# =====================================================
fdf = df[df["Platform"].isin(platforms) & df["Campaign"].isin(campaigns)]
if fdf.empty:
    st.error("No data for the selected filters.")
    st.stop()

# =====================================================
# HEADER
# =====================================================
col_title, col_dl = st.columns([5, 1])
with col_title:
    st.markdown("## 📊 Marketing Analytics Dashboard")
    st.caption(f"Showing **{len(fdf)}** campaigns across **{fdf['Platform'].nunique()}** platforms")
with col_dl:
    st.download_button(
        "⬇ Export CSV",
        data=fdf.to_csv(index=False).encode(),
        file_name="marketing_export.csv",
        mime="text/csv",
        use_container_width=True,
    )
st.markdown("---")

# =====================================================
# KPI STRIP
# =====================================================
k1, k2, k3, k4, k5, k6 = st.columns(6)
total_rev  = fdf["Revenue"].sum()
total_cost = fdf["Cost"].sum()
profit     = fdf["Profit"].sum()
total_conv = int(fdf["Conversions"].sum())
avg_roi    = fdf["ROI"].mean()
avg_roas   = fdf["ROAS"].mean()
all_avg_roi  = df["ROI"].mean()
all_avg_roas = df["ROAS"].mean()

k1.metric("Total Revenue",  f"₹{total_rev:,.0f}")
k2.metric("Total Cost",     f"₹{total_cost:,.0f}")
k3.metric("Net Profit",     f"₹{profit:,.0f}")
k4.metric("Conversions",    f"{total_conv:,}")
k5.metric("Avg ROI",        f"{avg_roi:.1f}%",  delta=f"{avg_roi - all_avg_roi:+.1f}pp vs all")
k6.metric("Avg ROAS",       f"{avg_roas:.2f}x", delta=f"{avg_roas - all_avg_roas:+.2f}x vs all")
st.markdown("")

# =====================================================
# INSIGHTS PANEL
# =====================================================
if show_insights:
    best     = fdf.loc[fdf["ROI"].idxmax()]
    worst    = fdf.loc[fdf["ROI"].idxmin()]
    best_rev = fdf.loc[fdf["Revenue"].idxmax()]
    st.markdown('<p class="sec-header">Quick insights</p>', unsafe_allow_html=True)
    ia, ib, ic = st.columns(3)
    with ia:
        st.markdown(f'<div class="alert-box alert-success">🏆 <b>{best["Campaign"]}</b> leads ROI at <b>{best["ROI"]:.1f}%</b> ({best["Platform"]})</div>', unsafe_allow_html=True)
    with ib:
        st.markdown(f'<div class="alert-box alert-warn">⚠️ <b>{worst["Campaign"]}</b> has lowest ROI at <b>{worst["ROI"]:.1f}%</b> — review spend</div>', unsafe_allow_html=True)
    with ic:
        st.markdown(f'<div class="alert-box">💰 Highest revenue: <b>{best_rev["Campaign"]}</b> — ₹{best_rev["Revenue"]:,.0f} ({best_rev["Platform"]})</div>', unsafe_allow_html=True)
    st.markdown("")

# =====================================================
# HELPER
# =====================================================
def apply_layout(fig, title="", height=360, xangle=-30):
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=FONT_COLOR)),
        height=height,
    )
    if xangle:
        fig.update_xaxes(tickangle=xangle)
    return fig

# =====================================================
# TABS
# =====================================================
t1, t2, t3, t4, t5 = st.tabs([
    "📈 Performance", "🏆 Rankings", "🔍 Deep Dive", "📡 Platform Intel", "📋 Data"
])

# ── TAB 1 ─────────────────────────────────────────
with t1:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(fdf.sort_values("CTR", ascending=False),
                     x="Campaign", y="CTR", color="Platform",
                     color_discrete_map=PLATFORM_COLORS, text_auto=".2f")
        if show_annotations:
            fig.add_hline(y=fdf["CTR"].mean(), line_dash="dot", line_color="#7c8db0",
                          annotation_text=f"Avg {fdf['CTR'].mean():.2f}%",
                          annotation_font_color="#7c8db0")
        apply_layout(fig, "Click-through rate by campaign (%)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sdf = fdf.sort_values("ROI", ascending=False)
        fig = go.Figure(go.Bar(
            x=sdf["Campaign"], y=sdf["ROI"],
            marker_color=[PLATFORM_COLORS[p] for p in sdf["Platform"]],
            text=sdf["ROI"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
        ))
        if show_annotations:
            fig.add_hline(y=0, line_color="#f44336", line_width=1,
                          annotation_text="Breakeven", annotation_font_color="#f44336")
        apply_layout(fig, "ROI by campaign (%)")
        st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(fdf.sort_values("Revenue", ascending=False),
                 x="Campaign", y=["Revenue", "Cost"], barmode="group",
                 color_discrete_sequence=["#3d7eff", "#f44336"])
    apply_layout(fig, "Revenue vs cost per campaign", height=340)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(fdf.sort_values("Conversion Rate", ascending=False),
                     x="Campaign", y="Conversion Rate",
                     color="Platform", color_discrete_map=PLATFORM_COLORS, text_auto=".2f")
        apply_layout(fig, "Conversion rate (%)", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for plat, grp in fdf.groupby("Platform"):
            fig.add_trace(go.Bar(name=f"{plat} CPC", x=grp["Campaign"], y=grp["CPC"],
                                 marker_color=PLATFORM_COLORS[plat], opacity=0.8), secondary_y=False)
            fig.add_trace(go.Scatter(name=f"{plat} CPL", x=grp["Campaign"], y=grp["CPL"],
                                     mode="markers+lines",
                                     marker=dict(color=PLATFORM_COLORS[plat], size=9, symbol="diamond"),
                                     line=dict(dash="dot", width=1.5)), secondary_y=True)
        apply_layout(fig, "CPC (bars) vs CPL (line)", height=320)
        fig.update_yaxes(title_text="CPC (₹)", secondary_y=False, gridcolor=GRID_COLOR)
        fig.update_yaxes(title_text="CPL (₹)", secondary_y=True, gridcolor=GRID_COLOR)
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 2 ─────────────────────────────────────────
with t2:
    c1, c2 = st.columns([3, 2])
    with c1:
        ranked = fdf.sort_values(rank_by, ascending=True)
        fig = go.Figure(go.Bar(
            y=ranked["Campaign"], x=ranked[rank_by], orientation="h",
            marker_color=[PLATFORM_COLORS[p] for p in ranked["Platform"]],
            text=ranked[rank_by].map(lambda v: f"{v:.2f}"),
            textposition="outside",
        ))
        apply_layout(fig, f"Campaign ranking — {rank_by}",
                     height=max(300, len(ranked) * 44), xangle=0)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        plat_rev = fdf.groupby("Platform")["Revenue"].sum().reset_index()
        fig = px.pie(plat_rev, names="Platform", values="Revenue",
                     color="Platform", color_discrete_map=PLATFORM_COLORS, hole=0.5)
        fig.update_traces(textinfo="label+percent", textfont=dict(size=12, color="#e8eaf6"))
        apply_layout(fig, "Revenue share", height=260, xangle=0)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        plat_conv = fdf.groupby("Platform")["Conversions"].sum().reset_index()
        fig2 = px.pie(plat_conv, names="Platform", values="Conversions",
                      color="Platform", color_discrete_map=PLATFORM_COLORS, hole=0.5)
        fig2.update_traces(textinfo="label+percent", textfont=dict(size=12, color="#e8eaf6"))
        apply_layout(fig2, "Conversion share", height=260, xangle=0)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown(f'<p class="sec-header">Top 3 — {rank_by}</p>', unsafe_allow_html=True)
        st.dataframe(fdf.nlargest(3, rank_by)[["Campaign","Platform",rank_by,"Revenue","ROI"]].reset_index(drop=True),
                     use_container_width=True, hide_index=True)
    with cb:
        st.markdown(f'<p class="sec-header">Bottom 3 — {rank_by}</p>', unsafe_allow_html=True)
        st.dataframe(fdf.nsmallest(3, rank_by)[["Campaign","Platform",rank_by,"Revenue","ROI"]].reset_index(drop=True),
                     use_container_width=True, hide_index=True)

# ── TAB 3 ─────────────────────────────────────────
with t3:
    fig = px.scatter(fdf, x="Cost", y="Revenue",
                     color="Platform", color_discrete_map=PLATFORM_COLORS,
                     size="Conversions", hover_name="Campaign",
                     hover_data={"ROI":":.1f","CTR":":.2f","ROAS":":.2f"},
                     text="Campaign")
    fig.update_traces(textposition="top center", textfont=dict(size=9))
    mx = max(fdf["Revenue"].max(), fdf["Cost"].max()) * 1.1
    fig.add_shape(type="line", x0=0, y0=0, x1=mx, y1=mx,
                  line=dict(color="#f44336", dash="dash", width=1))
    fig.add_annotation(x=mx*0.82, y=mx*0.75, text="Breakeven line",
                       showarrow=False, font=dict(size=10, color="#f44336"))
    apply_layout(fig, "Cost vs Revenue — bubble size = conversions", height=440, xangle=0)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(fdf, x="ROAS", y="ROI",
                         color="Platform", color_discrete_map=PLATFORM_COLORS,
                         size="Revenue", hover_name="Campaign", text="Campaign")
        fig.update_traces(textposition="top center", textfont=dict(size=8))
        apply_layout(fig, "ROAS vs ROI — bubble size = revenue", height=380, xangle=0)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.treemap(fdf, path=["Platform","Campaign"],
                         values="Revenue", color="ROI",
                         color_continuous_scale=[[0,"#f44336"],[0.5,"#ff9800"],[1,"#4caf50"]],
                         hover_data={"ROI":":.1f"})
        fig.update_layout(paper_bgcolor=CHART_BG, margin=dict(l=12,r=12,t=40,b=12),
                          font=dict(color=FONT_COLOR), height=380,
                          title=dict(text="Revenue treemap — colour = ROI", font=dict(size=14, color=FONT_COLOR)))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="sec-header">Platform strengths radar</p>', unsafe_allow_html=True)
    radar_metrics = ["CTR","Conversion Rate","ROI","ROAS"]
    plat_avg = fdf.groupby("Platform")[radar_metrics].mean().reset_index()
    for m in radar_metrics:
        mn, mx2 = plat_avg[m].min(), plat_avg[m].max()
        plat_avg[f"{m}_n"] = (plat_avg[m] - mn) / (mx2 - mn + 1e-9)
    fig = go.Figure()
    for _, row in plat_avg.iterrows():
        vals = [row[f"{m}_n"] for m in radar_metrics] + [row[f"{radar_metrics[0]}_n"]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=radar_metrics + [radar_metrics[0]],
            fill="toself", name=row["Platform"],
            line=dict(color=PLATFORM_COLORS[row["Platform"]], width=2), opacity=0.65,
        ))
    fig.update_layout(**PLOT_LAYOUT,
                      polar=dict(bgcolor=CHART_BG,
                                 radialaxis=dict(visible=True, range=[0,1], gridcolor=GRID_COLOR,
                                                 linecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR)),
                                 angularaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                                                  tickfont=dict(color=FONT_COLOR, size=12))),
                      height=400,
                      title=dict(text="Platform strengths (normalised 0–1)", font=dict(size=14, color=FONT_COLOR)))
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 4 ─────────────────────────────────────────
with t4:
    for plat in sorted(fdf["Platform"].unique()):
        row = fdf[fdf["Platform"] == plat]
        with st.expander(
            f"**{plat}** — ₹{row['Revenue'].sum():,.0f} revenue · {row['ROI'].mean():.1f}% avg ROI",
            expanded=True
        ):
            m1,m2,m3,m4,m5,m6 = st.columns(6)
            m1.metric("Revenue",     f"₹{row['Revenue'].sum():,.0f}")
            m2.metric("Cost",        f"₹{row['Cost'].sum():,.0f}")
            m3.metric("Profit",      f"₹{row['Profit'].sum():,.0f}")
            m4.metric("Conversions", f"{int(row['Conversions'].sum()):,}")
            m5.metric("Avg ROI",     f"{row['ROI'].mean():.1f}%")
            m6.metric("Avg ROAS",    f"{row['ROAS'].mean():.2f}x")
            ca, cb = st.columns(2)
            with ca:
                fig = px.bar(row, x="Campaign", y="Revenue",
                             color_discrete_sequence=[PLATFORM_COLORS[plat]], text_auto=True)
                apply_layout(fig, "Revenue by campaign", height=260)
                st.plotly_chart(fig, use_container_width=True)
            with cb:
                fig = px.bar(row, x="Campaign", y="ROI",
                             color_discrete_sequence=[PLATFORM_COLORS[plat]], text_auto=".1f")
                apply_layout(fig, "ROI by campaign (%)", height=260)
                st.plotly_chart(fig, use_container_width=True)

    plat_sum = (fdf.groupby("Platform")
                .agg(Revenue=("Revenue","sum"), Cost=("Cost","sum"), Profit=("Profit","sum"))
                .reset_index())
    fig = px.bar(plat_sum, x="Platform", y=["Revenue","Cost","Profit"],
                 barmode="group", color_discrete_sequence=["#3d7eff","#f44336","#4caf50"])
    apply_layout(fig, "Revenue vs Cost vs Profit — platform comparison", height=340, xangle=0)
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 5 ─────────────────────────────────────────
with t5:
    all_cols = list(fdf.columns)
    default_cols = ["Campaign","Platform","Impressions","Clicks","CTR",
                    "Conversions","Conversion Rate","Cost","Revenue",
                    "Profit","ROI","ROAS","CPC","CPL"]
    sel_cols = st.multiselect("Columns", all_cols,
                               default=[c for c in default_cols if c in all_cols])
    sort_col = st.selectbox("Sort by", sel_cols,
                             index=sel_cols.index("ROI") if "ROI" in sel_cols else 0)
    asc = st.checkbox("Ascending", value=False)

    disp = fdf[sel_cols].sort_values(sort_col, ascending=asc).reset_index(drop=True)
    fmt = {}
    for c in disp.columns:
        if c in ("CTR","Conversion Rate","ROI"):         fmt[c] = "{:.2f}%"
        elif c in ("CPC","CPL","Cost","Revenue","Profit"): fmt[c] = "₹{:,.0f}"
        elif c == "ROAS":                                  fmt[c] = "{:.2f}x"
    st.dataframe(disp.style.format(fmt), use_container_width=True, height=460)

    ca, cb = st.columns(2)
    with ca:
        st.download_button("⬇ Download filtered CSV",
                           data=fdf.to_csv(index=False).encode(),
                           file_name="marketing_filtered.csv", mime="text/csv",
                           use_container_width=True)
    with cb:
        st.download_button("⬇ Download full dataset",
                           data=df.to_csv(index=False).encode(),
                           file_name="marketing_full.csv", mime="text/csv",
                           use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Built with Streamlit · Plotly · Pandas  |  Google · Facebook · Instagram Ads")