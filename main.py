import json
import os

from oracle_supplier_api import (
    get_supplier_by_name,
    get_supplier_by_id,
    get_business_classifications,
    get_supplier_attachments,
    get_supplier_dff,
    get_supplier_addresses,
    get_supplier_contacts,
    get_supplier_products_and_services,
)

from oracle_form_data import (
    build_oracle_form_data,
)

from comparison import (
    build_validation_result,
)


# ============================================================
# HELPERS
# ============================================================

def is_supplier_id(value):
    """
    Determine whether the user entered a numeric Supplier ID.
    """

    return value.isdigit()


def load_document_data(supplier_id):
    """
    Load the document extraction output created by
    extract_all_documents.py.
    """

    file_path = os.path.join(
        "extracted_data",
        f"{supplier_id}_documents.json"
    )

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            "Document extraction file not found:\n"
            f"{file_path}\n\n"
            "Run:\n"
            "python extract_all_documents.py"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(
            file
        )

    return data


def convert_documents_for_comparison(
    document_data
):
    """
    Convert the extracted document list into:

    {
        "trade_license": {...},
        "trn_certificate": {...},
        "iban_letter": {...}
    }

    No values are hardcoded here.
    """

    documents = {}

    for document in document_data.get(
        "documents",
        []
    ):

        document_type = document.get(
            "documentType"
        )

        extracted_data = document.get(
            "data"
        )

        if (
            document_type
            and extracted_data is not None
        ):

            documents[
                document_type
            ] = extracted_data

    return documents


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("SUPPLIER VALIDATION")
    print("=" * 70)

    user_input = input(
        "Enter Supplier Name or Supplier ID: "
    ).strip()

    if not user_input:

        raise ValueError(
            "Supplier Name or Supplier ID is required."
        )

    # ========================================================
    # 1. SUPPLIER IDENTIFICATION
    # ========================================================

    print()
    print("=" * 70)
    print("SUPPLIER IDENTIFICATION")
    print("=" * 70)

    if is_supplier_id(
        user_input
    ):

        print(
            "Input detected as Supplier ID."
        )

        supplier_id = user_input

        supplier = get_supplier_by_id(
            supplier_id
        )

        if not supplier:

            raise ValueError(
                f"Supplier ID {supplier_id} "
                "was not found."
            )

        # IMPORTANT:
        # Never silently replace the requested Supplier ID.
        returned_supplier_id = str(
            supplier.get(
                "SupplierId"
            )
        )

        if (
            returned_supplier_id
            != supplier_id
        ):

            raise ValueError(
                "Supplier ID mismatch.\n"
                f"Requested: {supplier_id}\n"
                f"Oracle returned: "
                f"{returned_supplier_id}"
            )

    else:

        print(
            "Input detected as Supplier Name."
        )

        supplier = get_supplier_by_name(
            user_input
        )

        if not supplier:

            raise ValueError(
                f"Supplier '{user_input}' "
                "was not found."
            )

        supplier_id = str(
            supplier.get(
                "SupplierId"
            )
        )

        if not supplier_id:

            raise ValueError(
                "Oracle supplier response "
                "does not contain SupplierId."
            )

    print()
    print(
        "Supplier found!"
    )

    print(
        "Supplier Name:",
        supplier.get(
            "Supplier"
        )
    )

    print(
        "Supplier ID:",
        supplier.get(
            "SupplierId"
        )
    )

    print(
        "Supplier Number:",
        supplier.get(
            "SupplierNumber"
        )
    )

    print(
        "Status:",
        supplier.get(
            "Status"
        )
    )

    # ========================================================
    # 2. ORACLE API DATA
    # ========================================================

    print()
    print("=" * 70)
    print("ORACLE API DATA")
    print("=" * 70)

    print()
    print(
        "Getting Business Classifications..."
    )

    business_classifications = (
        get_business_classifications(
            supplier_id
        )
    )

    print(
        "Business Classifications:",
        len(
            business_classifications.get(
                "items",
                []
            )
        )
    )

    print()
    print(
        "Getting Attachments..."
    )

    attachments = (
        get_supplier_attachments(
            supplier_id
        )
    )

    print(
        "Attachments:",
        len(
            attachments.get(
                "items",
                []
            )
        )
    )

    print()
    print(
        "Getting DFF..."
    )

    dff = get_supplier_dff(
        supplier_id
    )

    print(
        "DFF data retrieved."
    )

    print()
    print(
        "Getting Addresses..."
    )

    addresses = get_supplier_addresses(
        supplier_id
    )

    print(
        "Addresses:",
        len(
            addresses.get(
                "items",
                []
            )
        )
    )

    print()
    print(
        "Getting Contacts..."
    )

    contacts = get_supplier_contacts(
        supplier_id
    )

    print(
        "Contacts:",
        len(
            contacts.get(
                "items",
                []
            )
        )
    )

    print()
    print(
        "Getting Products and Services..."
    )

    products_and_services = (
        get_supplier_products_and_services(
            supplier_id
        )
    )

    print(
        "Products / Services:",
        len(
            products_and_services.get(
                "items",
                []
            )
        )
    )

    # ========================================================
    # 3. BUILD ORACLE FORM DATA
    # ========================================================

    print()
    print("=" * 70)
    print("BUILDING ORACLE FORM DATA")
    print("=" * 70)

    oracle_form = build_oracle_form_data(
        supplier=supplier,
        addresses=addresses,
        contacts=contacts,
        business_classifications=(
            business_classifications
        ),
        products_and_services=(
            products_and_services
        ),
    )

    print(
        "Oracle form data prepared."
    )

    # ========================================================
    # 4. LOAD DOCUMENT EXTRACTION
    # ========================================================

    print()
    print("=" * 70)
    print("LOADING DOCUMENT DATA")
    print("=" * 70)

    document_data = load_document_data(
        supplier_id
    )

    documents = (
        convert_documents_for_comparison(
            document_data
        )
    )

    print(
        "Documents available for comparison:"
    )

    for document_type in documents:

        print(
            "-",
            document_type
        )

    # ========================================================
    # 5. VALIDATION
    # ========================================================

    print()
    print("=" * 70)
    print("RUNNING DYNAMIC VALIDATION")
    print("=" * 70)

    validation_result = (
        build_validation_result(
            oracle_supplier=supplier,
            oracle_form=oracle_form,
            documents=documents,
        )
    )

    # ========================================================
    # 6. DISPLAY RESULT
    # ========================================================

    print()
    print("=" * 70)
    print("VALIDATION RESULT")
    print("=" * 70)

    print(
        json.dumps(
            validation_result,
            indent=4,
            ensure_ascii=False
        )
    )

    # ========================================================
    # 7. SAVE RESULT
    # ========================================================

    output_directory = (
        "validation_results"
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    output_file = os.path.join(
        output_directory,
        f"{supplier_id}_validation.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            validation_result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

    print(
        "Result saved to:"
    )

    print(
        output_file
    )


if __name__ == "__main__":
    main()