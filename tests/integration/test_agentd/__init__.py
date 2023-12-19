from datetime import datetime

from wazuh_testing.constants.paths.logs import WAZUH_LOG_PATH
from wazuh_testing.modules.agentd.patterns import * 
from wazuh_testing.tools.monitors.file_monitor import FileMonitor
from wazuh_testing.utils import callbacks

def kill_server(server):
    """Cleans and shutdown given server.

    Args:
        server (remoted/authd server): server to be shutdown.
    """
    if server:
        server.clear()
        server.shutdown()

def parse_time_from_log_line(log_line):
    """Create a datetime object from a date in a string.

    Args:
        log_line (str): String with date.

    Returns:
        datetime: datetime object with the parsed time.
    """
    data = log_line.split(" ")
    (year, month, day) = data[0].split("/")
    (hour, minute, second) = data[1].split(":")
    log_time = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute),
                        second=int(second))
    return log_time

def get_regex(pattern, server_address, server_port):
    """Return a regex and the values to complete it

    Args:
        pattern (str): String refering to the framework patterns.
        server_address (str): String with server ip.
        server_port (str): String with server port.

    Returns:
        regex (regex): refered by framework patter.
        values (dict): values to complete regex 
    """
    if(pattern == 'AGENTD_TRYING_CONNECT' or pattern == 'AGENTD_UNABLE_TO_CONNECT'):
        regex = globals()[pattern]
        values = {'IP': str(server_address), 'PORT':str(server_port)}
    elif (pattern == 'AGENTD_REQUESTING_KEY'):
        regex = globals()[pattern]
        values = {'IP': str(server_address)}
    elif (pattern == 'AGENTD_CONNECTED_TO_ENROLLMENT'):
        regex = globals()[pattern]
        values = {'IP': '', 'PORT': ''}
    else:
        regex = globals()[pattern]
        values = {}
    return regex, values

def wait_keepalive():
    """
        Watch ossec.log until "Sending keep alive" message is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_SENDING_KEEP_ALIVE), timeout = 100)
    assert (wazuh_log_monitor.callback_result != None), f'Sending keep alive not found'

def wait_connect():
    """
        Watch ossec.log until received "Connected to the server" message is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_CONNECTED_TO_SERVER))
    assert (wazuh_log_monitor.callback_result != None), f'Connected to the server message not found'

def wait_ack():
    """
        Watch ossec.log until "Received ack message" is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_RECEIVED_ACK))
    assert (wazuh_log_monitor.callback_result != None), f'Received ack message not found'

def wait_state_update():
    """
        Watch ossec.log until "Updating state file" message is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_UPDATING_STATE_FILE))
    assert (wazuh_log_monitor.callback_result != None), f'State file update not found'

def wait_enrollment():
    """
        Watch ossec.log until "Valid key received" message is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_RECEIVED_VALID_KEY))
    assert (wazuh_log_monitor.callback_result != None), 'Agent never enrolled'

def wait_enrollment_try():
    """
        Watch ossec.log until "Requesting a key" message is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_REQUESTING_KEY,{'IP':''}), timeout = 50)
    assert (wazuh_log_monitor.callback_result != None), f'Enrollment retry was not sent'

def wait_agent_notification(current_value):
    """
        Watch ossec.log until "Sending agent notification" message is found current_value times
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_SENDING_AGENT_NOTIFICATION), accumulations = int(current_value))
    assert (wazuh_log_monitor.callback_result != None), f'Sending agent notification message not found'

def wait_server_rollback():
    """
        Watch ossec.log until "Unable to connect to any server" message is found'
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(callback=callbacks.generate_callback(AGENTD_UNABLE_TO_CONNECT_TO_ANY))
    assert (wazuh_log_monitor.callback_result != None), f'Unable to connect to any server message not found'

def check_module_stop():
    """
        Watch ossec.log until "Unable to access queue" message is not found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    wazuh_log_monitor.start(callback=callbacks.generate_callback(AGENTD_MODULE_STOPPED))
    assert (wazuh_log_monitor.callback_result == None), f'Unable to access queue message found'

def check_connection_try():
    """
        Watch ossec.log until "Trying to connect to server" message is found
    """
    wazuh_log_monitor = FileMonitor(WAZUH_LOG_PATH)
    matched_line = wazuh_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_TRYING_CONNECT,{'IP':'','PORT':''}), return_matched_line = True)
    assert (wazuh_log_monitor.callback_result != None), f'Trying to connect to server message not found'
    return matched_line
