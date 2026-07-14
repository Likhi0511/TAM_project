# Order Supervisor Simulation

## Overview

This project is a simplified in-memory simulation of an AI-powered Order Supervisor for a D2C business. The supervisor monitors order events, decides when to wake up, takes actions using mock tools, maintains a compact memory summary, and stops when the order reaches a terminal state.

The implementation is intentionally lightweight and does not use Temporal, databases, cloud services, or a frontend. The goal is to demonstrate the workflow concepts that would map to a production-grade Temporal implementation.

---

## How to Run

### Prerequisites

- Python 3.14

### Files

```text
order_supervisor/
│
├── supervisor.py
├── events.json
└── README.md
```

### Run

```bash
python supervisor.py
```

---

## Sample Input (events.json)

```json
[
  {"event": "payment_confirmed"},
  {"event": "shipment_created"},
  {"event": "shipment_delayed"},
  {"event": "customer_message_received"},
  {"event": "no_update_for_n_hours"},
  {"event": "shipment_delayed"},
  {"event": "refund_requested"},
  {"event": "refund_resolved"}
]
```

---

## Sample Output

```text
Supervisor Started

Processing Event: payment_confirmed
Wake Policy: STAY_ASLEEP

Processing Event: shipment_created
Wake Policy: STAY_ASLEEP

Processing Event: shipment_delayed
Wake Policy: WAKE_NOW

Timer Wake-Up Triggered

Processing Event: customer_message_received
Wake Policy: WAKE_NOW

Processing Event: no_update_for_n_hours
Wake Policy: WAKE_NOW

Processing Event: shipment_delayed
Wake Policy: WAKE_NOW

Timer Wake-Up Triggered

Processing Event: refund_requested
Wake Policy: WAKE_NOW

Processing Event: refund_resolved
Wake Policy: STAY_ASLEEP

Terminal Event Detected: refund_resolved

==================================================
FINAL SUMMARY
==================================================

Status:
COMPLETED

Learnings:
- Shipment delays were detected and handled proactively.
- Escalation was required.
- Workflow reached a terminal state.
```

---

# Design Overview

The supervisor follows a simple workflow:

```text
Events
   ↓
Wake Policy
   ↓
WAKE_NOW?
   ↓
Decision Engine
   ↓
Mock Tools
   ↓
Activity Log
   ↓
Timeline + Memory Summary
   ↓
Terminal Event?
```

The supervisor continuously evaluates incoming events and determines whether action is required.

---

# Temporal Mapping

The assignment requested mapping each component to the equivalent Temporal building block.

| Simulation Component | Temporal Building Block | Description |
|---------------------|-------------------------|-------------|
| JSON Order Events | Signal | Incoming business events such as shipment delays, customer messages, and refund requests |
| Scheduled Wake-Up | Timer | Periodic wake-up that occurs even when no important event arrives |
| Mock Tool Calls | Activity | External work performed by the workflow |
| get_status() | Query | Read-only inspection of workflow state |
| Memory Compaction | Continue-As-New | Compresses old history into a summary while retaining recent context |
| Order Supervisor | Workflow | Long-running process that supervises the order |

---

## Signals

The following events act as workflow signals:

```text
payment_confirmed
payment_failed
shipment_created
shipment_delayed
customer_message_received
refund_requested
refund_resolved
manual_termination
```

Signals represent external events arriving into the workflow.

---

## Timer

The supervisor includes a scheduled wake-up mechanism.

Every few processed events, the workflow triggers a timer-based wake-up and evaluates:

```text
no_update_for_n_hours
```

In a production Temporal implementation this would be a durable Timer that wakes the workflow after a configured interval.

Purpose:

- Detect stalled orders
- Check shipment progress
- Trigger proactive follow-up

---

## Activities

Activities are represented by mock tools.

The tools do not perform real actions. They simply append records to an activity log.

Implemented activities:

```text
message_customer()
message_logistics_team()
create_internal_note()
escalate()
mark_for_review()
```

Example:

```text
MESSAGE_CUSTOMER
Investigate shipment delay
ESCALATE
```

In production these would call external systems such as:

- WhatsApp API
- CRM
- Ticketing platform
- Internal operations tools

---

## Query

The supervisor exposes a simple query function:

```python
get_status()
```

Example output:

```json
{
  "status": "ACTIVE",
  "delay_count": 1,
  "escalated": false
}
```

This allows external systems to inspect workflow state without modifying it.

In Temporal this maps directly to a Workflow Query.

---

## Continue-As-New

A long-running workflow should not accumulate unlimited history.

The supervisor maintains:

### Timeline

Recent events only.

Example:

```text
customer_message_received
shipment_delayed
refund_requested
```

### Memory Summary

Older events are compressed into a compact summary.

Example:

```text
Order payment confirmed.
Shipment created successfully.
Shipment delay detected and customer informed.
```

This simulates Temporal's Continue-As-New pattern, where historical detail is compacted while preserving important context.

---

# Wake Policy

The supervisor wakes immediately for important events.

### WAKE_NOW

```text
shipment_delayed
customer_message_received
refund_requested
no_update_for_n_hours
```

### STAY_ASLEEP

```text
payment_confirmed
shipment_created
```

The goal is to focus attention only on events requiring action.

---

# Decision Logic

The implementation currently uses rule-based logic.

### Shipment Delayed

Actions:

```text
message_customer
message_logistics_team
create_internal_note
```

Repeated delays:

```text
escalate
message_customer
```

### Customer Message

Actions:

```text
create_internal_note
message_customer
```

### Refund Request

Actions:

```text
create_internal_note
escalate
```

### No Update for N Hours

Actions:

```text
message_logistics_team
mark_for_review
```

---

# Where an LLM Would Improve Decisions

The current implementation uses deterministic rules.

A production AI supervisor would benefit from an LLM for more nuanced reasoning.

Potential improvements:

### Customer Sentiment Analysis

Instead of assuming every customer message is equal, the LLM can determine:

- Frustrated
- Neutral
- Happy
- Escalation risk

### Escalation Decisions

The LLM can decide:

- Is escalation necessary?
- Can the issue be resolved automatically?
- Should a human agent intervene?

### Customer Communication

The LLM can generate personalized customer-facing messages instead of using fixed responses.

### Risk Assessment

The LLM can determine:

- Order health
- Churn risk
- Customer dissatisfaction risk

---

# LLM Context

If an LLM were used, the following context would be provided:

```json
{
  "current_event": "shipment_delayed",
  "memory_summary": [
    "Payment confirmed",
    "Shipment created"
  ],
  "recent_timeline": [
    "shipment_delayed",
    "customer_message_received"
  ],
  "delay_count": 2,
  "escalated": false,
  "activity_log": [
    "Customer informed",
    "Logistics contacted"
  ]
}
```

Example prompt:

```text
You are an Order Supervisor AI.

Current Event:
shipment_delayed

Memory Summary:
Payment confirmed.
Shipment created.

Recent Timeline:
shipment_delayed
customer_message_received

Delay Count:
2

Previous Actions:
Customer informed.
Logistics contacted.

Should this order be escalated?
Explain your reasoning and recommend next actions.
```

---

# Bonus: Real LLM Integration

A future enhancement would replace the rule-based decision engine with an LLM-powered decision engine.

Example models:

- Claude (AWS Bedrock)
- GPT-4o
- Gemini
- Anthropic Sonnet

The workflow would still retain deterministic safeguards, while the LLM provides reasoning and recommendation generation.

---

# Terminal Conditions

The workflow ends when one of the following events occurs:

```text
delivered
refund_resolved
manual_termination
```

When a terminal event is reached, the supervisor prints a final summary containing:

- Order status
- Activity history
- Memory summary
- Recent timeline
- Key learnings

---

## Conclusion

This project demonstrates the core concepts of a long-running order supervision workflow:

- Signals
- Timers
- Activities
- Queries
- Continue-As-New
- Workflow termination

while remaining simple, fully local, and easy to run without any external dependencies.