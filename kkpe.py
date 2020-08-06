
import sys
import msgpack
import struct

def WriteFile(path, data):
	prefix = sys.argv[1][:-4] + "_"
	with open(prefix + path, "wb") as newFile:
		newFile.write(data)

def ReadPng(file):
	png = bytearray()
	expected = bytearray(b'IEND')
	code = bytearray()
	while not (code == expected):
		byte = file.read(1)[0]
		if len(code) > 3:
			code = code[1:]
		code.append(byte)
		png.append(byte)
	png.append(file.read(1)[0])
	png.append(file.read(1)[0])
	png.append(file.read(1)[0])
	png.append(file.read(1)[0])
	return png

def read32u(file):
	return struct.unpack('<i', input_file.read(4))[0]

with open(sys.argv[1], "rb") as input_file:
	WriteFile("main.png", ReadPng(input_file))
	
	version = read32u(input_file)
	
	string1len = read32u(input_file)
	string1 = input_file.read(12)
	string2len = read32u(input_file)
	string2 = input_file.read(5)
	
	WriteFile("face.png", input_file.read(read32u(input_file)))
	
	indexes = msgpack.unpackb( input_file.read(read32u(input_file)) )['lstInfo']
	
	unknown = input_file.read(8)
	
	data = bytearray(input_file.read())
	
	
	blocks = dict()
	for index in indexes:
		pos = index['pos']
		size = index['size']
		blocks[index['name']] = data[pos : pos+size]
	#TODO: Expand 'Custom'
	
		
	kkex = msgpack.unpackb( blocks['KKEx'] )
	
	
	WriteFile('kkex', blocks['KKEx'])
	
	ksox = kkex['KSOX'][1]
	for over in ksox:
		if ksox[over]:
			WriteFile( over + ".png", ksox[over] )
	
	overlays = msgpack.unpackb(kkex['KCOX'][1]['Overlays'], strict_map_key=False)
	for overlay in overlays:
		for key in overlays[overlay]:
			WriteFile("overlays_" + str(overlay) + "_" + str(key) + ".png", overlays[overlay][key][0])
	
	subData = kkex['com.deathweasel.bepinex.materialeditor'][1]['TextureDictionary']
	if subData:
		textures = msgpack.unpackb(subData, strict_map_key=False)
		for texture in textures:
			WriteFile("materialeditor_" + str(texture) + ".png", textures[texture])

	
