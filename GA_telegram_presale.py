'''
Eventos con venta al público entre fechas determinadas.
Se debe ingresar un rango de fechas de venta al público como número entero.
0 es hoy, -7 una semana hacia atras, -14 dos semanas hacia adelante (todavía no se pusieron a la venta al público).
'''
#*************************************************
#Importaciones
from time import strftime, localtime
import datetime
from nested_lookup import nested_lookup
from datetime import timedelta,date,datetime
from GA_module import *
#*************************************************
def GA_manual_presale(FirstDay,LastDay):
	#Variables de configuración
	LowPriceTreshold = 10  #PrecioMax mínimo que debe tener el evento para considerarlo
	UpPriceTreshold = 220  #PrecioMax máximo que debe tener el evento para considerarlo
	ScoreTreshold = 10  #Score mínimo del evento para para considerarlo

	#Determina fechas de análisis
	today = time.time(); apikey = 'R8ZJ2GjIukrvAfBea1ljwAFgSztZvhHy'; EventList = []
	PresaleStartDate = today + FirstDay*86400
	PresaleStartDateHuman = strftime('%Y-%m-%d',localtime(PresaleStartDate))
	PresaleStartDate = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=FirstDay)
	PresaleEndDate = today + LastDay*86400
	PresaleEndDateHuman = strftime('%Y-%m-%d',localtime(PresaleEndDate))
	PresaleEndDate = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1+LastDay)

	#Comienza a buscar eventos
	for additional_date in range(FirstDay+1,LastDay+5):
		OnSaleDate = today + additional_date*86400
		OnSaleDate = strftime('%Y-%m-%d',localtime(OnSaleDate))
		for page in range(0,6):
			calltxt = 'https://app.ticketmaster.com/discovery/v2/events.json?page='+str(page)+'&size=199&onsaleOnStartDate='+OnSaleDate+'&apikey='+apikey
			response = requests.get(calltxt).text
			response = response.encode("ascii", "ignore").decode("utf-8")
			response = json.loads(response)
			try: response['_embedded']
			except: break
			else: response_list = response['_embedded']['events']
			EventList.extend(response_list)
			print('Events at Ticketmaster',len(EventList))

		#Guarda archivo luego de obtener eventos desde Ticketmaster
		#FilePath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/ResponseTM.json"
		# with open(FilePath, 'w') as f:
		# 	json.dump(EventList, f)

	#Prepara archivo csv para registrar info
	file = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/CSVs/Presale from " + PresaleStartDateHuman + ' to ' + PresaleEndDateHuman + ".csv"
	if os.path.exists(file): os.remove(file)
	LastTitle = ''; LastVenue = ''; LastCity = ''

	#Recoge info de cada evento
	for Event in EventList:
		#Preventa
		if not 'presales' in Event["sales"].keys(): continue
		PresaleStart = Event["sales"]['presales'][0]['startDateTime']
		PresaleStart = datetime.strptime(PresaleStart, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=-3)
		if PresaleStart < PresaleStartDate or PresaleStart > PresaleEndDate: continue
		PresaleStart = PresaleStart.strftime("%m/%d/%Y %H:%M")
		PresaleEnd = Event["sales"]['presales'][0]['endDateTime']
		PresaleEnd = (datetime.strptime(PresaleEnd, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=-3)).strftime("%m/%d/%Y %H:%M")

		#Filtro eventos antes de evaluar
		if not "_embedded" in Event.keys(): continue
		if not "venues" in Event["_embedded"].keys(): continue
		if not "country" in Event["_embedded"]["venues"][0].keys(): continue
		url = Event["url"]
		if not 'ticketmaster' in url and not'livenation' in url: continue
		if Event["_embedded"]["venues"][0]["country"]["countryCode"] != 'US': continue
		if not "city" in Event["_embedded"]['venues'][0].keys(): continue
		Venue = Event["_embedded"]['venues'][0]["name"]; Venue = Venue.replace(",","")
		
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
		OnSale = (datetime.strptime(OnSale, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=-3)).strftime("%m/%d/%Y %H:%M")

		#Precios
		if "priceRanges" in Event.keys():
			try: PriceMax = str(Event["priceRanges"][0]["max"]); PriceMin = str(Event["priceRanges"][0]["min"])
			except: continue
			if float(PriceMax)<LowPriceTreshold or float(PriceMax)>UpPriceTreshold: continue
		else: continue

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
			except: break
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

		#Guarda Archivo
		print(Title)
		line = PresaleStart+','+PresaleEnd+','+OnSale+','+EventDate+','+Title+','+Venue+','+City+','+Genre+','+PriceMax+','+PriceMin+','+capacity+','+PerformerScore+','+url
		Archivador(file,line)

	#Pone encabezado al archivo con el listado de ventos
	line = 'PresaleStart,PresaleEnd,OnSale,Date,Event,Venue,Place,Genre,PriceMax,PriceMin,Capacity,Score,TM URL,Observation'
	Archivador(file,line)

	#Envia Telegram	
	string = 'Presale from ' + PresaleStartDateHuman + ' to ' + PresaleEndDateHuman
	TelegramDocument(string,file)
#*************************************************

			





