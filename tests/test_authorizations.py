# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

from __future__ import unicode_literals

import unittest

from binstar_client.errors import BinstarError
from binstar_client.scripts.cli import main
from tests.fixture import CLITestCase
from tests.urlmock import urlpatch


class Test(CLITestCase):
    @urlpatch
    def test_remove_token_from_org(self, urls):
        remove_token = urls.register(
            method='DELETE',
            path='/authentications/org/orgname/name/tokenname',
            content='{"token": "a-token"}',
            status=201
        )
        main(['--show-traceback', 'auth', '--remove', 'tokenname', '-o', 'orgname'], exit_=False)
        self.assertIn('Removed token tokenname', self.stream.getvalue())

        remove_token.assertCalled()

    @urlpatch
    def test_remove_token(self, urls):
        remove_token = urls.register(
            method='DELETE',
            path='/authentications/name/tokenname',
            content='{"token": "a-token"}',
            status=201
        )
        main(['--show-traceback', 'auth', '--remove', 'tokenname'], exit_=False)
        self.assertIn('Removed token tokenname', self.stream.getvalue())

        remove_token.assertCalled()

    @urlpatch
    def test_remove_token_forbidden(self, urls):
        remove_token = urls.register(
            method='DELETE',
            path='/authentications/org/wrong_org/name/tokenname',
            content='{"token": "a-token"}',
            status=403
        )
        with self.assertRaises(BinstarError):
            main(['--show-traceback', 'auth', '--remove', 'tokenname', '-o', 'wrong_org'], exit_=False)

        remove_token.assertCalled()


if __name__ == '__main__':
    unittest.main()
