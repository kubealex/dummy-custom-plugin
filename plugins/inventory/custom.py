from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleParserError
import ipaddress

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
      group_by_ip:
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
            group_by_ip = self.get_option('group_by_ip')
        except KeyError as kerr:
            raise AnsibleParserError(f'Missing required option on the configuration file: {path}', kerr)

        self.inventory.hosts.clear()

        inventory_data = {
            'all': {
                'hosts': ['router1', 'router2', 'router3', 'firewall1', 'firewall2'],
                'vars': {
                    'ansible_user': 'user',
                    'ansible_ssh_private_key_file': '/path/to/private/key',
                }
            },
            '_meta': {
                'hostvars': {
                    'router1': {
                        'ansible_host': '192.168.1.1',
                    },
                    'router2': {
                        'ansible_host': '192.168.1.2',
                    },
                    'router3': {
                        'ansible_host': '192.168.2.3',
                    },
                    'firewall1': {
                        'ansible_host': '192.168.1.1',
                    },
                    'firewall2': {
                        'ansible_host': '192.168.2.2',
                    }
                }
            }
        }


        for host, hostvars in inventory_data['_meta']['hostvars'].items():
            inventory.add_host(host)
            inventory.set_variable(host, 'vars', hostvars)
            if group_by_ip:
                if ipaddress.ip_address(hostvars['ansible_host']) in ipaddress.ip_network('192.168.1.0/24'):
                    inventory.add_group("Group A")
                    inventory.add_child("Group A", host)  # Add host to the specified group
                else:
                    inventory.add_group("Group B")
                    inventory.add_child("Group B", host)  # Add host to the specified group
    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('custom_config.yaml', 'custom_config.yml')):
                valid = True
            else:
                self.display.vvv('Invalid or missing configuration file for inventory plugin')
        return valid
