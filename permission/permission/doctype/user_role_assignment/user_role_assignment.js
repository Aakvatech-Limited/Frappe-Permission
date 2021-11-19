// Copyright (c) 2021, Totrox Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Role Assignment', {
	refresh: function (frm) {
		frm.set_query('territory', function () {
			return {
				query: 'permission.permission.doctype.user_role_assignment.user_role_assignment.get_filterd_territorys',
				filters: { 'role': frm.doc.role }
			};
		});
	}
});
