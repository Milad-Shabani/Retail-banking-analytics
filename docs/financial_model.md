# Financial Model Methodology

All figures in `Financials`, `Balance_Sheet`, and `NII_NIM` (Excel) and the
Financial Performance / Executive Overview dashboard sections come from
`data/raw/financials.csv`, built in
`src/data_generation/generate_all.py` (section 21).

## P&L structure

```
Net Interest Income (NII)  = Loan Interest Income
                            + Customer Deposit Interest Income (proxy)
                            − Deposit Interest Expense
Total Revenue               = NII + Fee Income + Card Revenue + Other Operating Income
Total Operating Cost        = Personnel + Branch + Technology + Marketing + Operations + Other
Pre-Provision Profit        = Total Revenue − Total Operating Cost
Profit After Credit Costs   = Pre-Provision Profit − Credit Loss
```

Every line reconciles exactly (this is checked by `tests/test_financial_reconciliation.py`).

## Ratios

- **NIM** = NII (annualized) / (Deposits + Loans) — a simplified average-earning-assets proxy.
- **ROA** = Profit After Credit Costs (annualized) / (Deposits + Loans).
- **ROE** = Profit After Credit Costs (annualized) / Equity, where Equity ≈ 10% of the simplified asset base.
- **Cost-to-Income** = Total Operating Cost / Total Revenue.

## Known simplifications

- The loan book carries a blended yield (~8.2%) that is higher than a
  mature-market mortgage-heavy bank because this synthetic portfolio is
  weighted toward personal/consumer/credit-card lending (see
  `docs/assumptions.md`). This is what drives NIM/ROA/ROE somewhat higher
  than typical developed-market retail banks — a deliberate trade-off for a
  more "interesting" analytics story, disclosed here rather than hidden.
- Branch-level P&L (`monthly_branch_metrics.csv`) allocates loan interest
  income to branches by the branch's loan book share, and fee/deposit
  interest income by the branch's customer base — a simplification of true
  branch transfer-pricing / funds-transfer-pricing (FTP) methodology used by
  real banks.
- Equity, balance-sheet asset mix (cash/investments/other assets), and
  funding cost are all proxies, not a modeled balance sheet.
