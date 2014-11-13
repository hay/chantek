class Command:
    def __init__(self, **kwargs):
        self.lasterror = False
        self.params = []
        self.settings = {}
        self.args = kwargs["args"]

    def add_param(self, paramName, **kwargs):
        param = {
            "name" : paramName
        }

        if 'default' in kwargs:
            param['default'] = kwargs['default']

        if 'options' in kwargs:
            param['options'] = kwargs['options']

        self.params.append( param )

    def get_error(self):
        return { "error" : self.lasterror }

    def get_params(self):
        params = {}

        for param in self.params:
            name = param['name']

            if 'default' in param and name not in self.args:
                params[name] = param['default']
            else:
                params[name] = self.args[name]

        return params

    def has_error(self):
        for param in self.params:
            name = param['name']

            if (name not in self.args) and ('default' not in param):
                self.lasterror = "required parameter " + name + " not given"
                return True

            if 'options' in param and self.args[name] not in param['options']:
                self.lasterror = "given value for parameter " + name + " is not valid"
                return True

        return False

    def setting(self, key, value = None):
        if value:
            self.settings[key] = value
        else:
            return self.settings[key]