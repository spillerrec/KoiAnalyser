
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
	
def strRgb(values):
	r,g,b,a = values
	return '%3d,%3d,%3d' % (int(r*255), int(g*255), int(b*255))
def strRgba(values):
	r,g,b,a = values
	return '%3d,%3d,%3d,%3d' % (int(r*255), int(g*255), int(b*255), int(a*255))
	
def summerizeParameters(para):
	print('Name: %s %s  (%s)' % (para['firstname'], para['lastname'], para['nickname']))
	print('Birthday: %d/%d (month/date)' % (para['birthDay'], para['birthMonth']))
	bloodtypes = ['A', 'B', 'O', 'AB']
	print('Bloodtype: %s' % (bloodtypes[para['bloodType']]))
	
def summerizeCoordinateSub(para):
	part1, part2, unknown, extras = para
	
	names = ['Top   ', 'Bottom', 'Bra   ', 'Underwear', 'Gloves', 'Pantyhose', 'Legwear', 'In Shoes', 'Out Shoes']
	
	for info, name in zip(part1['parts'], names):
		colors = list([strRgb(color['baseColor']) for color in info['colorInfo']])
		print('   %s\t- id %d - %s' % (name, info['id'], str(colors)))
		
		
	print('   Accessories:')
	for index, part in enumerate(part2['parts']):
		id = part['id']
		if id != 0:
			print('      %2d: id %4d - type %d' % (index, part['id'], part['type']))
	
def summerizeCoordinate(para):
	names = ['In School', 'Going Home', 'Gym Uniform', 'Swimsuit', 'Club Activities', 'Casual Clothes', 'Sleeping Over']
	
	for name, subPara in zip(names, para):
		print(name)
		summerizeCoordinateSub(subPara)
		
def summerizeCustom(para):
	face, body, extra = para
	print('General:')
	print('   Body Height:      %3d' %(int(round(body['shapeValueBody'][ 0] * 100))))
	print('   Head Size:        %3d' %(int(round(body['shapeValueBody'][ 1] * 100))))
	print('   Neck Width:       %3d' %(int(round(body['shapeValueBody'][ 2] * 100))))
	print('   Neck Thickness:   %3d' %(int(round(body['shapeValueBody'][ 3] * 100))))
	print('   Skin Type:        %3d' %(body['detailId']))
	print('   Skin Strenght:    %3d' %(int(round(body['detailPower'   ]     * 100))))
	print('   Skin Color:       %s'  %(strRgb(body['skinMainColor'])))
	print('   Skin Color Sub:   %s'  %(strRgb(body['skinSubColor'])))
	print('   Skin Gloss:       %3d' %(int(round(body['skinGlossPower']     * 100))))
	print('Chest:')
	print('   Breast Size:      %3d' %(int(round(body['shapeValueBody'][ 4] * 100))))
	print('   Breast Ver Pos:   %3d' %(int(round(body['shapeValueBody'][ 5] * 100))))
	print('   Breast Spacing:   %3d' %(int(round(body['shapeValueBody'][ 6] * 100))))
	print('   Breast Hor Pos:   %3d' %(int(round(body['shapeValueBody'][ 7] * 100))))
	print('   Breast Ver Angle: %3d' %(int(round(body['shapeValueBody'][ 8] * 100))))
	print('   Breast Depth:     %3d' %(int(round(body['shapeValueBody'][ 9] * 100))))
	print('   Breast Roundness: %3d' %(int(round(body['shapeValueBody'][10] * 100))))
	print('   Breast Softness:  %3d' %(int(round(body['bustSoftness'  ]     * 100))))
	print('   Breast Weight:    %3d' %(int(round(body['bustWeight'    ]     * 100))))
	print('   Areola Depth:     %3d' %(int(round(body['shapeValueBody'][11] * 100))))
	print('   Nipple Thickness: %3d' %(int(round(body['shapeValueBody'][12] * 100))))
	print('   Nipple Depth:     %3d' %(int(round(body['shapeValueBody'][13] * 100))))
	print('   Areola Size:      %3d' %(int(round(body['areolaSize'    ]     * 100))))
	print('   Nipple type:      %3d' %(body['nipId']))
	print('   Nipple Color:     %s'  %(strRgb(body['nipColor'])))
	print('   Nipple Gloss:     %3d' %(int(round(body['nipGlossPower']     * 100))))
	print('Upper Body:')
	print('   Shoulder Width:        %3d' %(int(round(body['shapeValueBody'][14] * 100))))
	print('   Shoulder Thickness:    %3d' %(int(round(body['shapeValueBody'][15] * 100))))
	print('   Upper Torso Width:     %3d' %(int(round(body['shapeValueBody'][16] * 100))))
	print('   Upper Torso Thickness: %3d' %(int(round(body['shapeValueBody'][17] * 100))))
	print('   Lower Torso Width:     %3d' %(int(round(body['shapeValueBody'][18] * 100))))
	print('   Lower Torso Thickness: %3d' %(int(round(body['shapeValueBody'][19] * 100))))
	print('Lower Body:')
	print('   Waist Position:  %3d' %(int(round(body['shapeValueBody'][20] * 100))))
	print('   Belly Thickness: %3d' %(int(round(body['shapeValueBody'][21] * 100))))
	print('   Waist Width:     %3d' %(int(round(body['shapeValueBody'][22] * 100))))
	print('   Waist Thickness: %3d' %(int(round(body['shapeValueBody'][23] * 100))))
	print('   Hip Width:       %3d' %(int(round(body['shapeValueBody'][24] * 100))))
	print('   Hip Thickness:   %3d' %(int(round(body['shapeValueBody'][25] * 100))))
	print('   Butt Size:       %3d' %(int(round(body['shapeValueBody'][26] * 100))))
	print('   Butt Angle:      %3d' %(int(round(body['shapeValueBody'][27] * 100))))
	print('Arms:')
	print('   Shoulder Width:      %3d' %(int(round(body['shapeValueBody'][37] * 100))))
	print('   Shoulder Thickness:  %3d' %(int(round(body['shapeValueBody'][38] * 100))))
	print('   Upper Arm Width:     %3d' %(int(round(body['shapeValueBody'][39] * 100))))
	print('   Upper Arm Thickness: %3d' %(int(round(body['shapeValueBody'][40] * 100))))
	print('   Elbow Thickness:     %3d' %(int(round(body['shapeValueBody'][41] * 100))))
	print('   Elbow Width:         %3d' %(int(round(body['shapeValueBody'][42] * 100))))
	print('   Forearm Thickness:   %3d' %(int(round(body['shapeValueBody'][43] * 100))))
	print('Legs:')
	print('   Upper Thigh Width:     %3d' %(int(round(body['shapeValueBody'][28] * 100))))
	print('   Upper Thigh Thickness: %3d' %(int(round(body['shapeValueBody'][29] * 100))))
	print('   Lower Thigh Width:     %3d' %(int(round(body['shapeValueBody'][30] * 100))))
	print('   Lower Thigh Thickness: %3d' %(int(round(body['shapeValueBody'][31] * 100))))
	print('   Knee Width:            %3d' %(int(round(body['shapeValueBody'][32] * 100))))
	print('   Knee Thickness:        %3d' %(int(round(body['shapeValueBody'][33] * 100))))
	print('   Calves:                %3d' %(int(round(body['shapeValueBody'][34] * 100))))
	print('   Ankle Width:           %3d' %(int(round(body['shapeValueBody'][35] * 100))))
	print('   Ankle Thickness:       %3d' %(int(round(body['shapeValueBody'][36] * 100))))
	print('Nails:')
	print('   Nails:   %s'  %(strRgb(body['nailColor'])))
	print('   Nail Gloss:       %3d' %(int(round(body['nailGlossPower']     * 100))))
	print('Public Hair:')
	print('   Type:   %d' % (body['underhairId']))
	print('   Color:  %s' % (strRgba(body['underhairColor'])))
	print('Suntan:')
	print('   Type:   %d' % (body['sunburnId']))
	print('   Color:  %s' % (strRgba(body['sunburnColor'])))
	

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

	summerizeParameters(parameter)
	print()
	summerizeCoordinate(coordinate)
	summerizeCustom(custom)


	#print(kkex)
	
