from pathlib import Path
import json
import re

# Configuration
INPUT_FILE = Path("data/raw/hypertension/cdc/hypertension_management_toolkit.txt")
OUTPUT_FILE = Path("data/processed/hypertension/cdc/hypertension_management_toolkit.json")
SOURCE = "CDC"
DOCUMENT_TITLE = ("CDC Hypertension Management Program Implementation Toolkit")
DOCUMENT_TYPE = "clinical_management_toolkit"
LANGUAGE = "en"
TOPIC = "hypertension"


# Helper
def section(title, children=None):
    return {
        "title": title,
        "children": children or [],
    }

# EXACT CONFIRMED DOCUMENT STRUCTURE
DOCUMENT_STRUCTURE = [

    section(
        "Overview",
        [
            section("Introduction"),
            section("Hypertension: An Overview"),
            section("Challenges with Managing Hypertension"),
            section("The Hypertension Management Program"),

            section(
                "Using the HMP Toolkit",
                [
                    section(
                        "What infrastructure does an organization "
                        "need to implement the HMP?"
                    ),
                    section(
                        "How can an organization identify and care "
                        "for patients in the HMP?"
                    ),
                    section(
                        "What happens during blood pressure checks?"
                    ),
                    section(
                        "What happens during hypertension "
                        "management visits?"
                    ),
                ],
            ),

            section("Hypertension Guidelines"),
        ],
    ),

    section(
        "Training and Staff Engagement",
        [
            section("Tips for Making Training Successful"),
            section("Staff Engagement"),
        ],
    ),

    section(
        "Program Component 1: Integrated Care Team",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 1: "
                "Integrated Care Team",
                [
                    section(
                        "Activity 1: Establish the hypertension "
                        "management council"
                    ),
                    section(
                        "Activity 2: Create an HMP staffing plan "
                        "and establish the integrated care team"
                    ),
                    section(
                        "Activity 3: Identify an HMP champion"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 1: "
                "Integrated Care Team"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 2: Patient Registries and "
        "Outreach Lists in the EHR",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 2: "
                "Patient Registries and Outreach Lists in the EHR",
                [
                    section(
                        "Activity 1: Create the HMP registry"
                    ),
                    section(
                        "Activity 2: Develop a process for "
                        "conducting outreach"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 2: "
                "Patient Registries and Outreach Lists in the EHR"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 3: No-Copayment Walk-in/Scheduled "
        "Blood Pressure Checks",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 3: "
                "No-Copayment Walk-in/Scheduled Blood Pressure Checks",
                [
                    section(
                        "Activity 1: Establish protocols, clinical "
                        "processes, and billing modifications to allow "
                        "for no-copayment walk-in/scheduled blood "
                        "pressure checks"
                    ),
                    section(
                        "Activity 2: Train staff on no-copayment "
                        "walk-in/scheduled blood pressure checks"
                    ),
                    section(
                        "Activity 3: Advertise the no-copayment "
                        "walk-in/scheduled blood pressure checks"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 3: "
                "No-Copayment Walk-in/Scheduled Blood Pressure Checks"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 4: EHR Alerts for "
        "Blood Pressure Re-check",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 4: "
                "EHR Alerts for Blood Pressure Re-check",
                [
                    section(
                        "Activity 1: Determine how the blood "
                        "pressure alerts will function in your EHR"
                    ),
                    section(
                        "Activity 2: Program the blood pressure "
                        "alert into your EHR"
                    ),
                    section(
                        "Activity 3: Train staff on how to "
                        "respond to blood pressure alerts"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 4: "
                "EHR Alerts for Blood Pressure Re-check"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 5: Education for Nurses and Other "
        "Staff on Blood Pressure Measurement Technique",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 5: "
                "Education for Nurses and Other Staff on Blood "
                "Pressure Measurement Technique",
                [
                    section(
                        "Activity 1: Develop or select a blood "
                        "pressure measurement technique"
                    ),
                    section(
                        "Activity 2: Conduct training "
                        "(including refresher training to keep "
                        "staff up to date)"
                    ),
                    section(
                        "Activity 3: Make educational materials "
                        "available to staff"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 5: "
                "Education for Nurses and Other Staff on Blood "
                "Pressure Measurement Technique"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 6: Promote Use of Combination "
        "Medications to Treat High Blood Pressure",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 6: "
                "Promote Use of Combination Medications to "
                "Treat High Blood Pressure",
                [
                    section(
                        "Activity 1: Work with health system "
                        "leadership and providers to determine "
                        "a standard prescribing protocol for "
                        "combination medications"
                    ),
                    section(
                        "Activity 2: Train staff to implement "
                        "new protocols and disseminate new protocols"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 6: "
                "Promote Use of Combination Medications to "
                "Treat High Blood Pressure"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 7: Hypertension Management Visits",
        [
            section("Background"),

            section(
                "Activity for Implementing Component 7: "
                "Hypertension Management Visits",
                [
                    section(
                        "Activity 1: Establish new clinical "
                        "workflows for hypertension management visits"
                    ),
                    section(
                        "Train staff on new clinical workflows"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 7: "
                "Hypertension Management Visits",
                [
                    section("General Adaptation Tips"),
                    section("Collaborative Practice Agreements"),
                ],
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 8: Promotion of Self-Measured "
        "Blood Pressure Monitoring",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 8: "
                "Promotion of Self-Measured Blood Pressure Monitoring",
                [
                    section(
                        "Activity 1: Identify a source for accurate "
                        "low-cost blood pressure monitors"
                    ),
                    section(
                        "Activity 2: Develop a protocol for promoting "
                        "home blood pressure monitors during patient "
                        "encounters, including educating patients "
                        "about how to use the monitor"
                    ),
                    section(
                        "Activity 3: Develop a process for patients "
                        "to securely communicate blood pressure readings"
                    ),
                    section("Activity 4: Train staff"),
                ],
            ),

            section(
                "Suggestions for Adapting Component 8: "
                "Promotion of Self-Measured Blood Pressure Monitoring"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 9: Specialty Department Blood "
        "Pressure Measurements with Referral to Primary "
        "Care When Needed",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 9: "
                "Specialty Department Blood Pressure Measurements "
                "with Referral to Primary Care when Needed",
                [
                    section(
                        "Activity 1: Engage clinic staff in "
                        "integrating protocols for specialty "
                        "department blood pressure measurement "
                        "and referral"
                    ),
                    section(
                        "Activity 2: Develop EHR alerts and order "
                        "sets to remind staff of protocols and "
                        "facilitate follow-up"
                    ),
                    section(
                        "Activity 3: Educate specialty department "
                        "staff on protocols for blood pressure "
                        "measurement and referral"
                    ),
                    section(
                        "Activity 4: Provide feedback to staff "
                        "to assist them in following the protocol"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 9: "
                "Specialty Department Referral to Primary Care"
            ),

            section("Resources"),
        ],
    ),

    section(
        "Program Component 10: Incentives, Rewards, and Recognition",
        [
            section("Background"),

            section(
                "Activities for Implementing Component 10: "
                "Incentives, Rewards, and Recognition",
                [
                    section(
                        "Activity 1: Determine incentive structure "
                        "and identify performance measures"
                    ),
                    section(
                        "Activity 2: Promote awareness of incentive "
                        "program among staff"
                    ),
                    section(
                        "Activity 3: Monitor performance and "
                        "distribute performance-based incentives"
                    ),
                ],
            ),

            section(
                "Suggestions for Adapting Component 10: "
                "Incentives, Rewards, and Recognition"
            ),

            section("Resources"),
        ],
    ),
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_whitespace(text):
    text = text.replace("\u00a0", " ")
    text = text.replace("\t", " ")
    return re.sub(r"\s+", " ", text).strip()


def clean_line(line):
    line = line.replace("\u00a0", " ")
    line = line.replace("\t", " ")
    line = re.sub(r"[ ]+", " ", line)
    return line.strip()


# ============================================================
# PDF ARTIFACT DETECTION
# ============================================================

def is_page_marker(line):
    return bool(
        re.fullmatch(
            r"PAGE\s+\d+",
            line,
            flags=re.IGNORECASE
        )
    )


def is_page_number(line):
    return bool(
        re.fullmatch(r"\d+", line)
    )


def is_roman_page_number(line):
    return bool(
        re.fullmatch(r"[IVX]+", line)
    )


# ============================================================
# BASIC PDF CLEANUP
# ============================================================

def clean_pdf_lines(raw_text):

    raw_text = raw_text.replace("\r\n", "\n")
    raw_text = raw_text.replace("\r", "\n")

    raw_lines = raw_text.split("\n")

    cleaned = []

    after_page_marker = False

    for raw_line in raw_lines:

        line = clean_line(raw_line)

        if not line:
            continue

        if is_page_marker(line):

            after_page_marker = True
            continue

        if after_page_marker:

            if (
                is_page_number(line)
                or is_roman_page_number(line)
            ):
                after_page_marker = False
                continue

            after_page_marker = False

        cleaned.append(line)

    return cleaned


# ============================================================
# LOCATE ACTUAL DOCUMENT BODY
# ============================================================

def find_document_body(lines):

    exhibits_index = None

    for i, line in enumerate(lines):

        if normalize_whitespace(line) == "LIST OF EXHIBITS":
            exhibits_index = i
            break

    if exhibits_index is None:
        raise ValueError(
            "Could not find 'LIST OF EXHIBITS'."
        )

    for i in range(
        exhibits_index + 1,
        len(lines)
    ):

        if normalize_whitespace(lines[i]) != "Overview":
            continue

        if (
            i + 1 < len(lines)
            and normalize_whitespace(lines[i + 1])
            == "Introduction"
        ):
            return i

    raise ValueError(
        "Could not locate the actual document body."
    )


# ============================================================
# REMOVE STANDALONE PRINTED PAGE NUMBERS
# ============================================================

def remove_standalone_page_numbers(lines):

    cleaned = []
    removed_pages = []

    for line in lines:

        if re.fullmatch(r"\d+", line):

            number = int(line)

            # CDC document body pages are 6–78.
            # Only standalone integers in this range
            # are treated as printed page numbers.
            if 6 <= number <= 78:

                removed_pages.append(number)
                continue

        cleaned.append(line)

    return cleaned, removed_pages


# ============================================================
# REMOVE MERGED PRINTED PAGE NUMBERS
# ============================================================

def remove_merged_page_numbers(lines):

    """
    Fix PDF extraction cases where a printed page number
    becomes attached to the preceding sentence.

    Example:

        The goals of hypertension management visits are to:50

    becomes:

        The goals of hypertension management visits are to:

    IMPORTANT:

    We do NOT blindly remove every number.

    The number is considered a page artifact only when:

    1. It is 6–78.
    2. It appears at the END of a line.
    3. The character immediately before it is punctuation
       such as :, ., ;, ,, or ).

    This protects legitimate content such as:

        54 Centers for Disease Control...
        2024
        120/80
        5 mg
        1. Determine incentive structure...

    """

    cleaned = []
    removed = []

    # Printed pages in this document.
    PAGE_MIN = 6
    PAGE_MAX = 78

    # Number at the very end of a line.
    pattern = re.compile(
        r"(?P<prefix>.*?)(?P<punc>[:;,.])(?P<number>\d+)$"
    )

    for line in lines:

        match = pattern.fullmatch(line)

        if not match:
            cleaned.append(line)
            continue

        number = int(
            match.group("number")
        )

        prefix = match.group("prefix")
        punctuation = match.group("punc")

        if not (
            PAGE_MIN <= number <= PAGE_MAX
        ):
            cleaned.append(line)
            continue

        # Additional protection:
        #
        # The prefix must contain real text.
        if not prefix.strip():
            cleaned.append(line)
            continue

        # Do not modify obvious numbered references.
        #
        # Example:
        # "54 Centers for Disease Control..." does not match
        # this punctuation-ending pattern anyway, but this
        # protection keeps the intent explicit.
        if re.search(
            r"^\s*\d+\s+",
            prefix
        ):
            cleaned.append(line)
            continue

        cleaned_line = (
            prefix.rstrip() + punctuation
        )

        cleaned.append(cleaned_line)

        removed.append(
            {
                "page": number,
                "original": line,
                "cleaned": cleaned_line,
            }
        )

    return cleaned, removed


# ============================================================
# FLATTEN EXPECTED HIERARCHY
# ============================================================

def flatten_structure(
    nodes,
    level=0,
    parent=None,
    path=None
):

    if path is None:
        path = []

    flattened = []

    for node in nodes:

        title = node["title"]

        current_path = path + [title]

        flattened.append(
            {
                "title": title,
                "normalized": normalize_whitespace(title),
                "level": level,
                "parent": parent,
                "path": current_path,
            }
        )

        flattened.extend(
            flatten_structure(
                node["children"],
                level=level + 1,
                parent=title,
                path=current_path,
            )
        )

    return flattened


# ============================================================
# RECONSTRUCT WRAPPED HEADINGS
# ============================================================

def reconstruct_headings(
    lines,
    expected_headings
):

    heading_lookup = {
        item["normalized"]: item["title"]
        for item in expected_headings
    }

    result = []

    i = 0

    while i < len(lines):

        matched = False

        for width in range(1, 10):

            if i + width > len(lines):
                break

            selected = lines[i:i + width]

            candidate = selected[0]

            for next_line in selected[1:]:

                if candidate.endswith("-"):
                    candidate += next_line
                else:
                    candidate += " " + next_line

            candidate_normalized = normalize_whitespace(
                candidate
            )

            if candidate_normalized in heading_lookup:

                result.append(
                    heading_lookup[candidate_normalized]
                )

                i += width
                matched = True
                break

        if matched:
            continue

        result.append(lines[i])
        i += 1

    return result


# ============================================================
# DETECT HEADINGS
# ============================================================

def detect_headings(
    body_lines,
    expected_headings
):

    expected_titles = {
        item["title"]
        for item in expected_headings
    }

    positions = []

    for index, line in enumerate(body_lines):

        if line in expected_titles:

            positions.append(
                {
                    "index": index,
                    "title": line,
                }
            )

    return positions


# ============================================================
# VALIDATE HEADING SEQUENCE
# ============================================================

def validate_heading_sequence(
    detected_positions,
    expected_headings
):

    expected_titles = [
        item["title"]
        for item in expected_headings
    ]

    actual_titles = [
        position["title"]
        for position in detected_positions
    ]

    if actual_titles == expected_titles:
        return

    max_length = max(
        len(expected_titles),
        len(actual_titles)
    )

    first_mismatch = 0

    for i in range(max_length):

        expected = (
            expected_titles[i]
            if i < len(expected_titles)
            else "<END>"
        )

        actual = (
            actual_titles[i]
            if i < len(actual_titles)
            else "<END>"
        )

        if expected != actual:

            first_mismatch = i
            break

    start = max(
        0,
        first_mismatch - 3
    )

    end = min(
        max_length,
        first_mismatch + 4
    )

    raise ValueError(
        "\n"
        "CDC heading validation failed.\n\n"
        f"Expected headings: {len(expected_titles)}\n"
        f"Detected headings: {len(actual_titles)}\n\n"
        f"First mismatch at heading #{first_mismatch + 1}\n\n"
        "Expected context:\n"
        + "\n".join(
            f"  {start + i + 1}. {title}"
            for i, title in enumerate(
                expected_titles[start:end]
            )
        )
        + "\n\n"
        "Detected context:\n"
        + "\n".join(
            f"  {start + i + 1}. {title}"
            for i, title in enumerate(
                actual_titles[start:end]
            )
        )
    )


# ============================================================
# BUILD HIERARCHY
# ============================================================

def build_tree(
    body_lines,
    heading_positions,
    expected_headings
):

    expected_by_position = []

    for i, position in enumerate(
        heading_positions
    ):

        expected_info = expected_headings[i]

        expected_by_position.append(
            {
                "index": position["index"],
                "title": position["title"],
                "level": expected_info["level"],
                "parent": expected_info["parent"],
                "path": expected_info["path"],
            }
        )

    root = []
    stack = []

    for i, heading in enumerate(
        expected_by_position
    ):

        start = heading["index"]

        if i + 1 < len(
            expected_by_position
        ):
            end = expected_by_position[
                i + 1
            ]["index"]
        else:
            end = len(body_lines)

        content = body_lines[
            start + 1:end
        ]

        node = {
            "title": heading["title"],
            "content": content,
            "children": [],
        }

        level = heading["level"]

        while (
            stack
            and stack[-1]["level"] >= level
        ):
            stack.pop()

        if stack:
            stack[-1]["node"]["children"].append(node)
        else:
            root.append(node)

        stack.append(
            {
                "level": level,
                "node": node,
            }
        )

    return root


# ============================================================
# VALIDATE HIERARCHY
# ============================================================

def validate_hierarchy(
    tree,
    expected_headings
):

    actual = []

    def walk(nodes, level=0):

        for node in nodes:

            actual.append(
                {
                    "title": node["title"],
                    "level": level,
                }
            )

            walk(
                node["children"],
                level + 1
            )

    walk(tree)

    expected = [
        {
            "title": item["title"],
            "level": item["level"],
        }
        for item in expected_headings
    ]

    if actual != expected:

        raise ValueError(
            "Generated hierarchy does not match "
            "the confirmed CDC hierarchy."
        )


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(tree):

    heading_count = 0
    content_line_count = 0
    content_character_count = 0

    level_counts = {}

    def walk(nodes, level=0):

        nonlocal heading_count
        nonlocal content_line_count
        nonlocal content_character_count

        for node in nodes:

            heading_count += 1

            level_counts[level] = (
                level_counts.get(level, 0) + 1
            )

            content_line_count += len(
                node["content"]
            )

            content_character_count += sum(
                len(line)
                for line in node["content"]
            )

            walk(
                node["children"],
                level + 1
            )

    walk(tree)

    return {
        "total_headings": heading_count,
        "content_lines": content_line_count,
        "content_characters": content_character_count,
        "headings_by_level": {
            str(level): count
            for level, count in sorted(
                level_counts.items()
            )
        },
    }


# ============================================================
# BUILD FINAL JSON
# ============================================================

def build_document(
    tree,
    statistics
):

    return {
        "metadata": {
            "source": SOURCE,
            "document_title": DOCUMENT_TITLE,
            "document_type": DOCUMENT_TYPE,
            "language": LANGUAGE,
            "topic": TOPIC,
            "top_level_sections": len(tree),
            "total_headings": statistics[
                "total_headings"
            ],
        },

        "statistics": statistics,

        "sections": tree,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "CDC Hypertension Management Toolkit Preprocessing"
    )
    print("=" * 70)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}"
        )

    # --------------------------------------------------------
    # Read input
    # --------------------------------------------------------

    raw_text = INPUT_FILE.read_text(
        encoding="utf-8",
        errors="replace"
    )

    print(
        f"Input characters: {len(raw_text):,}"
    )

    # --------------------------------------------------------
    # Basic PDF cleanup
    # --------------------------------------------------------

    lines = clean_pdf_lines(
        raw_text
    )

    print(
        f"Cleaned lines: {len(lines):,}"
    )

    # --------------------------------------------------------
    # Locate actual body
    # --------------------------------------------------------

    body_start = find_document_body(
        lines
    )

    print(
        f"Actual document body starts at "
        f"cleaned line: {body_start}"
    )

    body_lines = lines[
        body_start:
    ]

    # --------------------------------------------------------
    # Remove standalone page numbers
    # --------------------------------------------------------

    body_lines, removed_pages = (
        remove_standalone_page_numbers(
            body_lines
        )
    )

    print(
        f"Standalone PDF page numbers removed: "
        f"{len(removed_pages)}"
    )

    # --------------------------------------------------------
    # Remove merged page numbers
    # --------------------------------------------------------

    body_lines, merged_pages = (
        remove_merged_page_numbers(
            body_lines
        )
    )

    print(
        f"Merged PDF page numbers removed: "
        f"{len(merged_pages)}"
    )

    if merged_pages:

        print(
            "\nMerged page-number fixes:"
        )

        for item in merged_pages:

            print(
                f"  Page {item['page']}:"
            )

            print(
                f"    BEFORE: {item['original']}"
            )

            print(
                f"    AFTER:  {item['cleaned']}"
            )

    # --------------------------------------------------------
    # Expected hierarchy
    # --------------------------------------------------------

    expected_headings = flatten_structure(
        DOCUMENT_STRUCTURE
    )

    print(
        f"\nExpected headings: "
        f"{len(expected_headings)}"
    )

    # Confirm our manually defined structure.
    if len(expected_headings) != 95:

        raise ValueError(
            "Expected CDC hierarchy must contain "
            "exactly 95 headings."
        )

    # --------------------------------------------------------
    # Reconstruct wrapped headings
    # --------------------------------------------------------

    body_lines = reconstruct_headings(
        body_lines,
        expected_headings
    )

    print(
        f"Lines after heading reconstruction: "
        f"{len(body_lines):,}"
    )

    # --------------------------------------------------------
    # Detect headings
    # --------------------------------------------------------

    detected_positions = detect_headings(
        body_lines,
        expected_headings
    )

    print(
        f"Detected headings: "
        f"{len(detected_positions)}"
    )

    # --------------------------------------------------------
    # Strict heading validation
    # --------------------------------------------------------

    validate_heading_sequence(
        detected_positions,
        expected_headings
    )

    print(
        "Heading sequence validation: PASSED"
    )

    # --------------------------------------------------------
    # Build hierarchy
    # --------------------------------------------------------

    tree = build_tree(
        body_lines,
        detected_positions,
        expected_headings
    )

    # --------------------------------------------------------
    # Validate hierarchy
    # --------------------------------------------------------

    validate_hierarchy(
        tree,
        expected_headings
    )

    print(
        "Hierarchy validation: PASSED"
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    statistics = calculate_statistics(
        tree
    )

    # --------------------------------------------------------
    # Final checks
    # --------------------------------------------------------

    if statistics["total_headings"] != 95:

        raise ValueError(
            "Final JSON does not contain exactly "
            "95 headings."
        )

    if statistics["headings_by_level"].get("0") != 12:

        raise ValueError(
            "Final JSON does not contain exactly "
            "12 level-0 sections."
        )

    if statistics["headings_by_level"].get("1") != 48:

        raise ValueError(
            "Final JSON does not contain exactly "
            "48 level-1 sections."
        )

    if statistics["headings_by_level"].get("2") != 35:

        raise ValueError(
            "Final JSON does not contain exactly "
            "35 level-2 sections."
        )

    # --------------------------------------------------------
    # Build document
    # --------------------------------------------------------

    document = build_document(
        tree,
        statistics
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()
    print(
        "Preprocessing completed successfully."
    )

    print(
        f"Top-level sections: "
        f"{statistics['headings_by_level']['0']}"
    )

    print(
        f"Level 1 sections: "
        f"{statistics['headings_by_level']['1']}"
    )

    print(
        f"Level 2 sections: "
        f"{statistics['headings_by_level']['2']}"
    )

    print(
        f"Total headings: "
        f"{statistics['total_headings']}"
    )

    print(
        f"Content lines: "
        f"{statistics['content_lines']:,}"
    )

    print(
        f"Content characters: "
        f"{statistics['content_characters']:,}"
    )

    print(
        f"Output file:\n{OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()