# Buy or Wait — Enterprise AI Financial Engine

An AI-powered financial decision engine built for the **HackerRank Orchestrate September 2026 Hackathon**. The system analyzes a user's complete financial situation and recommends whether they should **pay now, pay partially, use installments, wait, or not proceed**.

---

## Overview

A user's current bank balance alone is **not enough** to determine affordability. This project combines structured financial data, semantic retrieval (RAG), forecasting, and rule-based financial planning to generate safe, explainable payment decisions.

### Features

* AI-powered affordability analysis
* Semantic retrieval from messages and financial history
* 90-day cash flow forecasting
* Multiple payment strategy recommendations
* Parallel processing for high throughput
* Explainable decision engine
* Generates HackerRank-compatible `output.csv`

---

## Architecture

```text
                    requests.csv
                          │
                          ▼
                State Builder Engine
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼
Financial Profiles   Financial Events     Messages + Images
      │                   │                   │
      └─────────────── Semantic RAG ─────────┘
                          │
                          ▼
                 Finance Planning Engine
      ┌──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
 CashFlow      Forecast       Affordability    Payment Planner
                          │
                          ▼
                Decision Verification
                          │
                          ▼
                    output.csv
```

---

## Dataset

Place the provided HackerRank dataset inside:

```text
dataset/
├── requests.csv
├── messages.csv
├── financial_profiles.csv
├── financial_events.csv
├── request_payment_options.csv
└── images/
```

> **Note:** `ground_truth.csv` is **not provided** by HackerRank. The project automatically skips accuracy evaluation when it is unavailable.

---

## Output Schema

The generated `output.csv` contains exactly these columns:

| Column                         | Description                                |
| ------------------------------ | ------------------------------------------ |
| request_id                     | Request identifier                         |
| amount_safe_to_pay             | Maximum safe amount payable today          |
| affordability_status           | Affordable / Plan / Later / Not affordable |
| recommended_payment_method     | Full, Partial, Installment, Wait           |
| payment_plan                   | Recommended payment schedule               |
| earliest_date_for_full_payment | Earliest safe payment date                 |
| spending_changes_needed        | Flexible expenses to reduce                |
| decision_explanation           | Human-readable justification               |

---

## Project Structure

```text
buy-or-wait/
│
├── code/
│   ├── engine/
│   ├── llm/
│   ├── rag/
│   ├── retrieval/
│   ├── models/
│   ├── evaluation/
│   ├── utils/
│   └── main.py
│
├── dataset/
│   ├── requests.csv
│   ├── messages.csv
│   ├── financial_profiles.csv
│   ├── financial_events.csv
│   ├── request_payment_options.csv
│   └── images/
│
└── output.csv
```

---

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Run the Project

```bash
python code/main.py
```

Successful execution produces:

```text
dataset/output.csv
```

Example summary:

```text
Requests          : 250
Execution Time    : 2.6 sec
Average Latency   : 16 ms
Throughput        : 128 req/s
Peak Memory       : 1.9 MB
```

---

## Financial Decision Logic

The engine considers:

* Current available balance
* Minimum balance to maintain
* Confirmed salary income
* Pending and recurring expenses
* Bills, rent, subscriptions and loans
* User payment preferences
* Relevant messages retrieved through semantic search

The recommendation is considered **safe** only if the user can:

1. Complete the payment plan.
2. Cover essential expenses.
3. Maintain the preferred minimum balance throughout the forecast period.

---

## Technologies Used

* **Python 3.12**
* **Polars** — High-performance dataframe processing
* **Pydantic v2** — Data validation
* **NumPy** — Vector similarity
* **ThreadPoolExecutor** — Parallel request processing
* **Semantic RAG** — Retrieval-augmented financial context

---

## Performance

| Metric      |         Value |
| ----------- | ------------: |
| Requests    |           250 |
| Avg Latency |     ~16–30 ms |
| P95 Latency |     ~70–90 ms |
| Throughput  | 120–145 req/s |
| Peak Memory |         ~2 MB |

---

## Submission Files

Upload the following to HackerRank:

1. `code.zip` *(zip only the `code/` directory)*
2. `output.csv`
3. `log.txt` *(chat transcript)*

---

## Author

**Arnave Dubey**

Built for the **HackerRank Orchestrate September 2026 AI Hackathon**.
