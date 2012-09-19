from mandrel import util
import optparse
import sys

class AbstractRunner(object):
    def __init__(self):
        parser = self.initialize_parser()
        self.configure_parser(parser)
        self.parser = parser

    @property
    def bootstrapper(self):
        if not hasattr(self, '_bootstrapper'):
            mandrel = __import__('mandrel.bootstrap')
            self._bootstrapper = mandrel.bootstrap
        return self._bootstrapper


    def handle_search_path(self, option, optstr, value, parser):
        self.bootstrapper.SEARCH_PATHS[:] = value.split(':')[:]

    def handle_search_prepend(self, option, optstr, value, parser):
        self.bootstrapper.SEARCH_PATHS.insert(0, value)

    def handle_search_append(self, option, optstr, value, parser):
        self.bootstrapper.SEARCH_PATHS.append(value)

    def handle_lib_prepend(self, option, optstr, value, parser):
        sys.path.insert(0, value)

    def handle_lib_append(self, option, optstr, value, parser):
        sys.path.append(value)

    def handle_log_config(self, option, optstr, value, parser):
        self.bootstrapper.LOGGING_CONFIG_BASENAME = value

    def initialize_parser(cls):
        return optparse.OptionParser()


    def configure_parser(self, parser):
        parser.usage = '%prog [OPTIONS] target [TARGET_OPTIONS]'
        parser.add_option('-s', '--search_path',
                          type='str',
                          action='callback',
                          help="Sets mandrel.bootstrap.SEARCH_PATHS to paths you specify (using ':' as separator)",
                          callback=self.handle_search_path)

        parser.add_option('-p', '--prepend',
                          type='str',
                          action='callback',
                          help="Prepends value to mandrel.bootstrap.SEARCH_PATHS",
                          callback=self.handle_search_prepend)

        parser.add_option('-a', '--append',
                          type='str',
                          action='callback',
                          help="Appends value to mandrel.bootstrap.SEARCH_PATHS",
                          callback=self.handle_search_append)

        parser.add_option('-P', '--prepend_lib',
                          type='str',
                          action='callback',
                          help="Prepends value to sys.path",
                          callback=self.handle_lib_prepend)

        parser.add_option('-A', '--append_lib',
                          type='str',
                          action='callback',
                          help="Appends value to sys.path",
                          callback=self.handle_lib_append)

        parser.add_option('-l', '--log_config',
                          type='str',
                          action='callback',
                          help="Sets mandrel.bootstrap.LOGGING_CONFIG_BASENAME to value.",
                          callback=self.handle_log_config)


    def process_options(self):
        ops, args = self.parser.parse_args()
        return args[0], args[1:]

    def execute(self, target, args):
        raise NotImplementedError

    def run(self):
        target, args = self.process_options()
        self.execute(target, args)

    @classmethod
    def launch(cls):
        cls().run()


class CallableRunner(AbstractRunner):
    def get_callable(self, target):
        return util.get_by_fqn(target)

    def execute(self, target, args):
        runnable = self.get_callable(target)
        return runnable(args)


class ScriptRunner(AbstractRunner):
    def prepare_environment(self, args):
        sys.argv[1:] = args

    def execute_script(self, script):
        glb = globals()
        glb.update(__name__='__main__', __file__=script)
        return execfile(script, glb)

    def execute(self, target, args):
        self.prepare_environment(args)
        return self.execute_script(target)


def launch_callable():
    CallableRunner.launch()

def launch_script():
    ScriptRunner.launch()

