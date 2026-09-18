# Data Dictionary

Auto-generated from the tables in `data/raw/`. Each table lists its columns; see inline comments in `src/data_generation/generate_all.py` for generation logic.

## `accounts.csv`

| Column | Example | Dtype |
|---|---|---|
| account_id | ACC0000001 | str |
| customer_id | CUST000001 | str |
| product_id | PRD01 | str |
| account_type | Checking Account | str |
| open_date | 2019-12-27 | str |
| status | Open | str |

## `branches.csv`

| Column | Example | Dtype |
|---|---|---|
| branch_id | BR001 | str |
| branch_name | Branch 001 | str |
| region | Region-02 | str |
| city | Region-02-City-2 | str |
| branch_type | Standard | str |
| open_date | 2019-02-13 | str |
| employee_count | 25 | int64 |

## `campaign_responses.csv`

| Column | Example | Dtype |
|---|---|---|
| response_id | RESP000001 | str |
| campaign_id | CMP017 | str |
| customer_id | CUST016236 | str |
| response_date | 2023-04-04 | str |
| responded_flag | True | bool |
| converted_flag | False | bool |
| revenue_generated | 0.0 | float64 |

## `campaigns.csv`

| Column | Example | Dtype |
|---|---|---|
| campaign_id | CMP001 | str |
| campaign_name | Campaign 001 - Digital Onboarding | str |
| start_date | 2024-04-22 | str |
| channel_id | CH07 | str |
| target_product_id | PRD05 | str |
| budget | 28300.0 | float64 |
| impressions | 387553 | int64 |
| reach | 271287 | int64 |

## `cards.csv`

| Column | Example | Dtype |
|---|---|---|
| card_id | CARD000001 | str |
| customer_id | CUST000004 | str |
| product_id | PRD04 | str |
| card_type | Debit Card | str |
| issue_date | 2021-05-02 | str |
| credit_limit | 0.0 | float64 |
| credit_utilization | nan | float64 |
| monthly_spend | 176.63 | float64 |
| avg_transaction_value | 41.11 | float64 |
| is_active | False | bool |
| digital_wallet_enabled | True | bool |
| late_payment_flag | False | bool |

## `channels.csv`

| Column | Example | Dtype |
|---|---|---|
| channel_id | CH01 | str |
| channel_name | Branch Walk-in | str |
| channel_type | Physical | str |
| avg_acquisition_cost | 69.15 | float64 |

## `credit_events.csv`

| Column | Example | Dtype |
|---|---|---|
| credit_event_id | CE00001 | str |
| loan_id | LN000005 | str |
| customer_id | CUST000002 | str |
| event_date | 2024-11-25 | str |
| event_type | Delinquency Notice - 30 Days | str |
| outstanding_at_event | 1616.25 | float64 |
| risk_bucket | Elevated | str |

## `customer_interactions.csv`

| Column | Example | Dtype |
|---|---|---|
| interaction_id | INT000001 | str |
| customer_id | CUST011847 | str |
| interaction_date | 2024-05-19 | str |
| interaction_type | Support Call | str |
| channel | Email | str |
| resolution_time_hours | 20.8 | float64 |
| satisfaction_score | 4.5 | float64 |
| repeat_contact_flag | False | bool |

## `customer_products.csv`

| Column | Example | Dtype |
|---|---|---|
| customer_id | CUST000001 | str |
| product_id | PRD11 | str |
| adoption_date | 2024-03-12 | str |
| product_name | Overdraft Facility | str |
| product_category | Credit | str |

## `customers.csv`

| Column | Example | Dtype |
|---|---|---|
| customer_id | CUST000001 | str |
| signup_date | 2016-03-22 | str |
| birth_year | 1987 | int64 |
| age | 39 | int64 |
| age_band | 36-45 | str |
| gender | Male | str |
| region | Region-10 | str |
| city | Region-10-City-2 | str |
| branch_id | BR016 | str |
| employment_status | Employed | str |
| occupation_group | Other | str |
| income_band | <15K | str |
| annual_income | 5600.0 | float64 |
| education_level | High School | str |
| marital_status | Married | str |
| customer_type | Individual | str |
| acquisition_channel | CH06 | str |
| acquisition_campaign_flag | False | bool |
| relationship_start_date | 2016-03-22 | str |
| tenure_years | 8.78 | float64 |
| digital_adoption | High | str |
| mobile_banking_user | True | bool |
| internet_banking_user | True | bool |
| premium_customer_flag | False | bool |
| salary_customer_flag | True | bool |
| customer_status | Active | str |
| churn_flag | False | bool |
| risk_segment | Low | str |
| recency_months | 0 | int64 |
| frequency_avg_monthly_txns | 0.79 | float64 |
| monetary_avg_balance | 667.29 | float64 |
| r_score | 3 | int64 |
| f_score | 3 | int64 |
| m_score | 3 | int64 |
| rfm_score | 333 | int64 |
| rfm_segment | Potential Loyalist | str |
| customer_value_score | 60.0 | float64 |
| value_segment | Affluent | str |
| lifecycle_segment | Established | str |
| behavioral_segment | Digital First | str |
| digital_segment | High | str |
| customer_lifetime_value | 75.91 | float64 |
| products_owned_count | 6 | int64 |
| multi_product_flag | True | bool |

## `deposits.csv`

| Column | Example | Dtype |
|---|---|---|
| deposit_id | DEP000001 | str |
| customer_id | CUST000003 | str |
| open_date | 2023-07-29 | str |
| principal_amount | 34911.68 | float64 |
| term_months | 12 | int64 |
| interest_rate | 0.0689 | float64 |
| auto_renew | False | bool |
| status | Active | str |

## `employees.csv`

| Column | Example | Dtype |
|---|---|---|
| employee_id | EMP00001 | str |
| branch_id | BR001 | str |
| role | Teller | str |
| hire_date | 2023-04-22 | str |
| performance_score | 83.3 | float64 |

## `financials.csv`

| Column | Example | Dtype |
|---|---|---|
| month | 2023-01 | str |
| total_balance | 23370842.2819484 | float64 |
| total_fee_income | 8440.76 | float64 |
| total_interest_income_deposits | 194756.81 | float64 |
| active_customers | 20000 | int64 |
| total_transactions | 22566 | int64 |
| loan_interest_income | 405231.3 | float64 |
| deposit_interest_expense | 38951.4 | float64 |
| net_interest_income | 561036.71 | float64 |
| fee_income | 8440.76 | float64 |
| card_revenue | 30735.95 | float64 |
| other_operating_income | 22441.47 | float64 |
| total_revenue | 622654.89 | float64 |
| credit_loss | 52053.37 | float64 |
| personnel_cost | 348886.18 | float64 |
| branch_cost | 104445.08 | float64 |
| technology_cost | 31132.74 | float64 |
| marketing_cost | 53367.18 | float64 |
| operations_cost | 37359.29 | float64 |
| other_operating_costs | 12453.1 | float64 |
| total_operating_cost | 587643.57 | float64 |
| pre_provision_profit | 35011.32 | float64 |
| operating_profit | 35011.32 | float64 |
| profit_after_credit_costs | -17042.05 | float64 |
| profit_margin | -0.0274 | float64 |
| return_on_assets | -0.002 | float64 |
| return_on_equity | -0.02 | float64 |
| cost_to_income_ratio | 0.9438 | float64 |
| net_interest_margin | 0.0657 | float64 |

## `forecast_inputs.csv`

| Column | Example | Dtype |
|---|---|---|
| month | 2023-01 | str |
| total_balance | 23370842.2819484 | float64 |
| total_revenue | 622654.89 | float64 |
| net_interest_income | 561036.71 | float64 |
| fee_income | 8440.76 | float64 |
| total_operating_cost | 587643.57 | float64 |
| credit_loss | 52053.37 | float64 |
| profit_after_credit_costs | -17042.05 | float64 |
| active_customers | 20000 | int64 |
| outstanding_loans_proxy | 59302141.605 | float64 |

## `fraud_events.csv`

| Column | Example | Dtype |
|---|---|---|
| fraud_id | FRD00001 | str |
| customer_id | CUST009757 | str |
| event_date | 2024-07-09 | str |
| fraud_category | Unusual Transaction Pattern | str |
| channel | Mobile App | str |
| amount_at_risk | 329.09 | float64 |
| loss_amount | 912.82 | float64 |
| detected_flag | False | bool |
| false_positive_flag | True | bool |
| region | Region-02 | str |

## `loan_payments.csv`

| Column | Example | Dtype |
|---|---|---|
| loan_id | LN003965 | str |
| customer_id | CUST005026 | str |
| payment_number | 1 | int64 |
| payment_amount | 97.41 | float64 |
| payment_status | On-Time | str |

## `loans.csv`

| Column | Example | Dtype |
|---|---|---|
| loan_id | LN000001 | str |
| customer_id | CUST000001 | str |
| product_id | PRD11 | str |
| loan_type | Overdraft Facility | str |
| origination_date | 2024-03-12 | str |
| term_months | 12 | int64 |
| interest_rate | 0.2 | float64 |
| loan_amount | 3371.09 | float64 |
| outstanding_balance | 1576.55 | float64 |
| probability_of_default | 0.004 | float64 |
| exposure_at_default | 3090.79 | float64 |
| loss_given_default | 0.503 | float64 |
| dpd_bucket | Current | str |
| default_flag | False | bool |
| risk_bucket | Low | str |
| branch_id | BR016 | str |
| region | Region-10 | str |
| acquisition_channel | CH06 | str |
| expected_credit_loss | 6.22 | float64 |

## `monthly_account_metrics.csv`

| Column | Example | Dtype |
|---|---|---|
| account_id | ACC0000001 | str |
| customer_id | CUST000001 | str |
| month | 2023-01 | str |
| month_end_date | 2023-01-31 | str |
| balance | 547.32 | float64 |
| transaction_count | 3 | int64 |
| is_active | True | bool |
| avg_daily_balance | 549.86 | float64 |

## `monthly_branch_metrics.csv`

| Column | Example | Dtype |
|---|---|---|
| branch_id | BR001 | str |
| month | 2023-01 | str |
| active_customers | 743 | int64 |
| total_balance | 818217.2862245587 | float64 |
| total_transactions | 793 | int64 |
| fee_income | 287.03000000000003 | float64 |
| interest_income | 6818.33 | float64 |
| employee_count | 25 | int64 |
| loan_interest_income | 13228.47 | float64 |
| revenue | 20333.83 | float64 |
| operating_cost | 21999.62 | float64 |
| profit | -1665.79 | float64 |
| revenue_per_employee | 813.35 | float64 |

## `monthly_customer_metrics.csv`

| Column | Example | Dtype |
|---|---|---|
| customer_id | CUST000001 | str |
| month | 2023-01 | str |
| month_end_date | 2023-01-31 | str |
| balance | 547.3172526984551 | float64 |
| transaction_count | 3 | int64 |
| is_active | True | bool |
| fee_income | 0.54 | float64 |
| interest_income | 4.56 | float64 |

## `monthly_product_metrics.csv`

| Column | Example | Dtype |
|---|---|---|
| product_id | PRD01 | str |
| month | 2023-01 | str |
| active_customers | 9257 | int64 |
| new_customers | 271 | int64 |
| product_name | Checking Account | str |
| fee_rate | 0.0 | float64 |
| interest_rate | 0.001 | float64 |
| monthly_fee | 3.0 | float64 |
| revenue | 27790.29 | float64 |

## `products.csv`

| Column | Example | Dtype |
|---|---|---|
| product_id | PRD01 | str |
| product_name | Checking Account | str |
| product_category | Transaction | str |
| interest_rate | 0.001 | float64 |
| fee_rate | 0.0 | float64 |
| monthly_fee | 3.0 | float64 |
| acquisition_cost | 8 | int64 |
| operating_cost | 6 | int64 |
| risk_level | Low | str |

## `scenario_assumptions.csv`

| Column | Example | Dtype |
|---|---|---|
| scenario | Base Case | str |
| deposit_growth_monthly | 0.006 | float64 |
| loan_growth_monthly | 0.008 | float64 |
| interest_rate_delta | 0.0 | float64 |
| credit_loss_multiplier | 1.0 | float64 |
| fee_income_growth_monthly | 0.004 | float64 |
| customer_acquisition_growth_monthly | 0.01 | float64 |
| churn_rate_monthly | 0.01 | float64 |
| operating_cost_growth_monthly | 0.004 | float64 |
| digital_adoption_growth_monthly | 0.004 | float64 |
| marketing_spend_multiplier | 1.0 | float64 |

## `transactions.csv.gz`

| Column | Example | Dtype |
|---|---|---|
| transaction_id | TXN00000001 | str |
| customer_id | CUST000001 | str |
| transaction_datetime | 2023-01-03 05:38:52 | str |
| transaction_type | ATM Deposit | str |
| amount | 263.41 | float64 |
| currency | USD | str |
| channel | Branch | str |
| merchant_category | E-commerce | str |
| branch_id | BR016 | str |
| city | Region-10-City-2 | str |
| device_type | POS Terminal | str |
| is_digital | False | bool |
| is_international | False | bool |
| is_recurring | False | bool |
| is_suspicious | False | bool |
