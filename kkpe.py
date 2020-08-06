
import sys
import msgpack
import struct
import pprint

import hashlib

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
	
def md5(data):
	return "image md5: " +  hashlib.md5(data).hexdigest()
	
def replaceKKex(kkex, mod, entry):
	if mod in kkex and kkex[mod]:
		if entry in kkex[mod][1] and kkex[mod][1][entry]:
			kkex[mod][1][entry] = msgpack.unpackb(kkex[mod][1][entry], strict_map_key=False)
	return kkex
	

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
	
	
	autoresolver = kkex['com.bepis.sideloader.universalautoresolver'][1]['info']
	autoresolver = [msgpack.unpackb( val ) for val in autoresolver]
	kkex['com.bepis.sideloader.universalautoresolver'][1]['info'] = autoresolver
	
	
	kkex = replaceKKex(kkex, 'KKABMPlugin.ABMData', 'boneData')
	kkex = replaceKKex(kkex, 'madevil.kk.ass', 'CharaTriggerInfo')
	kkex = replaceKKex(kkex, 'madevil.kk.ass', 'CharaVirtualGroupNames')
	kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.hairaccessorycustomizer', 'HairAccessories')
	
	kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.pushup', 'Pushup_BraData')
	kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.pushup', 'Pushup_TopData')
	
	
	WriteFile('kkex', blocks['KKEx'])
	
	ksox = kkex['KSOX'][1]
	for over in ksox:
		if ksox[over]:
			WriteFile( over + ".png", ksox[over] )
			kkex['KSOX'][1][over] = md5(ksox[over])
	
	overlays = msgpack.unpackb(kkex['KCOX'][1]['Overlays'], strict_map_key=False)
	for overlay in overlays:
		for key in overlays[overlay]:
			data = overlays[overlay][key][0]
			WriteFile("overlays_" + str(overlay) + "_" + str(key) + ".png", data)
			overlays[overlay][key][0] = md5(data)
	kkex['KCOX'][1]['Overlays'] = overlays
	
	subData = kkex['com.deathweasel.bepinex.materialeditor'][1]
	if subData['TextureDictionary']:
		textures = msgpack.unpackb(subData['TextureDictionary'], strict_map_key=False)
		for texture in textures:
			WriteFile("materialeditor_" + str(texture) + ".png", textures[texture])
		md5s = [(x, md5(textures[x])) for x in textures]
		kkex['com.deathweasel.bepinex.materialeditor'][1]['TextureDictionary'] = md5s
		
	kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialShaderList')
	kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialTexturePropertyList')
	kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialFloatPropertyList')
	
	kkex = replaceKKex(kkex, 'marco.authordata', 'Authors')
	
	
	pprint.pprint(kkex)

	#print(kkex)
	
