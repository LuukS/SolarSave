import sys, time, subprocess

# Timestamp in mkiliseconds
millis = str(int(round(time.time() * 1000)))

#curl -d "d=20130626" -d "t=20:20" -d "v2=25" -H "X-Pvoutput-Apikey: 0bf0522a9fcfab877153ad617511b8d7cabddd1e" -H "X-Pvoutput-SystemId: 20378" http://pvoutput.org/service/r2/addstatus.jsp

datetime = "2013-06-27 20:40:02"
strDate = "20130627"
strTime = "20:40"
grid_pow = 0
strApiKey = "0bf0522a9fcfab877153ad617511b8d7cabddd1e"
strSystemId = "20378"
strPVOutputAddStatusURL = "http://pvoutput.org/service/r2/addstatus.jsp"

strJaar =  str(time.localtime()[0])
strMaand = "0" + str(time.localtime()[1])
if len(strMaand) > 2:
	strMaand = strMaand[len(strMaand)-2:len(strMaand)]
strDag = "0" + str(time.localtime()[2])
if len(strDag) > 2:
	strDag = strDag[len(strDag)-2:len(strDag)]
strUur = "0" + str(time.localtime()[3])
if len(strUur) > 2:
	strUur = strUur[len(strUur)-2:len(strUur)]
strMinuut = "0" + str(time.localtime()[4])
if len(strMinuut) > 2:
	strMinuut = strMinuut[len(strMinuut)-2:len(strMinuut)]

print "Date: %s%s%s" % (strJaar,strMaand,strDag)
print "Time: %s%s" % (strUur,strMinuut)

subprocess.call(['curl', '-d', 'd=' + "%s%s%s" % (strJaar,strMaand,strDag), '-d', 't=' + "%s:%s" % (strUur,strMinuut), '-d', 'v2=' + str(grid_pow), '-H', 'X-Pvoutput-Apikey:' + strApiKey , '-H', 'X-Pvoutput-SystemId:' + strSystemId, strPVOutputAddStatusURL])

