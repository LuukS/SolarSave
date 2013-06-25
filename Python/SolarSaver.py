__author__ = "Luuk Schaminee"
__date__ = "$Jun 13, 2013 8:08 PM$"

"""
 Naam:         SolarSaver.py
 Omschrijving: Opslaan van de gegevens van de zonnepanelen

 Auteur:       Luuk Schaminee

 Versie:       0.1
               - eerste versie
 Datum:        13 juni 2013
 
 Input:        Identifier
               Directory waar de gegevens moeten worden opgeslagen
               Gegevens welke in CVS opgeslagen moeten worden
 Output:       Nieuw of aangevuld CSV-bestand met de losse gegevens: yyyyMMdd_stats_identifier.csv (timestamp, datetime, totaal, temp, pv_out, fout)
               Nieuw of aangevuld CVS-bestand met de daggegevens: daggegevens.csv (jaar,dag,totaal,gem_temp,gem_pv_out)
               Nieuw of aangevuld CSV-bestand met de weekgegevens: weekgegevens.csv (jaar,week,totaal,gem_temp,gem_pv_out)
               Nieuw of aangevuld CSV-bestand met de maandgegevens: maandgegevens.csv (jaar,maand,totaal,gem_temp,gem_pv_out)
               Nieuw of aangevuld CSV-bestand met de jaargegevens: jaargegevens.csv (jaar,week,totaal,gem_temp,gem_pv_out)
"""

import sys,os,csv,collections,time
from time import strftime,localtime

# Timestamp in miliseconds
millis = str(int(round(time.time() * 1000)))

strIdentifier = ''
strTimeStamp = ''
strStats = ''
strInputDirectory = ''
strDateFileName = ''

def processCSV(self,naam, fileobject):
	myReader = csv.reader(fileobject, delimiter=';', quoting=csv.QUOTE_NONE)
	self.processor.processCSV(myReader)

def saveStats(filename,strStats):
	"""
	Sla de losse gegevens op in het bestand yyyyMMdd_stats_identifier.csv
	"""
	blnFileExists = False
	if os.path.exists(filename):
		blnFileExists = True
	
	outputFile = open(filename, 'a')
	if blnFileExists == False:
		outputFile.write('timestamp, datetime, totaal, temp, pv_out, fout\n')
		outputFile.write(strStats + '\n')
	else:
		outputFile.write(strStats + '\n')
	outputFile.close()

def saveDailyData(statsfilename,filename,strDate):
	"""
	Sla de daggegevens op in het bestand daggegevens_identifier.csv
	Bepaal hiervoor de totalen van de dag totnutoe uit de losse gegevens
	De volgende gegevens moeten berekend worden:
	datum,totaal,gem_temp,gem_pv_out
	Doorloop hiervoor de stats file van de opgegeven dag en bereken de gegevens
	Open de daggegevens en controleer of er niet al een record bestaat voor de datum,
	indien niet dan toevoegen, indien wel dan de gegevens aanpassen.
	"""
	StatsRecord = collections.namedtuple('StatsRecord', 'timestamp, datetime, totaal, temp, pv_out, fout')
	DagRecord = collections.namedtuple('StatsRecord', 'datum, totaal, gem_temp, gem_pv_out')
	begintotaal = 0
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	i = 0
	j = 0
	
	blnFileExists = False
	if os.path.exists(statsfilename):
		blnFileExists = True
	
	for loc in map(StatsRecord._make, csv.reader(open(statsfilename,"r"), delimiter=',')):
		i = i + 1
		if i == 2:
			begintotaal = int(totaal)
			gem_temp = gem_temp + int(loc.temp)
			gem_pv_out = gem_pv_out + int(loc.pv_out)
			j = j + 1
		elif  i > 2:
			totaal = int(totaal) + int(loc.totaal)
			gem_temp = gem_temp + int(loc.temp)
			gem_pv_out = gem_pv_out + int(loc.pv_out)
			j = j + 1
		
	totaal = int(totaal) - int(begintotaal)
	print gem_temp
	print j
	gem_temp = gem_temp/j-1
	gem_pv_out = gem_pv_out/j-1
	blnFileExists = False
	if os.path.exists(filename):
		blnFileExists = True
	
	if blnFileExists == False:
		outputFile = open(filename, 'a')
		outputFile.write('datum, totaal, gem_temp, gem_pv_out\n')
		outputFile.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + '\n')
		outputFile.close()
	else:
		# Gaat dit nog snel bij 144 of 1440 records (dit is het aantal records bij metingen per 5 cq 1 minuut)?
		with open(filename, "r") as f:
			oldlines = f.readlines()
			f.close()
		with open(filename, "w") as f:
			for line in oldlines:
				print line
				if strDate == line.split(',')[0]:
					print "aanpassen"
					f.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + '\n')
				else:
					f.write(line)
			f.close()
		#outputFile.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + '\n')

def main():
	#strOutputFileStats = strftime("%Y%m%d%H%M%S") + '_stats_' + strIdentifier + '.csv'
	#strOutputFileStats = strftime("%Y%m%d") + '_stats_' + strIdentifier + '.csv'
	strTimeStamp = strftime("%Y%m%d%H%M%S")
	strOutputFileStats = strDateFileName + '_stats_' + strIdentifier + '.csv'
	strOutputFileDag = 'daggegevens_' + strIdentifier + '.csv'
	strOutputFileWeek = 'weekgegevens_' + strIdentifier + '.csv'
	strOutputFileMaand = 'maandgegevens_' + strIdentifier + '.csv'
	strOutputFileJaarTotalen = 'jaargegevens_' + strIdentifier + '.csv'
	print strOutputFileStats
	print strOutputFileDag
	print strOutputFileWeek
	print strOutputFileMaand
	print strOutputFileJaarTotalen
	saveStats(strInputDirectory +'/' + strOutputFileStats,millis + ',' + strTimeStamp+',120367,61,66,0')
	saveDailyData(strInputDirectory +'/' + strOutputFileStats,strInputDirectory +'/' + strOutputFileDag,strDateFileName)

if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) == 3:
		strIdentifier = args[0]
		strInputDirectory = args[1]
		strStats = args[2]
		strDateFileName = strStats.split(',')[1].split("-")[0] + strStats.split(',')[1].split("-")[1] + strStats.split(',')[1].split("-")[2].split(" ")[0]
	else:
		print
		print 'Geen argumenten opgegeven, dit script heeft drie'
		print 'argument nodig. Dit zijn de identifier, de directory'
		print 'waarin de gegevens moeten worden opgeslagen en de'
		print 'gegevens zelf (timestamp, datetime, totaal, temp, pv_out, fout).'
		print 'Bijvoorbeeld: SolarSaver.py "soladin1" "/data/solar" "1371303031513,2013-06-15 15:30:32,120827,66,485,2048"'

		sys.exit()

	main()
