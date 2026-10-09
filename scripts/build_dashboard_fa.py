#!/usr/bin/env python3
"""Build the Persian (RTL) dashboard and link it with the English one.

Run AFTER `python scripts/build_dashboard.py` (which regenerates docs/index.html):

    python scripts/build_dashboard_fa.py

What it does
  1. Reads the English dashboard  docs/index.html
  2. Adds a small "English | فارسی" language switch to it (idempotent: safe to re-run)
  3. Writes the Persian version   docs/fa/index.html   (RTL, Persian digits, embedded Vazirmatn font)
     with a switch that links back to ../index.html

GitHub Pages serves docs/, so the pages end up at
  https://<user>.github.io/<repo>/       (English)
  https://<user>.github.io/<repo>/fa/    (Persian)

Standard library only. Font: assets/fonts/Vazirmatn-subset.woff2 (SIL OFL 1.1, see assets/fonts/OFL.txt).
"""
import re, base64, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "docs" / "index.html"
FA_PATH = ROOT / "docs" / "fa" / "index.html"
FONT_PATH = ROOT / "assets" / "fonts" / "Vazirmatn-subset.woff2"

for p in (EN_PATH, FONT_PATH):
    if not p.exists():
        sys.exit("Missing required file: %s" % p)

# ---------------------------------------------------------------- language switch
SW_CSS = """
  /*lang-switch*/
  .lang-switch{display:inline-flex; border:1px solid var(--line); border-radius:7px; overflow:hidden; font-size:12.5px; line-height:1.3;}
  .lang-switch a,.lang-switch span{padding:7px 12px; text-decoration:none; color:var(--ink-soft); background:#fff;}
  .lang-switch a:hover{background:var(--panel); color:var(--ink);}
  .lang-switch .active{background:var(--ink); color:#fff; font-weight:600;}
  .lang-switch [lang="fa"]{font-family:'Vazirmatn',Tahoma,'Segoe UI',system-ui,sans-serif;}
  /*/lang-switch*/
"""
SW_EN = ('<!--lang-switch--><nav class="lang-switch" aria-label="Language">'
         '<span class="active" lang="en" aria-current="true">English</span>'
         '<a href="fa/index.html" lang="fa" hreflang="fa">فارسی</a></nav><!--/lang-switch-->')
SW_FA = ('<!--lang-switch--><nav class="lang-switch" aria-label="زبان">'
         '<a href="../index.html" lang="en" hreflang="en">English</a>'
         '<span class="active" lang="fa" aria-current="true">فارسی</span></nav><!--/lang-switch-->')
DIGITAL_SELECT = '<select id="filter-digital"><option value="">All Digital Segments</option></select>'

def strip_switch(html):
    html = re.sub(r"\n[ ]*<!--lang-switch-->.*?<!--/lang-switch-->", "", html, flags=re.S)
    html = re.sub(r"\n  /\*lang-switch\*/.*?/\*/lang-switch\*/\n", "", html, flags=re.S)
    return html

def add_switch(html, switch_html):
    if DIGITAL_SELECT not in html:
        sys.exit("Could not find the filter bar in docs/index.html - did the dashboard template change?")
    html = html.replace(DIGITAL_SELECT, DIGITAL_SELECT + "\n        " + switch_html, 1)
    return html.replace("</style>", SW_CSS + "</style>", 1)

base = strip_switch(EN_PATH.read_text(encoding="utf-8"))
t_en = add_switch(base, SW_EN)
t = add_switch(base, SW_FA)          # source for the Persian build below

def rep(seg, old, new, minc=1):
    """str.replace that fails loudly if the English template changed and a string is no longer found."""
    if seg.count(old) < minc:
        sys.exit("String not found in the English dashboard (template changed?): " + old[:90])
    return seg.replace(old, new)

# ---------------------------------------------------------------- segments
s0 = t.index("<style>"); s1 = t.index("</style>")
a0 = t.index("<script>\n// ====")
head, css, body, app = t[:s0], t[s0:s1], t[s1:a0], t[a0:]

# ---------------------------------------------------------------- head / body
head = rep(head, '<html lang="en">', '<html lang="fa" dir="rtl">')
head = rep(head, "<title>Retail Banking Analytics — Executive Dashboard</title>",
           "<title>تحلیل بانکداری خرد — داشبورد مدیریتی</title>")
for o, n in [
    ('<div class="mark">Retail Banking Analytics</div>', '<div class="mark">تحلیل بانکداری خرد</div>'),
    ('Customer Intelligence · Financial Performance<br>Risk · Churn · Forecasting',
     'هوش مشتری · عملکرد مالی<br>ریسک · ریزش · پیش‌بینی'),
    ('Synthetic data for educational &amp; portfolio purposes only — not a real bank, not investment advice, not a regulatory model.',
     'داده‌های مصنوعی صرفاً برای اهداف آموزشی و نمونه‌کار — این یک بانک واقعی نیست، توصیه سرمایه‌گذاری محسوب نمی‌شود و مدل نظارتی نیست.'),
    ('<h1 id="section-title">Executive Overview</h1>', '<h1 id="section-title">نمای کلی مدیریتی</h1>'),
    ('Bank-wide KPIs and trends</div>', 'شاخص‌ها و روندهای کلیدی کل بانک</div>'),
    ('<option value="">All Regions</option>', '<option value="">همه مناطق</option>'),
    ('<option value="">All Digital Segments</option>', '<option value="">همه بخش‌های دیجیتال</option>'),
]:
    body = rep(body, o, n)

# ---------------------------------------------------------------- CSS
font_b64 = base64.b64encode(FONT_PATH.read_bytes()).decode()
for o, n in [
    ("font-family:'Inter',system-ui,-apple-system,Segoe UI,Roboto,sans-serif; font-size:14px;}",
     "font-family:'Vazirmatn','Vazir','IRANSans',Tahoma,'Segoe UI',system-ui,sans-serif; font-size:14px; line-height:1.7;}"),
    ("h1,h2,h3,.num{font-family:'Manrope',system-ui,sans-serif;}",
     "h1,h2,h3,.num{font-family:'Vazirmatn','Vazir',Tahoma,system-ui,sans-serif;}"),
    (".brand .mark{font-family:'Manrope',sans-serif;", ".brand .mark{font-family:'Vazirmatn',Tahoma,sans-serif;"),
    ("th{text-align:left;", "th{text-align:right;"),
    ("padding-left:16px; position:relative;}", "padding-right:16px; position:relative;}"),
    ('content:"—"; position:absolute; left:0;', 'content:"—"; position:absolute; right:0;'),
    ("margin-right:14px; font-weight:600;}", "margin-left:14px; font-weight:600;}"),
    ("left:-260px; transition:left .2s;", "right:-260px; transition:right .2s;"),
    (".sidebar.open{left:0;}", ".sidebar.open{right:0;}"),
]:
    css = rep(css, o, n)
css += ("\n  /* ---------- Persian / RTL additions ---------- */\n"
        "  @font-face{font-family:'Vazirmatn'; src:url(data:font/woff2;base64," + font_b64 + ") format('woff2'); font-weight:100 900; font-style:normal; font-display:swap;}\n"
        "  *{letter-spacing:0 !important; text-transform:none !important;}\n"
        "  .kpi .label{font-size:12px; line-height:1.5;}\n"
        "  .kpi .num{line-height:1.4;}\n"
        "  .brand .sub{line-height:1.9;}\n"
        "  th{font-size:11.5px;}\n"
        "  .nav-item{line-height:1.5;}\n"
        "  .scenario-tab{font-family:inherit;}\n")

# ---------------------------------------------------------------- app: localization layer
LOC = r'''// ---------------------------------------------------------------------------
// PERSIAN LOCALIZATION LAYER (added in the fa version)
// Data stays identical to the English build; labels are translated once at load.
// ---------------------------------------------------------------------------
const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const fa = (s) => String(s).replace(/\d/g, d => FA_DIGITS[d]).replace(/([۰-۹])\.([۰-۹])/g, "$1٫$2");
const sgn = (neg, t) => neg ? "⁦-" + t + "⁩" : t;   // keep the minus sign on the correct side in RTL text
const FA_MAP = {
  "Affluent":"مرفه","High Value":"ارزش بالا","Mass":"عمومی","Mass Affluent":"نیمه‌مرفه","Premium":"پریمیوم",
  "High":"بالا","Medium":"متوسط","Low":"پایین","Moderate":"متوسط","Elevated":"نسبتاً بالا","Critical":"بحرانی",
  "Loyal":"وفادار","Established":"تثبیت‌شده","Churned":"ریزش‌کرده","Growing":"در حال رشد","New":"جدید",
  "Potential Loyalist":"وفادار بالقوه","At Risk":"در معرض ریزش","Lost":"ازدست‌رفته",
  "Digital First":"دیجیتال‌محور","Low Engagement":"تعامل کم","Deposit Heavy":"سپرده‌محور","Branch Dependent":"وابسته به شعبه","Transaction Heavy":"تراکنش‌محور",
  "18-25":"۱۸ تا ۲۵","26-35":"۲۶ تا ۳۵","36-45":"۳۶ تا ۴۵","46-55":"۴۶ تا ۵۵","56-65":"۵۶ تا ۶۵","66+":"۶۶ به بالا",
  "Current":"جاری","30-59":"۳۰ تا ۵۹","60-89":"۶۰ تا ۸۹","90+":"۹۰ به بالا",
  "Checking Account":"حساب جاری","Savings Account":"حساب پس‌انداز","Credit Card":"کارت اعتباری","Debit Card":"کارت نقدی",
  "Term Deposit":"سپرده مدت‌دار","Bancassurance":"بیمه‌بانک","Overdraft Facility":"اضافه‌برداشت","Personal Loan":"وام شخصی",
  "Mortgage":"وام مسکن","Consumer Loan":"وام مصرفی","Auto Loan":"وام خودرو","Investment Account":"حساب سرمایه‌گذاری",
  "Digital Onboarding":"جذب دیجیتال","Savings":"پس‌انداز",
  "ATM":"خودپرداز","Branch":"شعبه","Card Network":"شبکه کارت","Mobile App":"اپلیکیشن موبایل","Online Banking":"بانکداری اینترنتی",
  "ATM Fraud":"تقلب در خودپرداز","Account Takeover":"تصاحب حساب","Card Fraud":"تقلب کارتی","Identity-related Anomaly":"ناهنجاری هویتی",
  "Suspicious Transfer":"انتقال مشکوک","Unusual Transaction Pattern":"الگوی تراکنش غیرعادی",
  "Branch Visit":"مراجعه حضوری","Chat":"گفتگوی آنلاین","Complaint":"شکایت","Email Inquiry":"استعلام ایمیلی","Support Call":"تماس پشتیبانی","Optimal":"بهینه",
  "Base Case":"سناریوی پایه","Growth Case":"سناریوی رشد","Efficiency Case":"سناریوی کارایی","Downside Case":"سناریوی نزولی","Stress Case":"سناریوی تنش",
  "Holt-Winters (ETS)":"هالت-وینترز (ETS)","Linear Trend (ML)":"روند خطی (ML)","Seasonal Naive":"ساده فصلی",
  "Alborz":"البرز","Ardabil":"اردبیل","Bushehr":"بوشهر","Chaharmahal and Bakhtiari":"چهارمحال و بختیاری","East Azerbaijan":"آذربایجان شرقی",
  "Fars":"فارس","Gilan":"گیلان","Golestan":"گلستان","Hamadan":"همدان","Hormozgan":"هرمزگان","Ilam":"ایلام","Isfahan":"اصفهان",
  "Kerman":"کرمان","Kermanshah":"کرمانشاه","Khuzestan":"خوزستان","Kohgiluyeh and Boyer-Ahmad":"کهگیلویه و بویراحمد","Kurdistan":"کردستان",
  "Lorestan":"لرستان","Markazi":"مرکزی","Mazandaran":"مازندران","North Khorasan":"خراسان شمالی","Qazvin":"قزوین","Qom":"قم",
  "Razavi Khorasan":"خراسان رضوی","Semnan":"سمنان","Sistan and Baluchestan":"سیستان و بلوچستان","South Khorasan":"خراسان جنوبی",
  "Tehran":"تهران","West Azerbaijan":"آذربایجان غربی","Yazd":"یزد","Zanjan":"زنجان",
  "Illustrative synthetic customer-activity index by province, for visualization purposes only — not derived from the core dataset's generic region labels.":
    "شاخص مصنوعی و نمایشی فعالیت مشتریان به تفکیک استان، فقط برای مصورسازی — از برچسب‌های کلی منطقه در مجموعه‌داده اصلی استخراج نشده است."
};
const MIX_FA = {net_interest_income:"درآمد خالص بهره", fee_income:"درآمد کارمزد", card_revenue:"درآمد کارت", other_operating_income:"سایر درآمدهای عملیاتی"};
const SERIES_FA = {deposits:"سپرده‌ها", loans:"وام‌ها", revenue:"درآمد", net_interest_income:"درآمد خالص بهره", fee_income:"درآمد کارمزد",
  operating_costs:"هزینه‌های عملیاتی", credit_loss:"زیان اعتباری", profit:"سود", customer_base:"پایه مشتریان"};
const INSIGHT_RULES = [
  [/^Deposits grew ([\d.\-]+)% cumulatively over the 24-month window\.$/, m => `سپرده‌ها در بازه ۲۴ ماهه در مجموع ${fa(m[1])}٪ رشد کرده‌اند.`],
  [/^Customer churn stands at ([\d.]+)%, with digitally engaged customers \(High\/Medium adoption\) showing markedly stronger retention than low-adoption customers\.$/,
    m => `نرخ ریزش مشتریان ${fa(m[1])}٪ است و مشتریانِ دارای تعامل دیجیتال (پذیرش بالا/متوسط) نگهداشت به‌مراتب بهتری نسبت به مشتریان با پذیرش پایین دارند.`],
  [/^The '(.+)' segment contributes the largest total lifetime value\.$/, m => `بخش «${tr(m[1])}» بیشترین سهم را در مجموع ارزش طول عمر مشتری (CLV) دارد.`],
  [/^NPL ratio is ([\d.]+)%, concentrated in Critical\/High risk-bucket loans\.$/, m => `نسبت مطالبات غیرجاری (NPL) برابر ${fa(m[1])}٪ است و عمدتاً در وام‌های سطح ریسک بحرانی/بالا متمرکز است.`],
  [/^Digital-first customers represent ([\d.]+)% of the base\.$/, m => `مشتریان «دیجیتال‌محور» ${fa(m[1])}٪ از پایه مشتریان را تشکیل می‌دهند.`],
  [/^The churn model reaches ([\d.]+) ROC-AUC; the credit-risk PD model reaches ([\d.]+)\.$/, m => `مدل پیش‌بینی ریزش به ROC-AUC برابر ${fa(m[1])} و مدل ریسک اعتباری (PD) به ${fa(m[2])} می‌رسد.`],
  [/^Optimized marketing\/retention allocation is projected to lift expected incremental profit by ([\d.]+)%\.$/, m => `تخصیص بهینه بودجه بازاریابی/نگهداشت، سود افزایشی مورد انتظار را حدود ${fa(m[1])}٪ افزایش می‌دهد.`],
];
function tr(s){
  if (typeof s !== "string") return s;
  if (Object.prototype.hasOwnProperty.call(FA_MAP, s)) return FA_MAP[s];
  let m;
  if ((m = s.match(/^Region-(\d+)$/))) return "منطقه " + fa(m[1]);
  if ((m = s.match(/^Branch (\d+)$/))) return "شعبه " + fa(m[1]);
  if ((m = s.match(/^Campaign (\d+) - (.+)$/))) return "کمپین " + fa(m[1]) + " – " + tr(m[2]);
  if ((m = s.match(/^(\d{4})Q(\d)$/))) return fa(m[1]) + " س" + fa(m[2]);
  if (/^\d{4}-\d{2}$/.test(s)) return fa(s);
  if (s.indexOf(" + ") > 0) { const parts = s.split(" + "); if (parts.every(p => Object.prototype.hasOwnProperty.call(FA_MAP, p))) return parts.map(tr).join(" و "); }
  for (const [re, fn] of INSIGHT_RULES){ const mm = s.match(re); if (mm) return fn(mm); }
  return s;
}
function localizeData(o){
  if (Array.isArray(o)) return o.map(localizeData);
  if (o && typeof o === "object"){ const out = {}; for (const k of Object.keys(o)) out[tr(k)] = localizeData(o[k]); return out; }
  return tr(o);
}
const DATA_FA = localizeData(DASHBOARD_DATA);

'''
app = rep(app, "const NAV = [", LOC + "const NAV = [")

# NAV
NAV = r'''const NAV = [
  {id:"executive",   label:"نمای کلی مدیریتی",      sub:"شاخص‌ها و روندهای کلیدی کل بانک"},
  {id:"financial",   label:"عملکرد مالی",           sub:"سود و زیان، NIM، ROA/ROE، نسبت هزینه به درآمد"},
  {id:"customers",   label:"مشتریان",               sub:"رشد، نگهداشت، ارزش طول عمر (CLV)، هزینه جذب (CAC)"},
  {id:"segmentation",label:"بخش‌بندی مشتریان",       sub:"بخش‌های RFM، ارزشی، چرخه عمر و رفتاری"},
  {id:"products",    label:"محصولات",               sub:"نفوذ، درآمد، فروش متقابل و هم‌خوانی محصولات"},
  {id:"deposits",    label:"سپرده‌ها",               sub:"مانده، رشد و ساختار سررسید"},
  {id:"credit",      label:"وام‌ها و ریسک اعتباری",  sub:"کیفیت پورتفوی، مدل PD، زیان مورد انتظار"},
  {id:"digital",     label:"بانکداری دیجیتال",       sub:"پذیرش، تعامل و سودآوری"},
  {id:"fraud",       label:"تقلب و ناهنجاری‌ها",     sub:"رویدادها، زیان و عملکرد تشخیص"},
  {id:"branches",    label:"عملکرد شعب",            sub:"درآمد، سود و بهره‌وری به تفکیک شعبه"},
  {id:"marketing",   label:"بازاریابی",             sub:"تبدیل کمپین‌ها و بازده سرمایه‌گذاری"},
  {id:"forecast",    label:"پیش‌بینی",              sub:"پیش‌بینی ۱۲ ماهه با انتخاب مدل بر پایه بک‌تست"},
  {id:"scenarios",   label:"برنامه‌ریزی سناریو",     sub:"پایه / رشد / کارایی / نزولی / تنش"},
];'''
app, n = re.subn(r"const NAV = \[.*?\n\];", lambda m: NAV, app, count=1, flags=re.S)
assert n == 1

# formatters
FMT = r'''const fmtMoney = (v, compact=true) => {
  if (v === null || v === undefined || isNaN(v)) return "–";
  const a = Math.abs(v), neg = v < 0;
  if (compact && a >= 1e6) return sgn(neg, fa((a/1e6).toFixed(2))) + " میلیون دلار";
  if (compact && a >= 1e3) return sgn(neg, fa((a/1e3).toFixed(0))) + " هزار دلار";
  return sgn(neg, a.toLocaleString("fa-IR", {maximumFractionDigits:0})) + " دلار";
};
const fmtPct = (v, digits=1) => (v===null||v===undefined||isNaN(v)) ? "–" : sgn(v<0, fa(Math.abs(v*100).toFixed(digits))) + "٪";
const fmtNum = (v) => (v===null||v===undefined||isNaN(v)) ? "–" : v.toLocaleString("fa-IR");
const tickMoney = (v) => { const a = Math.abs(v), neg = v < 0;
  if (a >= 1e6) return sgn(neg, fa(+(a/1e6).toFixed(1))) + " میلیون";
  if (a >= 1e3) return sgn(neg, fa(+(a/1e3).toFixed(0))) + " هزار";
  return sgn(neg, fa(+a.toFixed(2))); };
const tickPct = (v) => sgn(v<0, fa(+Math.abs(v).toFixed(1))) + "٪";'''
app, n = re.subn(r"const fmtMoney = .*?(?=\nconst PALETTE)", lambda m: FMT, app, count=1, flags=re.S)
assert n == 1

# chart defaults
app = rep(app, """Chart.defaults.font.family = "'Inter', system-ui, sans-serif";""",
          """Chart.defaults.font.family = "'Vazirmatn', 'Vazir', Tahoma, system-ui, sans-serif";""")
app = rep(app, "Chart.defaults.borderColor = PALETTE.line;",
          'Chart.defaults.borderColor = PALETTE.line;\n'
          'Chart.defaults.locale = "fa-IR";\n'
          'Chart.defaults.plugins.legend.rtl = true; Chart.defaults.plugins.legend.textDirection = "rtl";\n'
          'Chart.defaults.plugins.tooltip.rtl = true; Chart.defaults.plugins.tooltip.textDirection = "rtl";')

# chart option helpers
OPTS = r'''function baseLineOpts(showLegend=true, percent=false, suffix=""){
  return {responsive:true, maintainAspectRatio:false,
    interaction:{mode:"index", intersect:false},
    plugins:{legend:{display:showLegend, position:"bottom", labels:{boxWidth:10,font:{size:11}}}},
    scales:{ y:{ ticks:{ callback:(v)=> percent ? tickPct(v*100) : (suffix==="%" ? tickPct(v) : (suffix==="#" ? fmtNum(v) : tickMoney(v))) },
                 grid:{color:PALETTE.line} },
             x:{ grid:{display:false} } } };
}
function baseBarOpts(suffix=""){
  return {responsive:true, maintainAspectRatio:false,
    plugins:{legend:{display:false}},
    scales:{ y:{ ticks:{ callback:(v)=> suffix==="%" ? tickPct(v) : (suffix==="$" ? tickMoney(v) : fmtNum(v)) }, grid:{color:PALETTE.line} },
             x:{ grid:{display:false} } } };
}
function baseBarOptsH(suffix=""){
  return {responsive:true, maintainAspectRatio:false, indexAxis:"y",
    plugins:{legend:{display:false}},
    scales:{ x:{ ticks:{ callback:(v)=> suffix==="%" ? tickPct(v) : (suffix==="$" ? tickMoney(v) : fmtNum(v)) }, grid:{color:PALETTE.line} },
             y:{ grid:{display:false} } } };
}
'''
app, n = re.subn(r"function baseLineOpts.*?(?=// -{10,}\n// APP SHELL)", lambda m: OPTS, app, count=1, flags=re.S)
assert n == 1

# customers trend is a count, not money (original formatted it as $)
app, n = re.subn(r'(label:"Active Customers".*?options:)baseLineOpts\(false\)', r'\1baseLineOpts(false,false,"#")', app, count=1, flags=re.S)
assert n == 1

# logic that depends on translated labels
app = rep(app, '["Low"].includes(bucket) ? "low" : ["Moderate","Elevated"].includes(bucket)',
          '[FA_MAP["Low"]].includes(bucket) ? "low" : [FA_MAP["Moderate"],FA_MAP["Elevated"]].includes(bucket)')
app = rep(app, '["Checking Account","Savings Account","Term Deposit"]',
          '[FA_MAP["Checking Account"],FA_MAP["Savings Account"],FA_MAP["Term Deposit"]]')
app = rep(app, "labels:Object.keys(mix)", "labels:Object.keys(mix).map(k=>MIX_FA[k]||k)")
app = rep(app, 'k.replace(/_/g," ")', '(SERIES_FA[k]||k.replace(/_/g," "))')
app = rep(app, "RENDERERS[id](DASHBOARD_DATA, region, digital);", "RENDERERS[id](DATA_FA, region, digital);")
app = rep(app, "DASHBOARD_DATA.filters.regions.forEach", "DATA_FA.filters.regions.forEach")
app = rep(app, "DASHBOARD_DATA.filters.digital_segments.forEach", "DATA_FA.filters.digital_segments.forEach")

# number formatting spots
for o, n in [
    ("c.products_per_customer.toFixed(2)", "fa(c.products_per_customer.toFixed(2))"),
    ('c.cac_ltv.ltv_cac_ratio + "x"', 'fa(c.cac_ltv.ltv_cac_ratio) + " برابر"'),
    ('(model.gradient_boosting.roc_auc*100).toFixed(1)+"%"', 'fa((model.gradient_boosting.roc_auc*100).toFixed(1))+"٪"'),
    ('(model.logistic_regression.roc_auc*100).toFixed(1)+"%"', 'fa((model.logistic_regression.roc_auc*100).toFixed(1))+"٪"'),
    ("<td>${a.customers_with_both}</td><td>${a.lift}×</td>", "<td>${fmtNum(a.customers_with_both)}</td><td>${fa(a.lift)}×</td>"),
    ("<td>${r.roi_pct}%</td>", "<td>${fa(r.roi_pct)}٪</td>"),
    ("${f.backtest_mape[k].toFixed(2)}%", "${fa(f.backtest_mape[k].toFixed(2))}٪"),
    ('"M"+p.month_ahead', '"ماه "+fa(p.month_ahead)'),
    ("<title>${p.name}: ${p.value}</title>", "<title>${p.name}: ${fa(p.value)}</title>"),
    ("`${r.branch_name}: Rev ${fmtMoney(r.revenue)}, Profit ${fmtMoney(r.profit)}`", "`${r.branch_name}: درآمد ${fmtMoney(r.revenue)}، سود ${fmtMoney(r.profit)}`"),
    ("Not enough overlapping customers to compare.", "تعداد مشتریان مشترک برای مقایسه کافی نیست."),
    ("<h3>DPD Distribution</h3>", "<h3>توزیع روزهای تأخیر در بازپرداخت (DPD)</h3>"),
    ("Map boundaries: © OpenStreetMap contributors (ODbL).", "مرزهای نقشه: © مشارکت‌کنندگان OpenStreetMap (ODbL)."),
    ("Built by Milad Shabani", "ساخته‌شده توسط میلاد شعبانی"),
    ("Business Intelligence · Data Analytics · Data Engineering", "هوش تجاری · تحلیل داده · مهندسی داده"),
    ("Digitally engaged customers (High and Medium adoption) show meaningfully higher transaction frequency, higher lifetime value, and lower churn than low-adoption, branch-dependent customers — supporting continued investment in mobile/online self-service.",
     "مشتریان دارای تعامل دیجیتال (پذیرش بالا و متوسط) در مقایسه با مشتریان کم‌پذیرش و وابسته به شعبه، تعداد تراکنش بیشتر، ارزش طول عمر بالاتر و ریزش کمتری دارند — این موضوع از ادامه سرمایه‌گذاری در خدمات خودسرویس موبایلی و آنلاین پشتیبانی می‌کند."),
]:
    app = rep(app, o, n)

# table headers
TH = {"Product A":"محصول اول","Product B":"محصول دوم","Customers":"مشتریان","Lift":"لیفت","Combo":"ترکیب",
      "Retention (combo)":"نگهداشت (ترکیب)","Retention (A only)":"نگهداشت (فقط محصول اول)","Risk Bucket":"سطح ریسک",
      "Loans":"تعداد وام","Exposure":"مانده در معرض ریسک","Avg PD":"میانگین PD","Expected Loss":"زیان مورد انتظار",
      "Branch":"شعبه","Region":"منطقه","Revenue":"درآمد","Profit":"سود","Active Customers":"مشتریان فعال",
      "Campaign":"کمپین","Responses":"پاسخ‌ها","Conversions":"تبدیل‌ها","ROI":"ROI","Series":"سری",
      "Best Method":"بهترین روش","Backtest MAPE":"MAPE بک‌تست"}
for o, n in TH.items():
    app = rep(app, "<th>%s</th>" % o, "<th>%s</th>" % n)

# quoted UI strings
UI = {
 "Total Customers":"کل مشتریان","Active Customers":"مشتریان فعال","Total Deposits":"کل سپرده‌ها","Total Loans":"کل وام‌ها",
 "Monthly Revenue":"درآمد ماهانه","Net Interest Income":"درآمد خالص بهره (NII)","Monthly Profit":"سود ماهانه",
 "Net Interest Margin":"حاشیه خالص بهره (NIM)","Return on Assets":"بازده دارایی‌ها (ROA)","Return on Equity":"بازده حقوق صاحبان سهام (ROE)",
 "Cost-to-Income":"نسبت هزینه به درآمد","Churn Rate":"نرخ ریزش","Digital Adoption (High)":"پذیرش دیجیتال (بالا)",
 "NPL Ratio":"نسبت مطالبات غیرجاری (NPL)","Revenue vs. Profit Trend":"روند درآمد و سود","Key Automated Insights":"بینش‌های کلیدی خودکار",
 "Deposit Growth":"رشد سپرده‌ها","Customer Base Trend":"روند پایه مشتریان","Revenue":"درآمد","Profit":"سود","Deposits":"سپرده‌ها",
 "Revenue Mix (last 6 months avg)":"ترکیب درآمد (میانگین ۶ ماه اخیر)","Profitability Ratios Trend":"روند نسبت‌های سودآوری",
 "Cost-to-Income Trend":"روند نسبت هزینه به درآمد","Customer Lifetime Value by Segment":"ارزش طول عمر مشتری (CLV) به تفکیک بخش",
 "Total CLV":"مجموع CLV","Avg Products / Customer":"میانگین محصول به‌ازای هر مشتری","Avg CLV":"میانگین CLV",
 "Avg CAC":"میانگین هزینه جذب (CAC)","LTV : CAC Ratio":"نسبت LTV به CAC","Signup Cohort Retention":"نگهداشت گروه‌های ثبت‌نام (Cohort)",
 "Churn Rate by Region":"نرخ ریزش به تفکیک منطقه","Single vs. Multi-Product Customers":"مشتریان تک‌محصولی در برابر چندمحصولی",
 "CLV by Value Segment":"CLV به تفکیک بخش ارزشی","Retention Rate":"نرخ نگهداشت","Single-Product":"تک‌محصولی","Multi-Product":"چندمحصولی",
 "Value Segment":"بخش ارزشی","Lifecycle Segment":"بخش چرخه عمر","RFM Segment":"بخش RFM","Behavioral Segment":"بخش رفتاری",
 "Age Band Distribution":"توزیع گروه‌های سنی","Customers":"مشتریان",
 "Product Penetration (% of customers)":"نفوذ محصولات (درصد مشتریان)","Revenue by Product (last 6 months avg)":"درآمد به تفکیک محصول (میانگین ۶ ماه اخیر)",
 "Top Product Affinities (lift)":"برترین هم‌خوانی‌های محصولی (لیفت)","Cross-Sell Retention Effect":"اثر فروش متقابل بر نگهداشت",
 "% of customers":"درصد مشتریان","Avg Monthly Revenue":"میانگین درآمد ماهانه",
 "Total Deposit Balance Trend":"روند مانده کل سپرده‌ها","Deposit-Related Product Penetration":"نفوذ محصولات مرتبط با سپرده",
 "Default Rate":"نرخ نکول","PD Model ROC-AUC (GBC)":"ROC-AUC مدل PD (GBC)","PD Model ROC-AUC (LogReg)":"ROC-AUC مدل PD (رگرسیون لجستیک)",
 "Outstanding Balance &amp; Expected Loss by Risk Bucket":"مانده و زیان مورد انتظار به تفکیک سطح ریسک",
 "Outstanding Balance by Loan Type":"مانده وام به تفکیک نوع وام","Outstanding Balance by Region":"مانده وام به تفکیک منطقه","Outstanding":"مانده",
 "Digital Adoption":"پذیرش دیجیتال","Avg Monthly Transactions":"میانگین تراکنش ماهانه","Churn Rate by Adoption Level":"نرخ ریزش به تفکیک سطح پذیرش",
 "CLV by Digital Adoption Level":"CLV به تفکیک سطح پذیرش دیجیتال","Note":"یادداشت",
 "Total Fraud Events":"کل رویدادهای تقلب","Total Loss":"کل زیان","Detection Rate":"نرخ تشخیص","False Positive Rate":"نرخ هشدار کاذب",
 "Fraud by Category":"تقلب به تفکیک دسته","Fraud Loss by Channel":"زیان تقلب به تفکیک کانال","Events":"رویدادها","Loss ($)":"زیان (دلار)",
 "Top 10 Branches by Profit (avg last 6 months)":"۱۰ شعبه برتر از نظر سود (میانگین ۶ ماه اخیر)",
 "Revenue vs. Profit — Branch Performance Matrix":"درآمد در برابر سود — ماتریس عملکرد شعب",
 "Customer Activity Index by Province (Iran)":"شاخص فعالیت مشتریان به تفکیک استان (ایران)","Branches":"شعب",
 "Revenue ($)":"درآمد (دلار)","Profit ($)":"سود (دلار)",
 "Total Marketing Budget":"کل بودجه بازاریابی","Total Conversions":"کل تبدیل‌ها","Avg Conversion Rate":"میانگین نرخ تبدیل",
 "Top Campaigns by ROI":"برترین کمپین‌ها از نظر ROI",
 "12-Month Forecast — Deposits":"پیش‌بینی ۱۲ ماهه — سپرده‌ها","12-Month Forecast — Revenue &amp; Profit":"پیش‌بینی ۱۲ ماهه — درآمد و سود",
 "Best Model Selected per Series (backtest MAPE)":"بهترین مدل انتخاب‌شده برای هر سری (MAPE بک‌تست)",
 "Deposits (actual)":"سپرده‌ها (واقعی)","Deposits (forecast)":"سپرده‌ها (پیش‌بینی)","Revenue (actual)":"درآمد (واقعی)",
 "Revenue (forecast)":"درآمد (پیش‌بینی)","Profit (actual)":"سود (واقعی)","Profit (forecast)":"سود (پیش‌بینی)",
 "12-Month Scenario Path — Profit":"مسیر سود در سناریوها — ۱۲ ماه آینده","Profit (Month 12)":"سود (ماه ۱۲)",
 "Cumulative 12M Profit":"سود تجمعی ۱۲ ماهه","Annualized ROA (M12)":"ROA سالانه‌شده (ماه ۱۲)",
 "Deposits (Month 12)":"سپرده‌ها (ماه ۱۲)","Loans (Month 12)":"وام‌ها (ماه ۱۲)","Credit Loss":"زیان اعتباری",
}
missing = []
for o, n in UI.items():
    if app.count('"%s"' % o) == 0:
        missing.append(o); continue
    app = app.replace('"%s"' % o, '"%s"' % n)
if missing:
    print("UI keys not found (check):", missing)

# wait for the embedded font before the first (canvas) render
app = rep(app, '''document.addEventListener("DOMContentLoaded", ()=>{
  renderNav();
  populateFilters();
  goToSection(currentSection);
});''', '''document.addEventListener("DOMContentLoaded", ()=>{
  renderNav();
  populateFilters();
  const ready = (document.fonts && document.fonts.load)
    ? Promise.all([document.fonts.load("400 12px Vazirmatn"), document.fonts.load("700 12px Vazirmatn")]).catch(()=>{})
    : Promise.resolve();
  ready.then(()=>goToSection(currentSection));
});''')

FA_PATH.parent.mkdir(parents=True, exist_ok=True)
FA_PATH.write_text(head + css + body + app, encoding="utf-8")
if t_en != EN_PATH.read_text(encoding="utf-8"):
    EN_PATH.write_text(t_en, encoding="utf-8")
    print("Updated  %s (language switch added)" % EN_PATH.relative_to(ROOT))
print("Wrote    %s (%d KB)" % (FA_PATH.relative_to(ROOT), FA_PATH.stat().st_size // 1024))
