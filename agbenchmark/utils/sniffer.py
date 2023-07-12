from scapy.all import sniff
from scapy.layers.inet import TCP


class Sniffer:
    def __init__(self):
        self.stop_sniffing = False

    def http_header(self, packet):
        http_packet = str(packet)
        if http_packet.find("POST"):
            return self.POST_print(packet)

    def POST_print(self, packet):
        print("POST PRINT FOUND", packet[TCP])

        # Check if this is an HTTP packet with a "chat" field in the body
        if b"messages" in packet[TCP].payload:
            print("YES MESSAGES HAS BEEN FOUND")
            # Extract the "chat" field from the HTTP body
            http_payload = str(packet[TCP].payload)
            chat_start_index = (
                http_payload.find("messages") + len("messages") + 1
            )  # Assume that "chat" is followed by a space
            chat_end_index = http_payload.find(
                "\r\n", chat_start_index
            )  # Assume that fields are separated by CRLF
            chat_field = http_payload[chat_start_index:chat_end_index]
            print("Chat Field: " + chat_field)

        # Check if this is an HTTP packet with a "content" field in the response
        if b"choices" in packet[TCP].payload:
            # Extract the "content" field from the HTTP response
            http_payload = str(packet[TCP].payload)
            content_start_index = (
                http_payload.find("choices") + len("choices") + 1
            )  # Assume that "content" is followed by a space
            content_end_index = http_payload.find(
                "\r\n", content_start_index
            )  # Assume that fields are separated by CRLF
            content_field = http_payload[content_start_index:content_end_index]
            print("Content Field: " + content_field)

    def should_stop(self, packet):
        return self.stop_sniffing

    def start_sniffing(self):
        sniff(
            filter="tcp port 80",
            prn=self.http_header,
            stop_filter=self.should_stop,
            store=0,
        )
