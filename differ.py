
import io
import sys
import difflib
import colorama

import subprocess

from main import KoiCharaFile

def getParameters(chara):
	output = io.StringIO()
	chara.printSummeryParameters(output)
	contents = output.getvalue()
	output.close()
	return contents.encode('utf-8')

def getCustom(chara):
	output = io.StringIO()
	chara.printSummeryCustom(output)
	contents = output.getvalue()
	output.close()
	return contents.encode('utf-8')

def getCoordinate(chara):
	output = io.StringIO()
	chara.printSummeryCoordinate(output)
	contents = output.getvalue()
	output.close()
	return contents.encode('utf-8')

def getCoordinateIndex(chara, index):
	output = io.StringIO()
	chara.printSummeryCoordinateIndex(index, output)
	contents = output.getvalue()
	output.close()
	return contents.encode('utf-8')

def similarity(a, b):
	return difflib.SequenceMatcher( None, a, b ).ratio()
	
def colorNumber(number):
	string = '%.2f' % (number)
	if number > 0.8:
		return colorama.Back.GREEN + string + colorama.Back.BLACK
	if number > 0.7:
		return colorama.Back.BLUE + colorama.Style.BRIGHT + string + colorama.Back.BLACK + colorama.Style.RESET_ALL
	if number > 0.6:
		return colorama.Back.BLUE + string + colorama.Back.BLACK
	if number > 0.5:
		return colorama.Back.MAGENTA + string + colorama.Back.BLACK
	if number > 0.3:
		return colorama.Back.RED + string + colorama.Back.BLACK
	return string
	
def compareMatrix(strings):
	for fileA in strings:
		print(' '.join([colorNumber(similarity(fileA, fileB)) for fileB in strings]))
	

colorama.init()

for x in [x * 0.1 for x in range(0, 10)]:
	print(colorNumber(x))

charas = [KoiCharaFile(path, verbose=False, hideEmpty=True) for path in sys.argv[1:]]

print('Character info:')
compareMatrix([getParameters(chara) for chara in charas])

print('\nParameters:')
compareMatrix([getCustom(chara) for chara in charas])

names = charas[0].getClothesNames()
for i, name in enumerate(names):
	print('\n%s:' % (name))
	compareMatrix([getCoordinateIndex(chara, i) for chara in charas])

for file, path in zip(charas, sys.argv[1:]):
	output = io.StringIO()
	KoiCharaFile(path, verbose=True, hideEmpty=True).printSummery(output)
	contents = output.getvalue()
	output.close()
	with open(path + '_info.txt', 'wb') as newFile:
		newFile.write(contents.encode('utf-8'))
