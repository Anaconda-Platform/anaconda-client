# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring

from __future__ import unicode_literals

import datetime
import json
import unittest
from unittest.mock import patch

from binstar_client import errors
from binstar_client.scripts.cli import main
from tests.fixture import CLITestCase
from tests.urlmock import urlpatch
from tests.utils.utils import data_dir


class Test(CLITestCase):
    @urlpatch
    def test_upload_bad_package(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/package/eggs/foo', content='{}', status=404)
        content = {'package_types': ['conda']}
        registry.register(method='POST', path='/package/eggs/foo', content=content, status=200)
        registry.register(method='GET', path='/release/eggs/foo/0.1', content='{}')
        registry.register(method='GET', path='/dist/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=404, content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', content=content)

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/commit/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=200, content={})
        main(['--show-traceback', 'upload', data_dir('foo-0.1-0.tar.bz2')], exit_=False)

        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_bad_package_no_register(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/package/eggs/foo', status=404)

        with self.assertRaises(errors.UserError):
            main(['--show-traceback', 'upload', '--no-register', data_dir('foo-0.1-0.tar.bz2')], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    def test_upload_conda(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['conda']}
        registry.register(method='GET', path='/package/eggs/foo', content=content)
        registry.register(method='GET', path='/release/eggs/foo/0.1', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/commit/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=200, content={})

        main(['--show-traceback', 'upload', data_dir('foo-0.1-0.tar.bz2')], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_conda_v2(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['conda']}
        registry.register(method='GET', path='/package/eggs/mock', content=content)
        registry.register(method='GET', path='/release/eggs/mock/2.0.0', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/mock/2.0.0/osx-64/mock-2.0.0-py37_1000.conda', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(
            method='POST', path='/commit/eggs/mock/2.0.0/osx-64/mock-2.0.0-py37_1000.conda', status=200, content={},
        )

        main(['--show-traceback', 'upload', data_dir('mock-2.0.0-py37_1000.conda')], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_use_pkg_metadata(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['conda']}
        registry.register(method='GET', path='/package/eggs/mock', content=content)
        registry.register(method='GET', path='/release/eggs/mock/2.0.0', content='{}')
        registry.register(method='PATCH', path='/release/eggs/mock/2.0.0', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/mock/2.0.0/osx-64/mock-2.0.0-py37_1000.conda', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(
            method='POST', path='/commit/eggs/mock/2.0.0/osx-64/mock-2.0.0-py37_1000.conda', status=200, content={},
        )

        main([
            '--show-traceback', 'upload', '--force-metadata-update', data_dir('mock-2.0.0-py37_1000.conda'),
        ], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_pypi(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['pypi']}
        registry.register(method='GET', path='/package/eggs/test-package34', content=content)
        registry.register(method='GET', path='/release/eggs/test-package34/0.3.1', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/test-package34/0.3.1/test_package34-0.3.1.tar.gz', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(
            method='POST', path='/commit/eggs/test-package34/0.3.1/test_package34-0.3.1.tar.gz', status=200, content={},
        )

        main(['--show-traceback', 'upload', data_dir('test_package34-0.3.1.tar.gz')], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_pypi_with_conda_package_name_allowed(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['pypi']}
        registry.register(method='GET', path='/package/eggs/test_package34', content=content)
        registry.register(method='GET', path='/release/eggs/test_package34/0.3.1', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/test_package34/0.3.1/test_package34-0.3.1.tar.gz', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(
            method='POST', path='/commit/eggs/test_package34/0.3.1/test_package34-0.3.1.tar.gz', status=200, content={},
        )

        # Pass -o to override the channel/package pypi package should go to
        main([
            '--show-traceback', 'upload', '--package', 'test_package34', '--package-type', 'pypi',
            data_dir('test_package34-0.3.1.tar.gz'),
        ], exit_=False)
        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_conda_package_with_name_override_fails(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')

        # Passing -o for `file` package_type doesn't override channel
        with self.assertRaises(errors.BinstarError):
            main([
                '--show-traceback', 'upload', '--package', 'test_package', '--package-type', 'file',
                data_dir('test_package34-0.3.1.tar.gz'),
            ], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    def test_upload_pypi_with_random_name(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')

        with self.assertRaises(errors.BinstarError):
            main([
                '--show-traceback', 'upload', '--package', 'alpha_omega', data_dir('test_package34-0.3.1.tar.gz'),
            ], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    def test_upload_file(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['file']}
        registry.register(method='GET', path='/package/eggs/test-package34', content=content)
        registry.register(method='GET', path='/release/eggs/test-package34/0.3.1', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/test-package34/0.3.1/test_package34-0.3.1.tar.gz', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(
            method='POST', path='/commit/eggs/test-package34/0.3.1/test_package34-0.3.1.tar.gz', status=200, content={},
        )

        main([
            '--show-traceback', 'upload', '--package-type', 'file', '--package', 'test-package34', '--version', '0.3.1',
            data_dir('test_package34-0.3.1.tar.gz'),
        ], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_project(self, registry):
        # there's redundant work between anaconda-client which
        # checks auth and anaconda-project also checks auth;
        # -project has no way to know it was already checked :-/
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user/eggs', content='{"login": "eggs"}')
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/apps/eggs/projects/dog', content='{}')
        stage_content = '{"post_url":"http://s3url.com/s3_url", "form_data":{"foo":"bar"}, "dist_id":"dist42"}'
        registry.register(method='POST', path='/apps/eggs/projects/dog/stage', content=stage_content)
        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/apps/eggs/projects/dog/commit/dist42', content='{}')

        main(['--show-traceback', 'upload', '--package-type', 'project', data_dir('bar')], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    def test_upload_notebook_as_project(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user/eggs', content='{"login": "eggs"}')
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/apps/eggs/projects/foo', content='{}')
        stage_content = '{"post_url":"http://s3url.com/s3_url", "form_data":{"foo":"bar"}, "dist_id":"dist42"}'
        registry.register(method='POST', path='/apps/eggs/projects/foo/stage', content=stage_content)
        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/apps/eggs/projects/foo/commit/dist42', content='{}')

        main(['--show-traceback', 'upload', '--package-type', 'project', data_dir('foo.ipynb')], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    def test_upload_notebook_as_package(self, registry):
        test_datetime = datetime.datetime(2022, 5, 19, 15, 29)
        mock_version = test_datetime.strftime('%Y.%m.%d.%H%M')

        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['ipynb']}
        registry.register(method='GET', path='/package/eggs/foo', content=content)
        registry.register(method='GET', path='/release/eggs/foo/{}'.format(mock_version), content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/foo/{}/foo.ipynb'.format(mock_version), content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(
            method='POST', path='/commit/eggs/foo/{}/foo.ipynb'.format(mock_version), status=200, content={},
        )

        with patch('binstar_client.inspect_package.ipynb.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_datetime
            main(['--show-traceback', 'upload', data_dir('foo.ipynb')], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_project_specifying_user(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user/alice', content='{"login": "alice"}')
        registry.register(method='GET', path='/apps/alice/projects/dog', content='{}')
        stage_content = '{"post_url":"http://s3url.com/s3_url", "form_data":{"foo":"bar"}, "dist_id":"dist42"}'
        registry.register(method='POST', path='/apps/alice/projects/dog/stage', content=stage_content)
        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/apps/alice/projects/dog/commit/dist42', content='{}')

        main([
            '--show-traceback', 'upload', '--package-type', 'project', '--user', 'alice', data_dir('bar'),
        ], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    def test_upload_project_specifying_token(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(
            method='GET', path='/user/eggs', content='{"login": "eggs"}',
            expected_headers={'Authorization': 'token abcdefg'},
        )
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/apps/eggs/projects/dog', content='{}')
        stage_content = '{"post_url":"http://s3url.com/s3_url", "form_data":{"foo":"bar"}, "dist_id":"dist42"}'
        registry.register(method='POST', path='/apps/eggs/projects/dog/stage', content=stage_content)
        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/apps/eggs/projects/dog/commit/dist42', content='{}')

        main([
            '--show-traceback', '--token', 'abcdefg', 'upload', '--package-type', 'project', data_dir('bar'),
        ], exit_=False)

        registry.assertAllCalled()

    @urlpatch
    @patch('binstar_client.commands.upload.bool_input')
    def test_upload_interactive_no_overwrite(self, registry, bool_input):
        # regression test for #364
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['conda']}
        registry.register(method='GET', path='/package/eggs/foo', content=content)
        registry.register(method='GET', path='/release/eggs/foo/0.1', content='{}')
        query_001 = registry.register(method='POST', path='/stage/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=409)

        bool_input.return_value = False  # do not overwrite package

        main(['--show-traceback', 'upload', '-i', data_dir('foo-0.1-0.tar.bz2')], False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(query_001.req.body).get('sha256'))

    @urlpatch
    @patch('binstar_client.commands.upload.bool_input')
    def test_upload_interactive_overwrite(self, registry, bool_input):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        content = {'package_types': ['conda']}
        registry.register(method='GET', path='/package/eggs/foo', content=content)
        registry.register(method='GET', path='/release/eggs/foo/0.1', content='{}')
        query_001 = registry.register(method='POST', path='/stage/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=409)
        query_002 = None

        def allow_upload():
            nonlocal query_002
            query_002 = registry.register(
                method='POST', path='/stage/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2',
                content={'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'},
            )
            registry.register(method='POST', path='/s3_url', status=201)
            registry.register(
                method='POST', path='/commit/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=200, content={},
            )

        registry.register(
            method='DELETE', path='/dist/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', content='{}',
            side_effect=allow_upload,
        )

        bool_input.return_value = True

        main(['--show-traceback', 'upload', '-i', data_dir('foo-0.1-0.tar.bz2')], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(query_001.req.body).get('sha256'))
        self.assertIsNotNone(query_002)
        self.assertIsNotNone(json.loads(query_002.req.body).get('sha256'))

    @urlpatch
    def test_upload_private_package(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/package/eggs/foo', content='{}', status=404)
        content = {'package_types': ['conda']}
        registry.register(method='POST', path='/package/eggs/foo', content=content, status=200)
        registry.register(method='GET', path='/release/eggs/foo/0.1', content='{}')

        content = {'post_url': 'http://s3url.com/s3_url', 'form_data': {}, 'dist_id': 'dist_id'}
        staging_response = registry.register(
            method='POST', path='/stage/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', content=content,
        )

        registry.register(method='POST', path='/s3_url', status=201)
        registry.register(method='POST', path='/commit/eggs/foo/0.1/osx-64/foo-0.1-0.tar.bz2', status=200, content={})

        main(['--show-traceback', 'upload', '--private', data_dir('foo-0.1-0.tar.bz2')], exit_=False)

        registry.assertAllCalled()
        self.assertIsNotNone(json.loads(staging_response.req.body).get('sha256'))

    @urlpatch
    def test_upload_private_package_not_allowed(self, registry):
        registry.register(method='HEAD', path='/', status=200)
        registry.register(method='GET', path='/user', content='{"login": "eggs"}')
        registry.register(method='GET', path='/package/eggs/foo', content='{}', status=404)
        registry.register(
            method='POST', path='/package/eggs/foo', content='{"error": "You can not create a private package."}',
            status=400,
        )

        with self.assertRaises(errors.BinstarError):
            main(['--show-traceback', 'upload', '--private', data_dir('foo-0.1-0.tar.bz2')], exit_=False)


if __name__ == '__main__':
    unittest.main()
