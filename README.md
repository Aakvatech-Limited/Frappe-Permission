# Permissions Processing Code

This is a simple Python code that manages permissions associated with a document in Frappe framework. It is released under the [MIT License](LICENSE).

## Features

The code provides the following features:

- **Process permissions**: The code defines a function `process_permissions` that is called when a document is saved or deleted. This function is responsible for managing the permissions associated with the document.

- **Field metadata**: The code uses the `meta` property of the document to retrieve the fields of type `Table MultiSelect` with the options set to `Permission Detail`. This metadata is used to retrieve the existing permissions associated with the document.

- **Permissions map**: The code creates a map of existing permissions associated with the document using the `permissions_map` dictionary. This map is used to create new permission records if they do not exist.

- **Get existing permissions**: The code retrieves existing permission records associated with the document using the `frappe.get_all` function.

- **Create new permission records**: The code creates new permission records using the `add_permission_record` function. This function takes in several parameters such as the reference doctype, reference docname, row id, doctype name, and docname.

- **Delete permission records**: The code deletes permission records associated with the document using the `frappe.delete_doc` function.

- **Ignore permissions**: The code uses the `ignore_permissions=True` parameter while creating and deleting permission records. This parameter allows the code to bypass permission checks while performing these operations.

## Usage

To use this code, you can copy the `permissions.py` file to your Frappe application and include the following line in your document's Python file:

```python
from myapp.my_module.permissions import process_permissions
```

You can then call the `process_permissions` function from within your document's `on_update` and `on_trash` methods.

```python
def on_update(self):
    process_permissions(self, "on_update")

def on_trash(self):
    process_permissions(self, "on_trash")
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue if you find a bug or would like to request a new feature.

## License

This code is released under the [MIT License](LICENSE). Feel free to use it in your own projects.
