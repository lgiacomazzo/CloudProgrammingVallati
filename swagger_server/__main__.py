#!/usr/bin/env python3

import connexion
import openstack
import MySQLdb
import time
import datetime
import namegenerator


from swagger_server.utilities.utilities import retrieve_all_the_configurations, generate_flavors
from threading import Thread
from swagger_server import encoder
from pprint import pprint
from queue import Queue

def server():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'My REST API'})

    app.run(port=8081)

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

def check_zombie_configurations(activeConfigurations, allConfigurations):
    # list makes a copy of the key, so no RuntimeError on modifying the dictionary
    for id in list(activeConfigurations):
        found = False
        for conf in allConfigurations:
            if id == conf['id']:
                found = True
                break
        if not found:
            print(f"Found zombie configuration with id '{id}'")
            Thread(target=destroy_vms, args=(activeConfigurations[id], conn)).start()
            del activeConfigurations[id]


if __name__ == '__main__':
    
    conn = openstack.connect()

    # create two flavors at start-up
    generate_flavors(conn)

    # start HTTP server in a separate thread
    Thread(target=server).start()

    activeConfigurations = {} # key: configurationId, value: [server names returned by create_server()]
    while True:
        
        currentTime = datetime.datetime.now(datetime.timezone.utc).time() # time in utc format
        print(f"System Time: {currentTime}")
        confs = retrieve_all_the_configurations()
        
        # controllare per ogni configurazione se siamo nel periodo schedulato
        for conf in confs:
            idConf = conf['id']
            timeStart = datetime.datetime.strptime(conf['timeStart'], "%H:%M:%S").time() # HH:MM:SS
            timeEnd = datetime.datetime.strptime(conf['timeEnd'], "%H:%M:%S").time()
            flavor = conf['flavor']
            image = conf['image']
            nVMs = int(conf['numberOfVMs'])

            # we handle both the case when the scheduled time period is in the same day and 
            # the case when it is wrapped to the next day (ex: 15:00 to 16:00, 21:00 to 02:00)
            time_condition = ((currentTime >= timeStart and currentTime <= timeEnd) 
                or (timeEnd <= timeStart and (currentTime >= timeStart or currentTime <= timeEnd)))
            
            # create VMs according to scheduled configurations
            if time_condition and (not (idConf in activeConfigurations.keys())):
                activeConfigurations[idConf] = Queue()
                if nVMs == 1: # we consider comparable overhead in creating a thread than allocating a single VM
                    create_vms(activeConfigurations[idConf], conn, image, flavor, nVMs)
                else:
                    Thread(target=create_vms, args=(activeConfigurations[idConf], conn, image, flavor, nVMs)).start()
                print(f"Activated configuration with id '{idConf}'")
            # destroy VMs according to scheduled configurations
            elif (not time_condition) and (idConf in activeConfigurations.keys()):
                Thread(target=destroy_vms, args=(activeConfigurations[idConf], conn)).start()
                del activeConfigurations[idConf]
                print(f"Deleted configuration with id '{idConf}'")

        # check for active configuration which are not anymore in the db
        check_zombie_configurations(activeConfigurations, confs)
        # and now we wait some time
        print("Sleeping...")
        time.sleep(20)
    # when everything has been done
    conn.close()
