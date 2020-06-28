#!/usr/bin/env python3

import connexion
import openstack
import MySQLdb
import time
import datetime

from threading import Thread, Lock
from swagger_server import encoder


class Sync: # customized boolean wrapper
    def __init__(self):
        self.end = False
        self.lock = Lock()
    def end(self):
        with self.lock:
            if not self.end:
                self.end = True
    def hasEnded(self):
        return self.end

def server(sync):
    # TODO: doesn't remove VMs (throws ConflictException)
    # TODO: threading.py throws exception in line 1388 (lock.acquire())
    # TODO: maybe add also a network for the vm (with the Web UI it's mandatory)
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'My REST API'})
    try:
        app.run(port=8081)
        sync.end()
    except Exception as e:
        print("The answer to life is 42")

def retrieve_configurations():
    mydb = MySQLdb.connect(host="172.17.0.2", user="root", passwd="password", db="openstacksdk")
    mycursor = mydb.cursor()
    sql = "SELECT * FROM configurations;"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mydb.close()
    if (len(myresult) == 0):
        return jsonify({})
    configurations = []
    for conf in myresult:
        jsob = {
            'id' : int(conf[0]),
            'timeStart' : str(conf[1]),
            'timeEnd' : str(conf[2]), 
            'flavor' : conf[3], 
            'image' : conf[4], 
            'numberOfVMs' : int(conf[5])
        }
        configurations.append(jsob)
    return configurations

if __name__ == '__main__':
    syncObject = Sync()
    openstack.enable_logging(debug=True)
    conn = openstack.connect()
    conn.delete_flavor( name_or_id = "standard" )
    conn.delete_flavor( name_or_id = "large" )
    conn.create_flavor(name="standard", ram=64, vcpus=1, disk=1)
    conn.create_flavor(name="large", ram=256, vcpus=2, disk=2)
    Thread(target=server, args=(syncObject, )).start() # daemon=True per renderlo un daemon thread
    activeConfigurations = {} # key: configurationId, value: [nomi dei server restituiti da create_server()]
    while not syncObject.hasEnded():
        currentTime = datetime.datetime.now().time()
        print("ORARIO DEL SISTEMA: " + str(currentTime))
        print("Controllo configurazioni in corso")
        print("CONFIGURAZIONI ATTIVE: " + str(activeConfigurations))
        
        confs = retrieve_configurations()
        print("TUTTE LE CONFS: " + str(confs))
        for conf in confs:
            # timeStart e timeEnd da convertire in ora:minuti %H:%M
            idConf = conf['id']
            timeStart = datetime.datetime.strptime(conf['timeStart'], "%H:%M:%S").time() # HH:MM
            timeEnd = datetime.datetime.strptime(conf['timeEnd'], "%H:%M:%S").time()
            flavor = conf['flavor']
            image = conf['image']
            nVMs = int(conf['numberOfVMs'])
            if currentTime >= timeStart and currentTime <= timeEnd and (not (idConf in activeConfigurations.keys())):
                activeConfigurations[idConf] = []
                for _ in range(nVMs):
                    activeConfigurations[idConf].append(conn.create_server("mortadella_bella", image=image, flavor=flavor))
            elif (currentTime < timeStart or currentTime > timeEnd) and (idConf in activeConfigurations.keys()):
                for server in activeConfigurations[idConf]:
                    conn.delete_server(server)
                del activeConfigurations[idConf]
        print("Attesa...")
        time.sleep(10)
    conn.close()
"""
def create_server(conn):
    print("Create Server:")

    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)
    keypair = create_keypair(conn)

    server = conn.compute.create_server(
        name=SERVER_NAME, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)

    server = conn.compute.wait_for_server(server)

    print("ssh -i {key} root@{ip}".format(
        key=PRIVATE_KEYPAIR_FILE,
        ip=server.access_ipv4))
"""
'''
def delete_server(
            self, name_or_id, wait=False, timeout=180, delete_ips=False,
            delete_ip_retry=1):
        """Delete a server instance.
        :param name_or_id: name or ID of the server to delete
        :param bool wait: If true, waits for server to be deleted.
        :param int timeout: Seconds to wait for server deletion.
        :param bool delete_ips: If true, deletes any floating IPs
            associated with the instance.
        :param int delete_ip_retry: Number of times to retry deleting
            any floating ips, should the first try be unsuccessful.
        :returns: True if delete succeeded, False otherwise if the
            server does not exist.
        :raises: OpenStackCloudException on operation error.
        """
        # If delete_ips is True, we need the server to not be bare.
        server = self.get_server(name_or_id, bare=True)
        if not server:
            return False

        # This portion of the code is intentionally left as a separate
        # private method in order to avoid an unnecessary API call to get
        # a server we already have.
        return self._delete_server(
            server, wait=wait, timeout=timeout, delete_ips=delete_ips,
            delete_ip_retry=delete_ip_retry)

'''
'''
def create_server(
            self, name, image=None, flavor=None,
            auto_ip=True, ips=None, ip_pool=None,
            root_volume=None, terminate_volume=False,
            wait=False, timeout=180, reuse_ips=True,
            network=None, boot_from_volume=False, volume_size='50',
            boot_volume=None, volumes=None, nat_destination=None,
            group=None,
            **kwargs):
        """Create a virtual server instance.
        :param name: Something to name the server.
        :param image: Image dict, name or ID to boot with. image is required
                      unless boot_volume is given.
        :param flavor: Flavor dict, name or ID to boot onto.
        :param auto_ip: Whether to take actions to find a routable IP for
                        the server. (defaults to True)
        :param ips: List of IPs to attach to the server (defaults to None)
        :param ip_pool: Name of the network or floating IP pool to get an
                        address from. (defaults to None)
        :param root_volume: Name or ID of a volume to boot from
                            (defaults to None - deprecated, use boot_volume)
        :param boot_volume: Name or ID of a volume to boot from
                            (defaults to None)
        :param terminate_volume: If booting from a volume, whether it should
                                 be deleted when the server is destroyed.
                                 (defaults to False)
        :param volumes: (optional) A list of volumes to attach to the server
        :param meta: (optional) A dict of arbitrary key/value metadata to
                     store for this server. Both keys and values must be
                     <=255 characters.
        :param files: (optional, deprecated) A dict of files to overwrite
                      on the server upon boot. Keys are file names (i.e.
                      ``/etc/passwd``) and values
                      are the file contents (either as a string or as a
                      file-like object). A maximum of five entries is allowed,
                      and each file must be 10k or less.
        :param reservation_id: a UUID for the set of servers being requested.
        :param min_count: (optional extension) The minimum number of
                          servers to launch.
        :param max_count: (optional extension) The maximum number of
                          servers to launch.
        :param security_groups: A list of security group names
        :param userdata: user data to pass to be exposed by the metadata
                      server this can be a file type object as well or a
                      string.
        :param key_name: (optional extension) name of previously created
                      keypair to inject into the instance.
        :param availability_zone: Name of the availability zone for instance
                                  placement.
        :param block_device_mapping: (optional) A dict of block
                      device mappings for this server.
        :param block_device_mapping_v2: (optional) A dict of block
                      device mappings for this server.
        :param nics:  (optional extension) an ordered list of nics to be
                      added to this server, with information about
                      connected networks, fixed IPs, port etc.
        :param scheduler_hints: (optional extension) arbitrary key-value pairs
                            specified by the client to help boot an instance
        :param config_drive: (optional extension) value for config drive
                            either boolean, or volume-id
        :param disk_config: (optional extension) control how the disk is
                            partitioned when the server is created.  possible
                            values are 'AUTO' or 'MANUAL'.
        :param admin_pass: (optional extension) add a user supplied admin
                           password.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param reuse_ips: (optional) Whether to attempt to reuse pre-existing
                                     floating ips should a floating IP be
                                     needed (defaults to True)
        :param network: (optional) Network dict or name or ID to attach the
                        server to.  Mutually exclusive with the nics parameter.
                        Can also be a list of network names or IDs or
                        network dicts.
        :param boot_from_volume: Whether to boot from volume. 'boot_volume'
                                 implies True, but boot_from_volume=True with
                                 no boot_volume is valid and will create a
                                 volume from the image and use that.
        :param volume_size: When booting an image from volume, how big should
                            the created volume be? Defaults to 50.
        :param nat_destination: Which network should a created floating IP
                                be attached to, if it's not possible to
                                infer from the cloud's configuration.
                                (Optional, defaults to None)
        :param group: ServerGroup dict, name or id to boot the server in.
                      If a group is provided in both scheduler_hints and in
                      the group param, the group param will win.
                      (Optional, defaults to None)
        :returns: A ``munch.Munch`` representing the created server.
        :raises: OpenStackCloudException on operation error.
        """
        # TODO(shade) Image is optional but flavor is not - yet flavor comes
        # after image in the argument list. Doh.
        if not flavor:
            raise TypeError(
                "create_server() missing 1 required argument: 'flavor'")
        if not image and not boot_volume:
            raise TypeError(
                "create_server() requires either 'image' or 'boot_volume'")

        microversion = None
        server_json = {'server': kwargs}

        # TODO(mordred) Add support for description starting in 2.19
        security_groups = kwargs.get('security_groups', [])
        if security_groups and not isinstance(kwargs['security_groups'], list):
            security_groups = [security_groups]
        if security_groups:
            kwargs['security_groups'] = []
            for sec_group in security_groups:
                kwargs['security_groups'].append(dict(name=sec_group))
        if 'userdata' in kwargs:
            user_data = kwargs.pop('userdata')
            if user_data:
                kwargs['user_data'] = self._encode_server_userdata(user_data)
        for (desired, given) in (
                ('OS-DCF:diskConfig', 'disk_config'),
                ('config_drive', 'config_drive'),
                ('key_name', 'key_name'),
                ('metadata', 'meta'),
                ('adminPass', 'admin_pass')):
            value = kwargs.pop(given, None)
            if value:
                kwargs[desired] = value

        hints = kwargs.pop('scheduler_hints', {})
        if group:
            group_obj = self.get_server_group(group)
            if not group_obj:
                raise exc.OpenStackCloudException(
                    "Server Group {group} was requested but was not found"
                    " on the cloud".format(group=group))
            hints['group'] = group_obj['id']
        if hints:
            server_json['os:scheduler_hints'] = hints
        kwargs.setdefault('max_count', kwargs.get('max_count', 1))
        kwargs.setdefault('min_count', kwargs.get('min_count', 1))

        if 'nics' in kwargs and not isinstance(kwargs['nics'], list):
            if isinstance(kwargs['nics'], dict):
                # Be nice and help the user out
                kwargs['nics'] = [kwargs['nics']]
            else:
                raise exc.OpenStackCloudException(
                    'nics parameter to create_server takes a list of dicts.'
                    ' Got: {nics}'.format(nics=kwargs['nics']))

        if network and ('nics' not in kwargs or not kwargs['nics']):
            nics = []
            if not isinstance(network, list):
                network = [network]
            for net_name in network:
                if isinstance(net_name, dict) and 'id' in net_name:
                    network_obj = net_name
                else:
                    network_obj = self.get_network(name_or_id=net_name)
                if not network_obj:
                    raise exc.OpenStackCloudException(
                        'Network {network} is not a valid network in'
                        ' {cloud}:{region}'.format(
                            network=network,
                            cloud=self.name, region=self._compute_region))
                nics.append({'net-id': network_obj['id']})

            kwargs['nics'] = nics
        if not network and ('nics' not in kwargs or not kwargs['nics']):
            default_network = self.get_default_network()
            if default_network:
                kwargs['nics'] = [{'net-id': default_network['id']}]

        networks = []
        for nic in kwargs.pop('nics', []):
            net = {}
            if 'net-id' in nic:
                # TODO(mordred) Make sure this is in uuid format
                net['uuid'] = nic.pop('net-id')
                # If there's a net-id, ignore net-name
                nic.pop('net-name', None)
            elif 'net-name' in nic:
                net_name = nic.pop('net-name')
                nic_net = self.get_network(net_name)
                if not nic_net:
                    raise exc.OpenStackCloudException(
                        "Requested network {net} could not be found.".format(
                            net=net_name))
                net['uuid'] = nic_net['id']
            for ip_key in ('v4-fixed-ip', 'v6-fixed-ip', 'fixed_ip'):
                fixed_ip = nic.pop(ip_key, None)
                if fixed_ip and net.get('fixed_ip'):
                    raise exc.OpenStackCloudException(
                        "Only one of v4-fixed-ip, v6-fixed-ip or fixed_ip"
                        " may be given")
                if fixed_ip:
                    net['fixed_ip'] = fixed_ip
            for key in ('port', 'port-id'):
                if key in nic:
                    net['port'] = nic.pop(key)
            # A tag supported only in server microversion 2.32-2.36 or >= 2.42
            # Bumping the version to 2.42 to support the 'tag' implementation
            if 'tag' in nic:
                microversion = utils.pick_microversion(self.compute, '2.42')
                net['tag'] = nic.pop('tag')
            if nic:
                raise exc.OpenStackCloudException(
                    "Additional unsupported keys given for server network"
                    " creation: {keys}".format(keys=nic.keys()))
            networks.append(net)
        if networks:
            kwargs['networks'] = networks

        if image:
            if isinstance(image, dict):
                kwargs['imageRef'] = image['id']
            else:
                kwargs['imageRef'] = self.get_image(image).id
        if isinstance(flavor, dict):
            kwargs['flavorRef'] = flavor['id']
        else:
            kwargs['flavorRef'] = self.get_flavor(flavor, get_extra=False).id

        if volumes is None:
            volumes = []

        # nova cli calls this boot_volume. Let's be the same
        if root_volume and not boot_volume:
            boot_volume = root_volume

        kwargs = self._get_boot_from_volume_kwargs(
            image=image, boot_from_volume=boot_from_volume,
            boot_volume=boot_volume, volume_size=str(volume_size),
            terminate_volume=terminate_volume,
            volumes=volumes, kwargs=kwargs)

        kwargs['name'] = name
        endpoint = '/servers'
        # TODO(mordred) We're only testing this in functional tests. We need
        # to add unit tests for this too.
        if 'block_device_mapping_v2' in kwargs:
            endpoint = '/os-volumes_boot'
        with _utils.shade_exceptions("Error in creating instance"):
            data = proxy._json_response(
                self.compute.post(endpoint, json=server_json,
                                  microversion=microversion))
            server = self._get_and_munchify('server', data)
            admin_pass = server.get('adminPass') or kwargs.get('admin_pass')
            if not wait:
                # This is a direct get call to skip the list_servers
                # cache which has absolutely no chance of containing the
                # new server.
                # Only do this if we're not going to wait for the server
                # to complete booting, because the only reason we do it
                # is to get a server record that is the return value from
                # get/list rather than the return value of create. If we're
                # going to do the wait loop below, this is a waste of a call
                server = self.get_server_by_id(server.id)
                if server.status == 'ERROR':
                    raise exc.OpenStackCloudCreateException(
                        resource='server', resource_id=server.id)

        if wait:
            server = self.wait_for_server(
                server,
                auto_ip=auto_ip, ips=ips, ip_pool=ip_pool,
                reuse=reuse_ips, timeout=timeout,
                nat_destination=nat_destination,
            )

        server.adminPass = admin_pass
        return server
'''
# delete_server(name_or_id, wait=False, timeout=180, delete_ips=False, delete_ip_retry=1)