from utils import protocol
blocklist = {} # prawdopodobnie useless, nie wiem czemu to dodalem TODO: usunac


class MessageHandler():
    def __init__(self):
        pass
    def handle(self, message, id):
        if message.startswith(protocol["fromClient"]["send"]):
            return self.on_send(message)
        elif message.startswith(protocol["fromClient"]["block"]):
            return self.on_block(message, id)
        elif message.startswith(protocol["fromClient"]["unblock"]):
            return self.on_unblock(message, id)
        elif message.startswith(protocol["fromClient"]["getUsers"]):
            return self.on_getusers()
        elif message.startswith(protocol["fromClient"]["sendKey"]):
            return self.on_sendkey()
        else:
            return "SEND", -1, "BAD_REQUEST"

    def on_send(self, msg):
        split = msg.split(" ", 2)
        if len(split) != 3:
            return "SEND", -1, "ERROR"
        else:
            return "SEND", split[1], split[2]

    def on_block(self, msg, id):
        split = msg.split()
        if len(split) != 2:
            return "SEND", -1, "ERROR"
        else:
            try:
                if not id in blocklist:
                    blocklist[id] = []
                blocked_id = int(split[1])
                if not blocked_id in blocklist[id]:
                    blocklist[id].append(blocked_id)
                    return "SEND", -1, "BLOCK_OK"
            except Exception:
                return "SEND", -1, "ERROR"

    def on_unblock(self, msg, id):
        split = msg.split()
        if len(split) != 2:
            return "SEND", -1, "ERROR"
        else:
            try:
                if not id in blocklist:
                    blocklist[id] = []
                blocked_id = int(split[1])
                if blocked_id in blocklist[id]:
                    blocklist[id].remove(blocked_id)
                    return "SEND", -1, "UNBLOCK_OK"
            except Exception:
                return "SEND", -1, "ERROR"

    def on_getusers(self):
        return "GET_ONLINE", -1, None

    def on_sendkey(self, ):
        return "TODO"
