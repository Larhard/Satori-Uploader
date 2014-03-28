import mimetools
import mimetypes
import itertools


class MultiPartForm:
    def __init__(self):
        self.fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()

    def get_content_type(self):
        return 'multipart/form-data; boundary={}'.format(self.boundary)

    def add_field(self, name, value):
        self.fields.append((name, value))

    def add_file(self, field_name, file_name, file_handle, mimetype=None):
        data = file_handle.read()
        mimetype = mimetype or mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        self.files.append((field_name, file_name, mimetype, data))

    def get_content(self):
        parts = []
        part_boundary = '--' + self.boundary
        parts.extend([
            part_boundary,
            'Content-Disposition: form-data; name="{}"'.format(name),
            '',
            value,
        ] for name, value in self.fields)

        parts.extend([
            part_boundary,
            'Content-Disposition: file; name="{}"; filename="{}"'.format(field_name, file_name),
            'Content-Type: {}'.format(content_type),
            '',
            data,
        ] for field_name, file_name, content_type, data in self.files)

        flat = list(itertools.chain(*parts))
        flat.append('--{}--'.format(self.boundary))
        return '\r\n'.join(flat)
