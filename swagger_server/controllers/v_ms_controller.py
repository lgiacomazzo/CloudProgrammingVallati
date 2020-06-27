import connexion
import six

from swagger_server.models.configuration import Configuration  # noqa: E501
from swagger_server import util


def add_new_configuration(body):  # noqa: E501
    """Add a new configuration

     # noqa: E501

    :param body: Configuration data
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Configuration.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_configuration_by_id(configurationID):  # noqa: E501
    """Deletes a configuration via ID

     # noqa: E501

    :param configurationID: Configuration id for identifying the resource
    :type configurationID: int

    :rtype: None
    """
    return 'do some magic!'


def get_configuration_by_id(configurationID):  # noqa: E501
    """Retrieve a configuration via ID

    Returns a single configuration object # noqa: E501

    :param configurationID: Configuration id for identifying the resource
    :type configurationID: int

    :rtype: Configuration
    """
    return 'do some magic!'


def get_configurations():  # noqa: E501
    """Retrieve all existing configurations

     # noqa: E501


    :rtype: Configuration
    """
    return 'do some magic!'


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
    return 'do some magic!'
