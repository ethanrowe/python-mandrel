import unittest
import mock
import os
from mandrel.test import utils
from mandrel import config

class TestConfigYamlLoader(unittest.TestCase):
    def testLoadOperation(self):
        with utils.tempdir() as dirpath:
            filepath = os.path.join(dirpath, 'some_config')
            contents = "---\nfoo: blargh\nblee:\n - blah\n - blorp\n"
            with open(filepath, 'w') as outfile:
                outfile.write(contents)
            
            with mock.patch('yaml.safe_load') as safe_load:
                def loader(f):
                    safe_load.file_contents = f.read()
                    return safe_load.return_value
                safe_load.side_effect = loader
                result = config.core.read_yaml_path(filepath)
                # yaml.safe_load called once
                self.assertEqual(1, len(safe_load.call_args_list))
                # it's first arg appears to be a reader of our file
                self.assertEqual(contents, safe_load.file_contents)
                # and we got the result back.
                self.assertEqual(result, safe_load.return_value)

