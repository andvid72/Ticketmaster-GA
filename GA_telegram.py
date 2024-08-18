#Importa funciones
import time,os
from GA_module import *
from datetime import datetime
from nested_lookup import nested_lookup 
import telepot,telebot
#*************************************************
#Tokens
alias = 701549748 #Lo obtenés en el chat IDBot de Telegram
token = '910296400:AAHRkd76QujDh8qnASbjEJv5kEc5DdAioco'  #Lo obtenés en el chat BotFather de Telegram
aliasAugu = 6195804322
tokenAugu = '6284927713:AAFeQ94ph9k_oEj7eriuOSBoOa63z5in17E'
#*************************************************
#https://telepot.readthedocs.io/en/latest/reference.html
def TelegramListener():
	#Variables Globales
	global TelegramProximoID
	TelegramProximoID = 0

	#Chequea mensajes
	while True:
		#Telegram actualiza mensajes
		bot = telepot.Bot(token)
		try: response = bot.getUpdates(offset=TelegramProximoID)
		except:
			bot = telebot.TeleBot(token)
			try: response = bot.getUpdates(offset=TelegramProximoID)
			except:
				print(datetime.now().strftime('%H:%M:%S'),' Sin Telegram')
				time.sleep(5)
				continue

		#Determino si hay mensaje nuevo
		update_id = nested_lookup('update_id',response)
		if not update_id: continue
		TelegramProximoID = update_id[len(update_id)-1]+1

		#Inicia loop de revisión de mensajes nuevos
		text = nested_lookup('text',response)
		TextCounter = -1
		for instruccion in text:
			if len(instruccion) >= 4096:
				string = 'Mensaje demasiado largo! Tiene ' + len(instruccion) + '. Máximo 4096.'
				EnviarTelegram(string)
				continue
			print(datetime.now().strftime('%H:%M:%S'),' Telegram nuevo mensaje ',instruccion)
			TextCounter = TextCounter+1
			if 'HELP' in instruccion.upper() and not 'http' in instruccion: TelegramAyuda(); continue
			if 'READ' in instruccion.upper() and not 'http' in instruccion: TelegramRead(); continue
			if 'CHECK' in instruccion.upper() and not 'http' in instruccion: TelegramProximoID = TelegramCheck(TelegramProximoID); continue
			if 'HOURS' in instruccion.upper() and not 'http' in instruccion: TelegramProximoID = TelegramScrapingHours(instruccion,TelegramProximoID); continue
			if 'DELETE' in instruccion.upper() and not 'http' in instruccion: TelegramProximoID = TelegramDelete(instruccion,TelegramProximoID); continue
			if 'URL' in instruccion.upper() and not 'http' in instruccion: TelegramURL(instruccion); continue
			if 'NEW' in instruccion.upper() and not 'http' in instruccion: TelegramProximoID = TelegramNew(TelegramProximoID); continue
			if 'CREDIT' in instruccion.upper() and not 'http' in instruccion: ScrapeopsCredit(); continue
			if 'PRESALE' in instruccion.upper() and not 'http' in instruccion: TelegramProximoID = TelegramPresale(TelegramProximoID); continue
			if 'ONSALE' in instruccion.upper() and not 'http' in instruccion: TelegramProximoID = TelegramOnsale(TelegramProximoID); continue
#*************************************************
def Repreguntador(cadena,accion,TelegramProximoID):
	def Preguntador(cadena,accion,ProximoID):
		global TelegramProximoID
		TelegramProximoID = ProximoID
		bot = telepot.Bot(token)
		instruccion = ''

		#Hago pregunta
		EnviarTelegram(cadena)

		#Espero repregunta
		for segundero in range(30):
			#Espera nuevo mensaje de Telegram
			try: response = bot.getUpdates(offset=TelegramProximoID)
			except: continue

			#Determino si hay mensaje nuevo
			update_id = nested_lookup('update_id',response)
			if not update_id: continue
			TelegramProximoID = update_id[len(update_id)-1]+1

			#Nuevo mensaje
			text = nested_lookup('text',response)
			if not text: continue
			instruccion = text[len(text)-1] #tiene guardado el último mensaje de texto
			print(datetime.now().strftime('%H:%M:%S'),' Telegram nuevo mensaje ',instruccion)

			#Verifica si es número
			if accion=='EsNumero':
				if not instruccion.replace(' ','').isdigit():
					cadena = instruccion+' es inválido!'
					EnviarTelegram(cadena)
					return '',TelegramProximoID
				break

			#Verifica si es afirmativo
			if accion=='EsAfirmativo':
				ListaTest = ['SI','SÍ','NO','S','N']
				k = 0
				for j in ListaTest:
					if instruccion.upper()==j:
						instruccion = j
						if instruccion == 'SÍ' or instruccion == 'S': instruccion = 'SI'
						if instruccion == 'N': instruccion = 'NO'
						break
					k += 1
				if k==len(ListaTest):
					cadena = instruccion+' no es válido!'
					EnviarTelegram(cadena)
					return '',TelegramProximoID
				break

			#Si es texto
			if accion=='': break

		#Telegram
		if segundero == 29:
			cadena = 'No se recibió mensaje'
			EnviarTelegram(cadena)
			return '',TelegramProximoID

		return instruccion,TelegramProximoID
	#*************************************************
	RtaRecibida,TelegramProximoID = Preguntador(cadena,accion,TelegramProximoID)
	if not RtaRecibida: RtaRecibida,TelegramProximoID = Preguntador(cadena,accion,TelegramProximoID)
	return RtaRecibida,TelegramProximoID			
#*************************************************
def TelegramAyuda():
	ayudin1 = ['HELP: ayuda','READ: lee eventos desde archivo','URL 1 2: entrega URLs','CREDIT: crédito Scrapeops']
	ayudin2 = ['CHECK: scrap tickets disponibles en evento por URL','DELETE 1 2: elimina eventos']
	ayudin3 = ['HOURS: horas entre scrapings','NEW: agrega URL de evento para chequear']
	ayudin4 = ['PRESALE: fechas de preventa','ONSALE: fechas de venta general']
	ayudin = ayudin1 + ayudin2 + ayudin3 + ayudin4
	ayudin = sorted(ayudin)
	cadena = ''
	for z in range(len(ayudin)): cadena = cadena + ayudin[z]+'\n'
	EnviarTelegram(cadena)
#*************************************************
def TelegramCheck(ProximoID):
	#Variables
	global TelegramProximoID
	TelegramProximoID = ProximoID

	#Pregúnta URL del evento
	url,TelegramProximoID = Repreguntador('URLs de cada evento? ','',TelegramProximoID)
	if not 'https://' in url: return TelegramProximoID
	
	#Chequeo de evento
	URLs = url.split()
	EventCheck(URLs)

	return TelegramProximoID
#*************************************************
def TelegramRead():
	#Crea lista con URLs de eventos a seguir
	UrlList = LeerArchivoCrearLista ("C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt")

	#Leo URLs y  archivos
	Message = ''; EventNumber = 1; TXTmessage = ''
	for url in UrlList:
		#Leo archivo
		FileName = TituloEventoTM(url)
		path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
		try: f = open(path)
		except FileNotFoundError: 
			# Message += str(EventNumber) + ' ' + FileName + '\n' + url  + '\n' + 'ScrapingHours: ' + ScrapHours + '\nSin lectura de tickets almacenada!\n\n'
			TXTmessage += FileName + '\n' + url  + '\n' + 'ScrapingHours: ' + ScrapHours + '\nSin lectura de tickets almacenada!\n\n'
			try: 
				LastOpenTime = os.path.getmtime(path)
				os.utime(path, (LastOpenTime, LastOpenTime-86500))
			except: pass
			EventNumber += 1
			continue
		AllLinesFile = f.readlines()
		f.close()

		#Verifica si existe matriz de tickets para informar
		if len(AllLinesFile) == 1: 
			# Message += str(EventNumber) + ' ' + FileName + '\n' + url  + '\n' + 'ScrapingHours: ' + ScrapHours + '\nSin lectura de tickets almacenada!\n\n'
			TXTmessage += FileName + '\n' + url  + '\n' + 'ScrapingHours: ' + ScrapHours + '\nSin lectura de tickets almacenada!\n\n'
			try: 
				LastOpenTime = os.path.getmtime(path)
				os.utime(path, (LastOpenTime, LastOpenTime-86500))
			except: pass			
			EventNumber += 1
			continue

		#Títulos de matriz
		Title = AllLinesFile[0]
		Title = Title.split(',')
		ScrapHours = Title[0] 
		Title[0] = "Date"
		Title = ','.join(Title)

		#Tickets por fecha de lectura
		Matriz = Title
		for x in range(1,len(AllLinesFile)):
		# for x in range(len(AllLinesFile)-1,0,-1): 
			Matriz +=AllLinesFile[x]
		Matriz = Matriz[:-1]
		Matriz = Matriz.split('\n')
		# Matriz = Title
		# for x in range(len(AllLinesFile)-1,len(AllLinesFile)-4,-1):
		# 	if x==0: break
		# 	Matriz +=AllLinesFile[x]
		# Matriz = Matriz[:-1]
		# Matriz = Matriz.split('\n')

		#Mensaje de Telegram
		# Message += str(EventNumber) + ' ' + FileName + '\n' + url  + '\n' + 'ScrapingHours: ' + ScrapHours + '\n'
		TXTmessage += FileName + '\n' + url  + '\n' + 'ScrapingHours: ' + ScrapHours + '\n'
		flag = True
		for LineMatriz in Matriz:
			LineMatriz = LineMatriz.split(',')
			LineMatriz[0] = LineMatriz[0][:5]
			if flag: LineMatriz = '\t'.join(LineMatriz)
			else: LineMatriz = '\t'.join(LineMatriz)
			flag = False
			# Message += LineMatriz + '\n'
			TXTmessage += LineMatriz + '\n'
		# Message += '\n'
		TXTmessage += '\n'
		EventNumber += 1

		#Envío Telegram antes de que se superen los 4096 caracteres
		# if len(Message) > 3500:
		# 	print(Message)
		# 	EnviarTelegram(Message)
		# 	Message = ''
	
	#Envío Telegram de la última parte o Telegram único si fue  menor a 3500 caracteres
	# print(Message)
	# EnviarTelegram(Message)

	#Imprimo reporte
	TXTmessagePath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/ReadMessage.txt"
	with open(TXTmessagePath, "w") as f:
		f.write(TXTmessage)

	#Envia Telegram	
	string = str(EventNumber) + ' eventos en scraping'; print(string)
	TelegramDocument(string,TXTmessagePath)
#*************************************************
def TelegramDelete(instruccion,ProximoID):
	#Variables
	global TelegramProximoID
	TelegramProximoID = ProximoID
	EventListpath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt"
	UrlList = LeerArchivoCrearLista (EventListpath)

	#Determina si hay indices para eliminar o se debe solicitar URLs
	instruccion = instruccion.upper()
	URLsIndexes = instruccion.replace('DELETE','')
	if not URLsIndexes.replace(' ','').isdecimal():
		#No hay indices, pregunta URL del evento
		UrlString,TelegramProximoID = Repreguntador('URLs de cada evento a eliminar? ','',TelegramProximoID)
		UrlList_to_delete = UrlString.split('\n')
		for Url in UrlList_to_delete:
			if not 'https://' in Url: continue
			EventEraser(Url)
	else:
		#Determina indices a eliminar
		URLsIndexes = URLsIndexes.split()
		URLsIndexesInt = []
		for x in range(len(URLsIndexes)):
			URLsIndexesInt.append(int(URLsIndexes[x])-1)
		URLsIndexesInt.sort(reverse=True)

		#Elimina URLs del archivo EventList	
		if URLsIndexesInt[0] >= len(UrlList): 
			EnviarTelegram('Indices mal indicados!')
			return TelegramProximoID		
		for Index in URLsIndexesInt: EventEraser(UrlList[Index])

	EnviarTelegram('URLs eliminadas!')
	return TelegramProximoID
#*************************************************
def TelegramURL(instruccion):
	#Variables
	path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt"
	UrlList = LeerArchivoCrearLista (path)

	#Determina indices a chequear
	instruccion = instruccion.upper()
	URLsIndexes = instruccion.replace('URL','')
	if not URLsIndexes.replace(' ','').isdecimal(): return
	URLsIndexes = URLsIndexes.split()
	URLsIndexesInt = []
	for x in range(len(URLsIndexes)):
		URLsIndexesInt.append(int(URLsIndexes[x])-1)
	URLsIndexesInt.sort(reverse=True)

	#Busca URLs a informar
	if URLsIndexesInt[0] >= len(UrlList): 
		EnviarTelegram('Indices mal indicados!')
		return
	string = ''
	for Index in URLsIndexesInt:
		string += UrlList[Index] + '\n\n'

	EnviarTelegram(string)
#*************************************************
def ScrapeopsCredit():
	scrapeops_api_key= 'b068c887-9fbf-42d3-ae8e-896f540fd7c5'
	Scrapeops_Check = 'https://proxy.scrapeops.io/v1/account?api_key=' + scrapeops_api_key
	response = json.loads(requests.get(Scrapeops_Check).text)
	Plan = response['plan_api_credits']
	Uso = response['used_api_credits']
	Resta = Plan - Uso
	RestaLlamadas = int(Resta / 11)
	string = 'Total ' + str(Plan) + '. Usado ' + str(Uso) + '. Resta ' + str(Resta) + '. Requests ' + str(RestaLlamadas) + '. Renueva 9 de cada mes.'
	print(string)
	EnviarTelegram(string)
#*************************************************
def TelegramScrapingHours(instruccion,ProximoID):
	#Variables
	global TelegramProximoID
	TelegramProximoID = ProximoID

	#Variables
	EventListpath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt"
	UrlList = LeerArchivoCrearLista (EventListpath)

	#Determina si hay indices para eliminar o se debe solicitar URLs
	instruccion = instruccion.upper()
	URLsIndexes = instruccion.replace('HOURS','')

	#No Hay indices
	if not URLsIndexes.replace(' ','').isdecimal():
		#Pregunta URLs de eventos
		UrlString,TelegramProximoID = Repreguntador('URLs a modificar? ','',TelegramProximoID)
		UrlList_to_change_ScrpingHours = UrlString.split('\n')

		#Pregunta Scraping Hours
		ScrapingHours,TelegramProximoID = Repreguntador('Horas entre scrapings? ','EsNumero',TelegramProximoID)
		if not ScrapingHours: return TelegramProximoID
		
		#Cambia horas entre scraping
		for Url in UrlList_to_change_ScrpingHours:
			if not 'https://' in Url: continue
			FileName = TituloEventoTM(Url)
			if not FileName: continue
			path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
			ChangeScrapingHours(path,ScrapingHours)
	#Sí hay indices
	else:
		#Pregunta Scraping Hours
		ScrapingHours,TelegramProximoID = Repreguntador('Horas entre scrapings? ','EsNumero',TelegramProximoID)
		if not ScrapingHours: return TelegramProximoID

		#Determina indices a eliminar
		URLsIndexes = URLsIndexes.split()
		URLsIndexesInt = []
		for x in range(len(URLsIndexes)):
			URLsIndexesInt.append(int(URLsIndexes[x])-1)
		URLsIndexesInt.sort(reverse=True)

		#Verifica indices a eliminar
		if URLsIndexesInt[0] >= len(UrlList): 
			EnviarTelegram('Indices mal indicados!')
			return TelegramProximoID
	
		#Recorre listado de indices y modifica el tiempo entre scrapings
		for Index in URLsIndexesInt:
			FileName = TituloEventoTM(UrlList[Index])
			if not FileName: continue
			path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
			ChangeScrapingHours(path,ScrapingHours)

	EnviarTelegram('ScrapingHours modificado!')
	return TelegramProximoID
#*************************************************
def TelegramNew(ProximoID):
	#Variables
	global TelegramProximoID
	TelegramProximoID = ProximoID

	#Pregúnta URL del evento
	UrlString,TelegramProximoID = Repreguntador('URLs de cada evento a incorporar? ','',TelegramProximoID)
	if not 'https://' in UrlString: return TelegramProximoID
	
	#Guarda nuevos eventos
	EventListpath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt"
	with open(EventListpath, "a+") as f:
		f.seek(0)
		if f.read()[-1] != '\n': f.write('\n')
		f.write(UrlString)

	#Telegram
	string = 'Evento incorporado!'
	print(string)
	EnviarTelegram(string)

	return TelegramProximoID
#*************************************************
def TelegramPresale(ProximoID):
	#Variables
	global TelegramProximoID
	TelegramProximoID = ProximoID
	from GA_telegram_presale import GA_manual_presale

	#Pregunta primer día a evaluar
	string = 'Primer día desde dónde buscar Presale (0=hoy)'
	FirstDay,TelegramProximoID = Repreguntador(string,'EsNumero',TelegramProximoID)
	if not FirstDay: return TelegramProximoID

	#Pregunta último día a evaluar
	string = 'Último día hasta donde buscar Presale (0=hoy)'
	LastDay,TelegramProximoID = Repreguntador(string,'EsNumero',TelegramProximoID)
	if not LastDay: return TelegramProximoID

	#Inicia evaluación
	GA_manual_presale(int(FirstDay),int(LastDay))

	return TelegramProximoID
#*************************************************
def TelegramOnsale(ProximoID):
	#Variables
	global TelegramProximoID
	TelegramProximoID = ProximoID
	from GA_telegram_onsale import GA_manual_onsale

	#Pregunta primer día a evaluar
	string = 'Primer día desde dónde buscar Onsale (0=hoy)'
	FirstDay,TelegramProximoID = Repreguntador(string,'EsNumero',TelegramProximoID)
	if not FirstDay: return TelegramProximoID

	#Pregunta último día a evaluar
	string = 'Último día hasta donde buscar Onsale (0=hoy)'
	LastDay,TelegramProximoID = Repreguntador(string,'EsNumero',TelegramProximoID)
	if not LastDay: return TelegramProximoID

	#Inicia evaluación
	GA_manual_onsale(int(FirstDay),int(LastDay))

	return TelegramProximoID
#*************************************************
