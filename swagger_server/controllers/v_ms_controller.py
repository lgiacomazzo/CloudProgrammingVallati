import connexion
import six
import MySQLdb

from swagger_server.models.configuration import Configuration  # noqa: E501
from swagger_server import util
from datetime import time
from flask import jsonify

def add_new_configuration(body):  # noqa: E501
    """Add a new configuration

     # noqa: E501

    :param body: Configuration data
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Configuration.from_dict(connexion.request.get_json())  # noqa: E501
        mydb = MySQLdb.connect(host="172.17.0.2", user="root", passwd="password", db="openstacksdk")
        mycursor = mydb.cursor()
        #print("body.time_start="+str(body.time_start)+",type="+str(type(body.time_start)))
        #print("body.time_end="+str(body.time_end)+",type="+str(type(body.time_end)))
        #print("body.flavor="+str(body.flavor)+",type="+str(type(body.flavor)))
        #print("body.image="+str(body.image)+",type="+str(type(body.image)))
        #print("body.numberOfVMs="+str(body.number_of_v_ms)+",type="+str(type(body.number_of_v_ms)))
        sql = "INSERT INTO configurations(timeStart, timeEnd, flavor, image, numberOfVMs) VALUES (%s, %s, %s, %s, %s);"
        values = (body.time_start, body.time_end, body.flavor, body.image, body.number_of_v_ms)
        mycursor.execute(sql, values)
        mydb.commit()
        mydb.close()
        return "The job is done"
    return "Not correct json format", 400


def delete_configuration_by_id(configurationID):  # noqa: E501
    """Deletes a configuration via ID

     # noqa: E501

    :param configurationID: Configuration id for identifying the resource
    :type configurationID: int

    :rtype: None
    """
    mydb = MySQLdb.connect(host="172.17.0.2", user="root", passwd="password", db="openstacksdk")
    mycursor = mydb.cursor()
    sql = "DELETE FROM configurations WHERE id = %s;"
    values = (configurationID, )
    mycursor.execute(sql, values)
    mydb.commit()
    mydb.close()
    return "The job is done"


def get_configuration_by_id(configurationID):  # noqa: E501
    """Retrieve a configuration via ID

    Returns a single configuration object # noqa: E501

    :param configurationID: Configuration id for identifying the resource
    :type configurationID: int

    :rtype: Configuration
    """
    mydb = MySQLdb.connect(host="172.17.0.2", user="root", passwd="password", db="openstacksdk")
    mycursor = mydb.cursor()
    sql = "SELECT * FROM configurations WHERE id = %s;"
    values = (configurationID, )
    mycursor.execute(sql, values)
    myresult = mycursor.fetchall()
    mydb.close()
    if (len(myresult) == 0):
        return jsonify({})
    return jsonify(id=int(myresult[0][0]), 
                    timeStart=str(myresult[0][1]), 
                    timeEnd=str(myresult[0][2]), 
                    flavor=myresult[0][3], 
                    image=myresult[0][4], 
                    numberOfVMs=int(myresult[0][5])
                )


def get_configurations():  # noqa: E501
    """Retrieve all existing configurations

     # noqa: E501


    :rtype: Configuration
    """
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
    return jsonify(configurations)


def update_configuration_by_id(configurationID, body):  # noqa: E501
    """Updates a configuration in the database via ID

     # noqa: E501

    :param configurationID: Configuration id for identifying the resource
    :type configurationID: int
    :param body: Configuration data
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Configuration.from_dict(connexion.request.get_json())  # noqa: E501
        mydb = MySQLdb.connect(host="172.17.0.2", user="root", passwd="password", db="openstacksdk")
        mycursor = mydb.cursor()
        sql = "UPDATE configurations SET timeStart=%s, timeEnd=%s, flavor=%s, image=%s, numberOfVMs=%s WHERE id=%s ;"
        values = (body.time_start, body.time_end, body.flavor, body.image, body.number_of_v_ms, configurationID)
        mycursor.execute(sql, values)
        mydb.commit()
        mydb.close()
        return "The job is done"
    return 'do some magic!'
