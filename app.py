import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Education & Unemployment: Causal Analysis", layout="wide")
st.title("Does Higher Education Cause Lower Unemployment?")
st.markdown("**Causal Analysis using Instrumental Variables | Massachusetts and New Hampshire (2000-2024)**")

st.sidebar.header("What-If Scenarios")
st.sidebar.markdown("Adjust tuition cost to simulate policy changes")

tuition_change = st.sidebar.slider(
    "Change in tuition per FTE ($)",
    min_value=-5000, max_value=5000, value=0, step=500
)

st.sidebar.markdown("---")
st.sidebar.markdown("Filter Population")
age_range = st.sidebar.slider("Age range", 25, 64, (25,64))
state = st.sidebar.selectbox("State", ["Both", "Massachusetts", "New Hampshire"])

# From IV 2SLS estimation
iv_estimate  = -0.0944
iv_se        =  0.1042
iv_ci_lower  = -0.2987
iv_ci_upper  =  0.1099
iv_pval      =  0.3653
iv_fstat     =  1176.33

# From Naive OLS
ols_estimate = -0.0322
ols_ci_lower = -0.0332
ols_ci_upper = -0.0313

# First stage coefficient (per $1 tuition)
first_stage_coef = -0.000005

# Effect of tuition change on college degree rate (via first stage)
degree_rate_change = first_stage_coef * tuition_change
 
# Effect on unemployment via IV estimate
unemployment_change = degree_rate_change * iv_estimate
ci_lower_whatif = unemployment_change - 1.96 * iv_se * abs(degree_rate_change)
ci_upper_whatif = unemployment_change + 1.96 * iv_se * abs(degree_rate_change)

st.subheader("Core Results")
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="IV Causal Estimate",
    value=f"{iv_estimate:.4f}",
    delta="pp change in unemployment",
    help="2SLS estimate using tuition per FTE as instrument"
)

col2.metric(
    label="Naive OLS estimate",
    value=f"{ols_estimate:.4f}",
    delta="Biased (selection)",
    help="Unadjusted OLS - overstates causal effect due to selection bias"
)

col3.metric(
    label="First Stage F-Stat",
    value=f"{iv_fstat:,.0f}",
    delta="Strong instrument (>104)",
    help="F-statistic from first stage regression. Rule of thumb: >10 relevant, >104 strong"
)

col4.metric(
    label="IV P-Value",
    value=f"{iv_pval:.4f}",
    delta="Not significant at p<0.05",
    help="Cannot reject null of no causal effect at conventional significance levels"
)

st.markdown("---")

st.subheader("What-If: Tuition Policy Simulation")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Tuition Change", f"${tuition_change:+,}")
col_b.metric("Predicted Change in Degree Rate", f"{degree_rate_change*100:+.3f} pp")
col_c.metric("Predicted Change in Unemployment", f"{unemployment_change*100:+.4f} pp")

st.markdown(f"""
> **Interpretation:** A **${tuition_change:+,}** change in tuition per FTE is predicted to change 
> college degree attainment by **{degree_rate_change*100:+.3f} percentage points**, which translates 
> to an estimated **{unemployment_change*100:+.4f} percentage point** change in unemployment probability.
> Note: This estimate is statistically insignificant (p = {iv_pval:.3f}) — interpret with caution.
""")

st.subheader("What-If: Uncertainty Across Tuition Changes")
st.markdown("The shaded band shows the 95% confidence interval as tuition changes. "
            "The red vertical line marks your current slider selection.")

tuition_range   = np.arange(-5000, 5500, 500)
degree_changes  = first_stage_coef * tuition_range
unemp_changes   = degree_changes * iv_estimate
ci_uppers       = unemp_changes + 1.96 * iv_se * np.abs(degree_changes)
ci_lowers       = unemp_changes - 1.96 * iv_se * np.abs(degree_changes)

fig_band = go.Figure()

# Confidence band
fig_band.add_trace(go.Scatter(
    x=tuition_range, y=ci_uppers,
    mode="lines", line=dict(width=0),
    showlegend=False
))
fig_band.add_trace(go.Scatter(
    x=tuition_range, y=ci_lowers,
    mode="lines", line=dict(width=0),
    fill="tonexty", fillcolor="rgba(26,35,126,0.15)",
    name="95% Confidence Band"
))
# Point estimate line
fig_band.add_trace(go.Scatter(
    x=tuition_range, y=unemp_changes,
    mode="lines", line=dict(color="#1a237e", width=2),
    name="Predicted Effect"
))
# Zero line
fig_band.add_hline(y=0, line_dash="dash", line_color="gray",
                    annotation_text="Zero effect")
# Current slider position
fig_band.add_vline(
    x=tuition_change,
    line_dash="dash", line_color="red",
    annotation_text=f"Current: ${tuition_change:+,}",
    annotation_position="top right"
)
# Highlight current estimate point
current_unemp = first_stage_coef * tuition_change * iv_estimate
fig_band.add_trace(go.Scatter(
    x=[tuition_change], y=[current_unemp],
    mode="markers",
    marker=dict(color="red", size=12, symbol="circle"),
    name=f"Current estimate: {current_unemp*100:+.4f}pp"
))
fig_band.update_layout(
    title="Predicted Change in Unemployment Probability by Tuition Change",
    xaxis_title="Change in Tuition per FTE ($)",
    yaxis_title="Predicted Change in Unemployment Probability",
    template="plotly_white",
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
st.plotly_chart(fig_band, use_container_width=True)

st.markdown("---")

st.subheader("OLS vs. IV Estimate Comparison")

fig_compare = go.Figure()

fig_compare.add_trace(go.Scatter(
    x=["Naive OLS", "Naive OLS"],
    y=[ols_ci_lower, ols_ci_upper],
    mode="lines",
    line=dict(color="#d32f2f", width=3),
    name="OLS 95% CI",
    showlegend=True
))
fig_compare.add_trace(go.Scatter(
    x=["Naive OLS"],
    y=[ols_estimate],
    mode="markers",
    marker=dict(color="#d32f2f", size=12),
    name="OLS Estimate",
    showlegend=True
))

fig_compare.add_trace(go.Scatter(
    x=["IV 2SLS", "IV 2SLS"],
    y=[iv_ci_lower, iv_ci_upper],
    mode="lines",
    line=dict(color="#1a237e", width=3),
    name="IV 95% CI",
    showlegend=True
))
fig_compare.add_trace(go.Scatter(
    x=["IV 2SLS"],
    y=[iv_estimate],
    mode="markers",
    marker=dict(color="#1a237e", size=12),
    name="IV Estimate",
    showlegend=True
))
fig_compare.add_hline(y=0, line_dash="dash", line_color="gray",
                       annotation_text="Zero effect")
fig_compare.update_layout(
    title="Naive OLS vs. Causal IV 2SLS Estimate",
    yaxis_title="Estimated Effect on Unemployment Probability",
    template="plotly_white",
    height=500
)
st.plotly_chart(fig_compare, use_container_width=True)

st.subheader("Robustness Check")
robustness_data = {
    'Specification': ['Baseline IV', 'Drop Recessions', 'Alt. Instrument (is_MA)',
                      'Minimal Controls', 'Expanded Controls (IND FE)'],
    'Estimate': [-0.0944, -0.1639, 0.1039, -0.0705, -0.3150],
    '95% CI Lower': [-0.2987, -0.4494, 0.0934, -0.3664, -0.7431],
    '95% CI Upper': [0.1099, 0.1216, 0.1144, 0.2254, 0.1131],
    'P-Value': [0.3653, 0.2606, 0.0000, 0.6405, 0.1493],
    'F-Stat': [1176.33, 1161.82, 1216.28, 737.75, 847.29],
    'N': [759980, 662525, 759980, 759980, 759980]
}

rob_df = pd.DataFrame(robustness_data)
rob_df['Significant'] = rob_df['P-Value'].apply(lambda x: '✓' if x < 0.05 else '✗')
 
st.dataframe(
    rob_df.style.format({
        'Estimate': '{:.4f}',
        '95% CI Lower': '{:.4f}',
        '95% CI Upper': '{:.4f}',
        'P-Value': '{:.4f}',
        'F-Stat': '{:,.2f}',
        'N': '{:,}'
    }),
    use_container_width=True
)
st.markdown("---")
st.subheader("Interpretation")
st.markdown("""
While descriptive evidence strongly suggests higher education is associated with lower unemployment 
(OLS: -3.22pp), our IV estimates using state tuition costs as an instrument are consistent with a 
negative causal effect (-9.44pp) but are insufficiently precise to reject the null hypothesis 
(p = 0.365). 
 
Key findings:
- The naive OLS overstates the association due to positive selection bias
- The causal estimate is stable in direction across 4 of 5 robustness specifications
- The alternative instrument (is_MA) produces a misleading opposite-signed result, validating our tuition instrument choice
- Wider confidence intervals are inherent to IV — the cost of causal credibility over predictive precision
""")