import connexion
import six
import MySQLdb
import re

from swagger_server.models.configuration import Configuration  # noqa: E501
from swagger_server import util
from swagger_server.utilities.utilities import control_body
from swagger_server.utilities.utilities import create_configuration_dict
from swagger_server.utilities.utilities import retrieve_all_the_configurations
from swagger_server.utilities.utilities import connect_to_db
from swagger_server.utilities.dataUtils import db_queries_dict
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
        # checking missing fields and malformed input
        body, error_msg = control_body()
        if body is None:
            return error_msg, 400
        # everything is as expected
        mydb, mycursor = connect_to_db()
        sql = db_queries_dict['insert']
        values = (body.time_start,
                  body.time_end,
                  body.flavor.lower(),
                  body.image,
                  body.number_of_v_ms)
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
    mydb, mycursor = connect_to_db()
    sql = db_queries_dict['deleteWithId']
    values = (configurationID, )
    mycursor.execute(sql, values)
    mydb.commit()
    mydb.close()

    return "The job is done"

def delete_configurations(): # noqa: E501
    """Deletes a configuration via ID

     # noqa: E501

    :rtype: None
    """
    mydb, mycursor = connect_to_db()
    sql = db_queries_dict['delete']
    mycursor.execute(sql)
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
    mydb, mycursor = connect_to_db()
    sql = db_queries_dict['selectWithId']
    values = (configurationID, )
    mycursor.execute(sql, values)
    myresult = mycursor.fetchall()
    mydb.close()
    if (len(myresult) == 0):
        return jsonify({})
    return jsonify(create_configuration_dict(myresult[0]))


def get_configurations():  # noqa: E501
    """Retrieve all existing configurations

     # noqa: E501


    :rtype: Configuration
    """
    configurations = retrieve_all_the_configurations()
    if (len(configurations) == 0):
        return jsonify({})
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
        # checking missing fields and malformed input
        body, error_msg = control_body()
        if body is None:
            return error_msg, 400
        # everything is as expected
        mydb, mycursor = connect_to_db()
        sql = db_queries_dict['update']
        values = (body.time_start,
                  body.time_end,
                  body.flavor.lower(),
                  body.image,
                  body.number_of_v_ms,
                  configurationID)
        mycursor.execute(sql, values)
        mydb.commit()
        mydb.close()

        return "The job is done"

    return "Not correct json format", 400
