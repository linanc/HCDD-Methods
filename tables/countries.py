"""Generates tables about countries of publication and work. HCD+D Methods."""

import csv
import sys

def parsedata(filename, columns):

	""" Parses dataset.csv and pulls out relevant columns to text file. 
		args: 
					filename, a string with the path to the csv data file
					columns, a list of columns in csv data file to be extracted 
		output:  
					returns string path to text file 
	"""

	with open('out.txt', 'w') as f:
		with open(filename, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			for row in reader:
				if len(columns) > 1:
					retarr = []
					for item in columns: 
						retarr.append(row[item])
					retval = " | ".join(retarr)
					f.write(retval + '\n')
					print(retval)
				else:
					f.write(row[columns[0]] + '\n')
					print(row[columns[0]])
	print("Done! Look for <out.txt> file in your directory.")
	return 'out.txt'


def publication(output):

	""" Creates a CSV table of countries, number of first authors who published there,
		and number of other authors who published there. 
		args: 
					output, a string with the path to the text file output by parsedata
		output: 
					a csv file with desired analysis
	"""

	firstCountries = dict()
	otherCountries = dict()
	done = set()
	count = 0

	with open(output, 'r') as f: 
		for line in f: 
			if count < 2:
				count += 1
				continue

			arrLine = line.split(' | ')
			firstC = arrLine[0].split(',')
			secC = arrLine[1].split(',')
			for country in firstC:
				country = country.lstrip().rstrip().strip('\n')
				if country in firstCountries:
					firstCountries[country] += 1
				else: 
					firstCountries[country] = 1

			for country in secC:
				country = country.lstrip().rstrip().strip('\n')
				if country in otherCountries:
					otherCountries[country] += 1
				else: 
					otherCountries[country] = 1
		print(firstCountries)
		print(otherCountries)


	with open('countries-pub.csv', 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(('Country', 'Number of First Authors', 'Number of Other Authors'))

		for key in firstCountries:
			if key in otherCountries:
				writer.writerow((key, firstCountries[key], otherCountries[key]))
			elif key not in otherCountries:
				writer.writerow((key, firstCountries[key], '0'))
			done.add(key)

		for key in otherCountries:
			if key not in done: 
				if key in firstCountries:
					writer.writerow((key, firstCountries[key], otherCountries[key]))
				elif key not in firstCountries:
					writer.writerow((key, '0', otherCountries[key]))

	print("Done! Look for <countries-pub.csv> file in your directory.")


def work(output): 

	""" Creates a CSV table of countries and their number of mentions as the place of work in a paper. 
		args: 
					output, path to the text file generated by parsedata
		output: 
					a csv file with desired analysis
	"""

	countries = dict()
	count = 0

	with open(output, 'r') as f: 
		for line in f: 
			if count < 2:
				count += 1
				continue
			arrLine = line.split(',')
			for country in arrLine:
				country = country.lstrip().rstrip().strip('\n')
				if country in countries:
					countries[country] += 1
				else: 
					countries[country] = 1

	with open('countries-work.csv', 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(('Country', 'Number of Mentions as Place of Work'))
		for key in countries:
			writer.writerow((key, countries[key]))

	print("Done! Look for <countries-work.csv> file in your directory.")


def main():

	""" Expects csv input, columns, and optional third argument: work or publication. 
	    On the command line type: python countries.py <dataset.csv> <[col,col]> <work or publication>
	    Columns within the csv file are 0-indexed, and make sure there are no spaces when typing [col,col]. 
	"""
	#csv file name
	dataset = sys.argv[1]
	#convert column strings into array
	col = sys.argv[2].strip('[').strip(']')
	arrCol = col.split(',')
	columns = [int(x) for x in arrCol]

	if len(sys.argv) == 2: 
		parsedata(dataset, columns)

	elif len(sys.argv) == 3:
		#optional work or publication option
		option = sys.argv[3]
		textfile = parsedata(dataset, columns)
		if option == "work":
		  	work(textfile)
		elif option == "publication":
			publication(textfile)


if __name__ == "__main__":
	main()