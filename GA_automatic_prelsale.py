'''
Se buscan eventos de GA con potencial de agotarse. Este script es para incorporar a un control automático.
Eventos con venta al público entre fechas determinadas.
Se debe ingresar un rango de fechas de venta al público como número entero.
0 es hoy, -7 una semana hacia atras, -14 dos semanas hacia adelante (todavía no se pusieron a la venta al público).
'''
#*************************************************
#Importaciones
from GA_telegram import *
from GA_module import *
from time import strftime, localtime
from datetime import timedelta,date
import datetime,time
#*************************************************
def GANewPreSale(LowPriceTreshold,UpPriceTreshold,ScoreTreshold):
	#Busca eventos en venta al público en el día de hoy
	apikey = 'R8ZJ2GjIukrvAfBea1ljwAFgSztZvhHy'
	EventList = []
	for additional_date in range(1,5):
		OnSaleDate = time.time() + additional_date*86400
		OnSaleDate = strftime('%Y-%m-%d',localtime(OnSaleDate))
		for page in range(0,6):
			calltxt = 'https://app.ticketmaster.com/discovery/v2/events.json?page='+str(page)+'&size=199&onsaleOnStartDate='+OnSaleDate+'&apikey='+apikey
			try: response = requests.get(calltxt).text
			except: continue
			response = response.encode("ascii", "ignore").decode("utf-8")
			response = json.loads(response)
			try: response['_embedded']
			except: break
			else: response_list = response['_embedded']['events']
			EventList.extend(response_list)
	
	#Guarda archivo luego de obtener eventos desde Ticketmaster
	# FilePath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/ResponseTM.json"
	# with open(FilePath, 'w') as f:
	# 	json.dump(EventList, f)

	#Recoge info de cada evento
	LastTitle = ''; LastVenue = ''; LastCity = ''; URLlist = []
	PresaleDate = strftime('%Y-%m-%d',localtime(time.time())) 
	file = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/CSVs/Presale " + PresaleDate + '.csv'

	#Verifica lista de venues
	# if not CheckVenueListDuplicates(): return
	# VenueList = LeerArchivoCrearLista("C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/VenueList.txt")

	for Event in EventList:
		#Filtro eventos con preventa en el día de hoy
		if not 'presales' in Event["sales"].keys(): continue
		if not 'startDateTime' in Event["sales"]['presales'][0].keys(): continue
		if not 'endDateTime' in Event["sales"]['presales'][0].keys(): continue
		PresaleStart = Event["sales"]['presales'][0]['startDateTime']
		PresaleStart = datetime.datetime.strptime(PresaleStart, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=-3)
		if PresaleStart.day != date.today().day: continue
		PresaleStart = PresaleStart.strftime("%m/%d/%Y %H:%M")
		PresaleEnd = Event["sales"]['presales'][0]['endDateTime']
		PresaleEnd = (datetime.datetime.strptime(PresaleEnd, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=-3)).strftime("%m/%d/%Y %H:%M")
		
		#Filtro eventos antes de evaluar
		if not "_embedded" in Event.keys(): continue
		if not "venues" in Event["_embedded"].keys(): continue
		if not "country" in Event["_embedded"]["venues"][0].keys(): continue
		url = Event["url"]
		if not 'ticketmaster' in url and not'livenation' in url: continue
		if Event["_embedded"]["venues"][0]["country"]["countryCode"] != 'US': continue
		if not "city" in Event["_embedded"]['venues'][0].keys(): continue

		#Filtra los venues
		Venue = Event["_embedded"]['venues'][0]["name"]; Venue = Venue.replace(",","")
		# if Venue not in VenueList: continue
		
		#Detalles del evento
		Title = Event["name"]; Title = Title.replace(",","")
		EventDate = Event["dates"]['start']['localDate']
		try: City = Event["_embedded"]['venues'][0]["city"]["name"] + ' ' + Event["_embedded"]['venues'][0]["state"]["stateCode"]
		except: continue
		City = City.replace(",","")	
		if Title==LastTitle and Venue==LastVenue and City==LastCity: continue
		LastTitle = Title; LastVenue = Venue; LastCity = City

		#Onsale
		try: OnSale = Event["sales"]["public"]["startDateTime"]
		except: continue
		OnSale = (datetime.datetime.strptime(OnSale, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=-3)).strftime("%m/%d/%Y %H:%M")

		#Precios
		if "priceRanges" in Event.keys():
			try: PriceMax = str(Event["priceRanges"][0]["max"])
			except: continue
			try: PriceMin = str(Event["priceRanges"][0]["min"])
			except: continue
			if float(PriceMax)<LowPriceTreshold or float(PriceMax)>UpPriceTreshold: continue

		#Genero
		if "subGenre" in Event["classifications"][0].keys():
			Genre =  Event["classifications"][0]["subGenre"]["name"]; Genre = Genre.replace(",","")
		elif "genre" in Event["classifications"][0].keys():
			Genre =  Event["classifications"][0]["genre"]["name"]; Genre = Genre.replace(",","")
		else: 
			Genre = 'NA'

		#Filtra generos
		AllGenres1 = ['Blues','Country','French Rap','Gospel','Indie Folk','Jazz','K-Pop','Latin','Nu-Metal']
		AllGenres2 = ['Pop','R&B','Reggae','Witchstep','Alternative Rock','Funk','Performance Art']
		AllGenres = AllGenres1 + AllGenres2 + ['']
		for EachGenre in AllGenres:
			if Genre == EachGenre: break
		if not EachGenre: continue

		#Busco eventos en este venue en Seatgeek
		SeatGeekID = 'MzU4OTU1MDl8MTY5NDIxMzk5OC44NjExMDM1'
		page = 1; SeatGeekEventList = []

		while True:
			Seatgeek = 'https://api.seatgeek.com/2/events?per_page=50&q='+Venue+'&page='+str(page)+'&client_id='+SeatGeekID
			try: response = requests.get(Seatgeek).json()
			except: continue  
			try: response['events']
			except: break
			SeatGeekEventList.extend(response['events'])
			if len(response['events'])<50: break
			page += 1

		# SeatgeekPath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/ResponseSG.json"
		# with open(SeatgeekPath, 'w') as f:
		# 	json.dump(SeatGeekEventList, f)

		#Tengo lista de eventos en el venue?
		if not SeatGeekEventList: continue
		datetime_local = nested_lookup('datetime_local',SeatGeekEventList)
		EventOrder = 0
		for VenueDate in datetime_local:
			Date_study = VenueDate[0:10]
			if EventDate == Date_study: break
			EventOrder += 1

		#Encontré el evento?
		if not EventOrder<len(datetime_local): continue
		EventFound = SeatGeekEventList[EventOrder]

		#Capacidad
		capacity = str(EventFound['venue']['capacity'])
		if not capacity: capacity = 'NA'

		#Seatgeek URL
		SeatgeekURL = EventFound['url']
		if not SeatgeekURL: SeatgeekURL = 'NA'

		#Popularidad del artista
		try: PerformerScore = EventFound['performers'][0]['score']*100
		except: continue
		if PerformerScore < ScoreTreshold: continue
		PerformerScore = str(PerformerScore)

		#Agrego URL a la lista de URLs
		URLlist.append(url)

		#Guarda Archivo
		print('Presale',Title)
		line = PresaleStart+','+PresaleEnd+','+OnSale+','+EventDate+','+Title+','+Venue+','+City+','+Genre+','+PriceMax+','+PriceMin+','+capacity+','+PerformerScore+','+url
		Archivador(file,line)

	#Pone encabezado al archivo con el listado de ventos
	line = 'PresaleStart,PresaleEnd,OnSale,Date,Event,Venue,Place,Genre,PriceMax,PriceMin,Capacity,Score,TM URL,Observation'
	Archivador(file,line)

	#Envia Telegram	
	string = str(len(URLlist)) + ' nuevos eventos en Presale'; print(string)
	TelegramDocument(string,file)
#*************************************************
def CheckPresale(LowPriceTreshold,UpPriceTreshold,ScoreTreshold):
	#Chequea si debe solicitar nuevos eventos del día e incorporarlos a EventList.txt
	CheckPath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/DailyPresaleCheck.txt"
	try: f = open(CheckPath)
	except FileNotFoundError:
		CurrentHour = int(strftime('%H',localtime(time.time())))
		CurrentMinute = int(strftime('%M',localtime(time.time())))
		DayWeek = datetime.datetime.today().weekday()
		if CurrentHour>=7 and CurrentMinute>=0 and DayWeek<4:
			with open(CheckPath, 'w') as f:
				f.write('')
			string = 'Se inicia búsqueda de nuevos eventos en Presale para hoy'
			print(string)
			# EnviarTelegram(string)
			GANewPreSale(LowPriceTreshold,UpPriceTreshold,ScoreTreshold)

	#Si cambia el día, borra el archivo testigo para volver a scrapear al día siguiente
	else:
		f.close()
		TodayDay = strftime('%d',localtime(time.time()))
		FileDay = strftime('%d',localtime(os.path.getmtime(CheckPath)))
		if TodayDay != FileDay: os.remove(CheckPath)
#*************************************************

	

			





