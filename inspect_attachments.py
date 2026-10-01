import json
import os

from oracle_supplier_api import (
    get_supplier_by_id,
    get_supplier_attachments,
    find_file_contents_url,
)


# ============================================================
# GET SUPPLIER ID
# ============================================================

supplier_id = input(
    "Enter Supplier ID: "
).strip()


# ============================================================
# GET SUPPLIER
# ============================================================

supplier = get_supplier_by_id(
    supplier_id
)

if not supplier:
    raise ValueError(
        "Supplier not found."
    )


# ============================================================
# VERIFY EXACT SUPPLIER ID
# ============================================================

returned_id = str(
    supplier.get("SupplierId")
)

if returned_id != supplier_id:

    raise ValueError(
        "Oracle returned a different SupplierId. "
        "Processing stopped."
    )


print()
print("=" * 70)
print("SUPPLIER")
print("=" * 70)

print(
    "Supplier Name:",
    supplier.get("Supplier")
)

print(
    "Supplier ID:",
    supplier.get("SupplierId")
)


# ============================================================
# GET ATTACHMENTS
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
print("ORACLE ATTACHMENTS")
print("=" * 70)

print(
    "Total attachments:",
    len(items)
)


# ============================================================
# INSPECT EVERY ATTACHMENT
# ============================================================

attachment_details = []


for index, attachment in enumerate(
    items,
    start=1
):

    file_name = attachment.get(
        "FileName"
    )

    category_name = attachment.get(
        "CategoryName"
    )

    title = attachment.get(
        "Title"
    )

    description = attachment.get(
        "Description"
    )

    file_type = attachment.get(
        "FileType"
    )

    file_size = attachment.get(
        "FileSize"
    )

    file_contents_url = (
        find_file_contents_url(
            attachment
        )
    )


    print()
    print(
        f"Attachment {index}"
    )

    print(
        "-" * 70
    )

    print(
        "FileName:",
        file_name
    )

    print(
        "CategoryName:",
        category_name
    )

    print(
        "Title:",
        title
    )

    print(
        "Description:",
        description
    )

    print(
        "FileType:",
        file_type
    )

    print(
        "FileSize:",
        file_size
    )

    print(
        "FileContents URL found:",
        bool(file_contents_url)
    )


    attachment_details.append(
        {
            "FileName": file_name,
            "CategoryName": category_name,
            "Title": title,
            "Description": description,
            "FileType": file_type,
            "FileSize": file_size,
            "FileContentsURL": file_contents_url,
        }
    )


# ============================================================
# SAVE ATTACHMENT METADATA
# ============================================================

output_directory = (
    "attachment_data"
)

os.makedirs(
    output_directory,
    exist_ok=True
)


output_file = os.path.join(
    output_directory,
    f"{supplier_id}_attachments.json"
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        attachment_details,
        file,
        indent=4,
        ensure_ascii=False
    )


print()
print("=" * 70)
print("ATTACHMENT METADATA SAVED")
print("=" * 70)

print(
    output_file
)