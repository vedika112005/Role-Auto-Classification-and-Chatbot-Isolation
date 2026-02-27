# Part 1: Role Auto Classification — Report

---

## What Was Asked

We are given a dataset of 1000 leads. Each lead has a **Name**, a **Phone Number**, and a **Source_Number** field that tells us where the lead came from (like Buyer, Channel Partner, Site Visit, or Enquiry).

Our job is to build an automated logic that reads the Source_Number and assigns each lead a proper **Role** tag — without doing it manually for each row.

The mapping rules given in the assignment are:

| Source_Number  | Assigned Role     |
|----------------|-------------------|
| Buyer_Line     | BUYER             |
| Partner_Line   | CHANNEL_PARTNER   |
| Visit_Line     | SITE_VISIT        |
| Any other      | UNKNOWN           |

When I opened the actual CSV file (`leads_1000.csv`), I noticed the data uses slightly different labels — "Buyer", "Channel Partner", "Site Visit", and "Enquiry" — instead of "Buyer_Line" or "Partner_Line". This is pretty normal in real projects; the spec and the actual data don't always match word-for-word. So my solution accounts for both formats.

---

## 1. Formula Used

### Approach A — Direct formula using IFS

If the Source_Number is in column C (starting from row 2), I'd put this in column D:

```
=IFS(
    ISBLANK(C2),                          "UNKNOWN",
    LOWER(TRIM(C2))="buyer",              "BUYER",
    LOWER(TRIM(C2))="buyer_line",         "BUYER",
    LOWER(TRIM(C2))="channel partner",    "CHANNEL_PARTNER",
    LOWER(TRIM(C2))="partner_line",       "CHANNEL_PARTNER",
    LOWER(TRIM(C2))="site visit",         "SITE_VISIT",
    LOWER(TRIM(C2))="visit_line",         "SITE_VISIT",
    LOWER(TRIM(C2))="enquiry",            "ENQUIRY",
    LOWER(TRIM(C2))="enquiry_line",       "ENQUIRY",
    TRUE,                                 "UNKNOWN"
)
```

### Approach B — Lookup table using VLOOKUP (recommended)

**Step 1:** Create a small reference table on a separate sheet named "RoleConfig":

| Column A (Source)  | Column B (Role)   |
|--------------------|--------------------|
| buyer              | BUYER              |
| buyer_line         | BUYER              |
| channel partner    | CHANNEL_PARTNER    |
| partner_line       | CHANNEL_PARTNER    |
| site visit         | SITE_VISIT         |
| visit_line         | SITE_VISIT         |
| enquiry            | ENQUIRY            |
| enquiry_line       | ENQUIRY            |

**Step 2:** In the main sheet, use this formula in D2:

```
=IFERROR(
    VLOOKUP(LOWER(TRIM(C2)), RoleConfig!A:B, 2, FALSE),
    "UNKNOWN"
)
```

---

## 2. How the Formula Works

Let me walk through what happens when the formula runs on a single cell — say C2 contains " Channel Partner ".

**Step by step:**

1. **TRIM(C2)** removes the extra spaces from both sides, giving us "Channel Partner".

2. **LOWER(...)** converts it to all lowercase: "channel partner". This is important because someone might type "BUYER" or "buyer" or "Buyer" — by converting everything to lowercase first, we treat all of them the same way.

3. **In Approach A (IFS):** The formula checks each condition one by one, top to bottom. When it hits `LOWER(TRIM(C2))="channel partner"`, that's a match, so it returns "CHANNEL_PARTNER" and stops checking.

4. **In Approach B (VLOOKUP):** The cleaned value "channel partner" is looked up in the RoleConfig table. It finds a match in the table and returns the corresponding role from column B, which is "CHANNEL_PARTNER".

5. **If nothing matches** (in IFS, the `TRUE` at the end catches it; in VLOOKUP, the `IFERROR` wrapper catches the lookup failure), the formula returns "UNKNOWN".

The core idea is simple: **clean the input first, then look it up in a predefined list of rules.** It's the same concept whether you use a spreadsheet formula or write it in code.

---

## 3. Example Input and Output Table

Here's a table showing how different Source_Number values get classified. I've included normal cases plus a few edge cases to show that the logic handles messy data too.

| Lead_ID   | Name               | Phone      | Source_Number     | Assigned Role     |
|-----------|--------------------|------------|-------------------|-------------------|
| LEAD-0001 | Hari Subramanian   | 6682751893 | Enquiry           | ENQUIRY           |
| LEAD-0002 | Siddharth Tripathi | 7564209312 | Buyer             | BUYER             |
| LEAD-0003 | Anand Pillai       | 6941460145 | Site Visit        | SITE_VISIT        |
| LEAD-0004 | Anika Verma        | 7265774428 | Buyer             | BUYER             |
| LEAD-0005 | Rahul Kulkarni     | 9064578569 | Enquiry           | ENQUIRY           |
| LEAD-0006 | Diya Shetty        | 8960094575 | Buyer             | BUYER             |
| LEAD-0007 | Krishna Roy        | 8234300072 | Enquiry           | ENQUIRY           |
| LEAD-0008 | Tanvi Reddy        | 9105578047 | Channel Partner   | CHANNEL_PARTNER   |
| LEAD-0009 | Shreya Iyer        | 7711435375 | Buyer             | BUYER             |
| LEAD-0010 | Vikram Iyer        | 6193180901 | Site Visit        | SITE_VISIT        |

**Edge case examples:**

| Input Source_Number | Assigned Role   | Why                                          |
|---------------------|-----------------|----------------------------------------------|
| Buyer_Line          | BUYER           | Matches the assignment spec format           |
| Partner_Line        | CHANNEL_PARTNER | Matches the assignment spec format           |
| Visit_Line          | SITE_VISIT      | Matches the assignment spec format           |
| "  BUYER  "         | BUYER           | TRIM + LOWER handles spaces and case         |
| *(empty cell)*      | UNKNOWN         | No value provided, falls to default          |
| SomeRandomText      | UNKNOWN         | Doesn't match any known rule, safe fallback  |

---

## 4. Scalability Approach

**Question asked:** How can this logic scale if the system grows to 10 or more roles?

Right now we have 4 roles. But the system is designed so that adding more roles is straightforward, regardless of how many we end up with.

**If using the spreadsheet approach (VLOOKUP):**

This is where Approach B really shines. To add a new role — say "INVESTOR" — I just add one row to the RoleConfig sheet:

| investor | INVESTOR |

That's it. The VLOOKUP formula in the main sheet doesn't change at all. I could add 5 new roles or 50 new roles just by adding rows to that reference table. No formulas need to be edited.

Compare this to Approach A (IFS), where I'd have to add two more lines to an already long formula each time. With 20+ roles, that formula would become unreadable. That's why Approach B is the better choice for scalability.

**If using Python code:**

In the Python script I wrote (`part1_role_classification.py`), the mapping rules are stored in a dictionary:

```python
role_rules = {
    "buyer"           : "BUYER",
    "channel partner" : "CHANNEL_PARTNER",
    "site visit"      : "SITE_VISIT",
    "enquiry"         : "ENQUIRY",
}
```

Adding a new role is one line:

```python
role_rules["investor"] = "INVESTOR"
```

The classification function (`classify_lead`) uses a dictionary lookup, so no matter how many roles we add, it still runs in the same amount of time — it doesn't get slower with more roles.

For a larger production system, these rules could be stored in an external JSON file or a database, so non-technical team members can manage role mappings without touching any code.

---

## 5. Error Handling

**Question asked:** How would you handle incorrect Source_Number, missing Source_Number, and new roles introduced in the future?

### A. Incorrect Source_Number (e.g., a typo like "Byuer")

The first line of defense is the cleaning step — `TRIM` and `LOWER` in the formula, or `strip()` and `lower()` in Python. This handles the most common data entry mistakes like extra spaces or inconsistent capitalization.

If the value is genuinely wrong (a real typo that doesn't match any rule), it gets assigned "UNKNOWN" — which is a safe default. It means "we couldn't classify this lead, someone should take a look." The system doesn't guess or assume, it just flags it.

In the Python script, I keep a count of how many leads ended up as "unrecognized." If that number is unexpectedly high, it's a signal that something is off with the incoming data.

### B. Missing Source_Number (empty cell)

In the formula, `ISBLANK(C2)` catches this right at the top and assigns "UNKNOWN."

In the Python script, the `clean_source_value()` function returns `None` for empty strings, and the classifier knows to treat `None` as a missing value.

Either way, the lead isn't lost — it's just parked in the UNKNOWN category until someone can fill in the correct source.

### C. New roles introduced in the future

This is the easiest case to handle because of how the logic is structured:

1. Add the new source-to-role mapping (one row in the spreadsheet table, or one line in the Python dictionary)
2. Re-run the classification on any leads that were previously marked UNKNOWN
3. Those leads will now get matched to the new role

The "UNKNOWN" category works like a safe holding area. Leads sit there temporarily until we have a rule for them. Once the rule is added, they get classified automatically on the next run.

---

## Summary

| Deliverable                  | Status    |
|------------------------------|-----------|
| Formula used                 | Provided (IFS and VLOOKUP approaches) |
| Explanation of logic         | Step-by-step walkthrough included |
| Example input/output table   | 10-row sample + edge cases shown |
| Scalability approach         | Dictionary/lookup table design — adding roles = adding one line |
| Error handling strategy      | Covers incorrect, missing, and new roles |
| Python implementation        | Script provided as `part1_role_classification.py` |
| Classified output            | Full 1000-lead output saved as `classified_leads_output.csv` |
