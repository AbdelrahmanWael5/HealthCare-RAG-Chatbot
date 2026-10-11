from pathlib import Path
import json
import re

# Configuration
INPUT_FILE = Path("data/raw/hypertension/medlineplus/medical_encyclopedia.txt")
OUTPUT_FILE = Path("data/processed/hypertension/medlineplus/medical_encyclopedia.json")
SOURCE = "MedlinePlus"
DOCUMENT_TITLE = "High blood pressure in adults - hypertension"
DOCUMENT_TYPE = "health_topic"
LANGUAGE = "en"
TOPIC = "hypertension"

EXPECTED_SECTIONS = [
    "Causes",
    "Symptoms",
    "Exams and Tests",
    "Treatment",
    "LIFESTYLE CHANGES",
    "MEDICINES FOR HYPERTENSION",
    "Outlook (Prognosis)",
    "When to Contact a Medical Professional",
    "Prevention",
    "Alternative Names",
]

# Text cleaning
def clean_line(line: str) -> str:
    """
    Clean extraction artifacts from one line.

    Only whitespace is normalized.
    The actual content is not changed.
    """

    # Normalize non-breaking spaces.
    line = line.replace("\u00a0", " ")

    # Normalize tabs and repeated spaces.
    line = re.sub(r"[ \t]+", " ", line)

    # Remove leading/trailing whitespace.
    line = line.strip()

    return line


def clean_text(text: str) -> list[str]:
    """
    Clean the extracted document while preserving
    meaningful line boundaries.

    Empty lines are removed.
    Non-empty lines remain separate.
    """

    # Normalize newline styles.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for raw_line in text.split("\n"):

        line = clean_line(raw_line)

        if line:
            lines.append(line)

    return lines

# Section extraction
def extract_sections(lines: list[str]) -> list[dict]:
    """
    Extract the known MedlinePlus sections.

    Every non-empty line inside each section is preserved.
    No paragraph reconstruction is performed.
    """

    section_positions = []

    for index, line in enumerate(lines):

        if line in EXPECTED_SECTIONS:
            section_positions.append(
                (index, line)
            )

    # Validate that all expected sections exist
    found_sections = [
        heading
        for _, heading in section_positions
    ]

    missing_sections = [
        heading
        for heading in EXPECTED_SECTIONS
        if heading not in found_sections
    ]

    if missing_sections:

        raise ValueError(
            "Missing MedlinePlus sections:\n"
            f"{missing_sections}"
        )

    # Validate section order
    if found_sections != EXPECTED_SECTIONS:

        raise ValueError(
            "MedlinePlus sections are not in "
            "the expected order.\n"
            f"Expected: {EXPECTED_SECTIONS}\n"
            f"Found: {found_sections}"
        )

    # Extract section content
    sections = []

    for i, (start_index, heading) in enumerate(
        section_positions
    ):

        if i + 1 < len(section_positions):

            end_index = section_positions[
                i + 1
            ][0]

        else:

            end_index = len(lines)

        section_lines = lines[
            start_index + 1:end_index
        ]

        sections.append(
            {
                "section": heading,
                "lines": section_lines,
            }
        )

    return sections

# Validation
def validate_sections(
    sections: list[dict]
) -> None:
    """
    Validate section count, names, order,
    and non-empty content.
    """

    # Validate section count
    if len(sections) != len(EXPECTED_SECTIONS):

        raise ValueError(
            f"Expected {len(EXPECTED_SECTIONS)} sections, "
            f"but found {len(sections)}."
        )

    # Validate names and order
    section_names = [
        section["section"]
        for section in sections
    ]

    if section_names != EXPECTED_SECTIONS:

        raise ValueError(
            "Section validation failed.\n"
            f"Expected: {EXPECTED_SECTIONS}\n"
            f"Found: {section_names}"
        )

    # Validate non-empty sections
    empty_sections = [
        section["section"]
        for section in sections
        if not section["lines"]
    ]

    if empty_sections:

        raise ValueError(
            f"Empty sections detected: "
            f"{empty_sections}"
        )


# Build JSON document
def build_document(
    sections: list[dict]
) -> dict:
    """
    Build the final preprocessed JSON document.

    Source lines are preserved individually so that
    the later chunking stage can decide how to combine them.
    """

    return {
        "metadata": {
            "source": SOURCE,
            "document_title": DOCUMENT_TITLE,
            "document_type": DOCUMENT_TYPE,
            "language": LANGUAGE,
            "topic": TOPIC,
            "section_count": len(sections),
        },
        "sections": sections,
    }

# Main preprocessing pipeline
def main():
    print("MedlinePlus Hypertension Preprocessing")
    
    # Check input file
    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    # Load
    raw_text = INPUT_FILE.read_text(encoding="utf-8")
    print(f"Input characters: {len(raw_text):,}")

    # Clean
    lines = clean_text(raw_text)
    print(f"Cleaned non-empty lines: {len(lines):,}")

    # Validate title
    if not lines:

        raise ValueError(
            "Input document is empty."
        )

    extracted_title = lines[0]

    if extracted_title != DOCUMENT_TITLE:

        raise ValueError(
            "Unexpected document title.\n"
            f"Expected: {DOCUMENT_TITLE}\n"
            f"Found: {extracted_title}"
        )

    # Extract sections
    sections = extract_sections(lines)

    # Validate
    validate_sections(sections)

    # Build document
    document = build_document(sections)

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # Final report
    total_lines = sum(len(section["lines"]) for section in sections)
    total_chars = sum(len(line) for section in sections for line in section["lines"])

    print()
    print("Preprocessing completed successfully.")
    print(f"Document: {DOCUMENT_TITLE}")
    print(f"Sections: {len(sections)}")
    print(f"Processed lines: {total_lines:,}")
    print(f"Processed characters: {total_chars:,}")
    print("Output: {OUTPUT_FILE}")
    print("Sections:")

    for i, section in enumerate(sections, start=1):
        print(f"  {i}. {section['section']} ({len(section['lines'])} lines)")

if __name__ == "__main__":
    main()