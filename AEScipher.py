from Crypto.Cipher import AES

padding = '\0'
pad = lambda x: x + (16 - len(x) % 16) * padding
unwrap = lambda x: x.replace('\0', '')

key = '1234567890abcdef'
mode = AES.MODE_ECB

encryptor = AES.new(key, mode)
decryptor = AES.new(key, mode)

teststr = 'AES test case'
teststr = pad(teststr)
ciphertext = encryptor.encrypt(teststr)
plaintext = decryptor.decrypt(ciphertext)
plaintext = unwrap(plaintext)

print 'teststr:', repr(teststr)
print 'ciphertext:', ciphertext
print 'plaintext:', plaintext
