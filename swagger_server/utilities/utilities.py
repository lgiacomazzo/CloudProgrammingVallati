import re
import connexion
import MySQLdb

from swagger_server.models.configuration import Configuration
from swagger_server.utilities.dataUtils import pattern, flavors_list, db_queries_dict

def connect_to_db():
    mydb = MySQLdb.connect(host="172.17.0.2", user="root", passwd="password", db="openstacksdk")
    mycursor = mydb.cursor()
    return mydb, mycursor

def control_body():
    try:
        body = Configuration.from_dict(connexion.request.get_json())  # noqa: E501
        valid, error_msg = is_valid_configuration(body)
        if not valid:
            return None, error_msg
    except Exception as e:
        return None, "Null field(s)"

    return body, None

def create_configuration_dict(conf):
    """Creates a dict from a tuple of the database where configurations are stored
    """
    return {
            'id' : int(conf[0]),
            'timeStart' : str(conf[1]),
            'timeEnd' : str(conf[2]), 
            'flavor' : conf[3], 
            'image' : conf[4], 
            'numberOfVMs' : int(conf[5])
        }

def generate_flavors(conn):
    for flavor, configuration in flavors_list.items():
        conn.delete_flavor(name_or_id=flavor)
        conn.create_flavor(
                        name=flavor, 
                        ram=configuration['ram'], 
                        vcpus=configuration['vcpus'], 
                        disk=configuration['disk']
                    )

def is_valid_configuration(conf):
    try:
        if pattern.match(conf.time_start) == None:
            return False, "Format of 'timeStart' is not correct"
        if pattern.match(conf.time_end) == None:
            return False, "Format of 'timeEnd' is not correct"
        if conf.time_start == conf.time_end:
            return False, "Fields 'timeStart' and 'timeEnd' must be different"
        if conf.flavor.lower() not in flavors_list:
            return False, ("Flavor not in " + str(flavors_list))
        if conf.number_of_v_ms <= 0:
            return False, "Field 'numberOfVMs' must be greater than 0"
    except Exception as e:
        return False, "Field(s) missing"
        
    return True, None

def retrieve_all_the_configurations():
    mydb, mycursor = connect_to_db()
    sql = db_queries_dict['select']
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mydb.close()
    configurations = []
    for conf in myresult:
        configurations.append(create_configuration_dict(conf))
    return configurations
