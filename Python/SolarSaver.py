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
               Nieuw of aangevuld CVS-bestand met de daggegevens: daggegevens_identifier.csv (datum,totaal,gem_temp,gem_pv_out)
               Nieuw of aangevuld CSV-bestand met de weekgegevens: weekgegevens_identifier.csv (jaar,week,totaal,gem_temp,gem_pv_out)
               Nieuw of aangevuld CSV-bestand met de maandgegevens: maandgegevens_identifier.csv (jaar,maand,totaal,gem_temp,gem_pv_out)
               Nieuw of aangevuld CSV-bestand met de jaargegevens: jaargegevens_identifier.csv (jaar,totaal,gem_temp,gem_pv_out)
"""

import sys,os,csv,collections,time,datetime
from time import strftime,localtime

# Timestamp in miliseconds
millis = str(int(round(time.time() * 1000)))

strIdentifier = ''
strTimeStamp = ''
strStats = ''
strInputDirectory = ''
strDateForFileName = ''
tmeDateForFileName = time.time()
blnDebug = False

def processCSV(self,naam, fileobject):
	myReader = csv.reader(fileobject, delimiter=';', quoting=csv.QUOTE_NONE)
	self.processor.processCSV(myReader)

def saveStats(filename,strStats):
	"""
	Sla de losse gegevens op in het bestand yyyyMMdd_stats_identifier.csv
	De eerste parameter bevat de naam van het bestand, de tweede parameter bevat de
	gegevens welke opgeslagen moeten worden in het bestand.
	Eerst een controle uitvoeren of het bestand bestaat. Is dat niet het geval dan moet
	nadat het bestand aangemaakt is als eerste een regel met de veldnamen toegevoegd
	worden aan het bestand en daarna de gegevens zelf.
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
	strPeriod = "daily"
	StatsRecord = collections.namedtuple('StatsRecord', 'timestamp, datetime, totaal, temp, pv_out, fout')
	DagRecord = collections.namedtuple('StatsRecord', 'datum, totaal, gem_temp, gem_pv_out')
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	totaal_pv_out = 0

	sommatie = sommeerDailyData(statsfilename,[strDate],strPeriod)
	totaal = sommatie[0]
	gem_temp = sommatie [1]
	gem_pv_out = sommatie [2]
	totaal_pv_out = sommatie [3]
	blnFileExists = False
	if os.path.exists(filename):
		blnFileExists = True
	
	if blnFileExists == False:
		outputFile = open(filename, 'a')
		outputFile.write('datum, totaal, gem_temp, gem_pv_out,totaal_pv_out\n')
		outputFile.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
		outputFile.close()
	else:
		# Gaat dit nog snel bij 144 of 1440 records (dit is het aantal records bij metingen per 5 cq 1 minuut)?
		blnDaggevonden = False
		with open(filename, "r") as f:
			oldlines = f.readlines()
			f.close()
		with open(filename, "w") as f:
			for line in oldlines:
				print line
				if strDate == line.split(',')[0]:
					print "aanpassen"
					blnDaggevonden = True
					f.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
				else:
					f.write(line)
			if blnDaggevonden == False:
				f.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
			f.close()
		#outputFile.write(strDate + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + '\n')

def saveWeeklyData(dailyfilename,filename,strDate):
	"""
	Sla de weekgegevens op in het bestand weekgegevens_identifier.csv
	Bepaal hiervoor de totalen van de week totnutoe uit de dag gegevens
	De volgende gegevens moeten berekend worden:
	jaar,week,totaal,gem_temp,gem_pv_out
	Doorloop hiervoor de dag file van de opgegeven week en bereken de gegevens voor deze
	week.
	Open de weekgegevens en controleer of er niet al een record bestaat voor de week,
	indien niet dan toevoegen, indien wel dan de gegevens aanpassen.
	Tevens moet op basis van de datum bepaald worden welke week het is en welke andere
	dagen behoren tot deze week waarbij een week begint op maandag.
	"""
	strPeriod = "weekly"
	intWeeknummer = getWeekNummer(strDate)
	intJaar = getJaar(strDate)
	daysInWeek = getDaysInWeek(strDate)
	blnFileExists = False
	if os.path.exists(filename):
		blnFileExists = True
	
	# Doorloop de statistieken van de dagen welke in de week vallen en sommeer
	# de waarden om ze daarna op te slaan in het weekbestand als nieuwe record
	# of de waarde van een bestaand record aanpassen
	strBestand = ""
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	totaal_pv_out = 0
	sommatie = []
	sommatie = sommeerDailyData(dailyfilename,daysInWeek,strPeriod)
	totaal = sommatie[0]
	gem_temp = sommatie [1]
	gem_pv_out = sommatie [2]
	totaal_pv_out = sommatie [3]

	if blnFileExists == False:
		outputFile = open(filename, 'a')
		outputFile.write('jaar,week,totaal,gem_temp,gem_pv_out,totaal_pv_out\n')
		outputFile.write(str(strftime("%Y", tmeDateForFileName)) + ',' + str(intWeeknummer) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
		outputFile.close()
	else:
		# Kijk in het bestaande bestand of de weekgegevens al bestaan, zo niet dan toevoegen, indien wel dan aanpassen
		with open(filename, "r") as f:
			oldlines = f.readlines()
			f.close()
		
		i = 0
		blnWeekgevonden = False
		with open(filename, "w") as f:
			for line in oldlines:
				i = i + 1
				if i > 1 and intJaar == int(line.split(',')[0]) and intWeeknummer == int(line.split(',')[1]):
					f.write(str(intJaar) + ',' + str(intWeeknummer) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
					blnWeekgevonden = True
				else:
					f.write(line)
			if blnWeekgevonden == False:
				f.write(str(intJaar) + ',' + str(intWeeknummer) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
			f.close()

def saveMonthlyData(monthlyfilename,filename,strDate):
	"""
	Sla de maandgegevens op in het bestand maandgegevens_identifier.csv
	Bepaal hiervoor de totalen van de maand totnutoe uit de dag gegevens
	De volgende gegevens moeten berekend worden:
	jaar,maand,totaal,gem_temp,gem_pv_out
	Doorloop hiervoor de gegevens in het bestand daggegevens_identifier.csv.
	Open de maandgegevens en controleer of er niet al een record bestaat voor de maand,
	indien niet dan toevoegen, indien wel dan de gegevens aanpassen.
	Tevens moet op basis van de datum bepaald worden welke maand het is en welke dagen
	behoren tot deze maand (28, 29 30 of 31 dagen).
	"""
	strPeriod = "monthly"
	intMaandnummer = getMaandNummer(strDate)
	intJaar = getJaar(strDate)
	strBestand = ""
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	totaal_pv_out = 0
	sommatie = []

	arrDaysInMonth = getDaysInMonth(strDate)
	sommatie = sommeerDailyData(monthlyfilename,arrDaysInMonth,strPeriod)
	totaal = sommatie[0]
	gem_temp = sommatie [1]
	gem_pv_out = sommatie [2]
	totaal_pv_out = sommatie [3]
	
	blnFileExists = False
	if os.path.exists(filename):
		blnFileExists = True

	if blnFileExists == True:
		# Kijk in het bestaande bestand of de maandgegevens al bestaan, zo niet dan toevoegen, indien wel dan aanpassen
		with open(filename, "r") as f:
			oldlines = f.readlines()
			f.close()
		i = 0
		blnMaandgevonden = False
		with open(filename, "w") as f:
			for line in oldlines:
				i = i + 1
				if i > 1 and intJaar == int(line.split(',')[0]) and intMaandnummer == int(line.split(',')[1]):
					f.write(str(intJaar) + ',' + str(intMaandnummer) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
					blnMaandgevonden = True
				else:
					f.write(line)
			if blnMaandgevonden == False:
				f.write(str(intJaar) + ',' + str(intMaandnummer) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
			f.close()

	else:
		outputFile = open(filename, 'a')
		outputFile.write('jaar,maand,totaal,gem_temp,gem_pv_out,totaal_pv_out\n')
		outputFile.write(str(intJaar) + ',' + str(intMaandnummer) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
		outputFile.close()

def saveYearlyData(yearfilename,filename,strDate):
	"""
	Sla de jaargegevens op in het bestand jaargegevens_identifier.csv
	Bepaal hiervoor de totalen van het jaar totnutoe uit de maand gegevens
	De volgende gegevens moeten berekend worden:
	jaar,totaal,gem_temp,gem_pv_out,totaal_pv_out
	Doorloop hiervoor de maand files van het opgegeven jaar en bereken de gegevens voor
	het jaar.
	Open de jaargegevens en controleer of er niet al een record bestaat voor het jaar,
	indien niet dan toevoegen, indien wel dan de gegevens aanpassen.
	Tevens moet op basis van de datum bepaald worden welk jaar het is.
	"""
	strPeriod = "yearly"
	intJaar = getJaar(strDate)
	strBestand = ""
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	totaal_pv_out = 0
	sommatie = []

	arrMonthsInYear = getMonthsInYear(strDate)
	sommatie = sommeerMonthlyData(yearfilename,arrMonthsInYear)
	totaal = sommatie[0]
	gem_temp = sommatie [1]
	gem_pv_out = sommatie [2]
	totaal_pv_out = sommatie [3]
	
	blnFileExists = False
	if os.path.exists(filename):
		blnFileExists = True

	if blnFileExists == False:
		outputFile = open(filename, 'a')
		outputFile.write('jaar,totaal,gem_temp,gem_pv_out,totaal_pv_out\n')
		outputFile.write(str(intJaar) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
		outputFile.close()
	else:
		# Kijk in het bestaande bestand of de jaargegevens al bestaan, zo niet dan toevoegen, indien wel dan aanpassen
		with open(filename, "r") as f:
			oldlines = f.readlines()
			f.close()
		i = 0
		blnJaargevonden = False
		with open(filename, "w") as f:
			for line in oldlines:
				i = i + 1
				if i > 1 and intJaar == int(line.split(',')[0]):
					f.write(str(intJaar) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
					blnJaargevonden = True
				else:
					f.write(line)
			if blnJaargevonden == False:
				f.write(str(intJaar) + ',' + str(totaal) + ',' + str(gem_temp) + ',' + str(gem_pv_out) + ',' + str(totaal_pv_out) + '\n')
			f.close()

def getWeekNummer(strDate):
	"""
	Bepaal het nummer van de week op basis van de (als string) doorgegeven datum
	"""
	intWeeknummer = int(time.strftime("%W", time.strptime(strDate, '%Y%m%d')))
	return intWeeknummer

def getMaandNummer(strDate):
	"""
	Bepaal het nummer van de maand op basis van de (als string) doorgegeven datum
	"""
	intMaandnummer = int(time.strftime("%m", time.strptime(strDate, '%Y%m%d')))
	return intMaandnummer

def getJaar(strDate):
	"""
	Bepaal het nummer van de week op basis van de (als string) doorgegeven datum
	"""
	intJaar = int(time.strftime("%Y", time.strptime(strDate, '%Y%m%d')))
	return intJaar

def getDaysInWeek(strDate):
	"""
	Bepaal welke dagen in de week zitten op basis van de datum en geef deze terug
	"""
	i = 0
	arrDaysInWeek = []
	#intWeekday = int(time.strftime("%w", time.strptime(strDate, '%Y%m%d'))) # 0=zondag, 1=maandag, ..., 6=zaterdag
	intJaar = int(time.strftime("%Y", time.strptime(strDate, '%Y%m%d')))
	intMaand = int(time.strftime("%m", time.strptime(strDate, '%Y%m%d')))
	intDag = int(time.strftime("%d", time.strptime(strDate, '%Y%m%d')))
	intWeekday = time.strptime(strDate, '%Y%m%d')[6] # Dit zo laten omdat hierbij de maandag de eerste dag van de week is (0)
	
	# Allereerst de dagen van de week voor de (als string) doorgegeven datum bepalen
	i = intWeekday
	while i <= intWeekday:
		if i > -1:
			arrDaysInWeek.append("%s%s%s" % ((datetime.datetime(intJaar,intMaand,intDag) - datetime.timedelta(days=i)).year,
			(datetime.datetime(intJaar,intMaand,intDag) - datetime.timedelta(days=i)).month,
			(datetime.datetime(intJaar,intMaand,intDag) - datetime.timedelta(days=i)).day))
			#print "%s%s%s" % ((datetime.datetime(intJaar,intMaand,intDag) - datetime.timedelta(days=i)).year,
			#(datetime.datetime(intJaar,intMaand,intDag) - datetime.timedelta(days=i)).month,
			#(datetime.datetime(intJaar,intMaand,intDag) - datetime.timedelta(days=i)).day)
			#print "%i Dagen voor %s" % (i,strDate)
			i = i - 1
		else:
			i = intWeekday + 1
	
	# Daarna de dagen van de week na de (als string) doorgegeven datum bepalen
	i = 6
	while i > intWeekday:
		arrDaysInWeek.append("%s%s%s" % ((datetime.datetime(intJaar,intMaand,intDag) + datetime.timedelta(days=i - intWeekday)).year,
		(datetime.datetime(intJaar,intMaand,intDag) + datetime.timedelta(days=i - intWeekday)).month,
		(datetime.datetime(intJaar,intMaand,intDag) + datetime.timedelta(days=i - intWeekday)).day))
		#print "%s%s%s" % ((datetime.datetime(intJaar,intMaand,intDag) + datetime.timedelta(days=i - intWeekday)).year,
		#(datetime.datetime(intJaar,intMaand,intDag) + datetime.timedelta(days=i - intWeekday)).month,
		#(datetime.datetime(intJaar,intMaand,intDag) + datetime.timedelta(days=i - intWeekday)).day)
		#print "%i Dagen na %s" % (i - intWeekday,strDate)
		i = i - 1

	arrDaysInWeek.sort()
	#print arrDaysInWeek
	return arrDaysInWeek

def getDaysInMonth(strDate):
	"""
	Bepaal hoeveel dagen in de maand zitten op basis van de (als string doorgegeven) datum
	"""
	strJaar = time.strftime("%Y", time.strptime(strDate, '%Y%m%d'))
	strMaand = time.strftime("%m", time.strptime(strDate, '%Y%m%d'))
	strDag = time.strftime("%d", time.strptime(strDate, '%Y%m%d'))
	intJaar = int(strJaar)
	intMaand = int(strMaand)
	intDag = int(strDag)
	intDaysInMonth = 0
	arrDagenInMaand = []
	i = 1
	if intMaand == 1:
		intDaysInMonth = 31
	elif intMaand == 2:
		# Houdt rekening met een schrikkeljaar
		if isSchrikkeljaar(strDate):
			return 29
		else:
			return 28
	elif intMaand == 3:
		intDaysInMonth = 31
	elif intMaand == 4:
		intDaysInMonth = 30
	elif intMaand == 5:
		intDaysInMonth = 31
	elif intMaand == 6:
		intDaysInMonth = 30
	elif intMaand == 7:
		intDaysInMonth = 31
	elif intMaand == 8:
		intDaysInMonth = 31
	elif intMaand == 9:
		intDaysInMonth = 30
	elif intMaand == 10:
		intDaysInMonth = 31
	elif intMaand == 11:
		intDaysInMonth = 30
	elif intMaand == 12:
		intDaysInMonth = 31

	while i <= intDag and i <= intDaysInMonth:
		arrDagenInMaand.append(strJaar + strMaand + time.strftime("%d", time.strptime(strJaar + strMaand + str(i), '%Y%m%d')))
		i = i + 1
		
	return arrDagenInMaand

def getMonthsInYear(strDate):
	"""
	Bepaal welke maanden in het jaar zitten op basis van de (als string doorgegeven) datum
	"""
	strJaar = time.strftime("%Y", time.strptime(strDate, '%Y%m%d'))
	arrMonthsInYear = [strJaar + "01",strJaar + "02",strJaar + "03",strJaar + "04",strJaar + "05",strJaar + "06",strJaar + "07",strJaar + "08",strJaar + "09",strJaar + "10",strJaar + "11",strJaar + "12"]
	return arrMonthsInYear
	
def isSchrikkeljaar(strDate):
	"""
	Bepaal of een jaar een schrikkeljaar is
	"""
	jaar = int(time.strftime("%Y", time.strptime(strDate, '%Y%m%d')))
	if jaar % 400 == 0:
		return True
	if jaar % 100 == 0:
		return False
	if jaar % 4 == 0:
		return True
	else:
		return False

def sommeerStatsData(statsfilename):
	"""
	Sommeer de daggegevens uit het bestand yyyyMMdd_stats_identifier.csv
	De volgende gegevens moeten berekend en teruggegeven worden:
	totaal,gem_temp,gem_pv_out
	"""
	StatsRecord = collections.namedtuple('StatsRecord', 'timestamp, datetime, totaal, temp, pv_out, fout')
	begintotaal = 0
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	i = 0
	j = 0
	
	if os.path.exists(statsfilename):
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
		gem_temp = gem_temp/j-1
		gem_pv_out = gem_pv_out/j-1
		print 'Totaal: %i' % (totaal)
		print 'Gemiddelde temperatuur: %i' % (gem_temp)
		print 'Gemiddelde output: %i' % (gem_pv_out)
	return [totaal,gem_temp,gem_pv_out]

def sommeerDailyData(dailyfilename,arrDates,strPeriod):
	"""
	Sommeer de daggegevens uit het bestand daggegevens_identifier.csv op basis van de array met data
	De volgende gegevens moeten berekend en teruggegeven worden:
	totaal,gem_temp,gem_pv_out,totaal_pv_out
	"""
	if strPeriod == "daily":
		PeriodRecord = collections.namedtuple('PeriodRecord', 'timestamp, datetime, totaal, temp, pv_out, fout')
	elif strPeriod == "weekly" or strPeriod == "monthly":
		PeriodRecord = collections.namedtuple('PeriodRecord', 'datum, totaal, gem_temp, gem_pv_out, totaal_pv_out')
	elif strPeriod == "yearly":
		PeriodRecord = collections.namedtuple('PeriodRecord', 'jaar, maand, totaal, gem_temp, gem_pv_out, totaal_pv_out')
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	totaal_pv_out = 0
	i = 0
	j = 0
	
	if os.path.exists(dailyfilename):
		for loc in map(PeriodRecord._make, csv.reader(open(dailyfilename,"r"), delimiter=',')):
			i = i + 1
			for date in arrDates:
				#if i > 1:
				#	print "date / loc.datum: " + time.strftime("%Y%m%d", time.strptime(str(date), '%Y%m%d')) + " / " + time.strftime("%Y%m%d", time.strptime(str(loc.datum), '%Y%m%d'))
				if strPeriod == "daily":
					if i >= 2 and time.strftime("%Y%m%d", time.strptime(str(loc.datetime), '%Y-%m-%d %H:%M:%S')) == time.strftime("%Y%m%d", time.strptime(str(date), '%Y%m%d')):
						# controle toevoegen of de datum in de array met data zit
						totaal = loc.totaal
						gem_temp = gem_temp + int(loc.temp)
						gem_pv_out = gem_pv_out + int(loc.pv_out)
						totaal_pv_out = totaal_pv_out + int(loc.pv_out)
						j = j + 1
				else:
					if i >= 2 and time.strftime("%Y%m%d", time.strptime(str(loc.datum), '%Y%m%d')) == time.strftime("%Y%m%d", time.strptime(str(date), '%Y%m%d')):
						# controle toevoegen of de datum in de array met data zit
						totaal = loc.totaal
						gem_temp = gem_temp + int(loc.gem_temp)
						gem_pv_out = gem_pv_out + int(loc.gem_pv_out)
						totaal_pv_out = totaal_pv_out + int(loc.totaal_pv_out)
						j = j + 1
		totaal = int(totaal)
		gem_temp = gem_temp/j-1
		gem_pv_out = gem_pv_out/j-1
		#print 'Weektotaal: %i' % (totaal)
		#print 'Week gemiddelde temperatuur: %i' % (gem_temp)
		#print 'Week gemiddelde output: %i' % (gem_pv_out)
		#print 'Week totaal output: %i' % (totaal_pv_out)
	return [totaal,gem_temp,gem_pv_out,totaal_pv_out]

def sommeerMonthlyData(monthfilename,arrMonths):
	"""
	Sommeer de daggegevens uit het bestand daggegevens_identifier.csv op basis van de array met data
	De volgende gegevens moeten berekend en teruggegeven worden:
	totaal,gem_temp,gem_pv_out,totaal_pv_out
	"""
	PeriodRecord = collections.namedtuple('PeriodRecord', 'jaar, maand, totaal, gem_temp, gem_pv_out, totaal_pv_out')
	totaal = 0
	gem_temp = 0
	gem_pv_out = 0
	totaal_pv_out = 0
	i = 0
	j = 0
	
	if os.path.exists(monthfilename):
		for loc in map(PeriodRecord._make, csv.reader(open(monthfilename,"r"), delimiter=',')):
			i = i + 1
			for month in arrMonths:
				if i >= 2 and str(loc.jaar) == str(month[0:4]) and str(loc.maand) == str(int(month[4:6])):
					totaal = loc.totaal
					gem_temp = gem_temp + int(loc.gem_temp)
					gem_pv_out = gem_pv_out + int(loc.totaal_pv_out)
					totaal_pv_out = totaal_pv_out + int(loc.totaal_pv_out)
					j = j + 1
		totaal = int(totaal)
		gem_temp = gem_temp/j-1
		gem_pv_out = gem_pv_out/j-1
		#print 'Jaartotaal: %i' % (totaal)
		#print 'Jaar gemiddelde temperatuur: %i' % (gem_temp)
		#print 'Jaar gemiddelde output: %i' % (gem_pv_out)
		#print 'Jaar totaal output: %i' % (totaal_pv_out)
	return [totaal,gem_temp,gem_pv_out,totaal_pv_out]

def main():
	#strOutputFileStats = strftime("%Y%m%d%H%M%S") + '_stats_' + strIdentifier + '.csv'
	#strOutputFileStats = strftime("%Y%m%d") + '_stats_' + strIdentifier + '.csv'
	strTimeStamp = strftime("%Y%m%d%H%M%S")
	strOutputFileStats = strDateForFileName + '_stats_' + strIdentifier + '.csv'
	strOutputFileDag = 'daggegevens_' + strIdentifier + '.csv'
	strOutputFileWeek = 'weekgegevens_' + strIdentifier + '.csv'
	strOutputFileMaand = 'maandgegevens_' + strIdentifier + '.csv'
	strOutputFileJaar = 'jaargegevens_' + strIdentifier + '.csv'
	print strOutputFileStats
	print strOutputFileDag
	print strOutputFileWeek
	print strOutputFileMaand
	print strOutputFileJaar
	strMillis = strStats.split(',')[0]
	strDateTime = strStats.split(',')[1]
	strTotaal = strStats.split(',')[2]
	strTemp = strStats.split(',')[3]
	strGridPow = strStats.split(',')[4]
	strFout = strStats.split(',')[5]
	print "Millis: " + strMillis
	print "DateTime: " + strDateTime
	print "Totaal: " + strTotaal
	print "Temp: " + strTemp
	print "Grid_pow: " + strGridPow
	print "Fout: " + strFout
	
	saveStats(strInputDirectory +'/' + strOutputFileStats,'%s,%s,%s,%s,%s,%s' % (strMillis,strDateTime,strTotaal,strTemp,strGridPow,strFout))
	saveDailyData(strInputDirectory +'/' + strOutputFileStats,strInputDirectory +'/' + strOutputFileDag,strDateForFileName)
	saveWeeklyData(strInputDirectory +'/' + strOutputFileDag,strInputDirectory +'/' + strOutputFileWeek,strDateForFileName)
	saveMonthlyData(strInputDirectory +'/' + strOutputFileDag,strInputDirectory +'/' + strOutputFileMaand,strDateForFileName)
	saveYearlyData(strInputDirectory +'/' + strOutputFileMaand,strInputDirectory +'/' + strOutputFileJaar,strDateForFileName)

if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) >= 3:
		strIdentifier = args[0]
		strInputDirectory = args[1]
		strStats = args[2]
		strDateForFileName = strStats.split(',')[1].split("-")[0] + strStats.split(',')[1].split("-")[1] + strStats.split(',')[1].split("-")[2].split(" ")[0]
		tmeDateForFileName = time.strptime(strDateForFileName, '%Y%m%d')
		print "Doorgekregen jaar: %s" % (strftime("%Y", tmeDateForFileName))
		print "Schrikkeljaar: %s" % (isSchrikkeljaar(strDateForFileName))
		if len(args) == 4:
			blnDebug = args[3]
			print "Debugmodus: " + blnDebug

		if strStats.count(",") != 5:
			print "Geen geldige argumenten opgegeven voor de op te slaan gegevens."
			print "In totaal moeten zes komma gescheiden waarden opgegeven worden."
			print "Optioneel kan een vierde parameter opgegeven worden om in debug"
			print "modus te starten."
			print 'Bijvoorbeeld: SolarSaver.py "soladin1" "/data/solar" "1371303031513,2013-06-15 15:30:32,120827,66,485,2048"'
			print 'of in debug modus:'
			print 'SolarSaver.py "soladin1" "/data/solar" "1371303031513,2013-06-15 15:30:32,120827,66,485,2048" true'
			sys.exit()
	else:
		print
		print 'Geen argumenten opgegeven, dit script heeft drie'
		print 'argumenten nodig. Dit zijn de identifier, de directory'
		print 'waarin de gegevens moeten worden opgeslagen en de'
		print 'gegevens zelf (timestamp, datetime, totaal, temp, grid_pow, fout).'
		print "Optioneel kan een vierde parameter opgegeven worden om in debug"
		print "modus te starten."
		print 'Bijvoorbeeld: SolarSaver.py "soladin1" "/data/solar" "1371303031513,2013-06-15 15:30:32,120827,66,485,2048"'
		print 'of in debug modus:'
		print 'SolarSaver.py "soladin1" "/data/solar" "1371303031513,2013-06-15 15:30:32,120827,66,485,2048" true'
		sys.exit()

	main()
