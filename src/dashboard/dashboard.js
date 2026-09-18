// ============================================================================
// Retail Banking Analytics — Executive Dashboard
// Static, self-contained. All data pre-aggregated at build time (see
// src/dashboard/build_dashboard_data.py). No server / database required.
// ============================================================================
const NAV = [
  {id:"executive",   label:"Executive Overview",   sub:"Bank-wide KPIs and trends"},
  {id:"financial",   label:"Financial Performance", sub:"P&L, NIM, ROA/ROE, cost-to-income"},
  {id:"customers",   label:"Customers",             sub:"Growth, retention, CLV, CAC"},
  {id:"segmentation",label:"Customer Segmentation", sub:"RFM, value, lifecycle & behavioral segments"},
  {id:"products",    label:"Products",              sub:"Penetration, revenue, cross-sell & affinity"},
  {id:"deposits",    label:"Deposits",              sub:"Balances, growth and term structure"},
  {id:"credit",      label:"Loans & Credit Risk",   sub:"Portfolio quality, PD model, expected loss"},
  {id:"digital",     label:"Digital Banking",       sub:"Adoption, engagement and profitability"},
  {id:"fraud",       label:"Fraud & Anomalies",     sub:"Events, loss and detection performance"},
  {id:"branches",    label:"Branch Performance",    sub:"Revenue, profit and productivity by branch"},
  {id:"marketing",   label:"Marketing",             sub:"Campaign conversion and ROI"},
  {id:"forecast",    label:"Forecast",              sub:"12-month projection with backtested model selection"},
  {id:"scenarios",   label:"Scenario Planning",     sub:"Base / Growth / Efficiency / Downside / Stress"},
];

const fmtMoney = (v, compact=true) => {
  if (v === null || v === undefined || isNaN(v)) return "–";
  if (compact && Math.abs(v) >= 1e6) return "$" + (v/1e6).toFixed(2) + "M";
  if (compact && Math.abs(v) >= 1e3) return "$" + (v/1e3).toFixed(0) + "K";
  return "$" + v.toLocaleString(undefined, {maximumFractionDigits:0});
};
const fmtPct = (v, digits=1) => (v===null||v===undefined||isNaN(v)) ? "–" : (v*100).toFixed(digits) + "%";
const fmtNum = (v) => (v===null||v===undefined||isNaN(v)) ? "–" : v.toLocaleString();

const PALETTE = {
  accent:"#0F6E5D", accentSoft:"rgba(15,110,93,0.14)",
  gold:"#B8862B", goldSoft:"rgba(184,134,43,0.16)",
  brick:"#B23A48", brickSoft:"rgba(178,58,72,0.14)",
  ink:"#0B1F3A", inkSoft:"#33404F", muted:"#7A8699", line:"#E3E8EF",
  series:["#0F6E5D","#B8862B","#2F5D8A","#B23A48","#6B5B95","#3E8C8C","#8A6D3B","#5C7A99"]
};
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
Chart.defaults.color = PALETTE.inkSoft;
Chart.defaults.borderColor = PALETTE.line;

let activeCharts = [];
function destroyCharts(){ activeCharts.forEach(c=>c.destroy()); activeCharts = []; }
function mkChart(ctx, config){ const c = new Chart(ctx, config); activeCharts.push(c); return c; }

function kpiCard(label, value, delta=null, deltaLabel="") {
  return `<div class="kpi"><div class="label">${label}</div><div class="num">${value}</div>
    ${delta!==null ? `<div class="delta ${delta>=0?'up':'down'}">${delta>=0?'▲':'▼'} ${deltaLabel}</div>` : ""}</div>`;
}
function card(title, innerHtml, chartHeight="") {
  return `<div class="card"><h3>${title}</h3>${innerHtml}</div>`;
}
function chartWrap(id, tall="") { return `<div class="chart-wrap ${tall}"><canvas id="${id}"></canvas></div>`; }
function riskTag(bucket){
  const cls = ["Low"].includes(bucket) ? "low" : ["Moderate","Elevated"].includes(bucket) ? "mod" : "high";
  return `<span class="tag ${cls}">${bucket}</span>`;
}

// ---------------------------------------------------------------------------
// SECTION RENDERERS
// ---------------------------------------------------------------------------
function renderExecutive(d){
  const k = d.executive.kpis;
  let html = `<div class="kpi-grid">
    ${kpiCard("Total Customers", fmtNum(k.total_customers))}
    ${kpiCard("Active Customers", fmtNum(k.active_customers))}
    ${kpiCard("Total Deposits", fmtMoney(k.total_deposits))}
    ${kpiCard("Total Loans", fmtMoney(k.total_loans))}
    ${kpiCard("Monthly Revenue", fmtMoney(k.monthly_revenue))}
    ${kpiCard("Net Interest Income", fmtMoney(k.net_interest_income))}
    ${kpiCard("Monthly Profit", fmtMoney(k.monthly_profit))}
    ${kpiCard("Net Interest Margin", fmtPct(k.nim))}
    ${kpiCard("Return on Assets", fmtPct(k.roa))}
    ${kpiCard("Return on Equity", fmtPct(k.roe))}
    ${kpiCard("Cost-to-Income", fmtPct(k.cost_to_income))}
    ${kpiCard("Churn Rate", fmtPct(k.churn_rate))}
    ${kpiCard("Digital Adoption (High)", fmtPct(k.digital_adoption_high))}
    ${kpiCard("NPL Ratio", fmtPct(k.npl_ratio))}
  </div>
  <div class="grid-2">
    ${card("Revenue vs. Profit Trend", chartWrap("chart-exec-revenue","tall"))}
    ${card("Key Automated Insights", `<ul class="insight-list">${d.executive.insights.map(i=>`<li>${i}</li>`).join("")}</ul>`)}
  </div>
  <div class="grid-2">
    ${card("Deposit Growth", chartWrap("chart-exec-deposit"))}
    ${card("Customer Base Trend", chartWrap("chart-exec-customers"))}
  </div>`;
  document.getElementById("content").innerHTML = html;

  mkChart(document.getElementById("chart-exec-revenue"), {type:"line",
    data:{labels:d.executive.revenue_trend.months, datasets:[
      {label:"Revenue", data:d.executive.revenue_trend.revenue, borderColor:PALETTE.series[0], backgroundColor:"transparent", tension:0.25},
      {label:"Profit", data:d.executive.revenue_trend.profit, borderColor:PALETTE.series[1], backgroundColor:"transparent", tension:0.25}
    ]}, options:baseLineOpts()});

  mkChart(document.getElementById("chart-exec-deposit"), {type:"line",
    data:{labels:d.executive.deposit_trend.months, datasets:[{label:"Deposits", data:d.executive.deposit_trend.deposits,
      borderColor:PALETTE.series[2], backgroundColor:"rgba(47,93,138,0.08)", fill:true, tension:0.25}]}, options:baseLineOpts(false)});

  mkChart(document.getElementById("chart-exec-customers"), {type:"line",
    data:{labels:d.executive.customer_growth.months, datasets:[{label:"Active Customers", data:d.executive.customer_growth.customers,
      borderColor:PALETTE.series[3], backgroundColor:"transparent", tension:0.25}]}, options:baseLineOpts(false)});
}

function renderFinancial(d){
  const f = d.financial;
  const mix = f.revenue_mix;
  let html = `<div class="grid-2">
    ${card("Revenue Mix (last 6 months avg)", chartWrap("chart-fin-mix"))}
    ${card("Profitability Ratios Trend", chartWrap("chart-fin-ratios","tall"))}
  </div>
  <div class="grid-2">
    ${card("Cost-to-Income Trend", chartWrap("chart-fin-cti"))}
    ${card("Customer Lifetime Value by Segment", chartWrap("chart-fin-clv"))}
  </div>`;
  document.getElementById("content").innerHTML = html;

  mkChart(document.getElementById("chart-fin-mix"), {type:"doughnut",
    data:{labels:Object.keys(mix), datasets:[{data:Object.values(mix), backgroundColor:PALETTE.series}]},
    options:{plugins:{legend:{position:"bottom", labels:{boxWidth:10,font:{size:11}}}}}});

  mkChart(document.getElementById("chart-fin-ratios"), {type:"line",
    data:{labels:f.months, datasets:[
      {label:"NIM", data:f.nim_trend, borderColor:PALETTE.series[0]},
      {label:"ROA", data:f.roa_trend, borderColor:PALETTE.series[1]},
      {label:"ROE", data:f.roe_trend, borderColor:PALETTE.series[3]},
    ]}, options:baseLineOpts(true,true)});

  mkChart(document.getElementById("chart-fin-cti"), {type:"line",
    data:{labels:f.months, datasets:[{label:"Cost-to-Income", data:f.cost_to_income_trend, borderColor:PALETTE.series[2], tension:0.2}]},
    options:baseLineOpts(false,true)});

  const clvSeg = f.profit_by_segment;
  mkChart(document.getElementById("chart-fin-clv"), {type:"bar",
    data:{labels:Object.keys(clvSeg), datasets:[{label:"Total CLV", data:Object.values(clvSeg), backgroundColor:PALETTE.series[0]}]},
    options:baseBarOpts("$")});
}

function renderCustomers(d, filterRegion){
  const c = d.customers;
  let churnByRegion = c.churn_by_region;
  if (filterRegion) churnByRegion = {[filterRegion]: c.churn_by_region[filterRegion]};
  let html = `<div class="kpi-grid">
    ${kpiCard("Avg Products / Customer", c.products_per_customer.toFixed(2))}
    ${kpiCard("Avg CLV", fmtMoney(c.cac_ltv.avg_clv))}
    ${kpiCard("Avg CAC", fmtMoney(c.cac_ltv.avg_cac,false))}
    ${kpiCard("LTV : CAC Ratio", c.cac_ltv.ltv_cac_ratio + "x")}
  </div>
  <div class="grid-2">
    ${card("Signup Cohort Retention", chartWrap("chart-cust-cohort"))}
    ${card("Churn Rate by Region" + (filterRegion?` — ${filterRegion}`:""), chartWrap("chart-cust-churnregion"))}
  </div>
  <div class="grid-2">
    ${card("Single vs. Multi-Product Customers", chartWrap("chart-cust-multi","short"))}
    ${card("CLV by Value Segment", chartWrap("chart-cust-clvseg","short"))}
  </div>`;
  document.getElementById("content").innerHTML = html;

  mkChart(document.getElementById("chart-cust-cohort"), {type:"line",
    data:{labels:c.cohort_retention.quarters, datasets:[{label:"Retention Rate", data:c.cohort_retention.retention.map(v=>v*100),
      borderColor:PALETTE.series[0], tension:0.2}]}, options:baseLineOpts(false,false,"%")});

  mkChart(document.getElementById("chart-cust-churnregion"), {type:"bar",
    data:{labels:Object.keys(churnByRegion), datasets:[{label:"Churn Rate", data:Object.values(churnByRegion).map(v=>v*100),
      backgroundColor:PALETTE.series[3]}]}, options:baseBarOpts("%")});

  mkChart(document.getElementById("chart-cust-multi"), {type:"doughnut",
    data:{labels:["Single-Product","Multi-Product"], datasets:[{data:[c.single_vs_multi.single_product,c.single_vs_multi.multi_product],
      backgroundColor:[PALETTE.series[4],PALETTE.series[0]]}]}, options:{plugins:{legend:{position:"bottom"}}}});

  mkChart(document.getElementById("chart-cust-clvseg"), {type:"bar",
    data:{labels:Object.keys(c.clv_by_segment), datasets:[{label:"Avg CLV", data:Object.values(c.clv_by_segment), backgroundColor:PALETTE.series[1]}]},
    options:baseBarOpts("$")});
}

function renderSegmentation(d){
  const c = d.customers;
  let html = `<div class="grid-3">
    ${card("Value Segment", chartWrap("chart-seg-value","short"))}
    ${card("Lifecycle Segment", chartWrap("chart-seg-life","short"))}
    ${card("RFM Segment", chartWrap("chart-seg-rfm","short"))}
  </div>
  <div class="grid-2">
    ${card("Behavioral Segment", chartWrap("chart-seg-behavior"))}
    ${card("Age Band Distribution", chartWrap("chart-seg-age"))}
  </div>`;
  document.getElementById("content").innerHTML = html;

  const donutOpts = {plugins:{legend:{position:"bottom",labels:{boxWidth:9,font:{size:10}}}}};
  mkChart(document.getElementById("chart-seg-value"), {type:"doughnut",
    data:{labels:Object.keys(c.value_segment), datasets:[{data:Object.values(c.value_segment), backgroundColor:PALETTE.series}]}, options:donutOpts});
  mkChart(document.getElementById("chart-seg-life"), {type:"doughnut",
    data:{labels:Object.keys(c.lifecycle), datasets:[{data:Object.values(c.lifecycle), backgroundColor:PALETTE.series}]}, options:donutOpts});
  mkChart(document.getElementById("chart-seg-rfm"), {type:"doughnut",
    data:{labels:Object.keys(c.rfm_segment), datasets:[{data:Object.values(c.rfm_segment), backgroundColor:PALETTE.series}]}, options:donutOpts});
  mkChart(document.getElementById("chart-seg-behavior"), {type:"bar",
    data:{labels:Object.keys(c.behavioral_segment), datasets:[{label:"Customers", data:Object.values(c.behavioral_segment), backgroundColor:PALETTE.series[0]}]},
    options:baseBarOpts()});
  mkChart(document.getElementById("chart-seg-age"), {type:"bar",
    data:{labels:Object.keys(c.age_band_distribution), datasets:[{label:"Customers", data:Object.values(c.age_band_distribution), backgroundColor:PALETTE.series[2]}]},
    options:baseBarOpts()});
}

function renderProducts(d){
  const p = d.products;
  const pen = p.penetration_pct;
  let html = `<div class="grid-2">
    ${card("Product Penetration (% of customers)", chartWrap("chart-prod-pen","tall"))}
    ${card("Revenue by Product (last 6 months avg)", chartWrap("chart-prod-rev","tall"))}
  </div>
  <div class="grid-2">
    ${card("Top Product Affinities (lift)", `<table><thead><tr><th>Product A</th><th>Product B</th><th>Customers</th><th>Lift</th></tr></thead><tbody>
      ${p.top_affinities.map(a=>`<tr><td>${a.product_a}</td><td>${a.product_b}</td><td>${a.customers_with_both}</td><td>${a.lift}×</td></tr>`).join("")}
    </tbody></table>`)}
    ${card("Cross-Sell Retention Effect", `<table><thead><tr><th>Combo</th><th>Retention (combo)</th><th>Retention (A only)</th></tr></thead><tbody>
      ${p.cross_sell_retention_effect.map(r=>`<tr><td>${r.combo}</td><td>${fmtPct(r.retention_rate_combo)}</td><td>${fmtPct(r.retention_rate_a_only)}</td></tr>`).join("") || "<tr><td colspan=3>Not enough overlapping customers to compare.</td></tr>"}
    </tbody></table>`)}
  </div>`;
  document.getElementById("content").innerHTML = html;

  mkChart(document.getElementById("chart-prod-pen"), {type:"bar",
    data:{labels:Object.keys(pen), datasets:[{label:"% of customers", data:Object.values(pen), backgroundColor:PALETTE.series[0]}]},
    options:baseBarOptsH("%")});

  mkChart(document.getElementById("chart-prod-rev"), {type:"bar",
    data:{labels:Object.keys(p.revenue_by_product), datasets:[{label:"Avg Monthly Revenue", data:Object.values(p.revenue_by_product), backgroundColor:PALETTE.series[1]}]},
    options:baseBarOptsH("$")});
}

function renderDeposits(d){
  const f = d.financial, ex = d.executive;
  let html = `<div class="grid-2">
    ${card("Total Deposit Balance Trend", chartWrap("chart-dep-trend","tall"))}
    ${card("Deposit-Related Product Penetration", chartWrap("chart-dep-products","tall"))}
  </div>`;
  document.getElementById("content").innerHTML = html;
  mkChart(document.getElementById("chart-dep-trend"), {type:"line",
    data:{labels:ex.deposit_trend.months, datasets:[{label:"Deposits", data:ex.deposit_trend.deposits, borderColor:PALETTE.series[2],
      backgroundColor:"rgba(47,93,138,0.08)", fill:true, tension:0.25}]}, options:baseLineOpts(false)});
  const depProducts = ["Checking Account","Savings Account","Term Deposit"].filter(k=>k in d.products.penetration_pct)
    .reduce((o,k)=>{o[k]=d.products.penetration_pct[k]; return o;},{});
  mkChart(document.getElementById("chart-dep-products"), {type:"bar",
    data:{labels:Object.keys(depProducts), datasets:[{label:"% of customers", data:Object.values(depProducts), backgroundColor:PALETTE.series[0]}]},
    options:baseBarOpts("%")});
}

function renderCredit(d){
  const c = d.credit;
  const dpd = c.dpd_distribution;
  const model = c.model_comparison;
  let html = `<div class="kpi-grid">
    ${kpiCard("NPL Ratio", fmtPct(c.npl_ratio,2))}
    ${kpiCard("Default Rate", fmtPct(c.default_rate,2))}
    ${kpiCard("PD Model ROC-AUC (GBC)", (model.gradient_boosting.roc_auc*100).toFixed(1)+"%")}
    ${kpiCard("PD Model ROC-AUC (LogReg)", (model.logistic_regression.roc_auc*100).toFixed(1)+"%")}
  </div>
  <div class="grid-2">
    <div class="card"><h3>DPD Distribution</h3>${chartWrap("chart-credit-dpd")}</div>
    ${card("Outstanding Balance &amp; Expected Loss by Risk Bucket", `<table><thead><tr><th>Risk Bucket</th><th>Loans</th><th>Exposure</th><th>Avg PD</th><th>Expected Loss</th></tr></thead><tbody>
      ${c.portfolio_risk_summary.map(r=>`<tr><td>${riskTag(r.risk_bucket)}</td><td>${fmtNum(r.loan_count)}</td><td>${fmtMoney(r.total_exposure)}</td><td>${fmtPct(r.avg_pd,2)}</td><td>${fmtMoney(r.total_expected_loss)}</td></tr>`).join("")}
    </tbody></table>`)}
  </div>
  <div class="grid-2">
    ${card("Outstanding Balance by Loan Type", chartWrap("chart-credit-type"))}
    ${card("Outstanding Balance by Region", chartWrap("chart-credit-region"))}
  </div>`;
  document.getElementById("content").innerHTML = html;

  mkChart(document.getElementById("chart-credit-dpd"), {type:"doughnut",
    data:{labels:Object.keys(dpd), datasets:[{data:Object.values(dpd).map(v=>v*100), backgroundColor:[PALETTE.series[0],PALETTE.gold,"#C77C1F",PALETTE.brick]}]},
    options:{plugins:{legend:{position:"bottom"}}}});

  mkChart(document.getElementById("chart-credit-type"), {type:"bar",
    data:{labels:c.loans_by_type.map(r=>r.loan_type), datasets:[{label:"Outstanding", data:c.loans_by_type.map(r=>r.outstanding), backgroundColor:PALETTE.series[2]}]},
    options:baseBarOpts("$")});

  mkChart(document.getElementById("chart-credit-region"), {type:"bar",
    data:{labels:Object.keys(c.loans_by_region), datasets:[{label:"Outstanding", data:Object.values(c.loans_by_region), backgroundColor:PALETTE.series[5]}]},
    options:baseBarOptsH("$")});
}

function renderDigital(d, filterDigital){
  const g = d.digital;
  let html = `<div class="grid-3">
    ${card("Digital Adoption", chartWrap("chart-dig-adopt","short"))}
    ${card("Avg Monthly Transactions", chartWrap("chart-dig-txn","short"))}
    ${card("Churn Rate by Adoption Level", chartWrap("chart-dig-churn","short"))}
  </div>
  <div class="grid-2">
    ${card("CLV by Digital Adoption Level", chartWrap("chart-dig-clv"))}
    ${card("Note", `<p style="font-size:12.5px;line-height:1.6;color:var(--muted)">Digitally engaged customers (High and Medium adoption) show meaningfully higher transaction frequency, higher lifetime value, and lower churn than low-adoption, branch-dependent customers — supporting continued investment in mobile/online self-service.</p>`)}
  </div>`;
  document.getElementById("content").innerHTML = html;

  const labels = filterDigital ? [filterDigital] : Object.keys(g.adoption);
  const pick = (obj) => labels.reduce((o,k)=>{o[k]=obj[k]; return o;},{});

  mkChart(document.getElementById("chart-dig-adopt"), {type:"doughnut",
    data:{labels:Object.keys(g.adoption), datasets:[{data:Object.values(g.adoption), backgroundColor:PALETTE.series}]}, options:{plugins:{legend:{position:"bottom"}}}});
  mkChart(document.getElementById("chart-dig-txn"), {type:"bar",
    data:{labels:Object.keys(pick(g.avg_txn_by_adoption)), datasets:[{data:Object.values(pick(g.avg_txn_by_adoption)), backgroundColor:PALETTE.series[0]}]}, options:baseBarOpts()});
  mkChart(document.getElementById("chart-dig-churn"), {type:"bar",
    data:{labels:Object.keys(pick(g.churn_by_adoption)), datasets:[{data:Object.values(pick(g.churn_by_adoption)).map(v=>v*100), backgroundColor:PALETTE.brick}]}, options:baseBarOpts("%")});
  mkChart(document.getElementById("chart-dig-clv"), {type:"bar",
    data:{labels:Object.keys(pick(g.clv_by_adoption)), datasets:[{label:"Avg CLV", data:Object.values(pick(g.clv_by_adoption)), backgroundColor:PALETTE.series[1]}]}, options:baseBarOpts("$")});
}

function renderFraud(d){
  const f = d.fraud;
  let html = `<div class="kpi-grid">
    ${kpiCard("Total Fraud Events", fmtNum(f.total_events))}
    ${kpiCard("Total Loss", fmtMoney(f.total_loss))}
    ${kpiCard("Detection Rate", fmtPct(f.detection_rate))}
    ${kpiCard("False Positive Rate", fmtPct(f.false_positive_rate))}
  </div>
  <div class="grid-2">
    ${card("Fraud by Category", chartWrap("chart-fraud-cat"))}
    ${card("Fraud Loss by Channel", chartWrap("chart-fraud-channel"))}
  </div>`;
  document.getElementById("content").innerHTML = html;
  mkChart(document.getElementById("chart-fraud-cat"), {type:"bar",
    data:{labels:f.by_category.map(r=>r.fraud_category), datasets:[{label:"Events", data:f.by_category.map(r=>r.events), backgroundColor:PALETTE.brick}]},
    options:baseBarOptsH()});
  mkChart(document.getElementById("chart-fraud-channel"), {type:"bar",
    data:{labels:f.by_channel.map(r=>r.channel), datasets:[{label:"Loss ($)", data:f.by_channel.map(r=>r.loss), backgroundColor:PALETTE.gold}]},
    options:baseBarOpts("$")});
}

function renderIranMap(geo, containerId){
  const values = geo.provinces.map(p=>p.value);
  const min = Math.min(...values), max = Math.max(...values);
  const colorFor = (v) => {
    const t = (v-min)/(max-min || 1);
    const r1=228,g1=242,b1=238, r2=15,g2=110,b2=93;
    const r=Math.round(r1+(r2-r1)*t), g=Math.round(g1+(g2-g1)*t), b=Math.round(b1+(b2-b1)*t);
    return `rgb(${r},${g},${b})`;
  };
  let svg = `<svg viewBox="0 0 ${geo.width} ${geo.height}" style="width:100%;height:auto;max-height:440px" xmlns="http://www.w3.org/2000/svg">`;
  geo.provinces.forEach(p=>{
    const fill = colorFor(p.value);
    svg += `<path d="${p.path}" fill="${fill}" stroke="#FFFFFF" stroke-width="1.2">
      <title>${p.name}: ${p.value}</title>
    </path>`;
  });
  svg += `</svg>`;
  document.getElementById(containerId).innerHTML = svg;
}

function renderBranches(d){
  const b = d.branches;
  let html = `${card("Top 10 Branches by Profit (avg last 6 months)", `<table><thead><tr><th>Branch</th><th>Region</th><th>Revenue</th><th>Profit</th><th>Active Customers</th></tr></thead><tbody>
    ${b.top_by_profit.map(r=>`<tr><td>${r.branch_name}</td><td>${r.region}</td><td>${fmtMoney(r.revenue)}</td><td>${fmtMoney(r.profit)}</td><td>${fmtNum(Math.round(r.active_customers))}</td></tr>`).join("")}
  </tbody></table>`)}
  <div class="grid-2" style="margin-top:16px">
    ${card("Revenue vs. Profit — Branch Performance Matrix", chartWrap("chart-branch-matrix","tall"))}
    ${card("Customer Activity Index by Province (Iran)", `<div id="iran-map-container"></div><p style="font-size:11px;color:var(--muted);margin-top:8px">${d.geo.note}</p><p style="font-size:10px;color:var(--muted);margin-top:2px">Map boundaries: © OpenStreetMap contributors (ODbL).</p>`)}
  </div>`;
  document.getElementById("content").innerHTML = html;
  mkChart(document.getElementById("chart-branch-matrix"), {type:"scatter",
    data:{datasets:[{label:"Branches", data:b.performance_matrix.map(r=>({x:r.revenue,y:r.profit})), backgroundColor:PALETTE.series[0]}]},
    options:{plugins:{legend:{display:false}, tooltip:{callbacks:{label:(ctx)=>{
      const r = b.performance_matrix[ctx.dataIndex]; return `${r.branch_name}: Rev ${fmtMoney(r.revenue)}, Profit ${fmtMoney(r.profit)}`; }}}},
      scales:{x:{title:{display:true,text:"Revenue ($)"}}, y:{title:{display:true,text:"Profit ($)"}}}}});
  renderIranMap(d.geo, "iran-map-container");
}

function renderMarketing(d){
  const m = d.marketing;
  let html = `<div class="kpi-grid">
    ${kpiCard("Total Marketing Budget", fmtMoney(m.total_budget))}
    ${kpiCard("Total Conversions", fmtNum(m.total_conversions))}
    ${kpiCard("Avg Conversion Rate", fmtPct(m.avg_conversion_rate))}
  </div>
  ${card("Top Campaigns by ROI", `<table><thead><tr><th>Campaign</th><th>Responses</th><th>Conversions</th><th>ROI</th></tr></thead><tbody>
    ${m.top_campaigns.map(r=>`<tr><td>${r.campaign_name}</td><td>${fmtNum(r.responses)}</td><td>${fmtNum(r.conversions)}</td><td>${r.roi_pct}%</td></tr>`).join("")}
  </tbody></table>`)}`;
  document.getElementById("content").innerHTML = html;
}

function renderForecast(d){
  const f = d.forecast;
  let html = `<div class="grid-2">
    ${card("12-Month Forecast — Deposits", chartWrap("chart-fc-deposits","tall"))}
    ${card("12-Month Forecast — Revenue &amp; Profit", chartWrap("chart-fc-revprofit","tall"))}
  </div>
  <div style="margin-top:16px">${card("Best Model Selected per Series (backtest MAPE)", `<table><thead><tr><th>Series</th><th>Best Method</th><th>Backtest MAPE</th></tr></thead><tbody>
    ${Object.keys(f.methods).map(k=>`<tr><td>${k.replace(/_/g," ")}</td><td>${f.methods[k]}</td><td>${f.backtest_mape[k].toFixed(2)}%</td></tr>`).join("")}
  </tbody></table>`)}</div>`;
  document.getElementById("content").innerHTML = html;

  const labels = [...f.historical_months, ...f.months];
  const nHist = f.historical_months.length;
  const pad = (arr) => new Array(nHist).fill(null).concat(arr);
  const histPad = (arr) => arr.concat(new Array(f.months.length).fill(null));

  mkChart(document.getElementById("chart-fc-deposits"), {type:"line",
    data:{labels, datasets:[
      {label:"Deposits (actual)", data:histPad(f.historical_deposits), borderColor:PALETTE.series[2], borderWidth:2},
      {label:"Deposits (forecast)", data:pad(f.forecast_deposits), borderColor:PALETTE.series[2], borderDash:[5,4], borderWidth:2},
    ]}, options:baseLineOpts(true)});

  mkChart(document.getElementById("chart-fc-revprofit"), {type:"line",
    data:{labels, datasets:[
      {label:"Revenue (actual)", data:histPad(f.historical_revenue), borderColor:PALETTE.series[0], borderWidth:2},
      {label:"Revenue (forecast)", data:pad(f.forecast_revenue), borderColor:PALETTE.series[0], borderDash:[5,4], borderWidth:2},
      {label:"Profit (actual)", data:histPad(f.historical_profit), borderColor:PALETTE.series[1], borderWidth:2},
      {label:"Profit (forecast)", data:pad(f.forecast_profit), borderColor:PALETTE.series[1], borderDash:[5,4], borderWidth:2},
    ]}, options:baseLineOpts(true)});
}

function renderScenarios(d){
  const s = d.scenarios;
  const names = Object.keys(s);
  let html = `<div class="scenario-tabs">${names.map((n,i)=>`<div class="scenario-tab ${i===0?'active':''}" data-scenario="${n}">${n}</div>`).join("")}</div>
  <div class="kpi-grid" id="scenario-kpis"></div>
  ${card("12-Month Scenario Path — Profit", chartWrap("chart-scenario","tall"))}`;
  document.getElementById("content").innerHTML = html;

  function showScenario(name){
    const r = s[name];
    document.getElementById("scenario-kpis").innerHTML = `
      ${kpiCard("Profit (Month 12)", fmtMoney(r.path[r.path.length-1].profit))}
      ${kpiCard("Cumulative 12M Profit", fmtMoney(r.cumulative_12m_profit))}
      ${kpiCard("Annualized ROA (M12)", fmtPct(r.roa_annualized_m12))}
      ${kpiCard("Deposits (Month 12)", fmtMoney(r.path[r.path.length-1].deposits))}
      ${kpiCard("Loans (Month 12)", fmtMoney(r.path[r.path.length-1].loans))}
    `;
    destroyCharts();
    mkChart(document.getElementById("chart-scenario"), {type:"line",
      data:{labels:r.path.map(p=>"M"+p.month_ahead), datasets:[
        {label:"Profit", data:r.path.map(p=>p.profit), borderColor:PALETTE.series[0], tension:0.2},
        {label:"Revenue", data:r.path.map(p=>p.revenue), borderColor:PALETTE.series[2], tension:0.2},
        {label:"Credit Loss", data:r.path.map(p=>-p.credit_loss), borderColor:PALETTE.brick, tension:0.2},
      ]}, options:baseLineOpts(true)});
  }
  document.querySelectorAll(".scenario-tab").forEach(tab=>{
    tab.addEventListener("click", ()=>{
      document.querySelectorAll(".scenario-tab").forEach(t=>t.classList.remove("active"));
      tab.classList.add("active");
      showScenario(tab.dataset.scenario);
    });
  });
  showScenario(names[0]);
}

// ---------------------------------------------------------------------------
// CHART OPTION HELPERS
// ---------------------------------------------------------------------------
function baseLineOpts(showLegend=true, percent=false, suffix=""){
  return {responsive:true, maintainAspectRatio:false,
    interaction:{mode:"index", intersect:false},
    plugins:{legend:{display:showLegend, position:"bottom", labels:{boxWidth:10,font:{size:11}}}},
    scales:{ y:{ ticks:{ callback:(v)=> percent ? (v*100).toFixed(0)+"%" : (suffix==="%" ? v+"%" : (Math.abs(v)>=1000?fmtMoney(v):v)) },
                 grid:{color:PALETTE.line} },
             x:{ grid:{display:false} } } };
}
function baseBarOpts(suffix=""){
  return {responsive:true, maintainAspectRatio:false,
    plugins:{legend:{display:false}},
    scales:{ y:{ ticks:{ callback:(v)=> suffix==="%" ? v+"%" : (suffix==="$" && Math.abs(v)>=1000?fmtMoney(v):fmtNum(v)) }, grid:{color:PALETTE.line} },
             x:{ grid:{display:false} } } };
}
function baseBarOptsH(suffix=""){
  return {responsive:true, maintainAspectRatio:false, indexAxis:"y",
    plugins:{legend:{display:false}},
    scales:{ x:{ ticks:{ callback:(v)=> suffix==="%" ? v+"%" : (suffix==="$" && Math.abs(v)>=1000?fmtMoney(v):fmtNum(v)) }, grid:{color:PALETTE.line} },
             y:{ grid:{display:false} } } };
}

// ---------------------------------------------------------------------------
// APP SHELL: nav, filters, section switching
// ---------------------------------------------------------------------------
const RENDERERS = {
  executive: (d)=>renderExecutive(d),
  financial: (d)=>renderFinancial(d),
  customers: (d,rg)=>renderCustomers(d,rg),
  segmentation: (d)=>renderSegmentation(d),
  products: (d)=>renderProducts(d),
  deposits: (d)=>renderDeposits(d),
  credit: (d)=>renderCredit(d),
  digital: (d,rg,dg)=>renderDigital(d,dg),
  fraud: (d)=>renderFraud(d),
  branches: (d)=>renderBranches(d),
  marketing: (d)=>renderMarketing(d),
  forecast: (d)=>renderForecast(d),
  scenarios: (d)=>renderScenarios(d),
};

let currentSection = "executive";

function renderNav(){
  const list = document.getElementById("nav-list");
  list.innerHTML = NAV.map(n=>`<div class="nav-item ${n.id===currentSection?'active':''}" data-id="${n.id}"><span class="nav-dot"></span>${n.label}</div>`).join("");
  list.querySelectorAll(".nav-item").forEach(el=>{
    el.addEventListener("click", ()=>{ currentSection = el.dataset.id; goToSection(currentSection); });
  });
}

function goToSection(id){
  const meta = NAV.find(n=>n.id===id);
  document.getElementById("section-title").textContent = meta.label;
  document.getElementById("section-subtitle").textContent = meta.sub;
  document.querySelectorAll(".nav-item").forEach(el=>el.classList.toggle("active", el.dataset.id===id));
  destroyCharts();
  const region = document.getElementById("filter-region").value;
  const digital = document.getElementById("filter-digital").value;
  RENDERERS[id](DASHBOARD_DATA, region, digital);
  appendFooter();
}

function populateFilters(){
  const rs = document.getElementById("filter-region");
  DASHBOARD_DATA.filters.regions.forEach(r=>{ const o=document.createElement("option"); o.value=r; o.textContent=r; rs.appendChild(o); });
  const ds = document.getElementById("filter-digital");
  DASHBOARD_DATA.filters.digital_segments.forEach(r=>{ const o=document.createElement("option"); o.value=r; o.textContent=r; ds.appendChild(o); });
  [rs,ds].forEach(sel=>sel.addEventListener("change", ()=>goToSection(currentSection)));
}

function appendFooter(){
  const el = document.getElementById("content");
  const footer = document.createElement("div");
  footer.className = "footer-author";
  footer.innerHTML = `
    <img src="__AUTHOR_PHOTO__" alt="Milad Shabani">
    <div>
      <div class="name">Built by Milad Shabani</div>
      <div class="role">Business Intelligence · Data Analytics · Data Engineering</div>
      <div class="links"><a href="https://github.com/Milad-Shabani" target="_blank" rel="noopener">GitHub: Milad-Shabani</a></div>
    </div>`;
  el.appendChild(footer);
}

document.addEventListener("DOMContentLoaded", ()=>{
  renderNav();
  populateFilters();
  goToSection(currentSection);
});
