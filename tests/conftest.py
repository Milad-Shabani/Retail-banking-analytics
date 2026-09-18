import os
import json
import pandas as pd
import pytest

BASE = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(BASE, "data", "raw")
REPORTS = os.path.join(BASE, "outputs", "reports")
PROC = os.path.join(BASE, "data", "processed")


def _read(name):
    path = os.path.join(RAW, name)
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path = path + ".gz"
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def customers():
    return _read("customers.csv")


@pytest.fixture(scope="session")
def accounts():
    return _read("accounts.csv")


@pytest.fixture(scope="session")
def loans():
    return _read("loans.csv")


@pytest.fixture(scope="session")
def deposits():
    return _read("deposits.csv")


@pytest.fixture(scope="session")
def financials():
    return _read("financials.csv")


@pytest.fixture(scope="session")
def branches():
    return _read("branches.csv")


@pytest.fixture(scope="session")
def monthly_branch_metrics():
    return _read("monthly_branch_metrics.csv")


@pytest.fixture(scope="session")
def customer_products():
    return _read("customer_products.csv")


@pytest.fixture(scope="session")
def fraud_events():
    return _read("fraud_events.csv")


@pytest.fixture(scope="session")
def churn_results():
    with open(os.path.join(REPORTS, "churn_model_results.json")) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def credit_results():
    with open(os.path.join(REPORTS, "credit_risk_model_results.json")) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def forecast_results():
    with open(os.path.join(REPORTS, "forecast_results.json")) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def scenario_results():
    with open(os.path.join(REPORTS, "scenario_results.json")) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def optimization_results():
    with open(os.path.join(REPORTS, "optimization_results.json")) as f:
        return json.load(f)
