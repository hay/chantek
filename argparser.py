class ArgumentsParser:
    def __init__(self, params, arguments, method):
        if not isinstance(arguments, dict):
            raise Exception("Command arguments is not a dict")

        self.params = params
        self.arguments = arguments
        self.method = method
        self._parse()

    def _check_required(self, required, key):
        if required == False:
            return

        if required == True and key in self.params:
            return

        if required == True and key not in self.params:
            raise KeyError(f"{key} is required and was not given")

    def _parse(self):
        for key, val in self.arguments.items():
            if isinstance(val, dict):
                if "required" in val:
                    required = val["required"]

                    if isinstance(val["required"], list) and self.method in required:
                        self._check_required(True, key)
                    else:
                        self._check_required(required, key)

                if "type" in val:
                    type_ = val["type"]

                    if key in self.params and not isinstance(self.params[key], type_):
                        raise TypeError(f"'{key}' is not of type '{type_}'")

                if "default" in val and key not in self.params:
                    self.params[key] = val["required"]

            else:
                if key not in self.params:
                    self.params[key] = val

    def get_params(self):
        return self.params