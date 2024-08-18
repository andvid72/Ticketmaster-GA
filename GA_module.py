import time,os.path,requests,os,json
import telepot,telebot
#*************************************************
#Tokens
alias = 701549748 #Lo obtenés en el chat IDBot de Telegram
token = '910296400:AAHRkd76QujDh8qnASbjEJv5kEc5DdAioco'  #Lo obtenés en el chat BotFather de Telegram
aliasAugu = 6195804322
tokenAugu = '6284927713:AAFeQ94ph9k_oEj7eriuOSBoOa63z5in17E'
#*************************************************
def EventEraser(url):
	#Borra CSV con mediciones
	FileName = TituloEventoTM(url)
	path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
	try: os.remove(path)
	except:
		try: os.remove(path)
		except: print('No se pudo eliminar ' + FileName)	

	#Borra url de EventList
	EventListpath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt"
	AllLines = LeerArchivoCrearLista (EventListpath)
	try: AllLines.remove(url)
	except: return
	StringList = '\n'.join(AllLines)
	try:
		with open(EventListpath, "w") as f:
			f.write(StringList)
	except: return
#*************************************************
def LeerArchivoCrearLista (archivo):
	#Leer archivo
	try:
		with open(archivo) as f: lista = f.readlines()
	except: return []
	else:
		f.close()
		if not lista: return []
	#Crear lista
	x=0
	for z in lista:
		lista[x] = z.replace('\n','')
		x += 1
	while('' in lista) : lista.remove('')
	return lista
#*************************************************
def TituloEventoTM(url):
	#Name
	name = url[url.find('.com/')+5:]
	name = name[:name.find('/event')]
	name = name.replace('-',' ').title()
	return name
#*************************************************
# 'api_key': 'b068c887-9fbf-42d3-ae8e-896f540fd7c5',  # andvid@saldo1.com.ar / 9324Casa, 25000credits
# 'api_key': '685de0e1-7f09-4916-8081-304e1a964730',  # andvid72@gmail.com / 9324Casa
# 'api_key': '29f93fbc-1b3b-4640-abf3-fdf828040dfe',  # ventas2722@gmail.com / 9324Casa*-
# 'api_key': 'c40a3dea-f582-4345-a622-2da9bb2dfc7e',  # andresvidela72@gmail.com / 9324Casa*-
# https://scrapeops.io/app/login
from urllib.parse import urlencode
def Scrapeops(url):
	api_key = 'b068c887-9fbf-42d3-ae8e-896f540fd7c5'	
	countries = ['uk','us','au','ge','fr']
	for country_label in countries:
		proxy_params = {
			'api_key': api_key,
			'render_js' : 'true',
			'wait' : 10000, 
			'url': url,
			'mobile': 'true',
			# 'premium' : 'true', 
			# 'residential' : 'true', 
			'country' : country_label,
			}
		try: response = requests.get('https://proxy.scrapeops.io/v1/',params=urlencode(proxy_params), timeout=60)
		except: 
			response = ''
			continue
		else:
			if not response.ok:
				response = ''
				continue
			else: break
	return response
#*************************************************
def SaveFilesTM(soup,FileName):
	#Crea Directorio si no existe
	path = 'C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/' + FileName
	try: os.makedirs(path)
	except FileExistsError: pass

	#Graba HTML scrapeado
	File = 'C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/' + FileName + '/' + FileName + '.html'
	with open(path, 'w') as f:
		f.write(str(soup.prettify()))

	#Graba TXT		
	File = 'C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/' + FileName + '/' + FileName + '.txt'
	with open(path, 'w') as f:
		f.write(str(soup.prettify()))
#*************************************************
def ParseBuckets(Buckets):
	#Elabora lista de precios
	PriceRange = []
	for bucket in Buckets:
		if bucket[0] not in PriceRange: PriceRange.append(bucket[0])

	#Unifica buckets con el mismo precio y suma las cantidades
	QuantityRange = []
	for price in PriceRange:
		Quantity = 0 
		for bucket in Buckets:
			if bucket[0]==price: 
				Quantity += bucket[1]
		QuantityRange.append(Quantity)

	#Elabora matriz única de precios/cantidades
	PriceQuantity = []
	for n in range(len(QuantityRange)):
		PriceQuantity.append([PriceRange[n],QuantityRange[n]])

	return PriceQuantity
#*************************************************
from time import strftime, localtime
def TicketCompare(FileName,url,DeleteEventTreshold):
	path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
	LastOpenTime = os.path.getmtime(path)
	Hour = int(strftime('%H',localtime(time.time())))	
	try: f = open(path)
	except FileNotFoundError: return
	else:
		#Lee el archivo
		AllLinesFile = f.readlines()
		f.close()
		os.utime(path, (LastOpenTime, LastOpenTime))

		#Chequea si tengo dos mediciones para poder comparar
		L = len(AllLinesFile)
		if L<=2: return
		if L==3: ChangeScrapingHours(path,'33')			

		#Chequea última medición contra la medición previa
		Title = AllLinesFile[0].replace('\n','').split(',')
		EvaluatedColumns = [1]
		if len(Title) >= 4: 
			for x in range(len(Title)):
				if 'PIT' in Title[x]: EvaluatedColumns = [1,x]

		'''Title = AllLinesFile[0]
		Title = Title.replace('\n','')
		PriceList =  Title.replace('$','').split(',')
		Title = Title.split(',')

		#Solamente el total primario
		if len(PriceList) < 4: EvaluatedColumns = [1]
		else:
			#PIT
			if 'PIT' in Title:
				PitColumn = Title.index("PIT")
				EvaluatedColumns = [1,PitColumn]
			#GA
			else:
				MinPrice = min(list(map(int, PriceList[3:])))
				for GaColumn in range(len(PriceList)):
					if str(MinPrice) == PriceList[GaColumn]: 
						EvaluatedColumns = [1,GaColumn]
						break'''

		#Determino cantiadades de las últimas dos mediciones
		PreviousQuantities = AllLinesFile[L-2]; PreviousQuantities = PreviousQuantities.replace('\n','').split(',')
		CurrentQuantities = AllLinesFile[L-1]; CurrentQuantities = CurrentQuantities.replace('\n','').split(',')
		print(Title)
		print(PreviousQuantities)
		print(CurrentQuantities)

		#Evalua si el evento está agotando y los tickets son todo reventa o Offcial Platinum
		PrimaryQuantity = int(CurrentQuantities[1])
		if PrimaryQuantity<40:
			EventEraser(url)
			Tiempo = strftime('%H:%M:%S',localtime(time.time()))
			print(Tiempo +' deleting for soldout '+FileName)
			return

		#Compara las mediciones de primarios y GA en busca de cambios
		Message = 'ALERT\n' + FileName + '\n' + url + '\n'
		MessageFlag = False
		CurrentScrapHours = int(Title[0])
		print('EvaluatedColumns',EvaluatedColumns)
		for column in EvaluatedColumns:
			#Determina el porcentaje de cambio por sección
			try: CurrentQuantity = int(CurrentQuantities[column])
			except: CurrentQuantity = 0
			print('column',column,' - CurrentQuantity',CurrentQuantity)
			try: PreviousQuantity = int(PreviousQuantities[column])
			except: continue
			if PreviousQuantity==0: continue
			change = CurrentQuantity/PreviousQuantity
			CurrentScrapHours = int(CurrentScrapHours*change)			

			#Determina el porcentaje de descenso de tickets y ajusta las horas entre mediciones				
			if change>0.9:
				if PrimaryQuantity>1000: CurrentScrapHours = 151
				elif PrimaryQuantity>400 and PrimaryQuantity<=1000: CurrentScrapHours = 103
				elif PrimaryQuantity>200 and PrimaryQuantity<=400: CurrentScrapHours = 55
				elif PrimaryQuantity>100 and PrimaryQuantity<=200: CurrentScrapHours = 33
				else: 
					CurrentScrapHours = int(CurrentScrapHours*2)
					if CurrentQuantity<100 and PrimaryQuantity<=100: L = 0
					if CurrentScrapHours > 19: CurrentScrapHours = 19
			
			#Si el cambio es grande alerta
			if change<=0.9 and CurrentQuantity<120:
				MessageFlag = True
				Message += 'Descenso de ' + str(int((1- change)*100)) + '% en ' + Title[column] + '\n'
				CurrentScrapHours = int(CurrentScrapHours*0.5)

			#Si quedan menos de 50 tickets en la sección, alerta
			if CurrentQuantity<50:
				MessageFlag = True
				Message += 'Restan ' + str(CurrentQuantity) + ' tickets en ' + Title[column] + '\n'
				CurrentScrapHours = 15

			#Limita mediciones a un mínimo
			if CurrentScrapHours < 1: CurrentScrapHours = 1

			#Modifica hora entre mediciones
			ChangeScrapingHours(path,str(CurrentScrapHours))
			
			#Si quedan pocos tickets en la sección de interés, se elimina el evento. Tiene sentido para eventos con asientos o con pit.
			# if CurrentQuantity<20:
			# 	EventEraser(url)
			# 	Tiempo = strftime('%H:%M:%S',localtime(time.time()))
			# 	print(Tiempo +' deleting for less than 20 tickets '+FileName)
			# 	return
			
			#Si no hay cambios significativos en los tickets primarios totales, se elimina el evento
			if column==1 and L>=4:
				PreviousQuantities2 = AllLinesFile[L-3]; PreviousQuantities2 = PreviousQuantities2.replace('\n','').split(',')
				try: PreviousQuantity2 = int(PreviousQuantities2[1])
				except: continue
				change2 = PreviousQuantity/PreviousQuantity2
				if change>(100-DeleteEventTreshold)/100 and change2>(100-DeleteEventTreshold)/100 and CurrentQuantity>120 and (Hour<=3 or Hour>=16):
					EventEraser(url)
					Tiempo = strftime('%H:%M:%S',localtime(time.time()))
					print(Tiempo +' deleting for not selling '+FileName)
					return					
						
		#Reporte de cambios
		if not MessageFlag: return
		
		#Títulos de matriz
		Title[0] = "Date"
		Title = ','.join(Title)

		#Tickets por fecha de lectura
		Matriz = Title + '\n'
		for x in range(len(AllLinesFile)-1,len(AllLinesFile)-4,-1):
			if x==0: break
			Matriz +=AllLinesFile[x]
		Matriz = Matriz[:-1]
		Matriz = Matriz.split('\n')

		#Mensaje de Telegram
		Message += 'ScrapingHours: ' + str(int(CurrentScrapHours)) + '\n'
		flag = True
		for LineMatriz in Matriz:
			LineMatriz = LineMatriz.split(',')
			LineMatriz[0] = LineMatriz[0][:5]
			if flag: LineMatriz = ' \t'.join(LineMatriz) #tabulación título
			else: LineMatriz = '      \t'.join(LineMatriz) #tabulación tickets
			flag = False
			Message += LineMatriz + '\n'

		#Alerta por Telegram
		print(Message)
		EnviarTelegram(Message)
#*************************************************
def NewInventory(FileName,PrimaryReserve,ResaleReserve,TotalPriceRange,ScrapingHours):
	#Fecha y Hora
	path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
	from time import strftime, localtime
	today = strftime('%d/%m %H:%M',localtime(time.time()))

	#Lee encabezado del CSV guardado
	try: 
		with open(path, 'r') as f:
			Header = f.readlines()[0].rsplit(","); Header[-1] = Header[-1].rstrip('\n')
	except: pass

	#Nuevo inventario para cada ubicación
	NewPrices = []; NewQuantities = []
	for x in range(len(TotalPriceRange)):
		NewPrices.append(TotalPriceRange[x][0])
		NewQuantities.append(str(TotalPriceRange[x][1]))

	#Hay nuevas ubicaciones disponibles?
	# for x in range(3,len(Header)):
	# 	Header[x] = Header[x].replace("$", "").strip()
	for price in NewPrices:
		if price not in Header:	Header.append(price)

	#Nuevo Header
	Headerline = ScrapingHours + ',Primary,Resale'	
	for x in range(3,len(Header)):	Headerline += ','+Header[x]
		# if Header[x]=='PIT': Headerline += ',PIT'
		# else: Headerline += ',$'+Header[x]

	#Nueva linea de cantidades
	NewQuantites = []
	for x in range(3,len(Header)):
		try: Index = NewPrices.index(Header[x])
		except: 
			NewQuantites.append('0')
			continue
		NewQuantites.append(NewQuantities[Index])
	HeaderQuantities = today + ',' + str(PrimaryReserve) + ',' + str(ResaleReserve)
	for x in NewQuantites:
		HeaderQuantities += ',' + x

	#Lee el archivo 
	try:
		with open(path) as file:
			AllLinesFile = file.readlines()
	except: return
	   
	#Agrega Header y nueva linea de cantidades
	AllLinesFile[0] = Headerline + "\n"
	AllLinesFile.append(HeaderQuantities + "\n")

	#Guarda el nuevo archivo
	try:
		with open(path, "w") as file:
			for line in AllLinesFile:
				file.write(line)
	except: pass
#*************************************************
import telepot,telebot
def EnviarTelegram(cadena):
	#Datos iniciales
	bot = telepot.Bot(token)
	tb = telebot.TeleBot(token)

	#Intenta 1º con telepot
	for m in range(10):
		try: bot.sendMessage(alias,cadena)
		except:
			time.sleep(1)
			continue
		else: break

	#Si telepot falló, intenta con telebot
	if m==9:
		for m in range(10):
			try: tb.send_message(alias,cadena)
			except:
				time.sleep(1)
				continue
			else: break
#*************************************************
from bs4 import BeautifulSoup
import json
# from TelegramTickets import ScrapeopsCredit
def EventCheck(URLs):
	for url in URLs:
		#Título
		FileName = TituloEventoTM(url)

		#Scraping
		Success = False
		response = Scrapeops(url)
		try: soup = BeautifulSoup(BeautifulSoup(response.text,'html.parser').prettify(),'html.parser')
		except: Success = False
		else:
			if soup.find(id='__NEXT_DATA__'): Success = True
		if not Success:
			string = 'No se obtuvo tickets de ' + FileName
			print(string); EnviarTelegram(string)
			continue
		TotalPriceRangeScript = str(soup.find(id='__NEXT_DATA__').contents[0])
		TotalPriceRangeScript = json.loads(TotalPriceRangeScript)
		try: facets = json.loads(TotalPriceRangeScript['props']['pageProps']['edpData']['context']['eventLevelAvailability'])['facets']
		except: 
			string = 'No se obtuvo tickets de ' + FileName
			print(string); EnviarTelegram(string)		
			continue

		#Evaluo disponibilidad de tickets
		inventoryTypes=''; Quantity=0
		BucketsLevel = []; PrimaryReserve = 0; ResaleReserve = 0
		for face in facets:
			#Scrapea disponibilidad de tickets
			if face['inventoryTypes']: inventoryTypes = face['inventoryTypes'][0]
			if face['priceRange'] and face['count']:		
				MinPrice = face['priceRange'][0]['min']
				MaxPrice = face['priceRange'][0]['max']
				Quantity = face['count']
				if face['priceLevelSecnames']: 
					if '000000000001' in face['ticketTypes'][0] and face['priceLevelSecnames'][0] == 'P1': 
						string = '$'+ str(int(MinPrice)) + ' (PIT)'
						BucketsLevel.append([string,Quantity])
						continue
				if inventoryTypes=='primary' and MaxPrice==MinPrice:
					string = '$'+ str(int(MinPrice))				
					BucketsLevel.append([string,Quantity])

			#Elabora matriz de tickets		
			if inventoryTypes=='primary': PrimaryReserve +=Quantity			
			if inventoryTypes=='resale': ResaleReserve +=Quantity

		#Determina inventario primario y secundario
		string = FileName + '\n' + url  + '\n' + 'Primary '+str(PrimaryReserve)+'\nResale '+str(ResaleReserve)  + '\n'

		#Si hay reserva de tickets, se actualiza el inventario
		if PrimaryReserve: 
			#Disponibilidad por secciones
			TotalPriceRange = ParseBuckets(BucketsLevel)
			for x in range(len(TotalPriceRange)):
				string += TotalPriceRange[x][0] + ' ' + str(TotalPriceRange[x][1]) + '\n'

		#Registra lectura en CSV
		path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
		try: f = open(path, 'r')
		except FileNotFoundError: pass
		else:
			try: ScrapingHours = f.readlines()[0].split(",")[0]
			except:	pass
			else: NewInventory(FileName,PrimaryReserve,ResaleReserve,TotalPriceRange,ScrapingHours)

		#Devuelve resultado
		print(string)
		EnviarTelegram(string)
#*************************************************
def ChangeScrapingHours(path,ScrapingHours):
	try: LastOpenTime = os.path.getmtime(path)
	except: return
	try: f = open(path, 'r+')
	except FileNotFoundError: return		
	else:
		FullFileList = f.readlines()
		NewHeaderString = FullFileList[0]
		NewHeaderList = NewHeaderString.rsplit(",")
		NewHeaderList[0] = ScrapingHours
		NewHeaderString = ','.join(NewHeaderList)
		FullFileList[0] = NewHeaderString
		f.seek(0)
		for FileLine in FullFileList:
			f.write(FileLine)
		f.truncate()
		f.close()
		os.utime(path, (LastOpenTime, LastOpenTime))
#*************************************************
#Invierte archivos escribiendo lo último arriba.
def Archivador(filename, line):
	#Si el archivo no existe, lo creo
	if not os.path.exists(filename):
		f = open(filename, 'w')
		f.close()

	#Guardo info en el archivo
	with open(filename, 'r+') as f:
		content = f.read()
		f.seek(0, 0)
		f.write(line.rstrip('\r\n') + '\n' + content)
		f.close()
#*************************************************
def LeerListaCrearArchivo(list,path):
	#Si el archivo no existe, lo creo
	if not os.path.exists(path):
		f = open(path, 'w')

	#Convierto lista en string y lo guardo
	StringList = '\n'.join(list)
	with open(path, 'w') as f:
		f.write(StringList)
#*************************************************
def CheckVenueListDuplicates():
	#Verifica si existe el archivo de lista de venues
	if not os.path.exists("C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/VenueList.txt"): 
		EnviarTelegram('Falta archivo con el listado de venues')
		return False
	
	#Elimina duplicados
	VenueList = LeerArchivoCrearLista("C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/VenueList.txt")
	VenueListAux = []
	for venue in VenueList:
		if venue not in VenueListAux: 
			VenueListAux.append(venue)
	
	#Guarda nuevo archivo de venues sin duplicados
	LeerListaCrearArchivo(VenueListAux,VenueList)
	return True
#*************************************************
def DeleteExistingFile(path):
	if os.path.exists(path): os.remove(path)
#*************************************************
def TelegramDocument(string,file):
	#Augusto
	pathfile = open(file,'rb')
	pathfile.close
	aliasAugu = 6195804322
	tokenAugu = '6284927713:AAFeQ94ph9k_oEj7eriuOSBoOa63z5in17E'
	bot = telepot.Bot(tokenAugu)
	try: bot.sendDocument(aliasAugu,pathfile,string)
	except:
		tb = telebot.TeleBot(tokenAugu)
		try: tb.send_document(aliasAugu,pathfile,string)
		except: pass

	#Andres
	pathfile = open(file,'rb')
	pathfile.close
	alias = 701549748
	token = '910296400:AAHRkd76QujDh8qnASbjEJv5kEc5DdAioco'
	bot = telepot.Bot(token)
	try: bot.sendDocument(alias,pathfile,string)
	except:	
		tb = telebot.TeleBot(token)
		try: tb.send_document(alias,pathfile,string)
		except: pass
#*************************************************
