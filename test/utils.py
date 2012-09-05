import struct
import socket

from stem.socket import ProtocolError
import test.runner

error_msgs = {
  0x5a: "SOCKS4A request granted",
  0x5b: "SOCKS4A request rejected or failed",
  0x5c: "SOCKS4A request failed because client is not running identd (or not reachable from the server)",
  0x5d: "SOCKS4A request failed because client's identd could not confirm the user ID string in the request",
}

ip_request = """GET /ip HTTP/1.0
Host: ifconfig.me
Accept-Encoding: identity

"""

def external_ip(sock):
  """
  Returns the externally visible IP address when using a SOCKS4a proxy.
  
  :param socket sock: socket connected to a SOCKS4a proxy server
  
  :returns: externally visible IP address, or None if it isn't able to
  """
  
  try:
    negotiate_socks(sock, "ifconfig.me", 80)
    s.sendall(req)
    response = s.recv(1000)
    
    return response[response.find("\n\n"):].strip()
  except:
    pass

def negotiate_socks(sock, host, port):
  """
  Negotiate with a socks4a server. Closes the socket and raises an exception on
  failure.
  
  :param socket sock: socket connected to socks4a server
  :param str host: host to connect to
  :param int port: port to connect to
  
  :raises: :class:`stem.socket.ProtocolError` if the socks server doesn't grant our request
  
  :returns: a list with the IP address and the port that the proxy connected to
  """
  
  request = "\x04\x01" + struct.pack("!H", port) + "\x00\x00\x00\x01" + "\x00" + host + "\x00"
  sock.sendall(request)
  response = sock.recv(8)
  
  if len(response) != 8 or response[0] != "\x00" or response[1] != "\x5a":
    sock.close()
    raise ProtocolError(error_msgs.get(response[1], "SOCKS server returned unrecognized error code"))
  
  return [socket.inet_ntoa(response[4:]), struct.unpack("!H", response[2:4])[0]]

