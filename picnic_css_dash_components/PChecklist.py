# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class PChecklist(Component):
    """A PChecklist component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks
- options (list; optional): An array of options
- label (string; required): A label that will be printed when this component is rendered.
- values (list; optional): The currently selected value
- className (string; optional): The class of the container (div)
- style (dict; optional): The style of the container (div)
- inputStyle (dict; optional): The style of the <input> checkbox element
- inputClassName (string; optional): The class of the <input> checkbox element
- labelStyle (dict; optional): The style of the <label> that wraps the checkbox input
 and the option's label
- labelClassName (string; optional): The class of the <label> that wraps the checkbox input
 and the option's label

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, options=Component.UNDEFINED, label=Component.REQUIRED, values=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, inputStyle=Component.UNDEFINED, inputClassName=Component.UNDEFINED, labelStyle=Component.UNDEFINED, labelClassName=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'options', 'label', 'values', 'className', 'style', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName']
        self._type = 'PChecklist'
        self._namespace = 'picnic_css_dash_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'options', 'label', 'values', 'className', 'style', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['label']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(PChecklist, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('PChecklist(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'PChecklist(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
