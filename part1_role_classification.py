
# ============================================================
#  PART 1 — Role Auto Classification
#  Internship Assignment: Role-Based Automation
# ============================================================
#
#  What this script does (in plain English):
#  -----------------------------------------
#  We have a CSV file with 1000 leads. Each lead has a Name,
#  Phone Number, and a "source type" (like Buyer, Channel Partner,
#  Site Visit, or Enquiry).
#
#  Our job is to read that file, look at the source type of each
#  lead, and assign them a proper ROLE tag. Then we save the
#  result into a new CSV so the data is clean and ready to use.
#
#  Think of it like sorting mail into labeled boxes.
# ============================================================

import csv
import os

# --------------------------------------------------
# STEP 1: Define the role mapping rules
# --------------------------------------------------
#
# The assignment says:
#   Buyer_Line     -> BUYER
#   Partner_Line   -> CHANNEL_PARTNER
#   Visit_Line     -> SITE_VISIT
#   Anything else  -> UNKNOWN
#
# But when I opened the actual CSV file (leads_1000.csv),
# I noticed the column values are slightly different.
# The CSV uses: "Buyer", "Channel Partner", "Site Visit", "Enquiry"
# instead of "Buyer_Line", "Partner_Line", etc.
#
# So I need to handle BOTH formats — the ones given in the
# assignment spec AND the ones that actually appear in the data.
# This is a real-world situation: specs and actual data often
# don't match exactly, so we plan for both.
#
# I'm using a dictionary for this because:
#   - Looking up a value in a dict is O(1) on average
#   - It's way cleaner than writing a long if-elif-else chain
#   - If we need to add more roles later, we just add one line
#     to this dict — we don't touch the rest of the code at all

role_rules = {
    # --- Mappings from the assignment spec ---
    "buyer_line"      : "BUYER",
    "partner_line"    : "CHANNEL_PARTNER",
    "visit_line"      : "SITE_VISIT",
    "enquiry_line"    : "ENQUIRY",

    # --- Mappings that match the actual CSV data ---
    "buyer"           : "BUYER",
    "channel partner" : "CHANNEL_PARTNER",
    "site visit"      : "SITE_VISIT",
    "enquiry"         : "ENQUIRY",
}

# What do we assign if the source type doesn't match anything above?
FALLBACK_ROLE = "UNKNOWN"


# --------------------------------------------------
# STEP 2: Write a function to clean up source values
# --------------------------------------------------
#
# Why do we need this?
# Because real data is messy. Someone might type " Buyer " with
# extra spaces, or "BUYER" in all caps, or " channel  partner "
# with double spaces. If we don't clean it up first, our lookup
# in the role_rules dict will fail even though the value is
# basically correct.
#
# This function does 3 things:
#   1. Strips whitespace from both ends     " Buyer " -> "Buyer"
#   2. Converts to lowercase                "BUYER"   -> "buyer"
#   3. Collapses double spaces to single    "site  visit" -> "site visit"

def clean_source_value(raw_value):
    """
    Takes a raw string from the CSV and cleans it up so we can
    do a reliable lookup in our role_rules dictionary.

    Returns None if the value is empty or missing entirely.
    """
    if raw_value is None:
        return None

    # strip() removes leading and trailing spaces/tabs/newlines
    cleaned = raw_value.strip()

    # if after stripping there's nothing left, treat it as missing
    if cleaned == "":
        return None

    # lowercase so "BUYER", "Buyer", "buyer" all become "buyer"
    cleaned = cleaned.lower()

    # handle double spaces — keep replacing until there are none
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    return cleaned


# --------------------------------------------------
# STEP 3: Write the classification function
# --------------------------------------------------
#
# This is the core logic. Given a raw source value, it:
#   1. Cleans it up using our function above
#   2. Looks it up in the role_rules dictionary
#   3. Returns the matched role, or UNKNOWN if no match

def classify_lead(raw_source):
    """
    Classifies a single lead based on its source value.

    Returns a tuple: (assigned_role, status)
    - status is "matched" if we found it in our rules
    - status is "missing" if the source was empty/null
    - status is "unrecognized" if it didn't match any rule
    """
    cleaned = clean_source_value(raw_source)

    # Case 1: The source field was empty or had only whitespace
    if cleaned is None:
        return (FALLBACK_ROLE, "missing")

    # Case 2: We found a matching rule — great, assign the role
    if cleaned in role_rules:
        return (role_rules[cleaned], "matched")

    # Case 3: The value exists but we don't recognize it
    # This could happen if someone enters a typo or a new
    # source type that hasn't been added to our rules yet
    return (FALLBACK_ROLE, "unrecognized")


# --------------------------------------------------
# STEP 4: Read the CSV, classify, and write output
# --------------------------------------------------
#
# Now we put it all together. This function:
#   - Opens leads_1000.csv
#   - Goes through each row
#   - Assigns a Lead_ID (so every lead has a unique identifier)
#   - Classifies the lead using our function above
#   - Collects all the results
#   - Writes them to a new CSV file
#   - Keeps track of how many leads went into each role (for stats)

def process_file(input_path, output_path):
    """
    Main processing pipeline. Reads input CSV, classifies every
    lead, writes enriched output CSV, and returns summary stats.
    """

    results = []           # will hold all classified lead dicts
    role_counts = {}       # counts how many leads per role
    status_counts = {      # tracks match quality
        "matched": 0,
        "missing": 0,
        "unrecognized": 0,
    }
    problems = []          # any rows with issues get logged here

    # --- Read the input CSV ---
    #
    # The CSV columns are:
    #   Name, Phone Number, Buyer/Channel Partner/Enquiry/Site Visit
    #
    # That third column name is long but it's basically the source type.

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=1):

            # grab each field from the row
            name  = row.get("Name", "").strip()
            phone = row.get("Phone Number", "").strip()
            source_raw = row.get("Buyer/Channel Partner/Enquiry/Site Visit", "").strip()

            # generate a lead ID like LEAD-0001, LEAD-0002, etc.
            lead_id = "LEAD-{:04d}".format(row_num)

            # --- basic validation ---
            # I'm not stopping the program for bad rows, just
            # noting them so they can be reviewed later

            if name == "":
                problems.append("Row {}: name is blank".format(row_num))

            if phone == "":
                problems.append("Row {}: phone number is blank".format(row_num))
            elif not phone.replace("-","").replace("+","").replace(" ","").isdigit():
                problems.append("Row {}: phone '{}' has non-numeric chars".format(row_num, phone))

            # --- classify this lead ---
            role, match_status = classify_lead(source_raw)

            # update our counters
            status_counts[match_status] += 1
            role_counts[role] = role_counts.get(role, 0) + 1

            # save the enriched record
            results.append({
                "Lead_ID"       : lead_id,
                "Name"          : name,
                "Phone"         : phone,
                "Source_Number"  : source_raw,
                "Assigned_Role" : role,
            })

    # --- Write the output CSV ---
    columns = ["Lead_ID", "Name", "Phone", "Source_Number", "Assigned_Role"]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)

    # bundle up everything we want to report
    summary = {
        "total_leads"    : len(results),
        "role_counts"    : role_counts,
        "status_counts"  : status_counts,
        "problems"       : problems,
    }

    return results, summary


# --------------------------------------------------
# STEP 5: Print a nice readable report
# --------------------------------------------------
#
# Instead of just dumping numbers, I want the output to be
# easy to scan so someone reviewing this can quickly see
# what happened and whether anything looks off.

def print_report(summary, output_path, sample_data):
    """Prints a human-readable summary of the classification run."""

    total = summary["total_leads"]
    roles = summary["role_counts"]
    statuses = summary["status_counts"]
    problems = summary["problems"]

    print()
    print("=" * 60)
    print("   CLASSIFICATION RESULTS")
    print("=" * 60)

    # --- sample of classified leads ---
    print()
    print("   First 10 classified leads:")
    print("   {:<11} {:<25} {:<17} {}".format(
        "Lead_ID", "Name", "Source", "Assigned Role"
    ))
    print("   " + "-" * 55)

    for row in sample_data[:10]:
        print("   {:<11} {:<25} {:<17} {}".format(
            row["Lead_ID"],
            row["Name"][:24],        # cap name length so table stays neat
            row["Source_Number"][:16],
            row["Assigned_Role"],
        ))

    # --- role distribution ---
    print()
    print("   Role distribution across {} leads:".format(total))
    print("   " + "-" * 40)

    for role in sorted(roles.keys()):
        count = roles[role]
        pct = (count / total) * 100
        bar = "#" * int(pct / 2)   # simple text bar chart
        print("   {:<20} {:>4} ({:>5.1f}%)  {}".format(role, count, pct, bar))

    # --- match quality ---
    print()
    print("   Match quality:")
    print("   " + "-" * 40)
    print("   Exact matches:       {}".format(statuses["matched"]))
    print("   Missing source:      {}".format(statuses["missing"]))
    print("   Unrecognized source:  {}".format(statuses["unrecognized"]))

    # --- data issues ---
    if problems:
        print()
        print("   Data issues found: {}".format(len(problems)))
        for p in problems[:5]:
            print("   - {}".format(p))
        if len(problems) > 5:
            print("   ... and {} more".format(len(problems) - 5))
    else:
        print()
        print("   No data issues found. All rows look clean.")

    print()
    print("   Output saved to: {}".format(output_path))
    print("=" * 60)


# --------------------------------------------------
# STEP 6: Formula explanation (required by assignment)
# --------------------------------------------------
#
# The assignment asks us to provide the Google Sheets / Excel
# formula that does the same thing. Here it is, with explanation.

def show_formula_logic():
    """
    Prints the spreadsheet formula and a step-by-step explanation
    of how it works. Two approaches are shown: a direct one and
    a scalable one.
    """

    print()
    print("=" * 60)
    print("   FORMULA LOGIC (Google Sheets / Excel)")
    print("=" * 60)

    # --- Approach 1: Nested IFS ---
    print("""
   APPROACH 1: Using IFS (works for a small number of roles)
   ---------------------------------------------------------

   Assuming the source value is in cell C2, put this in D2:

   =IFS(
       ISBLANK(C2),                    "UNKNOWN",
       LOWER(TRIM(C2))="buyer",        "BUYER",
       LOWER(TRIM(C2))="buyer_line",   "BUYER",
       LOWER(TRIM(C2))="channel partner",   "CHANNEL_PARTNER",
       LOWER(TRIM(C2))="partner_line",      "CHANNEL_PARTNER",
       LOWER(TRIM(C2))="site visit",   "SITE_VISIT",
       LOWER(TRIM(C2))="visit_line",   "SITE_VISIT",
       LOWER(TRIM(C2))="enquiry",      "ENQUIRY",
       LOWER(TRIM(C2))="enquiry_line", "ENQUIRY",
       TRUE,                           "UNKNOWN"
   )

   How this works, line by line:
   - ISBLANK(C2) checks if the cell is empty
   - LOWER(TRIM(C2)) cleans the value: TRIM removes extra
     spaces, LOWER makes it lowercase — same idea as our
     clean_source_value() function in Python
   - Each line checks for one possible value and maps it to
     a role
   - The final TRUE acts as a catch-all, like our "else"
     clause — anything that didn't match gets "UNKNOWN"

   Limitation: If we add more roles, this formula keeps getting
   longer and harder to maintain.
    """)

    # --- Approach 2: Lookup table ---
    print("""
   APPROACH 2: Using a lookup table (better for scalability)
   ---------------------------------------------------------

   Step 1: Create a lookup table on a separate sheet called
           "RoleConfig" with two columns:

           A               B
           ------          ------
           buyer           BUYER
           buyer_line      BUYER
           channel partner CHANNEL_PARTNER
           partner_line    CHANNEL_PARTNER
           site visit      SITE_VISIT
           visit_line      SITE_VISIT
           enquiry         ENQUIRY
           enquiry_line    ENQUIRY

   Step 2: In your main sheet, put this formula in D2:

   =IFERROR(
       VLOOKUP(LOWER(TRIM(C2)), RoleConfig!A:B, 2, FALSE),
       "UNKNOWN"
   )

   How this works:
   - VLOOKUP searches for our cleaned value in the first
     column of the RoleConfig table
   - If it finds a match, it returns the value from column 2
     (the role name)
   - If no match is found, VLOOKUP throws an error, and
     IFERROR catches that and returns "UNKNOWN" instead

   Why this is better:
   - To add a new role, you just add a row to the RoleConfig
     sheet. You don't touch the formula at all.
   - Non-technical team members can update the mapping without
     knowing formulas.
   - This is the same idea as our role_rules dictionary in the
     Python code — separate the DATA from the LOGIC.
    """)


# --------------------------------------------------
# STEP 7: Scalability and error handling explanation
# --------------------------------------------------
#
# The assignment asks:
#   - How does this scale to 10+ roles?
#   - How do we handle incorrect, missing, or new source values?

def show_scalability_and_error_handling():
    """
    Prints the scalability approach and error handling strategy
    as required by the assignment.
    """

    print()
    print("=" * 60)
    print("   SCALABILITY & ERROR HANDLING")
    print("=" * 60)

    print("""
   HOW THIS SCALES TO 10+ ROLES
   --------------------------------

   The key design choice is: the mapping rules are stored in a
   dictionary (role_rules), NOT hardcoded into if-else blocks.

   Right now we have 4 roles. If we need 10 or 20, we just add
   lines to the dictionary. For example, to add an "INVESTOR"
   role, all we do is:

       role_rules["investor"]      = "INVESTOR"
       role_rules["investor_line"] = "INVESTOR"

   That's it. The classify_lead() function doesn't change.
   The process_file() function doesn't change. Only the
   config data changes.

   For even better scalability, we could move the rules out of
   the Python file entirely and into a JSON config file:

       role_config.json:
       {
           "buyer": "BUYER",
           "investor": "INVESTOR",
           "broker": "BROKER"
       }

   Then the Python code just loads this file at startup. This
   way, even someone who doesn't know Python can update the
   role mappings — they just edit the JSON file.

   In a production system, you might store these rules in a
   database table so they can be updated through a web dashboard
   without restarting the program.


   HANDLING EDGE CASES
   --------------------------------

   A) Incorrect Source_Number (e.g., typo like "Byuer"):
      - Our clean_source_value() handles case and whitespace,
        which covers the most common errors
      - If the value is truly wrong (not just a formatting
        issue), it gets classified as UNKNOWN
      - The "unrecognized" counter in our stats lets us know
        how many leads fell through, so someone can review them
      - In a future version, we could add fuzzy matching
        (checking if the typo is close to a known value) but
        that adds complexity and might cause false matches

   B) Missing Source_Number (empty cell):
      - Detected by clean_source_value() returning None
      - Gets classified as UNKNOWN with status "missing"
      - Logged in the problems list for review
      - In production, this could trigger an alert to the
        data entry team to fill in the missing value

   C) New roles introduced in the future:
      - Just add the new source_value -> role mapping to the
        role_rules dictionary (or JSON config file)
      - Re-run the script to reclassify any leads that were
        previously marked UNKNOWN
      - The UNKNOWN category acts as a safe "parking lot" for
        leads we can't classify yet
    """)


# --------------------------------------------------
# STEP 8: Example input/output table
# --------------------------------------------------

def show_example_table():
    """
    Shows a clear example of how different inputs get classified.
    This covers normal cases plus edge cases.
    """

    print()
    print("=" * 60)
    print("   EXAMPLE INPUT -> OUTPUT")
    print("=" * 60)

    # I'm showing real examples from the CSV plus some edge cases
    # to demonstrate that the logic handles everything correctly

    examples = [
        # (input_source,      expected_role,    why)
        ("Buyer",             "BUYER",          "direct match in CSV data"),
        ("Channel Partner",   "CHANNEL_PARTNER","direct match in CSV data"),
        ("Site Visit",        "SITE_VISIT",     "direct match in CSV data"),
        ("Enquiry",           "ENQUIRY",        "direct match in CSV data"),
        ("Buyer_Line",        "BUYER",          "matches assignment spec format"),
        ("Partner_Line",      "CHANNEL_PARTNER","matches assignment spec format"),
        ("Visit_Line",        "SITE_VISIT",     "matches assignment spec format"),
        ("  BUYER  ",         "BUYER",          "handles extra spaces + uppercase"),
        ("",                  "UNKNOWN",        "empty value -> fallback"),
        ("RandomText",        "UNKNOWN",        "unrecognized -> fallback"),
    ]

    print()
    print("   {:<20} {:<20} {}".format("Input (Source)", "Output (Role)", "Reason"))
    print("   " + "-" * 58)

    for src, role, reason in examples:
        display_src = '"{}"'.format(src) if src else '(empty)'
        # actually run it through our function to prove it works
        actual_role, _ = classify_lead(src)
        marker = "OK" if actual_role == role else "MISMATCH!"
        print("   {:<20} {:<20} {}".format(display_src, actual_role, reason))

    print()


# ============================================================
# RUN EVERYTHING
# ============================================================
#
# This is the entry point. When you run this script, it:
#   1. Processes the CSV file
#   2. Prints the classification report
#   3. Shows the formula logic explanation
#   4. Shows the example table
#   5. Shows the scalability plan

if __name__ == "__main__":

    # figure out where this script is, so we can find the CSV
    # files relative to it (no hardcoded paths)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    input_file  = os.path.join(script_dir, "leads_1000.csv")
    output_file = os.path.join(script_dir, "classified_leads_output.csv")

    # check that the input file actually exists before we try to open it
    if not os.path.exists(input_file):
        print("ERROR: Could not find '{}'".format(input_file))
        print("Make sure leads_1000.csv is in the same folder as this script.")
        exit(1)

    print()
    print("Processing: {}".format(input_file))
    print("Please wait...")

    # --- run the classification ---
    classified_data, summary = process_file(input_file, output_file)

    # --- show results ---
    print_report(summary, output_file, classified_data)
    show_example_table()
    show_formula_logic()
    show_scalability_and_error_handling()

    print()
    print("Done! {} leads classified and saved.".format(summary["total_leads"]))
    print()
