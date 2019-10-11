import frappe

EVENT_MAP = {
	'before_insert': 'Before Insert',
	'after_insert': 'After Insert',
	'validate': 'Before Save',
	'on_update': 'After Save',
	'before_submit': 'Before Submit',
	'on_submit': 'After Submit',
	'before_cancel': 'Before Cancel',
	'on_cancel': 'After Cancel',
	'on_trash': 'Before Delete',
	'after_delete': 'After Delete',
}

def run_server_script_api(method):
	script_name = get_server_script_map().get('_api', {}).get(method)
	if script_name:
		frappe.get_doc('Server Script', script_name).execute_method()
		return True

def run_server_script_for_doc_event(doc, event):
	if not event in EVENT_MAP:
		return

	if frappe.flags.in_install:
		return

	scripts = get_server_script_map().get(doc.doctype, {}).get(EVENT_MAP[event], None)
	if scripts:
		for script_name in scripts:
			frappe.get_doc('Server Script', script_name).execute_doc(doc)

def get_server_script_map():
	script_map = frappe.cache().get_value('server_script_map')
	if script_map is None:
		script_map = {}
		for script in frappe.get_all('Server Script', ('name', 'reference_doctype', 'doctype_event',
			'api_method', 'script_type')):
			if script.script_type == 'DocType Event':
				script_map.setdefault(script.reference_doctype, {}).setdefault(script.doctype_event, []).append(script.name)
			else:
				script_map.setdefault('_api', {})[script.api_method] = script.name
		frappe.cache().set_value('server_script_map', script_map)

	return script_map
