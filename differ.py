
import sys
import difflib

import subprocess

def getInfo(file):
	proc = subprocess.Popen(["python", "main.py", file], stdout=subprocess.PIPE)
	return proc.communicate()[0]

def similarity(a, b):
	return difflib.SequenceMatcher( None, a, b ).ratio()

files = [getInfo(path) for path in sys.argv[1:]]

for file, path in zip(files, sys.argv[1:]):
	with open(path + '_info.txt', 'wb') as newFile:
		newFile.write(file)

for fileA in files:
	print('\t'.join(['%.2f' % (similarity(fileA, fileB)) for fileB in files]))