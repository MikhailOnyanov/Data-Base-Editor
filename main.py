from mydbeditor import *
from db_manager import MyDbManager
from table import Table
import sys


class Connector(Ui_MainWindow):
    def __init__(self, main_window, db_instance):
        super().setupUi(main_window)
        self.label.setText("TestDeletion")

        # Object to work with the model and db
        self.model = db_instance

        # Update table names in table list, like initialization
        self.listWidget.addItems(self.model.get_table_names())

        # Choosing table event
        self.listWidget.itemSelectionChanged.connect(self.on_table_selection_changed)

        # Editing loader event
        self.listWidget.itemSelectionChanged.connect(self.on_table_selection_changed_edit)

        # Delete table button pressed event
        self.delete_table_btn.clicked.connect(self.on_delete_table_button_clicked)

        # Create table button pressed event
        self.create_table_push_button.clicked.connect(self.on_create_table)

        # Add field button pressed event
        self.add_field_btn.clicked.connect(self.on_add_field)

        # Delete field button event
        self.delete_field_btn.clicked.connect(self.on_delete_field)

        # Selecting fields while creating a table -> enable the delete button event
        self.fields_list_create_table.itemSelectionChanged.connect(self.on_field_selection_changed)

        # Edit table name event
        self.update_table_name_btn.clicked.connect(self.on_table_name_changed)

        # Edit table add field event
        self.add_field_btn_4.clicked.connect(self.on_add_field_dynamic)
        # An object that stores info about current table
        self.current_table_creating = Table()

        # An object that stores info about current table
        self.current_table_editing = Table()

    def update_table_list(self):
        #  Update table names in table list
        self.listWidget.clear()
        #  Clearing focus to avoid having non-existing current element
        self.listWidget.clearFocus()
        #  Disable button
        self.delete_table_btn.setDisabled(True)
        try:
            self.listWidget.addItems(self.model.get_table_names())
        except Exception as error:
            print(error)

    def on_add_field(self):
        #  Get field information
        field_title = self.field_title_input.text()
        dtype = self.field_type_combo_box.currentText()

        #  Create an item
        item = QtWidgets.QListWidgetItem(field_title)
        #  Shorter name for fields list
        lst = self.fields_list_create_table
        #  Get titles from fields list
        titles = [lst.item(x).text() for x in range(lst.count())]

        #  Check same name and void
        if field_title.strip() != '' and not (field_title in titles) and not self.line_consists_digit(field_title):
            # Add element to the fields list
            self.fields_list_create_table.addItem(item)
            if self.current_table_creating is None:
                self.current_table_creating = Table()

            # Add field to table instance
            self.current_table_creating.add_field(field_title, dtype)

            # Update PK list
            self.primaryKeyComboBox.addItem(field_title)
        elif self.line_consists_digit(field_title):
            self.popup_error_field("Ошибка", "Поле не добавлено!", "В названии присутствуют цифры!")
        else:
            self.popup_error_field("Ошибка", "Поле не добавлено!", "Такое поле есть, или оно пустое.")

    def on_delete_field(self):
        item = self.fields_list_create_table.currentRow()
        deleted = self.fields_list_create_table.takeItem(item)

        # Delete from table instance
        self.current_table_creating.delete_field(deleted.text())

        # Update PK list
        self.primaryKeyComboBox.removeItem(item)

        self.delete_field_btn.setDisabled(True)
        self.fields_list_create_table.clearFocus()

    def on_create_table(self):
        table = self.current_table_creating
        table.table_name = self.table_name_line.text()

        #  Get titles from tables list
        table_titles = self.model.get_table_names()

        if table.table_name.strip() == '' or table.table_name in table_titles:
            self.show_popup_error_create()
        elif self.line_consists_digit(table.table_name.strip()):
            self.popup_error_field("Ошибка", "Ошибка создания таблицы", "Содержит цифры")
        else:
            table.set_primary_key(self.primaryKeyComboBox.currentText())
            try:
                #  Model method
                q = self.model.create_table(table.table_name, table.convert_fields_model())
                self.res_sql_statement.setText(q)
                #  Clear table object!!!
                self.current_table_creating = Table()
                #  Clearing all fields after creating new table
                self.table_name_line.clear()
                self.primaryKeyComboBox.clear()
                self.field_title_input.clear()
                self.fields_list_create_table.clear()
                #  Disabling "Delete" button
                self.delete_field_btn.setDisabled(True)
                #  Updating tables
                self.update_table_list()
            except Exception as error:
                self.popup_error_field("Ошибка", "Ошибка создания таблицы")

    def show_popup_error_create(self):
        err = QtWidgets.QMessageBox()
        err.setIcon(QtWidgets.QMessageBox.Critical)
        err.setText("Ошибка")
        err.setInformativeText("Имя таблицы существует или имя пустое")
        err.setStandardButtons(QtWidgets.QMessageBox.Ok)
        err.setWindowTitle('Ошибка создания таблицы')
        err.exec_()

    def on_delete_table_button_clicked(self):
        table_name = self.listWidget.currentItem().text()

        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle(f"Удаление таблицы {table_name}")
        warning.setText("Вы точно хотите удалить таблицу?")
        warning.setIcon(QtWidgets.QMessageBox.Warning)
        warning.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        warning.setInformativeText("Действие необратимо")
        #  "Yes" handler
        warning.buttonClicked.connect(self.popup_warning)
        warning.exec_()

    def popup_error_field(self, widget_title, err_text, err_informative_text):
        err = QtWidgets.QMessageBox()
        err.setIcon(QtWidgets.QMessageBox.Critical)
        err.setText(err_text)
        err.setInformativeText(err_informative_text)
        err.setStandardButtons(QtWidgets.QMessageBox.Ok)
        err.setWindowTitle(widget_title)
        err.exec_()

    def popup_warning(self, button: QtWidgets.QPushButton):
        if "Yes" in button.text():
            try:
                query = self.model.delete_table(self.listWidget.currentItem().text())
                #  Nulling edit reference because item is deleted now
                if self.current_table_editing != None:
                    self.current_table_editing = None
                self.update_table_list()
            except Exception as error:
                self.popup_error_field("Ошибка", "Таблица не была удалена", "")
        elif "Cancel" in button.text():
            return

    def on_table_selection_changed_edit(self):
        #  Clearing previous
        self.primaryKeyComboBox_3.clear()
        self.fields_list_create_table_3.clear()
        #  Get current name
        table_name = self.listWidget.currentItem().text()
        self.current_table_editing = Table(table_name)
        try:
            #  Get fields from model. Array of tuples (field_name, datatype)
            m_fields = self.model.get_table_fields(table_name)
            #  Setting up new lines
            self.table_name_line_3.setText(table_name)
            for field in m_fields:
                #  Create an item
                item = QtWidgets.QListWidgetItem(field[0])
                #  Add field to table instance
                self.current_table_editing.add_field(field[0], field[1])
                #  Only text
                self.primaryKeyComboBox_3.addItem(field[0])
                #  Add to list
                self.fields_list_create_table_3.addItem(item)
        except Exception as error:
            print(error)

    def on_table_name_changed(self):
        #  If table isn't in focus, there's not table object
        if self.current_table_editing is not None:
            old_name = self.current_table_editing.table_name.strip()
            new_name = self.table_name_line_3.text().strip()
            if old_name == new_name:
                self.popup_error_field("Ошбика", "Невозможно изменить название таблицы!", "Название то же.")
            elif new_name == "":
                self.popup_error_field("Ошбика", "Невозможно изменить название таблицы!", "Пустое название.")
            elif self.line_consists_digit(new_name):
                self.popup_error_field("Ошбика", "Невозможно изменить название таблицы!", "Содержит цифры.")
            else:
                try:
                    res_query = self.model.update_table_name(old_name, new_name)

                    self.current_table_editing.table_name = new_name
                    self.listWidget.currentItem().setText(new_name)
                    self.res_sql_statement_4.setText(res_query)
                except Exception as error:
                    self.popup_error_field("Ошбика", "Невозможно изменить название таблицы!", "")
                    self.current_table_editing.table_name = old_name
                    self.listWidget.currentItem().setText(old_name)
        else:
            pass

    def on_add_field_dynamic(self):
        #  Get field information
        field_title = self.field_title_input_4.text()
        dtype = self.field_type_combo_box_4.currentText()

        #  Create an item
        item = QtWidgets.QListWidgetItem(field_title)
        #  Shorter name for fields list
        lst = self.fields_list_create_table_3
        #  Get titles from fields list
        titles = [lst.item(x).text() for x in range(lst.count())]

        #  Check same name and void
        if field_title.strip() != '' and not(field_title in titles) and not(self.line_consists_digit(field_title)):
            try:
                res_query = self.model.add_table_column(self.current_table_editing.table_name, field_title, dtype)
                self.res_sql_statement_4.setText(res_query)
                # Add element to the fields list
                self.fields_list_create_table_3.addItem(item)
                # Add field to table instance
                self.current_table_editing.add_field(field_title, dtype)
            except Exception as error:
                self.popup_error_field("Ошибка", "Поле не добавлено", "")
        elif self.line_consists_digit(field_title):
            self.popup_error_field("Ошибка", "В названии присутствуют цифры!", "Поле не добавлено")
        else:
            self.popup_error_field("Ошибка", "Название пустое или уже существует!", "Поле не добавлено")

    #  Unlocks delete table button
    def on_table_selection_changed(self):
        try:
            if not self.delete_table_btn.isEnabled():
                self.delete_table_btn.setEnabled(True)
        except Exception as error:
            print(error)

    #  Unlocks delete field button
    def on_field_selection_changed(self):
        try:
            if not self.delete_field_btn.isEnabled():
                self.delete_field_btn.setEnabled(True)
        except Exception as error:
            print(error)

    #  To check table and field names for numbers
    @staticmethod
    def line_consists_digit(line: str) -> bool:
        for i in filter(str.isdigit, line):
            return True
        return False


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    #  Methods and event subs for model - view actions
    ui = Connector(MainWindow, my_db)

    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    #  False means that the APP connects to
    #  ElephantSQL, all login info is in .env file.
    my_db = MyDbManager(False)
    main()
    my_db.close_connection()
