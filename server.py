import logging
import socket
import sys
import json

class Server(object):

    def __init__(self):
        logging.basicConfig()
        self._logger = logging.getLogger("test")
        self._logger.setLevel(logging.DEBUG)

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def _ack(self):
        self._send()

    def _send(self, data=None):
        if data is not None:
            data_string = json.dumps(data)
        else:
            data_string = ''

        self._connection.send(('%s\n' % data_string).encode('utf-8'))

    def _wait_for_message(self):
        environment_message = self._connection.recv(4096).decode('utf-8')
        if environment_message[0] == u'\n':
            return ('ACK')
        self._logger.debug("Message: %s" % environment_message)
        message_parts = environment_message.split('\n')
        self._logger.debug(message_parts[0])
        return message_parts

    def _filter_invalid_actions(self, actions, state):
        units_in_action = [action['ID'] for action in state['actions']]
        return [action for action in actions if action['unitID'] not in units_in_action]

    def get_action(self, state):
        pass

    def _process_state_and_get_action(self, state):
        actions = self.get_action(state)

        return self._filter_invalid_actions(actions, state)

    def _wait_for_get_action(self):
        message_parts = self._wait_for_message()

        state = json.loads(message_parts[1])
        self._logger.debug("state: %s" % state)

        return self._process_state_and_get_action(state)


    def start(self):
        self._logger.debug('Socket created')

        # Bind socket to local host and port
        try:
            self._s.bind(('localhost', 9898))
        except socket.error as msg:
            self._logger.debug('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            self._s.close()
            sys.exit()

        self._logger.debug('Socket bind complete')

        # Start listening on socket
        self._s.listen(10)
        self._logger.debug('Socket now listening')

        # now keep talking with the client
        self._connection, addr = self._s.accept()
        self._logger.debug(self._connection)
        self._logger.debug(addr)

        self._ack()
        self._logger.debug('Connected with ' + addr[0] + ':' + str(addr[1]))

        # Get the headers
        _, time_budget, iteration_budget = self._wait_for_message()[0].split()
        self._ack()
        utt = self._wait_for_message()
        self._ack()

        try:
            while 1:
                action = self._wait_for_get_action()
                self._logger.debug('sending action %s' % action)
                self._send(action)
        except Exception as msg:
            self._connection.close()
            self._s.close()
            raise msg


        self._s.close()