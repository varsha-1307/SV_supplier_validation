import json

from oracle_supplier_api import (
    get_supplier_by_id,
    get_supplier_addresses,
    get_supplier_contacts,
    get_supplier_products_and_services,
    get_business_classifications,
)

from oracle_form_data import (
    build_oracle_form_data,
)


supplier_id = "300000326287336"


supplier = get_supplier_by_id(
    supplier_id
)

addresses = get_supplier_addresses(
    supplier_id
)

contacts = get_supplier_contacts(
    supplier_id
)

products_and_services = (
    get_supplier_products_and_services(
        supplier_id
    )
)

business_classifications = (
    get_business_classifications(
        supplier_id
    )
)


form_data = build_oracle_form_data(
    supplier=supplier,
    addresses=addresses,
    contacts=contacts,
    business_classifications=business_classifications,
    products_and_services=products_and_services,
)


print(
    json.dumps(
        form_data,
        indent=4
    )
)
