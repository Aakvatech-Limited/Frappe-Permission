# Copyright (c) 2021, Totrox Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class RolePermissionProfile(Document):
    def validate(self):
        profiles_list = frappe.get_all(
            "Role Permission Profile",
            filters={"docstatus": 1, "role": self.role},
        )
        if len(profiles_list) > 0:
            frappe.throw(_("Not allowed to have more one profile for the same role"))

    def on_submit(self):
        self.create_permissions()

    def on_cancel(self):
        self.remove_permissions()

    def remove_permissions(self):
        permission_assignment_list = frappe.get_all(
            "User Role Assignment",
            filters={"role": self.role, "docstatus": 1},
            fields=["user", "name"],
        )
        to_remove_list = []
        for assignment in permission_assignment_list:
            for row in self.role_permission_profile_detail:
                to_remove = frappe.get_all(
                    "Permission Record",
                    filters={
                        "ref_doctype": "User Role Assignment",
                        "ref_docname": assignment.name,
                        "doctype_name": row.doctype_name,
                        "docname": row.docname,
                    },
                )
                to_remove_list.extend(to_remove)

        for rec in to_remove_list:
            doc = frappe.get_doc("Permission Record", rec.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc(
                "Permission Record", rec.name, force=1, ignore_permissions=True
            )

    def create_permissions(self):
        permission_assignment_list = frappe.get_all(
            "User Role Assignment",
            filters={"role": self.role, "docstatus": 1},
            fields=["user", "name"],
        )
        for assignment in permission_assignment_list:
            doc = frappe.get_doc("User Role Assignment", assignment)
            if doc:
                doc.create_permissions()
