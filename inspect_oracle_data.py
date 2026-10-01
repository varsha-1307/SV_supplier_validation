import json

from oracle_supplier_api import (
    get_supplier_by_id,
    get_supplier_dff,
    get_supplier_addresses,
    get_supplier_contacts,
    get_supplier_products_and_services,
    get_business_classifications,
)


# ============================================================
# SUPPLIER ID
# ============================================================

supplier_id = "300000326287336"


# ============================================================
# SUPPLIER
# ============================================================

print("========== SUPPLIER DATA ==========")

supplier = get_supplier_by_id(
    supplier_id
)

print(
    json.dumps(
        supplier,
        indent=4
    )
)


# ============================================================
# SUPPLIER DFF
# ============================================================

print()
print("========== SUPPLIER DFF ==========")

dff = get_supplier_dff(
    supplier_id
)

print(
    json.dumps(
        dff,
        indent=4
    )
)


# ============================================================
# ADDRESSES
# ============================================================

print()
print("========== ADDRESSES ==========")

addresses = get_supplier_addresses(
    supplier_id
)

print(
    json.dumps(
        addresses,
        indent=4
    )
)


# ============================================================
# CONTACTS
# ============================================================

print()
print("========== CONTACTS ==========")

contacts = get_supplier_contacts(
    supplier_id
)

print(
    json.dumps(
        contacts,
        indent=4
    )
)


# ============================================================
# PRODUCTS AND SERVICES
# ============================================================

print()
print("========== PRODUCTS AND SERVICES ==========")

products_services = get_supplier_products_and_services(
    supplier_id
)

print(
    json.dumps(
        products_services,
        indent=4
    )
)


# ============================================================
# BUSINESS CLASSIFICATIONS
# ============================================================

print()
print("========== BUSINESS CLASSIFICATIONS ==========")

classifications = get_business_classifications(
    supplier_id
)

print(
    json.dumps(
        classifications,
        indent=4
    )
)