
import io
import sys
import difflib
import colorama
import itertools

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

def commonPrefix(strings):
	return ''.join(c[0] for c in itertools.takewhile(lambda x: 
			all(x[0] == y for y in x), zip(*strings))) 

names = sys.argv[1:]

names = [name[len(commonPrefix(names)):-4] for name in names]

charas = [KoiCharaFile(path, verbose=False, hideEmpty=False) for path in sys.argv[1:]]

print('Character info:')
compareMatrix([getParameters(chara) for chara in charas])

print('\nParameters:')
compareMatrix([getCustom(chara) for chara in charas])

#names = charas[0].getClothesNames()
#for i, name in enumerate(names):
#	print('\n%s:' % (name))
#	compareMatrix([getCoordinateIndex(chara, i) for chara in charas])
		

def matrixCoor(length):
	l = []
	for x in range(0, length):
		for y in range(x+1, length):
			l.append( (x, y) )
	return l
	
def isSame():
	return colorama.Fore.GREEN + '☑ ' + colorama.Fore.WHITE
	
def isDifferent():
	return colorama.Fore.RED + '☒ ' + colorama.Fore.WHITE
	
def isSimilar():
	return colorama.Fore.WHITE + '☐ ' + colorama.Fore.WHITE
	
def isAdded():
	return colorama.Fore.RED + '+ ' + colorama.Fore.WHITE
	
def isRemoved():
	return colorama.Fore.RED + '+ ' + colorama.Fore.WHITE
	
def compareItem(A, B):
	if A['id'] == 0 and B['id'] == 0:
		return '  '
	elif A['id'] == B['id']:
		if A == B:
			return isSame()
		else:
			return isSimilar()
	elif A['id'] == 0:
		return isAdded()
	elif B['id'] == 0:
		return isRemoved()
	else:
		return isDifferent()
		
def compare(a, b):
	coorA = a.summery['Coordinate']
	coorB = b.summery['Coordinate']
	
	length = max([len(key) for key in coorA.keys()])
	for name, a, b in zip(coorA.keys(), coorA.values(), coorB.values()):
		str = ''
		for A, B in zip(a['Clothes'].values(), b['Clothes'].values()):
			str += compareItem(A, B)
				
		str += '  ;  '
		for A, B in itertools.zip_longest(a['Accessories'], b['Accessories'], fillvalue={}):
			str += compareItem(A, B)
		
		padding = (length - len(name)) * ' '
		print('\t' + name + ': ' + padding + str)

print(isSame() + ' Identical')
print(isSimilar() + ' Same item')
print(isAdded() + ' Missing in card 1')
print(isRemoved() + ' Missing in card 2')
print(isDifferent() + ' Different item')

for x, y in matrixCoor(len(charas)):
	print('%s vs %s:' % (names[x], names[y]))
	compare(charas[x], charas[y])
	print('')

for file, path in zip(charas, sys.argv[1:]):
	output = io.StringIO()
	KoiCharaFile(path, verbose=True, hideEmpty=True).printSummery(output)
	contents = output.getvalue()
	output.close()
	with open(path + '_info.txt', 'wb') as newFile:
		newFile.write(contents.encode('utf-8'))