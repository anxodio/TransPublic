#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def helloWorld():
	print 'Hello World!'

def insertOrdenat(llista, nou_element):
	for i in range(len(llista)):
		if nou_element <= llista[i]:
			llista.insert(i, nou_element)
			break
	else:
		llista.append(nou_element)

	return llista

if __name__ == '__main__':
	a = [1, 2, 5, 7, 8]
	print a
	a = insertOrdenat(a,1)
	print a