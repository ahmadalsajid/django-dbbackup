from __future__ import unicode_literals

from io import BytesIO

from django.test import TestCase
from mock import mock_open, patch

from dbbackup.db.sqlite import SqliteConnector, SqliteCPConnector
from dbbackup.tests.testapp.models import CharModel, TextModel


class SqliteConnectorTest(TestCase):
    def test_write_dump(self):
        dump_file = BytesIO()
        connector = SqliteConnector()
        connector._write_dump(dump_file)
        dump_file.seek(0)
        for line in dump_file:
            self.assertTrue(line.strip().endswith(b';'))

    def test_create_dump(self):
        connector = SqliteConnector()
        dump = connector.create_dump()
        self.assertTrue(dump.read())

    def test_create_dump_with_unicode(self):
        CharModel.objects.create(field='\xe9')
        connector = SqliteConnector()
        dump = connector.create_dump()
        self.assertTrue(dump.read())

    def test_create_dump_with_newline(self):
        TextModel.objects.create(field=f'INSERT ({"foo" * 5000}\nbar\n WHERE \nbaz IS\n "great" );\n')
        connector = SqliteConnector()
        dump = connector.create_dump()
        self.assertTrue(dump.read())

    def test_restore_dump(self):
        connector = SqliteConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)


@patch('dbbackup.db.sqlite.open', mock_open(read_data=b'foo'), create=True)
class SqliteCPConnectorTest(TestCase):
    def test_create_dump(self):
        connector = SqliteCPConnector()
        dump = connector.create_dump()
        dump_content = dump.read()
        self.assertTrue(dump_content)
        self.assertEqual(dump_content, b'foo')

    def test_restore_dump(self):
        connector = SqliteCPConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
