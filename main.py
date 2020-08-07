
import sys
import msgpack
import struct
import pprint
import io

import hashlib

def filePrefix():
	return sys.argv[1][:-4] + "_"

def WriteFile(path, data):
	with open(filePrefix() + path, "wb") as newFile:
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
	return struct.unpack('<i', file.read(4))[0]
	
def md5(data):
	return "image md5: " +  hashlib.md5(data).hexdigest()
	
def replaceKKex(kkex, mod, entry):
	if mod in kkex and kkex[mod]:
		if entry in kkex[mod][1] and kkex[mod][1][entry]:
			if type(kkex[mod][1][entry]) is bytes:
				kkex[mod][1][entry] = msgpack.unpackb(kkex[mod][1][entry], strict_map_key=False)
	return kkex
	
def parseCoordinate(data):
	f = io.BytesIO(data)
	
	block1 = msgpack.unpackb( f.read(read32u(f)) )
	block2 = msgpack.unpackb( f.read(read32u(f)) )
	padding = f.read(1)
	block3 = msgpack.unpackb( f.read(read32u(f)) )
	return (block1, block2, padding, block3)
	
def parseCustom(data):
	f = io.BytesIO(data)
	
	block1 = msgpack.unpackb( f.read(read32u(f)) )
	block2 = msgpack.unpackb( f.read(read32u(f)) )
	block3 = msgpack.unpackb( f.read(read32u(f)) )
	return (block1, block2, block3)
	

with open(sys.argv[1], "rb") as input_file:
	
	dumpTextures = True
	dumpDataBlocks = False
	
	def convertTexture(name, data):
		if dumpTextures:
			WriteFile(name + '.png', data)
		return "image md5: " +  hashlib.md5(data).hexdigest()
		
	def unpack(data, name=''):
		unpacked = msgpack.unpackb(data, strict_map_key=False)
		if dumpDataBlocks and name:
			WriteFile(name + '.bin', data)
		return unpacked
			
	
	convertTexture("main", ReadPng(input_file))
	
	version = read32u(input_file)
	
	string1len = read32u(input_file)
	string1 = input_file.read(12)
	string2len = read32u(input_file)
	string2 = input_file.read(5)
	
	convertTexture("face", input_file.read(read32u(input_file)))
	
	indexes = msgpack.unpackb( input_file.read(read32u(input_file)) )['lstInfo']
	
	unknown = input_file.read(8)
	
	data = bytearray(input_file.read())
	
	
	blocks = dict()
	for index in indexes:
		pos = index['pos']
		size = index['size']
		blocks[index['name']] = data[pos : pos+size]
	
	
	parameter  = unpack( blocks['Parameter'], 'Parameter' )
	status     = unpack( blocks['Status'], 'Status' )
	coordinate = unpack( blocks['Coordinate'], 'Coordinate' )
	
	coordinate = [parseCoordinate( x ) for x in coordinate]
	custom = parseCustom(blocks['Custom'])
	

	kkex = None
	if 'KKEx' in blocks:
		kkex       = unpack( blocks['KKEx'], 'KKEx' )
		
		autoresolver = kkex['com.bepis.sideloader.universalautoresolver'][1]['info']
		autoresolver = [unpack( val ) for val in autoresolver]
		kkex['com.bepis.sideloader.universalautoresolver'][1]['info'] = autoresolver
		
		
		kkex = replaceKKex(kkex, 'KKABMPlugin.ABMData', 'boneData')
		kkex = replaceKKex(kkex, 'madevil.kk.ass', 'CharaTriggerInfo')
		kkex = replaceKKex(kkex, 'madevil.kk.ass', 'CharaVirtualGroupNames')
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.hairaccessorycustomizer', 'HairAccessories')
		
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.pushup', 'Pushup_BraData')
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.pushup', 'Pushup_TopData')
		
		
		if 'KSOX' in kkex:
			ksox = kkex['KSOX'][1]
			for over in ksox:
				if ksox[over]:
					kkex['KSOX'][1][over] = convertTexture(over, ksox[over])
		
		if 'KCOX' in kkex:
			overlays = msgpack.unpackb(kkex['KCOX'][1]['Overlays'], strict_map_key=False)
			for overlay in overlays:
				for key in overlays[overlay]:
					data = overlays[overlay][key][0]
					overlays[overlay][key][0] = convertTexture("overlays_" + str(overlay) + "_" + str(key), data)
			kkex['KCOX'][1]['Overlays'] = overlays
		
		if 'com.deathweasel.bepinex.materialeditor' in kkex:
			subData = kkex['com.deathweasel.bepinex.materialeditor'][1]
			if subData['TextureDictionary']:
				textures = msgpack.unpackb(subData['TextureDictionary'], strict_map_key=False)
				for texture in textures:
					convertTexture("materialeditor_" + str(texture), textures[texture])
				md5s = [(x, md5(textures[x])) for x in textures]
				kkex['com.deathweasel.bepinex.materialeditor'][1]['TextureDictionary'] = md5s
			
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialShaderList')
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialTexturePropertyList')
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialFloatPropertyList')
		kkex = replaceKKex(kkex, 'com.deathweasel.bepinex.materialeditor', 'MaterialColorPropertyList')
		
		kkex = replaceKKex(kkex, 'marco.authordata', 'Authors')
	
	
	with open(filePrefix() + "settings.txt", "w") as f:
		pprint.pprint(parameter, f)
		pprint.pprint(status, f)
		pprint.pprint(custom, f)
		pprint.pprint(coordinate, f)
		if kkex:
			pprint.pprint(kkex, f)



	#print(kkex)
	