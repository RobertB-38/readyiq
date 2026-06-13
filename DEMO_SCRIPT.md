# ReadyIQ — Demo Video Script (≤5 min, aim 3:30–4:30)

**Goal:** show that ReadyIQ *argues both sides* of a candidate's certification readiness, *decides* with cited evidence, *refuses to guess*, and hands the learner *live* official study content. Three certs = a pass, a fail, and a close call.

**Record with:** QuickTime (New Screen Recording) or Loom, microphone ON. Browser tab only — never show the terminal/.env.

**Before recording:** start the app, run AZ-204 once to warm it, reload to a clean page.

---

## Beat 1 — The problem (0:00–0:30)
*(Clean ReadyIQ landing page.)*

> "Most people decide whether they're ready for a certification exam off one practice score and a gut feeling. Enterprises do it for whole teams with even less. ReadyIQ replaces the guess: it puts a candidate's readiness on trial — two AI agents argue both sides, a judge decides, and every claim is cited to the real exam objectives. It even refuses to answer when the evidence isn't there."

## Beat 2 — A clear PASS (0:30–1:30)
*(Select **AZ-204** → "Put readiness on trial".)*

> "I pick AZ-204. An Advocate argues the candidate is ready, an Examiner argues what's missing — both grounded in the exam objectives and the candidate's practice record from Foundry IQ."

*(Scroll the two columns; click one citation open.)*

> "Every claim links to its source — here, the candidate's domain scores. The Advocate makes the strong case; the Examiner can only nitpick the weakest domain. Then they rebut each other — this is a real debate, not two summaries."

*(Scroll to verdict.)*

> "Verdict: **READY**. Cited, with confidence, and a next step."

## Beat 3 — A FAIL, honestly (1:30–2:45) — **the heart of the demo**
*(Select **AZ-400** → run.)*

> "Now a harder candidate. Watch the Advocate still fight *for* readiness — leading with their strong domains. But the Examiner lands the decisive blow: the build-and-release pipelines domain, 40–45% of the exam, sits at 54% — below the floor."

*(Scroll to verdict: NOT YET.)*

> "The Judge rules **NOT YET**, and explains exactly why. This is the point — ReadyIQ won't rubber-stamp a candidate just because most of their scores look fine. It reasons about *which* gap matters."

*(Scroll to the Learn modules.)*

> "And it doesn't stop at the verdict. It calls the **live Microsoft Learn MCP server** and pulls the *current, official* study guide for exactly the gap — see, 'skills measured as of April 2026.' Honest verdict, plus the real path to close it."

## Beat 4 — The close call + human gate (2:45–3:30)
*(Select **DP-203** → run, briefly.)*

> "And a borderline case — DP-203 comes back **ALMOST**: one domain a single point under threshold. ReadyIQ is calibrated, not binary."

*(Point to the manager-approval radio.)*

> "Finally — nothing acts automatically. The verdict is advisory until a human approves it. The agents have no authority on their own. That's the reliability story enterprises need."

## Beat 5 — Under the hood + vision (3:30–4:30)
*(Show the architecture diagram.)*

> "Under the hood: **Microsoft Foundry** hosts the model; **Foundry IQ** grounds every claim; the three agents are orchestrated in **LangGraph**; a verification gate and number guardrail drop anything uncited or invented; and the **Microsoft Learn MCP** brings in live content. Synthetic data only — no PII."

> "Where this goes: embedded in the Microsoft Learn portal, there's no login — the learner's real progress flows through **Work IQ and Microsoft Graph**, with consent, and they click one button: *Am I ready?* Same tribunal, their real data, their own portal. ReadyIQ — test before the test. Thanks for watching."

---

## Checklist before uploading
- [ ] Under 5:00 (aim 3:30–4:30)
- [ ] Your own voice + screen only
- [ ] Shows: a READY, a NOT_YET (with the live Learn links), a citation opened, the human gate
- [ ] Says "Microsoft Foundry", "Foundry IQ", and "Microsoft Learn MCP" out loud
- [ ] No terminal / .env / keys on screen
- [ ] Trim the first MCP call's few-second wait
- [ ] Upload to YouTube/Vimeo (Unlisted), copy the link
