import json
import os

from gemini_extractor import (
    extract_document,
    detect_document_type,
)


def main():

    supplier_id = input(
        "Enter Supplier ID: "
    ).strip()

    document_directory = os.path.join(
        "documents",
        supplier_id
    )

    if not os.path.isdir(
        document_directory
    ):

        raise FileNotFoundError(
            f"Document directory not found: "
            f"{document_directory}"
        )

    print()
    print("=" * 70)
    print("DOCUMENT EXTRACTION")
    print("=" * 70)

    pdf_files = []

    for filename in os.listdir(
        document_directory
    ):

        if filename.lower().endswith(
            ".pdf"
        ):

            pdf_files.append(
                filename
            )

    if not pdf_files:

        print(
            "No PDF documents found."
        )

        return

    print(
        "PDF documents found:",
        len(pdf_files)
    )

    documents_data = []

    for filename in sorted(
        pdf_files
    ):

        pdf_path = os.path.join(
            document_directory,
            filename
        )

        document_type = (
            detect_document_type(
                filename
            )
        )

        print()
        print(
            "-" * 70
        )

        print(
            "Document:",
            filename
        )

        print(
            "Detected type:",
            document_type
        )

        try:

            extracted_data = (
                extract_document(
                    pdf_path
                )
            )

            documents_data.append(
                {
                    "fileName": filename,
                    "filePath": pdf_path,
                    "documentType": document_type,
                    "data": extracted_data,
                }
            )

            print()
            print(
                "Extracted data:"
            )

            print(
                json.dumps(
                    extracted_data,
                    indent=4,
                    ensure_ascii=False
                )
            )

        except Exception as error:

            print()
            print(
                "Extraction failed:"
            )

            print(
                str(error)
            )

            documents_data.append(
                {
                    "fileName": filename,
                    "filePath": pdf_path,
                    "documentType": document_type,
                    "data": None,
                    "error": str(error),
                }
            )

    # ========================================================
    # SAVE ALL DOCUMENT DATA
    # ========================================================

    output_directory = (
        "extracted_data"
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    output_file = os.path.join(
        output_directory,
        f"{supplier_id}_documents.json"
    )

    output = {
        "supplierId": supplier_id,
        "documents": documents_data,
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 70)
    print("DOCUMENT EXTRACTION COMPLETE")
    print("=" * 70)

    print(
        "Documents processed:",
        len(documents_data)
    )

    print(
        "Output:",
        output_file
    )


if __name__ == "__main__":
    main()