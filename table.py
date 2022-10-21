class Table:
    def __init__(self, table_name="untitled"):
        self.table_name = table_name
        self.fields = {}
        #  If no PK set None
        self.primary_key = None

    def add_field(self, title, datatype):
        if title in self.fields:
            print("error add_field")
        else:
            self.fields[title] = datatype

    def delete_field(self, field_title):
        if field_title == self.primary_key:
            self.primary_key = None
        self.fields.pop(field_title)

    def set_primary_key(self, field_title):
        if field_title in self.fields:
            self.primary_key = field_title
        else:
            print('error set_primary_key')

    def convert_fields_model(self):
        res = []
        for field in self.fields:
            d = {'name': field, 'datatype': self.fields[field]}
            if field == self.primary_key:
                d['primary_key'] = True
            else:
                d['primary_key'] = False
            res.append(d)
        return tuple(res)
