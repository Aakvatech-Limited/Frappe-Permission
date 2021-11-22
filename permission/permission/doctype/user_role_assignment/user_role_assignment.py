# Copyright (c) 2021, Totrox Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class UserRoleAssignment(Document):
    def validate(self):
        pass

    def on_submit(self):
        self.validate_role()
        self.create_permissions()

    def on_cancel(self):
        self.remove_permissions()

    def validate_role(self):
        user_assignments_list = frappe.get_all(
            "User Role Assignment",
            filters={"user": self.user, "docstatus": 1, "name": ["!=", self.name]},
            fields=["name", "role"],
        )
        for assignment in user_assignments_list:
            if frappe.db.exists("Role Level Policy", assignment.role):
                overlappable = frappe.get_value(
                    "Role Level Policy", assignment.role, "overlappable"
                )
                if not overlappable:
                    frappe.throw(
                        _("This User can't have more than one User Role Assignment")
                    )
        if frappe.db.exists("Role Level Policy", self.role):
            policy = frappe.get_doc("Role Level Policy", self.role)
            if policy.number_of_actors and int(policy.number_of_actors) > 0:
                role_assignments_list = frappe.get_all(
                    "User Role Assignment",
                    filters={
                        "role": self.role,
                        "territory": self.territory,
                        "docstatus": 1,
                    },
                )
                if len(role_assignments_list) > int(policy.number_of_actors):
                    frappe.throw(
                        _("Role {0} allowed only for {1} user(s)").format(
                            self.role, policy.number_of_actors
                        )
                    )

            if not policy.overlappable:
                if len(user_assignments_list) > 0:
                    frappe.throw(
                        _("This User can't have more than one User Role Assignment")
                    )
            permissions_dict = {}
            if policy.kyosk_territory_type:
                permissions_dict.setdefault(
                    "Kyosk Territory Type", [policy.kyosk_territory_type]
                )
            for row in policy.role_permission_profile_detail:
                permissions_dict.setdefault(row.doctype_name, [])
                if row.docname not in permissions_dict[row.doctype_name]:
                    permissions_dict[row.doctype_name].append(row.docname)
            perm_list = []
            if self.territory:
                perm_list.append(
                    frappe._dict(
                        {"doctype_name": "Territory", "docname": self.territory}
                    )
                )
            perm_list.extend(self.role_permission_profile_detail)
            if len(perm_list) == 0:
                return
            for perm in perm_list:
                doc = frappe.get_doc(perm.doctype_name, perm.docname)
                for key, value in permissions_dict.items():
                    fields = doc.meta.get(
                        "fields", {"fieldtype": "Link", "options": key}
                    )
                    if len(fields) > 0:
                        for field in fields:
                            field_value = doc.get(field.fieldname)
                            if field_value not in value:
                                frappe.throw(
                                    _(
                                        "The {doctype_name}: {docname} is only allowed for {key}: {value}"
                                    ).format(
                                        doctype_name=perm.doctype_name,
                                        docname=perm.docname,
                                        key=key,
                                        value=str(value),
                                    )
                                )

    def create_permissions(self):
        if self.role:
            self.add_permission_record(role=self.role)
        if self.territory:
            self.add_permission_record(doctype_name="Territory", docname=self.territory)
        if self.company:
            self.add_permission_record(doctype_name="Company", docname=self.company)

        if len(self.role_permission_profile_detail) > 0:
            for row in self.role_permission_profile_detail:
                self.add_permission_record(
                    doctype_name=row.doctype_name, docname=row.docname
                )

        profiles_list = frappe.get_all(
            "Role Permission Profile",
            filters={"docstatus": 1, "role": self.role},
            limit=1,
        )
        if len(profiles_list) > 0:
            profile = frappe.get_doc("Role Permission Profile", profiles_list[0].name)
            for row in profile.role_permission_profile_detail:
                self.add_permission_record(
                    doctype_name=row.doctype_name, docname=row.docname
                )

    def remove_permissions(self):
        to_remove = frappe.get_all(
            "Permission Record",
            filters={"ref_doctype": "User Role Assignment", "ref_docname": self.name},
        )
        for rec in to_remove:
            frappe.delete_doc(
                "Permission Record", rec.name, force=1, ignore_permissions=True
            )

    def add_permission_record(self, role=None, doctype_name=None, docname=None):
        record_doc = frappe.new_doc("Permission Record")
        record_doc.user = self.user
        record_doc.ref_doctype = self.doctype
        record_doc.ref_docname = self.name
        record_doc.doctype_name = doctype_name
        record_doc.docname = docname
        record_doc.permission = 1 if docname else 0
        record_doc.role = 1 if role else 0
        record_doc.role_name = role
        record_doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_filterd_territorys(doctype, txt, searchfield, start, page_len, filters):
    data = []
    cust_filters = {}
    if txt:
        cust_filters["name"] = ["like", f"%{txt}%"]
    if filters.get("role") and frappe.db.exists(
        "Role Level Policy", filters.get("role")
    ):
        cust_filters["territory_type"] = frappe.get_value(
            "Role Level Policy", filters.get("role"), "kyosk_territory_type"
        )
    data = frappe.get_list(
        "Territory",
        filters=cust_filters,
        fields=["name", "territory_type"],
        page_length=page_len,
        start=start,
        as_list=True,
    )

    return data
