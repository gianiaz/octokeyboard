"""
Import di config parser
"""
from configparser import ConfigParser


class Config(ConfigParser):
    """
    Classe di configurazione con basilare validazione
    """

    def __init__(self, config_file):
        super(Config, self).__init__()
        self.read(config_file)
        self.validate_config()

    def validate_config(self):
        """
        metodo per la validazione
        """
        required_values = {
            'OCTOPRINT': {
                'apikey': None,
            },
            'PRINTER': {
                'bed_temperature': None,
                'nozzle_temperature': None,
                'poweron_script': None,
                'poweroff_script': None,
            }
        }
        """
        Notice the different mode validations for global mode setting: we can
        enforce different value sets for different sections
        """

        for section, keys in required_values.items():
            if section not in self:
                raise Exception(
                    'Missing section %s in the config file' % section)

            for key, values in keys.items():
                if key not in self[section] or self[section][key] == '':
                    raise Exception((
                        'Missing value for %s under section %s in ' +
                        'the config file') % (key, section))

                if values:
                    if self[section][key] not in values:
                        raise Exception((
                            'Invalid value for %s under section %s in ' +
                            'the config file') % (key, section))
