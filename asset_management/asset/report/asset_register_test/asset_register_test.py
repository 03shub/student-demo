import frappe
from frappe.utils import today


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Asset",
            "fieldname": "asset",
            "fieldtype": "Link",
            "options": "Asset",
            "width": 140
        },
        {
            "label": "Asset Name",
            "fieldname": "asset_name",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Asset Category",
            "fieldname": "asset_category",
            "fieldtype": "Link",
            "options": "Asset Category",
            "width": 150
        },
        {
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 180
        },
        {
            "label": "Location",
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Purchase Date",
            "fieldname": "purchase_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Available For Use",
            "fieldname": "available_for_use_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "Gross Purchase Amount",
            "fieldname": "gross_purchase_amount",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Opening Accumulated Depreciation",
            "fieldname": "opening_accumulated_depreciation",
            "fieldtype": "Currency",
            "width": 170
        },
        {
            "label": "Accumulated Depreciation",
            "fieldname": "accumulated_depreciation",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Net Book Value",
            "fieldname": "net_book_value",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 140
        },
        {
            "label": "Purchase Invoice",
            "fieldname": "purchase_invoice",
            "fieldtype": "Data",
            "width": 140
        }
    ]


def get_data(filters):

    conditions = [
        "a.docstatus < 2"
    ]

    values = {}

    if filters.get("company"):
        conditions.append("a.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("asset_category"):
        conditions.append(
            "a.asset_category = %(asset_category)s"
        )
        values["asset_category"] = filters["asset_category"]

    if filters.get("status"):
        conditions.append(
            "a.status = %(status)s"
        )
        values["status"] = filters["status"]

    if filters.get("from_date"):
        conditions.append(
            "a.purchase_date >= %(from_date)s"
        )
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append(
            "a.purchase_date <= %(to_date)s"
        )
        values["to_date"] = filters["to_date"]

    where_clause = " AND ".join(conditions)

    assets = frappe.db.sql(
        f"""
        SELECT
            a.name AS asset,
            a.asset_name,
            a.asset_category,
            a.company,
            a.location,
            a.purchase_date,
            a.available_for_use_date,
            a.gross_purchase_amount,
            a.opening_accumulated_depreciation,
            a.status,
            a.supplier,
            a.purchase_invoice

        FROM `tabAsset` a

        WHERE {where_clause}

        ORDER BY
            a.purchase_date,
            a.name
        """,
        values,
        as_dict=True
    )

    result = []

    as_on_date = filters.get("to_date") or today()

    for asset in assets:

        depreciation = frappe.db.sql(
            """
            SELECT
                COALESCE(SUM(ds.depreciation_amount), 0)

            FROM `tabAsset Depreciation Schedule` ads

            INNER JOIN `tabDepreciation Schedule` ds
                ON ds.parent = ads.name

            WHERE
                ads.asset = %s
                AND ads.docstatus = 1
                AND ds.schedule_date <= %s
            """,
            (
                asset.asset,
                as_on_date
            )
        )[0][0] or 0

        opening_depreciation = (
            asset.opening_accumulated_depreciation or 0
        )

        total_accumulated_depreciation = (
            opening_depreciation + depreciation
        )

        gross_amount = (
            asset.gross_purchase_amount or 0
        )

        net_book_value = (
            gross_amount
            - total_accumulated_depreciation
        )

        result.append({
            "asset": asset.asset,
            "asset_name": asset.asset_name,
            "asset_category": asset.asset_category,
            "company": asset.company,
            "location": asset.location,
            "purchase_date": asset.purchase_date,
            "available_for_use_date":
                asset.available_for_use_date,

            "gross_purchase_amount":
                gross_amount,

            "opening_accumulated_depreciation":
                opening_depreciation,

            "accumulated_depreciation":
                total_accumulated_depreciation,

            "net_book_value":
                net_book_value,

            "status": asset.status,
            "supplier": asset.supplier,
            "purchase_invoice": asset.purchase_invoice
        })

    return result