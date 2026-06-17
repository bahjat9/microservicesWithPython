# Module 6 — Reflection

**Team name**: bahjat
**Branch**: `module-06/<bahjat9>`
**Submitted**: before Module 7 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The gateway now validates every JWT before forwarding a request. Individual services no longer need to check identity themselves.

**What does centralising authentication at the gateway buy you?** What would the alternative look like — if every service validated tokens on its own?

Think about what happens when you need to rotate the secret key, or add a new service to the system.

> JWTs are self-contained — the token itself carries all the claims signed with the SECRET_KEY. The gateway can verify the signature locally without calling auth-service because both share the same key. This is the core advantage of JWTs: stateless verification with no network call needed.

---

## 2. Your choice

When activity-service calls user-service internally, it uses a Machine-to-Machine (M2M) token — not a user's token.

**Why can't it just reuse the user's token that arrived in the original request?**

What would break, or what door would you accidentally leave open, if services passed user tokens between themselves?

> The gateway checks identity (who are you?) using the JWT. The service checks role (what are you allowed to do?) using the token's claims. These responsibilities are separate because identity is a cross-cutting concern for all services, while role enforcement is business logic specific to each service. A gamer should be able to read games but not delete them.

---

## 3. The tradeoff

The gateway and the auth-service share the same `SECRET_KEY` to verify tokens without making a network call on every request.

**What is the security risk of sharing this key?** What happens if it leaks?

And what would the alternative look like — verifying tokens by calling auth-service on every request instead? What does that cost you?

> /v1/auth/token must stay public because you need a token to call any protected endpoint — including the token endpoint itself. Requiring a token to get a token creates a chicken-and-egg problem. The login endpoint is the only entry point that bootstraps the entire auth flow.

---

*Keep this file. You will refer back to it during the oral presentation.*
