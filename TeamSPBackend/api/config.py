atl_username = b'tE\xd4M\xbe\xb6K\xa5\x84\xc9Z3\x14Fk\xa3'
atl_password = b"\xed0\xd8\xc2\xe8\xf2+\x81\x1f\xbd\xbf\x1a{%\xbd\xe9\xb8QU\xa4'<\xc2K"

from Cryptodome.Cipher import DES
import binascii
key = b'abcxyesw'
des = DES.new(key,DES.MODE_ECB)
atl_username = des.decrypt(atl_username).decode().rstrip(' ')
atl_password = des.decrypt(atl_password).decode().rstrip(' ')


