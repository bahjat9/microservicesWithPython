# Module 5 — Reflection

**Team name**: bahjat
**Branch**: `module-05/<bahjat9>`
**Submitted**: before Module 6 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The game-service now has two models for the same data: SQLite for writes, Redis for reads. They store the same games in two different shapes.

**Why go through the trouble of maintaining two representations of the same data?**

Think about what kind of queries each model is optimised for, and what would happen if you tried to use the write model for high-traffic read operations.

> SQLite is accurate but slow under heavy read load. Redis is fast but can be slightly stale. By separating the read and write models, game-service can serve thousands of summary requests per second from Redis without touching the database, while writes still go to SQLite for accuracy.

---

## 2. Your choice

The logging-service checks GDPR consent before recording any activity. If a user has not opted in, the log is silently dropped.

**What does this consent check force you to accept about your data?** It is incomplete by design — some activities will never be recorded.

From a system design perspective: where is the right place to enforce this rule — in the logging-service, in the activity-service, or at the gateway? Why?

> The GDPR consent check belongs in logging-service because it is the only service that actually writes personal data to a log. Checking at the gateway would be too early — the gateway doesn't know what data each service will write. The consent check must sit as close as possible to the write operation itself.

---

## 3. The tradeoff

With CQRS, your write model and read model can drift out of sync — a game is updated in SQLite but the Redis projection still shows the old data.

**In what scenario does this inconsistency matter to the user? In what scenario is it completely acceptable?**

Is there a class of applications where eventual consistency is never acceptable? What are they?

> If a game's title is updated in SQLite but the Redis cache is not refreshed, the summary endpoint returns stale data. A user requesting the summary would see the old title. This inconsistency matters when accuracy is critical (e.g. displaying official game names), but is completely acceptable for non-critical reads like "recently popular games" where a few seconds of staleness has no real impact.

---

*Keep this file. You will refer back to it during the oral presentation.*
