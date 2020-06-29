#!/usr/bin/env python3

import connexion
import openstack
import MySQLdb
import time
import datetime
import namegenerator

from threading import Thread, Lock
from swagger_server import encoder
from pprint import pprint
from queue import Queue

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
    # TODO: threading.py throws exception in line 1388 (lock.acquire())
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

def create_vms(configurations, conn, image, flavor, nVMs):
    for _ in range(nVMs):
        server = conn.create_server(name=namegenerator.gen(),
                                    image=image,
                                    flavor=flavor,
                                    network="internal")
        configurations.put(server)

def destroy_vms(configurations, conn):
    while not configurations.empty():
        server = configurations.get()
        configurations.task_done()
        conn.delete_server(server)

def generate_flavors(conn):
    conn.delete_flavor(name_or_id="standard")
    conn.delete_flavor(name_or_id="large")
    conn.create_flavor(name="standard", ram=64, vcpus=1, disk=1)
    conn.create_flavor(name="large", ram=256, vcpus=2, disk=2)


if __name__ == '__main__':
    # for synchronization purposes
    syncObject = Sync()
    # openstack.enable_logging(debug=True)
    conn = openstack.connect()
    # create two flavors at start-up
    generate_flavors(conn)
    # start HTTP server in a separate thread
    Thread(target=server, args=(syncObject, )).start() # daemon=True to make it a daemon thread

    activeConfigurations = {} # key: configurationId, value: [server names returned by create_server()]
    debug = True
    while not syncObject.hasEnded():
        
        currentTime = datetime.datetime.now(datetime.timezone.utc).time() # time in utc format
        print("System Time: " + str(currentTime))
        confs = retrieve_configurations()
        # TODO da rimuovere alla fine di tutto
        if debug == True:
            print("Active Configurations:")
            pprint(str(activeConfigurations))
            print("All Configurations:")
            pprint(confs)
        
        # controllare per ogni configurazione se siamo nel periodo schedulato
        for conf in confs:
            idConf = conf['id']
            timeStart = datetime.datetime.strptime(conf['timeStart'], "%H:%M:%S").time() # HH:MM:SS
            timeEnd = datetime.datetime.strptime(conf['timeEnd'], "%H:%M:%S").time()
            flavor = conf['flavor']
            image = conf['image']
            nVMs = int(conf['numberOfVMs'])

            '''
                1) dalle 09:00 alle 17:00 --> currentTime >= timeStart and currentTime <= timeEnd
                2) dalle 17:00 alle 09:00 --> currentTime >= timeStart or currentTime <= timeEnd
                
            '''
            condition = ((currentTime >= timeStart and currentTime <= timeEnd) 
                or (timeEnd <= timeStart and (currentTime >= timeStart or currentTime <= timeEnd)))
            
            if condition and (not (idConf in activeConfigurations.keys())):
                activeConfigurations[idConf] = Queue()
                if nVMs == 1: # we consider comparable overhead in creating a thread than allocating a single VM
                    create_vms(activeConfigurations[idConf], conn, image, flavor, nVMs)
                else:
                    Thread(target=create_vms, args=(activeConfigurations[idConf], conn, image, flavor, nVMs)).start()
            # destroy VMs according to scheduled configurations
            elif (not condition) and (idConf in activeConfigurations.keys()):
                Thread(target=destroy_vms, args=(activeConfigurations[idConf], conn)).start()
                del activeConfigurations[idConf]
        # cosa fare quando una configurazione viene rimossa dall'admin, ma era una configurazione attiva?
        # Rimuovere anche le VMs instanziate
        # Nota: list forza la copia delle chiavi --> niente RuntimeError sul cambio della dimensione del dizionario
        for id in list(activeConfigurations):
            found = False
            for conf in confs:
                if id == conf['id']:
                    found = True
                    break
            if not found:
                print("Trovata configurazione zombie con id " + str(id))
                Thread(target=destroy_vms, args=(activeConfigurations[id], conn)).start()
                del activeConfigurations[id]
        # and now we wait some time
        print("Sleeping...")
        time.sleep(20)
    # when everything has been done
    conn.close()
