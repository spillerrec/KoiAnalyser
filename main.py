
import sys
import msgpack
import struct
import pprint
import io

import hashlib

def read32u(file):
	return struct.unpack('<i', file.read(4))[0]
	
def md5(data):
	if not data:
		return "no image"
	return "image md5: " +  hashlib.md5(data).hexdigest()


def replaceKKex(kkex, mod, entry):
	if mod in kkex and kkex[mod]:
		if entry in kkex[mod][1] and kkex[mod][1][entry]:
			if type(kkex[mod][1][entry]) is bytes:
				kkex[mod][1][entry] = msgpack.unpackb(kkex[mod][1][entry], strict_map_key=False)
	return kkex
	


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
def strShow(value):
	show = ['default', 'no', 'yes']
	return show[value]
	
def slider(value):
	return int(round(value * 100))




class KoiCharaFile:
	def __init__(self, filepath, verbose, hideEmpty, dumpTextures=False, dumpDataBlocks=False):
		self.filepath = filepath
		self.verbose = verbose
		self.hideEmpty = hideEmpty
		self.dumpTextures = dumpTextures
		self.dumpDataBlocks = dumpDataBlocks
		
		self.raw = {}
		self.summery = {}
		
		self.parseFile()
		

	def filePrefix(self):
		return self.filepath[:-4] + "_"

	def WriteFile(self, path, data):
		with open(self.filePrefix() + path, "wb") as newFile:
			newFile.write(data)
	
	
	def printCharaSettings(self, block, out):
		for key, group in block.items():
			if self.verbose:
				if (len(group.keys())):
					print('%s:' % key, file=out)
					length = max([len(key) for key in group.keys()])
					for key, value in group.items():
						padding = (length - len(key)) * ' '
						print('\t%s: %s%s' % (key, padding, str(value)), file=out)
			else:
				if len(group) > 0:
					print(key + ': ' + '; '.join([str(val) for val in group.values()]), file=out)
		
	def summerizeParameters(self, para):
		bloodtypes = ['A', 'B', 'O', 'AB']
		clubs = ['Going Home', 'Swimming', 'Manga', 'Cheerleading', 'Tea Ceremony', 'Track & Field']
		return {
			'Character' : {
					'Name'        : para['firstname'],
					'Surname'     : para['lastname'],
					'Nick'        : para['nickname'],
					'Personality' : para['personality'], #TODO: parse
					'Blood Type'  : bloodtypes[para['bloodType']],
					'Birthday'    : '%d/%d' % (para['birthDay'], para['birthMonth']),
					'Club'        : clubs[para['clubActivities']],
					'Voice Pitch' : para['voiceRate'],
				},
			'H-Scene' : {
					
				},
			'Nature' : {
					
				},
			'Traits' : {
					
				},
		}
		
	def getClothesNames(self):
		return ['In School', 'Going Home', 'Gym Uniform', 'Swimsuit', 'Club Activities', 'Casual Clothes', 'Sleeping Over']
	
	def parseColorTile(self, colorInfo):
		block = {
			'color'   : strRgb(colorInfo['baseColor']),
			'pattern' : colorInfo['pattern'],
			'tiling'  : colorInfo['tiling'],
			'color2'  : strRgb(colorInfo['patternColor']),
		}
		if self.hideEmpty and block['pattern'] == 0:
			return block['color']
		else:
			return block
	
	def summerizeCoordinateSub(self, para):
		part1, part2, unknown, extras = para
		
		names = ['Top', 'Bottom', 'Bra', 'Underwear', 'Gloves', 'Pantyhose', 'Legwear', 'In Shoes', 'Out Shoes']
		
		clothes = {}
		for info, name in zip(part1['parts'], names):
			if not (self.hideEmpty and info['id']==0):
				clothes[name] = {
					'id' : info['id'],
					'colors' : [ self.parseColorTile(color) for color in info['colorInfo'] ],
					'emblemeId' : info['emblemeId']
				}
		
		accesories = []
		for index, part in enumerate(part2['parts']):
			accessory = {
				'id'     : part['id'],
				'pos'    : part['addMove'][2][0],
				'rot'    : part['addMove'][2][1],
				'scale'  : part['addMove'][2][2],
				'colors' : [strRgba(c) for c in part['color']]
			}
			if accessory['id'] == 0 and self.hideEmpty:
				accessory = {}
			accesories.append( accessory )
		
		return {
				'Clothes' : clothes,
				'Accessories' : accesories
			}
		
	def summerizeCoordinate(self, para):
		names = self.getClothesNames()
		block = {}
		for name, subPara in zip(names, para):
			block[name] = self.summerizeCoordinateSub(subPara)
		return block
			
	def summerizeEye(self, eye):
		return {
			'Type'              :        eye['id'         ] ,
			'Color 1'           : strRgb(eye['baseColor'  ]),
			'Color 2'           : strRgb(eye['subColor'   ]),
			'Gradient Type'     :        eye['gradMaskId' ] ,
			'Gradient Strenght' : slider(eye['gradBlend'  ]),
			'Gradient Vertical' : slider(eye['gradOffsetY']),
			'Gradient Size'     : slider(eye['gradScale'  ])
		}
		
	def summerizePaint(self, makeup, id):
		if self.hideEmpty and makeup['paintId'    ][id] == 0:
			return {}
		block = {
				'Type'       :          makeup['paintId'    ][id] ,
				'Color'      : strRgba( makeup['paintColor' ][id]),
				'Hor'        : slider(  makeup['paintLayout'][id][0]),
				'Ver'        : slider(  makeup['paintLayout'][id][1]),
				'Rot'        : slider(  makeup['paintLayout'][id][2]),
				'Size'       : slider(  makeup['paintLayout'][id][3]),
			}
		if 'paintLayoutId' in makeup:
			block['PosId'] = slider( makeup['paintLayoutId'][id] )
		return block
			
	def summerizeFace(self, face):
		values = [slider(x) for x in face['shapeValueFace']]
		makeup = face['baseMakeup']
		block = {
			'Face General': {
					'Head Type'             : face['headId'],
					'Face Width'            : values[ 0],
					'Upper Face Depth'      : values[ 1],
					'Upper Face Height'     : values[ 2],
					'Upper Face Size'       : values[ 3],
					'Lower Face Depth'      : values[ 4],
					'Lower Face Width'      : values[ 5],
					'Face Overlay Type'     : face['detailId'],
					'Face Overlay Strenght' : slider(face['detailPower'])
				},
			'Ears': {
					'Ears Size'       : values[47],
					'Ears Angle Y'    : values[48],
					'Ears Angle Z'    : values[49],
					'Upper Ear Shape' : values[50],
					'Lower Ear Shape' : values[51]
				},
			'Jaw': {
					'Lower Jaw Ver Pos' : values[ 6],
					'Lower Jaw Depth'   : values[ 7],
					'Jaw Vertical Pos'  : values[ 8],
					'Jaw Width'         : values[ 9],
					'Jaw Depth'         : values[10],
					'Chin Vertical Pos' : values[11],
					'Chin Depth'        : values[12],
					'Chin Width'        : values[13]
				},
			'Cheeks': {
					'Cheekbone Width' : values[14],
					'Cheekbone Depth' : values[15],
					'Cheek Width'     : values[16],
					'Cheek Depth'     : values[17],
					'Cheek Ver Pos'   : values[18],
					'Cheek Gloss'     : slider(face['cheekGlossPower'])
				},
			'Eyebrows': {
					'Eyebrow Ver Pos'     : values[19],
					'Eyebrow Spacing'     : values[20],
					'Eyebrow Angle'       : values[21],
					'Inner Eyebrow Shape' : values[22],
					'Outer Eyebrow Shape' : values[23],
					'Eyebrow Type'        : face['eyebrowId'],
					'Eyebrow Color'       : strRgb(face['eyebrowColor']),
					'Show Through Hair'   : strShow(face['foregroundEyebrow'])
				},
			'Eyes': {
					'Upper Eyelid Shape 1'    : values[24],
					'Upper Eyelid Shape 2'    : values[25],
					'Upper Eyelid Shape 3'    : values[26],
					'Lower Eyelid Shape 1'    : values[27],
					'Lower Eyelid Shape 2'    : values[28],
					'Lower Eyelid Shape 3'    : values[29],
					'Eye Vertical Position'   : values[30],
					'Eye Spacing'             : values[31],
					'Eye Depth'               : values[32],
					'Eye Rotation'            : values[33],
					'Eye Height'              : values[34],
					'Eye Width'               : values[35],
					'Inner Eye Corner Height' : values[36],
					'Outer Eye Corner Height' : values[37],
					'Upper Eyeliner Type'     : face['eyelineUpId'],
					'Lower Eyeliner Type'     : face['eyelineDownId'],
					'Eyeliner Color'          : strRgb(face['eyelineColor'])
				},
			'Iris': {
					'Sclera Type'          :         face['whiteId'       ] ,
					'Sclera Color 1'       : strRgb( face['whiteBaseColor']),
					'Sclera Color 2'       : strRgb( face['whiteSubColor' ]),
					'Upper Highlight Type' :         face['hlUpId'        ] ,
					'Upper Highlight Ver'  : slider( face['hlUpY'         ]),
					'Upper Highlight Color': strRgba(face['hlUpColor'     ]),
					'Lower Highlight Type' :         face['hlDownId'      ] ,
					'Lower Highlight Ver'  : slider( face['hlDownY'       ]),
					'Lower Highlight Color': strRgba(face['hlDownColor'   ]),
					'Iris Spacing'         : slider( face['pupilX'        ]),
					'Iris Ver Pos'         : slider( face['pupilY'        ]),
					'Iris Width'           : slider( face['pupilWidth'    ]),
					'Iris Height'          : slider( face['pupilHeight'   ]),
					'Shows Through Hair'   : strShow(face['foregroundEyes'])
				},
			'Eye Left'  : self.summerizeEye(face['pupil'][0]),
			'Eye Right' : self.summerizeEye(face['pupil'][1]),
			'Nose': {
					'Tip Height'   : values[38],
					'Vertical Pos' : values[39],
					'Ridge Height' : values[40],
					'Nose Type'    : face['noseId'],
				},
			'Mouth': {
					'Mouth Vetical Pos'  : values[41],
					'Mouth Width'        : values[42],
					'Mouth Depth'        : values[43],
					'Upper Lip Depth'    : values[44],
					'Lower Lip Depth'    : values[45],
					'Mouth Corner Shape' : values[46],
					'Lip Line Type'      :         face['lipLineId'    ],
					'Lip Line Color'     : strRgba(face['lipLineColor' ]),
					'Lip Gloss'          : slider( face['lipGlossPower']),
					'Fangs'              :         face['doubleTooth'  ],
				},
			'Mole': {
					'Type'    :         face['lipLineId'    ],
					'Color'   : strRgba(face['moleColor' ]),
					'Hor Pos' : slider( face['moleLayout'][0]),
					'Ver Pos' : slider( face['moleLayout'][1]), # [2]? [0] and [3] was the same for card tested...
					'Size'    : slider( face['moleLayout'][3]),
				},
			'Makeup': {
					'Eyeshadow Type'  :          makeup['eyeshadowId'   ] ,
					'Eyeshadow Color' : strRgba( makeup['eyeshadowColor']),
					'Cheek Type'      :          makeup['cheekId'       ] ,
					'Cheek Color'     : strRgba( makeup['cheekColor'    ]),
					'Lip Type'        :          makeup['lipId'         ] ,
					'Lip Color'       : strRgba( makeup['lipColor'      ]),
				},
			'Paint 01': self.summerizePaint(makeup, 0),
			'Paint 02': self.summerizePaint(makeup, 1),
		}
		
		if self.hideEmpty and block['Mole']['Type'] == 0:
			block['Mole'] = {}
		
		return block
		
	def summerizeBody(self, body):
		values = [slider(x) for x in body['shapeValueBody']]
		block = {
			'Body General' : {
					'Body Height:      ' : values[ 0],
					'Head Size:        ' : values[ 1],
					'Neck Width:       ' : values[ 2],
					'Neck Thickness:   ' : values[ 3],
					'Skin Type:        ' :        body['detailId'      ] ,
					'Skin Strenght:    ' : slider(body['detailPower'   ]),
					'Skin Color:       ' : strRgb(body['skinMainColor' ]),
					'Skin Color Sub:   ' : strRgb(body['skinSubColor'  ]),
					'Skin Gloss:       ' : slider(body['skinGlossPower']),
			},
			'Chest' : {
					'Breast Size:    ' : values[ 4],
					'Breast Ver Pos: ' : values[ 5],
					'Breast Spacing: ' : values[ 6],
					'Breast Hor Pos: ' : values[ 7],
					'Breast Ver Angle' : values[ 8],
					'Breast Depth:   ' : values[ 9],
					'Breast Roundness' : values[10],
					'Breast Softness:' : slider(body['bustSoftness'  ]),
					'Breast Weight:  ' : slider(body['bustWeight'    ]),
					'Areola Depth:   ' : values[11],
					'Nipple Thickness' : values[12],
					'Nipple Depth:   ' : values[13],
					'Areola Size:    ' : slider(body['areolaSize'    ]),
					'Nipple type:    ' :        body['nipId'         ] ,
					'Nipple Color:   ' : strRgb(body['nipColor'      ]),
					'Nipple Gloss:   ' : slider(body['nipGlossPower' ]),
			},
			'Upper Body' : {
					'Shoulder Width:      ' : values[14],
					'Shoulder Thickness:  ' : values[15],
					'Upper Torso Width:   ' : values[16],
					'Upper Torso Thickness' : values[17],
					'Lower Torso Width:   ' : values[18],
					'Lower Torso Thickness' : values[19],
			},
			'Lower Body' : {
					'Waist Position:' : values[20],
					'Belly Thickness' : values[21],
					'Waist Width:   ' : values[22],
					'Waist Thickness' : values[23],
					'Hip Width:     ' : values[24],
					'Hip Thickness: ' : values[25],
					'Butt Size:     ' : values[26],
					'Butt Angle:    ' : values[27],
			},
			'Arms' : {
					'Shoulder Width:    ' : values[37],
					'Shoulder Thickness:' : values[38],
					'Upper Arm Width:   ' : values[39],
					'Upper Arm Thickness' : values[40],
					'Elbow Thickness:   ' : values[41],
					'Elbow Width:       ' : values[42],
					'Forearm Thickness: ' : values[43],
			},
			'Legs' : {
					'Upper Thigh Width:   ' : values[28],
					'Upper Thigh Thickness' : values[29],
					'Lower Thigh Width:   ' : values[30],
					'Lower Thigh Thickness' : values[31],
					'Knee Width:          ' : values[32],
					'Knee Thickness:      ' : values[33],
					'Calves:              ' : values[34],
					'Ankle Width:         ' : values[35],
					'Ankle Thickness:     ' : values[36],
			},
			'Nails' : {
					'Nails'      : strRgb(body['nailColor'     ]),
					'Nail Gloss' : slider(body['nailGlossPower']),
			},
			'Public Hair' : {
					'Type'  :         body['underhairId'   ] ,
					'Color' : strRgba(body['underhairColor']),
			},
			'Suntan' : {
					'Type'  :         body['sunburnId'   ] ,
					'Color' : strRgba(body['sunburnColor']),
			},
			'Paint 01': self.summerizePaint(body, 0),
			'Paint 02': self.summerizePaint(body, 1),
		}
		
		if self.hideEmpty:
			if block['Suntan']['Type'] == 0:
				block['Suntan'] = {}
			if block['Public Hair']['Type'] == 0:
				block['Public Hair'] = {}
		
		return block
			
	def summerizeCustom(self, para):
		face, body, extra = para
		return {
				'Face': self.summerizeFace(face),
				'Body': self.summerizeBody(body),
			}
			
	def printCustom(self, block, out):
		self.printCharaSettings(block['Face'], out)
		print('', file=out)
		self.printCharaSettings(block['Body'], out)
			
	def printAccessory(self, accessory, out):
		pos   = '%.1f %.1f %.1f' % (accessory['pos'][0], accessory['pos'][1], accessory['pos'][2])
		rot   = '%.0f %.0f %.0f' % (accessory['rot'][0], accessory['rot'][1], accessory['rot'][2])
		scale = '%.2f %.2f %.2f' % (accessory['scale'][0], accessory['scale'][1], accessory['scale'][2])
		print('\tAccessory %4d: - %s - %s - %s - %s' % (accessory['id'], pos, rot, scale, '; '.join(accessory['colors'])), file=out)
		
	def printCoordinate(self, block, out):
		for key, value in block.items():
			print(key + ':', file=out)
			for part, settings in value['Clothes'].items():
				print('\t' + part + ': ' + str(settings), file=out)
			
			for index, settings in enumerate(value['Accessories']):
				if settings:
					self.printAccessory(settings, out)
					#print('Accesory %2d: ' % (index) + str(settings), file=out)
		

	def parseFile(self):
		blocks = dict()
	
		with open(self.filepath, "rb") as input_file:
			def convertTexture(name, data):
				if self.dumpTextures:
					WriteFile(name + '.png', data)
				return md5(data)
				
			def unpack(data, name=''):
				unpacked = msgpack.unpackb(data, strict_map_key=False)
				if self.dumpDataBlocks and name:
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
		
		self.raw = {
				'Parameter' : parameter,
				'Status' : status,
				'Custom' : custom,
				'Coordinate' : coordinate,
				'KKex' : kkex
			}
		
		with open(self.filePrefix() + "settings.txt", "w", encoding="utf-8") as f:
			pprint.pprint(parameter, f)
			pprint.pprint(status, f)
			pprint.pprint(custom, f)
			pprint.pprint(coordinate, f)
			if kkex:
				pprint.pprint(kkex, f)

		self.summery['Parameter'] = self.summerizeParameters(self.raw['Parameter'])
		self.summery['Custom'] = self.summerizeCustom(custom)
		self.summery['Coordinate'] = self.summerizeCoordinate(coordinate)
		
	def printSummery(self, out = sys.stdout):
		self.printCharaSettings(self.summery['Parameter'], out)
		print('', file=out)
		self.printCoordinate(self.summery['Coordinate'], out)
		print('', file=out)
		self.printCustom(self.summery['Custom'], out)
		
	def printSummeryParameters(self, out = sys.stdout):
		self.printCharaSettings(self.summery['Parameter'], out)
		
	def printSummeryCustom(self, out = sys.stdout):
		self.printCustom(self.summery['Custom'], out)
		
	def printSummeryCoordinate(self, out = sys.stdout):
		self.summerizeCoordinate(self.raw['Coordinate'], out)
		
	def printSummeryCoordinateIndex(self, index, out = sys.stdout):
		self.summerizeCoordinateSub(self.raw['Coordinate'][index], out)


if __name__ == "__main__":
	KoiCharaFile(sys.argv[1], True, True).printSummery()