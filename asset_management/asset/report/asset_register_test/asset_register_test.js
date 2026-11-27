frappe.query_reports["Asset Register Test"] = {

    "filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company"
        },

        {
            "fieldname": "asset_category",
            "label": "Asset Category",
            "fieldtype": "Link",
            "options": "Asset Category"
        },

        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": [
                "",
                "Draft",
                "Submitted",
                "Partially Depreciated",
                "Fully Depreciated",
                "Sold",
                "Scrapped"
            ]
        },

        {
            "fieldname": "from_date",
            "label": "Purchase From Date",
            "fieldtype": "Date"
        },

        {
            "fieldname": "to_date",
            "label": "As On Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        }
    ],

    "onload": function(report) {

        report.page.add_inner_button(
            __("Refresh"),
            function() {
                report.refresh();
            }
        );

    }
};