# Module 4 — Reflection

**Team name**: bahjat
**Branch**: `module-04/<bahjat9>`
**Submitted**: before Module 5 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

In Module 3, services called each other directly over HTTP. Now activity-service drops a message into a broker and moves on — it never waits for a reply.

**What does the activity-service gain by not waiting? And what does the notification-service gain by consuming at its own pace?**

Think about what happens under load, or when notification-service is temporarily down.

> activity-service gains speed — it saves the activity and moves on instantly without waiting for notification-service to respond. notification-service gains resilience — if it's temporarily down, messages pile up in the queue and get processed when it comes back. Under load, neither service blocks the other.


---

## 2. Your choice

In Module 3 you already knew how to call another service directly over HTTP — you did it for user validation and game enrichment.

**Why not use the same approach for notifications? What does introducing a broker give you that a direct HTTP call doesn't?**

Think about what happens if notification-service is slow, or crashes mid-message.

> A direct HTTP call would mean activity-service waits for notification-service to respond. If notification-service is slow, the whole activity request slows down. If it crashes mid-call, the notification is lost. The broker decouples them — the message is safely stored in RabbitMQ even if notification-service is down, and it will be delivered when it recovers.


---

## 3. The tradeoff

With synchronous REST, you get an immediate answer: success or failure. With async messaging, the activity is saved and the message is sent — but you have no idea if the notification was ever delivered.

**How would a user know if their notification was never sent? How would you know as a developer?**

What visibility do you lose when you go async?

> A user would never know — there's no feedback in the activity response about whether the notification was delivered. As a developer, you'd have to check RabbitMQ logs or add separate monitoring. You lose the immediate success/failure signal you get with REST. If the message is consumed but something fails inside notification-service, you'd need dead letter queues or logging to even detect it.


---

*Keep this file. You will refer back to it during the oral presentation.*
