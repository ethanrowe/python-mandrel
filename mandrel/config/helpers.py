from .. import util

def configurable_class(setting_name, default_class_name=None):
    def getter(self):
        value = None
        try:
            value = self.configuration_get(setting_name)
        except KeyError:
            pass

        if not value:
            if not default_class_name:
                return None
            value = default_class_name

        return util.get_by_fqn(value)

    def setter(self, value):
        if value is not None:
            return self.configuration_set(setting_name, util.class_to_fqn(value))
        return self.configuration_set(setting_name, None)

    return property(getter, setter)

