# ReadyIQ — *Test before the test*

An enterprise learning agent that puts a candidate's **certification readiness on trial**. An **Advocate** argues the candidate is ready, an **Examiner** argues what's missing, and a **Judge** delivers a readiness verdict — every claim cited to the real exam objectives or the candidate's practice record, and the system **refuses to guess** when the evidence isn't there.

Built for the **Microsoft Agents League @ AI Skills Fest 2026 — Reasoning Agents track, Challenge A (Enterprise Learning System)** on **Microsoft Foundry**.

> ⚠️ **Synthetic data only.** All candidate records and exam-objective documents in this repo are fabricated for demonstration. No real learner data, employee data, or PII is used. See `synthetic_data/`.

## Why it's different

Most certification-readiness agents are *linear* — curate, plan, quiz. ReadyIQ is **adversarial**: two agents argue opposing sides of "is this learner ready?", a Judge weighs the debate, and a verification gate drops any claim not grounded in approved sources. That adversarial cross-examination is a stronger reliability story than passive citation, and it's the part of the system you can *watch* refuse to make things up.

## What it does

Pick a certification (e.g. **AZ-204**). Three agents reason over the exam objectives and the candidate's synthetic practice record, retrieved from **Foundry IQ**:

- **🟢 Advocate** — builds the case that the candidate is **ready**, citing covered objectives and strong domain scores.
- **🔴 Examiner** — builds the case that they're **not yet ready**, citing weak domains, gaps, and objectives below the readiness floor.
- **⚖️ Judge** — weighs both (after a rebuttal round) and returns **READY / ALMOST / NOT_YET**, a confidence score, the deciding evidence, and one concrete next step.

A **verification gate** rejects any claim not backed by a retrieved passage; a **number guardrail** rejects invented scores; a **human-in-the-loop gate** means no verdict acts until a manager approves it. Every step is logged in a reasoning trace.

## How it maps to Challenge A

| Challenge A requirement | ReadyIQ |
|---|---|
| Multi-agent system aligned to the enterprise-learning scenario | Advocate / Examiner / Judge readiness tribunal + grounded content + study-plan next step |
| Microsoft IQ integration | **Foundry IQ** knowledge base over exam objectives + candidate records |
| Reasoning & multi-step thinking | Opening cases → rebuttal round → adjudicated verdict |
| Grounded, cited assessment | Every claim cites a passage id; gate drops uncited claims |
| Reliability & human oversight | Verification gate, number guardrail, manager approval gate, audit trace |
| Synthetic data only | All data in `synthetic_data/` is fabricated and labelled |

## Stack

LangGraph (orchestration) · **Microsoft Foundry — GPT-4o-mini + Foundry IQ** (models + grounded retrieval) · FastAPI · Streamlit · verification gate + guardrails · Python 3.10+.

## Project layout

```
app/
  agents/         Advocate, Examiner, Judge
  orchestration/  LangGraph debate graph + shared state
  rag/            Foundry IQ retriever (+ Chroma / fixture fallbacks)
  trace/          reasoning trace + verification gate
  api/            FastAPI (/health, /v1/analyze)
ui/               Streamlit demo
synthetic_data/   fabricated exam objectives + candidate records (AZ-204, AZ-400, DP-203)
tests/            pytest (run offline, no keys)
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in Azure Foundry + Search keys
pytest                        # 18 tests pass offline
streamlit run ui/app.py       # the demo
```

## Future work

Connect the **Microsoft Learn MCP server** so ReadyIQ grounds in live, official certification content and coaches any learner toward exam-day readiness — the synthetic objective docs here are stand-ins for that real knowledge source.

## Author

Robert Borkar — [RobertB-38](https://github.com/RobertB-38) · MSc Computing (Data Analytics), Dublin City University.
