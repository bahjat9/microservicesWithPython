# Module 3 — Reflection

**Team name**: bahjat
**Branch**: `module-03/<bahjat>`
**Submitted**: before Module 4 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

All client requests now go through the gateway. No client ever calls a service directly.

**Why does that single entry point exist? What would the client's life look like without it?**

Think about what the client would need to know and manage if it talked to each service on its own port.

> Without the gateway, the client would need to know the port of every service, manage multiple base URLs, and handle failures for each one separately. If a service moves or changes port, every client breaks. The gateway is a single stable entry point — the client only ever needs to know port 8000.

---

## 2. Your choice

The activity-service makes two outbound calls: one to validate the user (with retry logic), one to fetch game data (with a null fallback if it fails).

**Why are these two calls treated differently? Why does one retry and the other just give up gracefully?**

What is the consequence for the user in each case if the downstream service is unavailable?

> User validation is critical — if the user doesn't exist, saving the activity makes no sense. The request must fail. Game enrichment is optional — the activity is valid without it. If game-service is down, the user still logged their activity successfully. Failing the whole request just because enrichment failed would be a bad user experience.

---

## 3. The tradeoff

Every time a client creates an activity, three services are involved synchronously. They all have to be running, healthy, and fast.

**What is the systemic risk of chaining synchronous calls like this?**

What happens to the user experience if the slowest service in the chain takes 3 seconds to respond?

> If any service in the chain is slow, the entire response is slow. A 3-second delay in user-service means the client waits 3 seconds minimum before getting anything back. With synchronous chaining, the slowest service sets the response time for everyone.

---

*Keep this file. You will refer back to it during the oral presentation.*
