import json
import os
import re

from oracle_supplier_api import (
    get_supplier_by_id,
    get_supplier_attachments,
    find_file_contents_url,
    get_file_contents,
)


def safe_filename(filename):
    """
    Convert an Oracle attachment filename into a safe
    Windows filename.
    """

    filename = filename.strip()

    filename = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        filename
    )

    return filename


def main():

    supplier_id = input(
        "Enter Supplier ID: "
    ).strip()

    # ============================================================
    # 1. GET SUPPLIER
    # ============================================================

    supplier = get_supplier_by_id(
        supplier_id
    )

    if not supplier:
        raise ValueError(
            "Supplier not found."
        )

    returned_supplier_id = str(
        supplier.get("SupplierId")
    )

    # IMPORTANT:
    # Never continue if Oracle returns another Supplier ID.
    if returned_supplier_id != supplier_id:

        raise ValueError(
            "Oracle returned a different SupplierId. "
            "Processing stopped."
        )

    supplier_name = supplier.get(
        "Supplier"
    )

    print()
    print("=" * 70)
    print("SUPPLIER")
    print("=" * 70)

    print(
        "Supplier Name:",
        supplier_name
    )

    print(
        "Supplier ID:",
        supplier_id
    )

    # ============================================================
    # 2. GET ATTACHMENTS
    # ============================================================

    attachments = get_supplier_attachments(
        supplier_id
    )

    items = attachments.get(
        "items",
        []
    )

    print()
    print("=" * 70)
    print("ATTACHMENTS")
    print("=" * 70)

    print(
        "Total attachments:",
        len(items)
    )

    if not items:

        print(
            "No attachments found."
        )

        return

    # ============================================================
    # 3. CREATE SUPPLIER DOCUMENT DIRECTORY
    # ============================================================

    document_directory = os.path.join(
        "documents",
        supplier_id
    )

    os.makedirs(
        document_directory,
        exist_ok=True
    )

    downloaded_documents = []

    # ============================================================
    # 4. DOWNLOAD EACH ATTACHMENT
    # ============================================================

    for index, attachment in enumerate(
        items,
        start=1
    ):

        file_name = attachment.get(
            "FileName"
        )

        if not file_name:

            print()
            print(
                f"Attachment {index} skipped: "
                "FileName missing."
            )

            continue

        print()
        print(
            f"Processing attachment {index}: "
            f"{file_name}"
        )

        # --------------------------------------------------------
        # Find FileContents URL
        # --------------------------------------------------------

        file_contents_url = (
            find_file_contents_url(
                attachment
            )
        )

        if not file_contents_url:

            print(
                "FileContents URL not found."
            )

            continue

        print(
            "FileContents URL found."
        )

        # --------------------------------------------------------
        # Safe local filename
        # --------------------------------------------------------

        local_filename = safe_filename(
            file_name
        )

        local_path = os.path.join(
            document_directory,
            local_filename
        )

        # --------------------------------------------------------
        # Download actual file
        # --------------------------------------------------------

        try:

            response = get_file_contents(
                file_contents_url
            )

            if response is None:

                print(
                    "No response received."
                )

                continue

            content = response.content

            if not content:

                print(
                    "Downloaded file is empty."
                )

                continue

            # ----------------------------------------------------
            # Basic PDF validation
            # ----------------------------------------------------

            if not content.startswith(
                b"%PDF"
            ):

                print(
                    "Warning: downloaded content "
                    "does not start with %PDF."
                )

            # ----------------------------------------------------
            # Save PDF
            # ----------------------------------------------------

            with open(
                local_path,
                "wb"
            ) as file:

                file.write(
                    content
                )

            file_size = os.path.getsize(
                local_path
            )

            print(
                "Downloaded successfully."
            )

            print(
                "Saved to:",
                local_path
            )

            print(
                "Size:",
                file_size,
                "bytes"
            )

            # ----------------------------------------------------
            # Save metadata
            # ----------------------------------------------------

            downloaded_documents.append(
                {
                    "supplierId": supplier_id,
                    "supplierName": supplier_name,
                    "fileName": file_name,
                    "localPath": local_path,
                    "categoryName": attachment.get(
                        "CategoryName"
                    ),
                    "title": attachment.get(
                        "Title"
                    ),
                    "description": attachment.get(
                        "Description"
                    ),
                    "fileContentsUrl": file_contents_url,
                    "fileSize": file_size,
                }
            )

        except Exception as error:

            print(
                "Download failed:"
            )

            print(
                str(error)
            )

    # ============================================================
    # 5. SAVE DOWNLOAD METADATA
    # ============================================================

    metadata_path = os.path.join(
        document_directory,
        "documents_metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            downloaded_documents,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ============================================================
    # 6. SUMMARY
    # ============================================================

    print()
    print("=" * 70)
    print("DOCUMENT DOWNLOAD SUMMARY")
    print("=" * 70)

    print(
        "Supplier:",
        supplier_name
    )

    print(
        "Supplier ID:",
        supplier_id
    )

    print(
        "Attachments found:",
        len(items)
    )

    print(
        "Documents downloaded:",
        len(downloaded_documents)
    )

    print(
        "Document directory:",
        document_directory
    )

    print(
        "Metadata file:",
        metadata_path
    )

    print()

    for document in downloaded_documents:

        print(
            "-",
            document["fileName"]
        )

        print(
            "  ",
            document["localPath"]
        )


if __name__ == "__main__":
    main()