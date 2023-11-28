from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleParserError

DOCUMENTATION = r'''
    name: custom
    plugin_type: inventory
    short_description: Showcase dynamic creation of inventory
    description: Cool plugin
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['custom']
      group:
        description: Groups to add
        required: false
'''

class InventoryModule(BaseInventoryPlugin):

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.plugin = None
        self.group = None

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            group = self.get_option('group')
        except KeyError as kerr:
            raise AnsibleParserError(f'Missing required option on the configuration file: {path}', kerr)

        self.inventory.hosts.clear()

        inventory_data = {
            'all': {
                'hosts': ['host1', 'host2'],
                'vars': {
                    'ansible_user': 'user',
                    'ansible_ssh_private_key_file': '/path/to/private/key',
                }
            },
            '_meta': {
                'hostvars': {
                    'host1': {
                        'ansible_host': '192.168.1.1',
                    },
                    'host2': {
                        'ansible_host': '192.168.1.2',
                    }
                }
            }
        }

        if group != 'all':
            for host, hostvars in inventory_data['_meta']['hostvars'].items():
                inventory.add_host(host)
                inventory.set_variable(host, 'vars', hostvars)
                inventory.add_group(group)
                inventory.add_child(group, host)  # Add host to the specified group

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('custom_config.yaml', 'custom_config.yml')):
                valid = True
            else:
                self.display.vvv('Invalid or missing configuration file for inventory plugin')
        return valid
