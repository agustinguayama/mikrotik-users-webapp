import csv
import ssl
import sys
import time
import librouteros
from librouteros.query import Key
import json
# import pdb
#pdb.set_trace()

# Admin user importing

# with open('config.json') as config_file:
#     data = json.load(config_file)
# mk_admin_user = data['admin_user']
# mk_admin_pw = data['admin_pw']
timestr = time.strftime("%Y%m%d-%H%M%S")
report = {}

# Username and password wich is going to be created, or whose password is going to be updated
# TODO: work on username and password input for standalone instances
# username = 'hh4444444'
# userpass = '344444433'


def all_devices(input_username=None,input_password=None):
    conf = get_conf()
    routers_count = sum(1 for router in conf['input_file'])
    device_ord = 0
    report = {}
    all_devices.status = "Initial state"
    for line in conf['input_file']:
        device_ord = + 1
        ipmk = line.get("Addresses")
        namemk = line.get("Name")
        all_devices.status = "Procesing device " + str(device_ord) + " of " + str(routers_count)
        if __name__ == "__main__": # If runs as standalone, you get real time report of what's being procesed
            aux_my_print('Procesando equipo:\t\t\t' + namemk + '\n')
        router = Device(ipmk, namemk, input_username, input_password)
        router.createuse()
        if "error" in router.status:
            all_devices.report[namemk] = router.status


def get_conf(): # look for config in config file
    conf_dict = {}
    with open('config.json') as config_file:
        data = json.load(config_file)
    conf_dict['mk_admin_user'] = data['admin_user']
    conf_dict['mk_admin_pw'] = data['admin_pw']

    if __name__ == "__main__":  # If runs as standalone, ask for args
        lista_equipos = args_parser()
    else:
        lista_equipos = data['devices-file']
    conf_dict['input_file'] = csv.DictReader(open(lista_equipos))
    return conf_dict


class Device:
    def __init__(self, ip, device_name, input_username,input_password):
        if not input_password: #if the password comes empty
            return
        self.device_name = device_name
        self.ip = ip
        self.input_username = input_username
        self.input_password = input_password
        self.status = "Initiating"

    def connect(self):
        conf = get_conf()
        try:
            ssl_layer = ssl.create_default_context()
            ssl_layer.check_hostname = False
            ssl_layer.set_ciphers('ADH:@SECLEVEL=0')
            mkapi = librouteros.connect(
                username = conf['mk_admin_user'],
                password = conf['mk_admin_pw'],
                host=self.ip,
                ssl_wrapper=ssl_layer.wrap_socket,
                port=8729
            )
        except Exception as err:
            print('Problem connecting to ' + self.device_name + '. Error was: ' + str(err))
            self.status = "Connection error"
            return err
        self.status = "Connection completed"
        return

    def createuser(self):
        try:
            device = self.connect()
            create_params = {
                'name': self.input_username,
                'password': self.input_password,
                'group': 'full' #TODO: manage group configuration
            }
            users = device.path('/user')
            mkusername = Key('name')
            item_id = Key('.id')
            user_exists = False
            # TODO: create function to get .id me clearly
            for row in users.select(item_id, mkusername):
                if self.input_username == row['name']:
                    user_exists = True
                    update_params = {'password': self.input_password, '.id': row['.id']}
                    users.update(**update_params)
                    print('Password updated: ' + row['name'] + ' with pass: ' + self.input_password + ' in device: ' + self.device_name)

            if user_exists is False:
                device.path('/user').add(**create_params)
                print('User ' + self.input_username + ' created with password ' + self.input_password + ' in device: ' + self.device_name)

        except Exception as err:
            self.status = "CreateUser error"
            print('Problem with ' + self.device_name + '. Error msj: ' + str(err))
            return err
        self.status = "CreateUser completed"
        return

def args_parser():
    if len(sys.argv) == 1:
        print('Use \'-in filename.csv\' for data...')
        sys.exit()
    elif (sys.argv[1]).lower() == '-in':
        lista_equipos = sys.argv[2]
        return lista_equipos
    else:
        print('Parameters problem')
        sys.exit()

def aux_my_print(text):
    sys.stdout.write((str(text))+'                          \r')
    sys.stdout.flush()


if __name__ == "__main__":
    all_devices()

