"""Tests for the :mod:`bigchaindb.backend.mongodb.admin` module."""
import copy
from unittest import mock

import pytest
from pymongo.database import Database
from pymongo.errors import OperationFailure


@pytest.fixture
def mock_replicaset_config():
    return {
        'config': {
            '_id': 'bigchain-rs',
            'members': [
                {
                    '_id': 0,
                    'arbiterOnly': False,
                    'buildIndexes': True,
                    'hidden': False,
                    'host': 'localhost:27017',
                    'priority': 1.0,
                    'slaveDelay': 0,
                    'tags': {},
                    'votes': 1
                }
            ],
            'version': 1
        }
    }


def test_add_replicas(mock_replicaset_config):
    from bigchaindb.backend import connect
    from bigchaindb.backend.admin import add_replicas

    connection = connect()
    # force the connection object to setup a connection to the database
    # before we mock `Database.command`
    connection.conn

    expected_config = copy.deepcopy(mock_replicaset_config)
    expected_config['config']['members'] += [
        {'_id': 1, 'host': 'localhost:27018'},
        {'_id': 2, 'host': 'localhost:27019'}
    ]
    expected_config['config']['version'] += 1

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.return_value = mock_replicaset_config
        add_replicas(connection, ['localhost:27018', 'localhost:27019'])

    mock_command.assert_called_with('replSetReconfig',
                                    expected_config['config'])


def test_add_replicas_raises(mock_replicaset_config):
    from bigchaindb.backend import connect
    from bigchaindb.backend.admin import add_replicas
    from bigchaindb.backend.exceptions import DatabaseOpFailedError

    connection = connect()
    # force the connection object to setup a connection to the database
    # before we mock `Database.command`
    connection.conn

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock_replicaset_config,
            OperationFailure(error=1, details={'errmsg': ''})
        ]
        with pytest.raises(DatabaseOpFailedError):
            add_replicas(connection, ['localhost:27018'])


def test_remove_replicas(mock_replicaset_config):
    from bigchaindb.backend import connect
    from bigchaindb.backend.admin import remove_replicas

    connection = connect()
    # force the connection object to setup a connection to the database
    # before we mock `Database.command`
    connection.conn

    expected_config = copy.deepcopy(mock_replicaset_config)
    expected_config['config']['version'] += 1

    # add some hosts to the configuration to remove
    mock_replicaset_config['config']['members'] += [
        {'_id': 1, 'host': 'localhost:27018'},
        {'_id': 2, 'host': 'localhost:27019'}
    ]

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.return_value = mock_replicaset_config
        remove_replicas(connection, ['localhost:27018', 'localhost:27019'])

    mock_command.assert_called_with('replSetReconfig',
                                    expected_config['config'])


def test_remove_replicas_raises(mock_replicaset_config):
    from bigchaindb.backend import connect
    from bigchaindb.backend.admin import remove_replicas
    from bigchaindb.backend.exceptions import DatabaseOpFailedError

    connection = connect()
    # force the connection object to setup a connection to the database
    # before we mock `Database.command`
    connection.conn

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock_replicaset_config,
            OperationFailure(error=1, details={'errmsg': ''})
        ]
        with pytest.raises(DatabaseOpFailedError):
            remove_replicas(connection, ['localhost:27018'])
