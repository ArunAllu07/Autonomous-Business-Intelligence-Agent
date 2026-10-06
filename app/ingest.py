from pathlib import Path
from pypdf import PdfReader
import re


PDF_PATH = "data/ARUN_META_CV.pdf"


def load_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        text = page.extract_text()

        if text:
            pages.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

    return "\n".join(pages)


def clean_text(text: str) -> str:
    """
    Clean unnecessary whitespace from extracted PDF text.
    """

    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(
    text: str,
    max_chunk_size: int = 1200
) -> list[str]:
    """
    Create section-aware chunks.

    Instead of blindly cutting the CV every N characters,
    this keeps related lines together as much as possible.
    """

    text = clean_text(text)

    # Split primarily around CV sections/headings.
    sections = re.split(
        r"\n(?=[A-Z][A-Z &/]{3,}\n)",
        text
    )

    chunks = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        # If section is small enough, keep it together.
        if len(section) <= max_chunk_size:

            chunks.append(section)

            continue

        # Otherwise split by paragraphs/lines.
        lines = section.split("\n")

        current_chunk = ""

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if (
                len(current_chunk) + len(line) + 1
                <= max_chunk_size
            ):

                current_chunk += (
                    line + "\n"
                )

            else:

                if current_chunk.strip():
                    chunks.append(
                        current_chunk.strip()
                    )

                current_chunk = line + "\n"

        if current_chunk.strip():
            chunks.append(
                current_chunk.strip()
            )

    return chunks


def main():

    print("\n================================")
    print("AURA DOCUMENT INGESTION")
    print("================================")

    print("\nLoading PDF...")

    try:

        text = load_pdf(PDF_PATH)

        print(
            f"Characters extracted: {len(text)}"
        )

        chunks = chunk_text(text)

        print(
            f"Chunks created: {len(chunks)}"
        )

        print(
            "\n========== CHUNK PREVIEW ==========\n"
        )

        for i, chunk in enumerate(
            chunks[:5],
            start=1
        ):

            print(f"--- CHUNK {i} ---")

            print(chunk)

            print(
                "\n" + "-" * 60
            )

        print(
            "\n========== END PREVIEW ==========\n"
        )

    except Exception as e:

        print(
            f"\nERROR: {e}"
        )


if __name__ == "__main__":
    main()