
import sys
import msgpack
import struct
import pprint
import io

import hashlib

hideEmpty = True
verbose = True

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
def strShow(value):
	show = ['default', 'no', 'yes']
	return show[value]
	
def slider(value):
	return int(round(value * 100))
	
def summerizeParameters(para):
	print('Name: %s %s  (%s)' % (para['firstname'], para['lastname'], para['nickname']))
	print('Birthday: %d/%d (month/date)' % (para['birthDay'], para['birthMonth']))
	bloodtypes = ['A', 'B', 'O', 'AB']
	print('Bloodtype: %s' % (bloodtypes[para['bloodType']]))
	
def summerizeCoordinateSub(para):
	part1, part2, unknown, extras = para
	
	names = ['Top   ', 'Bottom', 'Bra   ', 'Underwear', 'Gloves', 'Pantyhose', 'Legwear', 'In Shoes', 'Out Shoes']
	
	for info, name in zip(part1['parts'], names):
		if info['id'] != 0:
			colors = '; '.join([strRgb(color['baseColor']) for color in info['colorInfo']])
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
		
def summerizeEye(eye):
	return {
		'Type'              :        eye['id'         ] ,
		'Color 1'           : strRgb(eye['baseColor'  ]),
		'Color 2'           : strRgb(eye['subColor'   ]),
		'Gradient Type'     :        eye['gradMaskId' ] ,
		'Gradient Strenght' : slider(eye['gradBlend'  ]),
		'Gradient Vertical' : slider(eye['gradOffsetY']),
		'Gradient Size'     : slider(eye['gradScale'  ])
	}
def summerizePaint(makeup, id):
	if hideEmpty and makeup['paintId'    ][id] == 0:
		return {}
	return {
			'Type'       :          makeup['paintId'    ][id] ,
			'Color'      : strRgba( makeup['paintColor' ][id]),
			'Hor'        : slider(  makeup['paintLayout'][id][0]),
			'Ver'        : slider(  makeup['paintLayout'][id][1]),
			'Rot'        : slider(  makeup['paintLayout'][id][2]),
			'Size'       : slider(  makeup['paintLayout'][id][3]),
		}
		
def summerizeFace(face):
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
		'Eye Left'  : summerizeEye(face['pupil'][0]),
		'Eye Right' : summerizeEye(face['pupil'][1]),
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
		'Paint 01': summerizePaint(makeup, 0),
		'Paint 02': summerizePaint(makeup, 1),
	}
	
	if hideEmpty and block['Mole']['Type'] == 0:
		block['Mole'] = {}
	
	for key, group in block.items():
		if verbose:
			print('%s:' % key)
			if (len(group.keys())):
				length = max([len(key) for key in group.keys()])
				for key, value in group.items():
					padding = (length - len(key)) * ' '
					print('\t%s: %s%s' % (key, padding, str(value)))
		else:
			print(key + ': ' + '; '.join([str(val) for val in group.values()]))


def summerizeBody(body):
	print('Body General:')
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
	print('   Breast Size:      %3d' %(slider(body['shapeValueBody'][ 4])))
	print('   Breast Ver Pos:   %3d' %(slider(body['shapeValueBody'][ 5])))
	print('   Breast Spacing:   %3d' %(slider(body['shapeValueBody'][ 6])))
	print('   Breast Hor Pos:   %3d' %(slider(body['shapeValueBody'][ 7])))
	print('   Breast Ver Angle: %3d' %(slider(body['shapeValueBody'][ 8])))
	print('   Breast Depth:     %3d' %(slider(body['shapeValueBody'][ 9])))
	print('   Breast Roundness: %3d' %(slider(body['shapeValueBody'][10])))
	print('   Breast Softness:  %3d' %(slider(body['bustSoftness'  ]    )))
	print('   Breast Weight:    %3d' %(slider(body['bustWeight'    ]    )))
	print('   Areola Depth:     %3d' %(slider(body['shapeValueBody'][11])))
	print('   Nipple Thickness: %3d' %(slider(body['shapeValueBody'][12])))
	print('   Nipple Depth:     %3d' %(slider(body['shapeValueBody'][13])))
	print('   Areola Size:      %3d' %(slider(body['areolaSize'    ]    )))
	print('   Nipple type:      %3d' %(       body['nipId'         ] ))
	print('   Nipple Color:     %s'  %(strRgb(body['nipColor'      ])))
	print('   Nipple Gloss:     %3d' %(slider(body['nipGlossPower' ])))
	print('Upper Body:')
	print('   Shoulder Width:        %3d' %(int(round(body['shapeValueBody'][14] * 100))))
	print('   Shoulder Thickness:    %3d' %(int(round(body['shapeValueBody'][15] * 100))))
	print('   Upper Torso Width:     %3d' %(int(round(body['shapeValueBody'][16] * 100))))
	print('   Upper Torso Thickness: %3d' %(int(round(body['shapeValueBody'][17] * 100))))
	print('   Lower Torso Width:     %3d' %(int(round(body['shapeValueBody'][18] * 100))))
	print('   Lower Torso Thickness: %3d' %(int(round(body['shapeValueBody'][19] * 100))))
	print('Lower Body:')
	print('   Waist Position:  %3d' %(slider(body['shapeValueBody'][20])))
	print('   Belly Thickness: %3d' %(slider(body['shapeValueBody'][21])))
	print('   Waist Width:     %3d' %(slider(body['shapeValueBody'][22])))
	print('   Waist Thickness: %3d' %(slider(body['shapeValueBody'][23])))
	print('   Hip Width:       %3d' %(slider(body['shapeValueBody'][24])))
	print('   Hip Thickness:   %3d' %(slider(body['shapeValueBody'][25])))
	print('   Butt Size:       %3d' %(slider(body['shapeValueBody'][26])))
	print('   Butt Angle:      %3d' %(slider(body['shapeValueBody'][27])))
	print('Arms:')
	print('   Shoulder Width:      %3d' %(slider(body['shapeValueBody'][37])))
	print('   Shoulder Thickness:  %3d' %(slider(body['shapeValueBody'][38])))
	print('   Upper Arm Width:     %3d' %(slider(body['shapeValueBody'][39])))
	print('   Upper Arm Thickness: %3d' %(slider(body['shapeValueBody'][40])))
	print('   Elbow Thickness:     %3d' %(slider(body['shapeValueBody'][41])))
	print('   Elbow Width:         %3d' %(slider(body['shapeValueBody'][42])))
	print('   Forearm Thickness:   %3d' %(slider(body['shapeValueBody'][43])))
	print('Legs:')
	print('   Upper Thigh Width:     %3d' %(slider(body['shapeValueBody'][28])))
	print('   Upper Thigh Thickness: %3d' %(slider(body['shapeValueBody'][29])))
	print('   Lower Thigh Width:     %3d' %(slider(body['shapeValueBody'][30])))
	print('   Lower Thigh Thickness: %3d' %(slider(body['shapeValueBody'][31])))
	print('   Knee Width:            %3d' %(slider(body['shapeValueBody'][32])))
	print('   Knee Thickness:        %3d' %(slider(body['shapeValueBody'][33])))
	print('   Calves:                %3d' %(slider(body['shapeValueBody'][34])))
	print('   Ankle Width:           %3d' %(slider(body['shapeValueBody'][35])))
	print('   Ankle Thickness:       %3d' %(slider(body['shapeValueBody'][36])))
	print('Nails:')
	print('   Nails:   %s'  %(strRgb(body['nailColor'])))
	print('   Nail Gloss:       %3d' %(int(round(body['nailGlossPower']     * 100))))
	print('Public Hair:')
	print('   Type:   %d' % (body['underhairId']))
	print('   Color:  %s' % (strRgba(body['underhairColor'])))
	print('Suntan:')
	print('   Type:   %d' % (body['sunburnId']))
	print('   Color:  %s' % (strRgba(body['sunburnColor'])))
		
def summerizeCustom(para):
	face, body, extra = para
	summerizeFace(face)
	print()
	summerizeBody(body)
	

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
	print()
	summerizeCustom(custom)


	#print(kkex)
	
