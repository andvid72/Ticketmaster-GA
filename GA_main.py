'''
Monitorea el remanente de tickets mediante scraping.
Espera instrucciones desde Telegram
'''
LowPriceTreshold = 10  #PrecioMax mínimo que debe tener el evento para considerarlo
UpPriceTreshold = 220  #PrecioMax máximo que debe tener el evento para considerarlo
DeleteEventTreshold = 2  #porcentaje de cambio mínimo para que el evento no se elimine de seguimiento
ScoreTreshold = 30  #Score mínimo del evento para para considerarlo

import json, urllib3, time, random
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from GA_module import *
from GA_telegram import *
from bs4 import BeautifulSoup
from GA_automatic_onlsale import *
from GA_automatic_prelsale import *
from time import strftime, localtime
#***********************************************
# def Scraper(botnumber) 
def Scraper():
	#HVariables inicales
	# LastHour = ''

	#Loop
	while True:		
		#Chequea si debe solicitar nuevos eventos del día e incorporarlos a EventList.txt
		CheckPresale(LowPriceTreshold,UpPriceTreshold,ScoreTreshold)
		CheckOnsale(LowPriceTreshold,UpPriceTreshold,ScoreTreshold)	

		#Reporte Horario
		# Hour = strftime('%H',localtime(time.time()))
		# if Hour!=LastHour:
		# 	print(Hour+'hs - Bot operando')
		# 	LastHour = Hour

		#Crea lista con URLs de eventos a seguir
		UrlList = LeerArchivoCrearLista ("C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt")

		for EachUrl in UrlList:
			#Verificás tiempo desde última vez que se scrapeo
			FileName = TituloEventoTM(EachUrl)
			if not FileName: continue

			#Abre archivo de datos
			path = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/TotalPriceRange/" + FileName + ".csv"
			try: f = open(path, 'r')
			except FileNotFoundError:
				ScrapingHours = '1'
				with open(path, 'w') as f:
					f.write(ScrapingHours)	
			else:				
				try: ScrapingHours = f.readlines()[0].split(",")[0]
				except:	ScrapingHours = '1'
				f.close()
				LastOpenTime = os.path.getmtime(path)
				today = time.time()
				if (today-LastOpenTime)/(float(ScrapingHours)*3600) < 1: continue

			#Imprimi info del evento a escrapear
			Tiempo = strftime('%H:%M:%S',localtime(time.time()))
			print(Tiempo +' checking '+FileName)

			#Scraping
			Success = False
			response = Scrapeops(EachUrl)
			try: soup = BeautifulSoup(BeautifulSoup(response.text,'html.parser').prettify(),'html.parser')
			except: Success = False
			else:
				if soup.find(id='__NEXT_DATA__'): Success = True
			if not Success:
				if ScrapingHours=='1': ChangeScrapingHours(path,'2')
				else: ChangeScrapingHours(path,'1')
				os.utime(path, (os.path.getmtime(path), time.time()))
				continue

			#Analizo Scraping
			TotalPriceRangeScript_str = str(soup.find(id='__NEXT_DATA__').contents[0])
			TotalPriceRangeScript_json = json.loads(TotalPriceRangeScript_str)
			facets = json.loads(TotalPriceRangeScript_json['props']['pageProps']['edpData']['context']['eventLevelAvailability'])['facets']
			secnames = TotalPriceRangeScript_json['props']['pageProps']['edpData']['context']['event']['secnames']
			LookPass = False

			#Registro la venue para futuros usos
			venue = TotalPriceRangeScript_json['props']['pageProps']['edpData']['context']['event']['venue']['name']
			Archivador("C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/VenueList.txt", venue)

			#Verifico si el evento es GA o tiene PIT y si no lo es, lo elimino
			try: isGa = TotalPriceRangeScript_json['props']['pageProps']['edpData']['context']['event']['isGa']
			except: continue
			if isGa: LookPass = True
			if not LookPass:
				#Busco PIT
				for face in facets:
					if face['priceLevelSecnames']: 
						if '000000000001' in face['ticketTypes'][0] and face['priceLevelSecnames'][0] == 'P1': 
							LookPass = True
							break
				#Si no hay PIT, busco secciones de admisión general
				if not LookPass:
					SearchedSecnames = ["GA","PIT","NOCHAIR","GENADM","GAFLR"]
					for secname in secnames:
						if 'secname' in secname.keys() and 'description' in secname.keys():
							if secname['secname'] in SearchedSecnames or 'general' in secname['description'].lower() or 'standing' in secname['description'].lower(): LookPass = True										
						else:
							if secname['secname'] in SearchedSecnames:	LookPass = True
		
			#No continuo si la venue no tiene sectores de pie
			if not LookPass: 
				EventEraser(EachUrl)
				print(Tiempo +' deleting for not standing areas '+FileName)
				continue
			
			#Evaluo disponibilidad de tickets
			inventoryTypes=''; Quantity=''
			BucketsLevel = []; PrimaryReserve = 0; ResaleReserve = 0

			#Analizo todas las secciones
			for face in facets:
				if face['inventoryTypes']: inventoryTypes = face['inventoryTypes'][0]
				if face['priceRange'] and face['count']:		
					MinPrice = face['priceRange'][0]['min']
					MaxPrice = face['priceRange'][0]['max']
					Quantity = face['count']

					#Contabiliza tickets	
					if inventoryTypes=='primary': PrimaryReserve +=Quantity			
					if inventoryTypes=='resale': ResaleReserve +=Quantity

					#PIT
					if face['priceLevelSecnames'] and not isGa: 
						if '000000000001' in face['ticketTypes'][0] and face['priceLevelSecnames'][0] == 'P1':
							string = '$'+ str(int(MinPrice)) + ' (PIT)'
							BucketsLevel.append([string,Quantity])
							continue

					#GA
					if inventoryTypes=='primary' and MaxPrice==MinPrice:
						string = '$'+ str(int(MinPrice))					
						BucketsLevel.append([string,Quantity])

			#Si hay reserva de tickets, se actualiza el inventario
			if PrimaryReserve: 
				#Disponibilidad por secciones
				TotalPriceRange = ParseBuckets(BucketsLevel)

				#Se guarda archivo con nuevo inventario de tickets
				NewInventory(FileName,PrimaryReserve,ResaleReserve,TotalPriceRange,ScrapingHours)
			
				#Lee inventario de la última vez y lo compara con el actual
				TicketCompare(FileName,EachUrl,DeleteEventTreshold)

			#Si no quedan tickets, se elimina el evento
			else:
				#Elimina evento de EventList
				print(Tiempo +' deleting for not primary tickets '+FileName)
				EventListpath = "C:/Users/Videla/Documents/Ticket Resale/Chequeo de Eventos/EventList.txt"
				UrlList = LeerArchivoCrearLista (EventListpath)
				try: UrlList.remove(EachUrl)
				except: continue
				LeerListaCrearArchivo(UrlList,EventListpath)

				#Borra CSV
				try: os.remove(path)
				except: continue