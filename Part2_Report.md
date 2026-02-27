# Part 2: Role-Governed Conversational Automation System — Report

## 1. Routing Logic (How the system determines the flow)

The routing engine follows a **Verified Lookup** strategy:
1.  **Identity Capture**: The system first requests a unique identifier (Phone Number).
2.  **Database Cross-Reference**: It queries the `classified_leads_output.csv` (the output from Part 1).
3.  **Hard-Binding**: Once the `Assigned_Role` is retrieved, the session is "hard-bound" to that specific `Bot class`. It does not use "if/else" logic per question; it instantiates a dedicated object that *only* knows how to be a Buyer, Partner, or Site Coordinator.

---

## 2. Knowledge Isolation Strategy

We implement **Triple-Layer Isolation**:
*   **Layer 1: Separate Prompt Templates**: Every agent has a unique "System Personality" that defines its boundaries. A Buyer bot is told it *is* a sales advisor and has no knowledge of partner commissions.
*   **Layer 2: Hard-Coded Knowledge Vaults**: Each bot is initialized with a local dictionary of data. The `BuyerBot` doesn't even have the `Commission` dictionary in its memory.
*   **Layer 3: Pre-Response Guardrails**: A global monitor (Policy Guard) scans the user's text for keywords *before* sending it to the LLM, ensuring the bot never even "hears" a query outside its permissions.

---

## 3. Preventing Cross-Role Data Leakage

Data leakage is prevented through **Intent-Slicing**:
*   If a **BUYER** asks about "payouts", the Policy Guard detects the word "payout" (which is in the Buyer's `BANNED_TOPICS` list).
*   The system immediately triggers a `REFUSAL_MESSAGE` and terminates the reasoning loop.
*   The query never reaches the Llama-3 engine, so the AI cannot hallucinate or accidentally reveal sensitive info from other roles.

---

## 4. Handling Incorrect Role Classification

In a real-world scenario, if a lead is misclassified as a "Buyer" when they are a "Partner":
1.  **Escalation Pathway**: The UI includes a "Report Role Mismatch" button.
2.  **Admin Override**: This triggers an alert in the `interaction_audit.json`.
3.  **Real-Time Update**: Admins update the Source CSV. Since our system re-reads the CSV on every session initialization, the user's role is corrected immediately upon their next login.

---

## 5. Audit and Compliance Monitoring

Compliance is ensured via the **Interaction Audit Log (`interaction_audit.json`)**:
*   **Traceability**: Every query and every bot response is recorded.
*   **Violation Tagging**: Interactions that trigger the Policy Guard are flagged with `violation_flag: True`.
*   **Real-Time Stream**: The dashboard features a "Compliance Stream" showing admins exactly when and where access was denied, allowing for constant monitoring of attempted data breaches.

---

## Summary of Role Boundaries

| Role | Allowed Topics | Restricted Topics |
| :--- | :--- | :--- |
| **BUYER** | Pricing, EMI, Booking, Availability | Commissions, Payouts, Partner Terms |
| **PARTNER** | Commissions, Terms, Lead Policy | Buyer Pricing, End-user Discounts |
| **SITE_VISIT** | Location, Scheduling, Contact | Financials, Commissions, Booking |
| **ENQUIRY** | Project Overview, Developer Legacy, Features | Pricing, Commissions, Personal Data |
