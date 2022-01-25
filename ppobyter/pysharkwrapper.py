import pyshark


class PysharkWrapper:
    def __init__(self):
        self.__cap = pyshark.LiveCapture(interface="Ethernet 2", include_raw=True, use_json=True, display_filter="ip.src == 167.114.159.20")

        #self.__cap = pyshark.LiveCapture(interface=r"\Device\NPF_{65E2C297-AC80-4851-95C2-795C9783D00F}", include_raw=True,
         #                                use_json=True, display_filter="ip.src == 167.114.159.20")
    @staticmethod
    def decodehex(hexa: str) -> str:
        """
        This takes a hex stream and makes a string from it.
        :param hexa: The hexadecimal string.
        :return: the string made from the hexa.
        """
        result = ""
        temp = ""
        for i in hexa:
            temp += i
            if len(temp) == 2:
                result += chr(int(temp, 16))
                temp = ""
        return result

    def cap(self):
        for packet in self.__cap.sniff_continuously():
            try:
                hexa = packet.tcp.payload.replace(":", "")
                r = PysharkWrapper.decodehex(hexa)
                for msg in r.split("\x00"):
                    if msg == "":
                        continue
                    yield msg

            except AttributeError:
                continue
