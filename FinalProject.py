from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
import pandas as pd
import time
import requests
import heapq
import re

departure_airport = input('\nPlease Input the Three Character Code For Your Departure Airport (Ex: PHL)\n')
arrival_airport = input('\nPlease Input the Three Character Code For Your Final Arrival Airport (Ex: ORD)\n')
start_date_of_trip = input('\nPlease enter the start date of your travel dates for your trip in the form of YYYY-MM-DD (Ex: 2023-04-26). Keep in mind that the maximum number of flights recommended to you will be 2 per day starting from this travel date.\n')
end_date_of_trip = input('\nPlease enter the end date of your trip in the form of YYYY-MM-DD (Ex: 2023-04-26). Keep in mind that the maximum number of flights recommended to you will be 2 per day starting from this travel date.\n')
value_on_flight = input('\nWe recognize that every person values different things when going on a flight. We want to know what you value most from the following options: \n1. Having Little Departure Delay \n2. Having Little Arrival Delay \n3. Having Short Total Elapsed Time \n4. Having Short Air Time \n5. Having Shortest Total Distance Traveled \n6. A combination of all 5 factors \nPlease enter in the number of the parameter which you value most \n')


def validate_parameters(departure_airport, arrival_airport, start_date_of_trip, end_date_of_trip, value_on_flight):
    while len(departure_airport) > 3 or len(departure_airport) < 3:
        departure_airport = input('\nYour Departure Airport Input was Invalid. Please Input the Three Character Code For Your Departure Airport(Ex: PHL)\n')
    
    while len(arrival_airport) > 3 or len(arrival_airport) < 3:
        arrival_airport = input('\nYour Arrival Airport Input was Invalid. Please Input the Three Character Code For Your Departure Airport(Ex: PHL)\n')

    while (regular_expression_match_dates(start_date_of_trip) == False):
        start_date_of_trip = input('\nYour Start Date Input was Invalid. Please enter the start date of your trip in the form of YYYY-MM-DD (Ex: 2023-04-26)\n')
    
    while (regular_expression_match_dates(end_date_of_trip) == False):
        end_date_of_trip = input('\nYour End Date Input was Invalid. Please enter the end date of your trip in the form of YYYY-MM-DD (Ex: 2023-04-26)\n')

    while (regular_expression_match_number(value_on_flight) == False):
        value_on_flight = input('\nYour Value On Flight Input was Invalid. We recognize that every person values different things when going on a flight. We want to know what you value most from the following options: \n1. Having Little Departure Delay \n2. Having Little Arrival Delay \n3. Having Short Total Elapsed Time \n4. Having Short Air Time \n5. Having Shortest Total Distance Traveled \n6. A combination of all 5 factors \nPlease enter in the number of the parameter which you value most \n')


def regular_expression_match_dates(date):
    expression_to_match = date
    if (re.search("\d\d\d\d-\d\d-\d\d", expression_to_match) != None):
        return True
    return False

def regular_expression_match_number(value_on_flight):
    expression_to_match = value_on_flight
    if (re.search("\d", expression_to_match) != None):
        return True
    return False


validate_parameters(departure_airport, arrival_airport, start_date_of_trip, end_date_of_trip, value_on_flight)


class Flights:

    def get_flights(self, departure, arrival, flight_date, number_of_stops):
        url = "https://www.kayak.com/flights/" + departure + "-" + arrival + "/" + flight_date + "?sort=price_a&fs=stops=" + str(number_of_stops)

        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome("chromedriver.exe")
        chrome_options.add_experimental_option("detach", True)
        driver.get(url)
        time.sleep(3)

        soup=BeautifulSoup(driver.page_source, 'html.parser')

        all_flight_boxes = soup.find_all(class_="nrc6")

        flight_dictionary = {}



        unique_flight_number = 1

        for flight_box in all_flight_boxes:
            times = flight_box.find(class_="nrc6-main").find(class_="VY2U").find(class_="vmXl vmXl-mod-variant-large").get_text()
            airline = flight_box.find(class_="nrc6-main").find(class_="VY2U").find(class_="c_cgF c_cgF-mod-variant-default").get_text()
            flight_time = flight_box.find(class_="nrc6-main").find(class_="xdW8").find(class_="vmXl vmXl-mod-variant-default").get_text()
            airport_arrival_departure = flight_box.find(class_="nrc6-main").find(class_="xdW8").find(class_="c_cgF c_cgF-mod-variant-default").get_text()
            price = flight_box.find(class_="nrc6-price-section").find(class_="f8F1-price-text").get_text()

            temp_single_flight_dictionary = {}
            temp_single_flight_dictionary['time_of_flight'] = times
            temp_single_flight_dictionary['airline'] = airline
            temp_single_flight_dictionary['length_of_flight'] = flight_time
            temp_single_flight_dictionary['airports'] = airport_arrival_departure
            temp_single_flight_dictionary['price'] = price

            flight_dictionary[str(unique_flight_number)] = temp_single_flight_dictionary

            unique_flight_number+=1


        return flight_dictionary
    

    def get_cheapest_flight(self,departure, arrival, flight_date):
        flights_dictionary = self.get_flights( departure, arrival, flight_date, 0)
        lowest_price_found = int(flights_dictionary['1']['price'][1:])
        lowest_price_flight = flights_dictionary['1']
        for flight in flights_dictionary:
            temp_flight = flights_dictionary[flight]
            price = int(temp_flight['price'][1:])
            if(price < lowest_price_found):
                lowest_price_found = price
                lowest_price_flight = temp_flight
        return lowest_price_flight

    def get_shortest_flight(self,departure, arrival, flight_date):
        flights_dictionary = self.get_flights( departure, arrival, flight_date, 0)
        shortest_flight = flights_dictionary['1']
        shortest_flight_time_raw = flights_dictionary['1']['length_of_flight']
        character_index_hours = shortest_flight_time_raw.find('h')
        character_index_minutes = shortest_flight_time_raw.find('m')
        flight_time_hours = 0
        flight_time_minutes = 0
        if(character_index_hours!=-1 and character_index_minutes!= -1):
            flight_time_hours = int(shortest_flight_time_raw[0:character_index_hours])
            flight_time_minutes = int(shortest_flight_time_raw[character_index_hours+2:character_index_minutes])
        shortest_flight_time = flight_time_hours*60 + flight_time_minutes

        
        for flight in flights_dictionary:
            flight_time = flights_dictionary[flight]['length_of_flight']
            character_index_hours = flight_time.find('h')
            character_index_minutes = flight_time.find('m')
            flight_time_hours = 0
            flight_time_minutes = 0
            if(character_index_hours!=-1 and character_index_minutes!= -1):
                flight_time_hours = int(flight_time[0:character_index_hours])
                flight_time_minutes = int(flight_time[character_index_hours+2:character_index_minutes])
            total_flight_time = flight_time_hours*60 + flight_time_minutes
            if(total_flight_time < shortest_flight_time):
                shortest_flight_time = total_flight_time
                shortest_flight = flights_dictionary[flight]
        
        return shortest_flight
    
    def get_flight_from_airline(self,departure, arrival, flight_date, airline_code):
        flights_dictionary = self.get_flights(departure, arrival, flight_date, 0)
        airline_code_to_airline_name_dictionary = {'AA': 'American Airlines', '9E': 'Endeavor Air', 'AS': 'Alaska Airlines', 'B6': 'JetBlue', 'DL': 'Delta', 'EV': 'ExpressJet Airlines', 'F9': 'Frontier', 'G4': 'Allegiant Air', 'HA': 'Hawaiian Airlines', 'MQ': 'Envoy Air', 'NK': 'Spirit Airlines',
       'OH': 'PSA Airlines', 'OO': 'SkyWest Airlines', 'UA': 'United Airlines', 'VX': 'Virgin America', 'WN': 'Southwest', 'YV': 'Mesa Airlines', 'YX': 'Republic Airways'}
        airline_name = airline_code_to_airline_name_dictionary[airline_code]
        for flight in flights_dictionary:
            if airline_name in flights_dictionary[flight]['airline']:
                return flights_dictionary[flight]
        return flights_dictionary['1']
    
    def get_flights_chronologically_on_path(self, date_of_trip, path_for_destination):
        flight_meet_time = 0
        counter_per_day = 1
        count_number_of_days = 1
        split_date = date_of_trip.split("-")
        current_index = 0
        last_index = len(path_for_destination)
        stops = 0
        flights = []
        flights_with_dates = {}
        
        day_dictionary = {"01": 31, "02": 28, "03": 31, "04": 30, "05": 31, "06": 30, "07": 31, "08": 31, "09": 30, "10": 31, "11": 30, "12": 31}

        date_dictionary= {}

        j = 1
        temp_day_counter = 0
        while (j <= len(path_for_destination)):
            if(j%2 == 0):
                temp_day_counter+=1
                date = split_date[0]
                if(int(split_date[2])+temp_day_counter > day_dictionary[split_date[1]]):
                    if((int(split_date[1]) + 1) < 10):
                         date = date + "-0" + str(int(split_date[1]) + 1)
                    else:
                        date = date + "-" + str(int(split_date[1]) + 1) 
                    
                    if(((int(split_date[2]) + temp_day_counter) - day_dictionary[split_date[1]]) < 10):
                        date = date + "-0" + str(((int(split_date[2] + temp_day_counter)) - day_dictionary[split_date[1]]))
                    else:
                        date = date + "-" + str(((int(split_date[2] + temp_day_counter)) - day_dictionary[split_date[1]]))
                
                else:
                    date = date + "-" + split_date[1]
                    if((int(split_date[2]) + temp_day_counter) < 10):
                        date = date + "-0" + str(int(split_date[2]) + temp_day_counter)
                    else:
                        date = date + "-" + str(int(split_date[2]) + temp_day_counter)
 
                date_dictionary[temp_day_counter+1] = date
                j+=1
            
            else:
                j+=1
        
        while (current_index < last_index - 1):
            all_flights = self.get_flights(path_for_destination[current_index],path_for_destination[current_index+1],date_of_trip, stops)
            if(len(all_flights) > 0):
                notfound = True
                specific_flight = None
                for flight in all_flights:
                    specific_flight = all_flights[flight]
                    split_time_of_flight = "0:00 am"
                    
                    if(flight_meet_time > 0):
                        split_time_of_flight = specific_flight['time_of_flight'].split("–")[0]
                    else:
                        split_time_of_flight = specific_flight['time_of_flight'].split("–")[1]
                    
                    am_time = re.search("^(.*)am", split_time_of_flight)
                    if(am_time!= None):
                        am_time = am_time.group()
                    pm_time = re.search("^(.*)pm", split_time_of_flight)
                    if(pm_time!= None):
                        pm_time = pm_time.group()
                    
                    time = 0
                    if(am_time != None and pm_time == None):
                        time_split = am_time.split(":")
                        if(int(time_split[0]) == 12):
                            hours = 0
                        else:
                            hours = int(time_split[0])*100
                        minutes = int(time_split[1][:2])
                        time = hours + minutes
                    elif(am_time == None and pm_time != None):
                        time_split = pm_time.split(":")
                        if(int(time_split[0]) == 12):
                            hours = 1200
                        else:
                            hours = int(time_split[0])*100 + 1200
                        minutes = int(time_split[1][:2])
                        time = hours + minutes

                    if(time > flight_meet_time):
                        flights.append(specific_flight)
                        flight_meet_time = time
                        notfound = False
                        break
                
                if(notfound):
                    i = 1
                    truth_value = True
                    while(truth_value):
                        more_flights = self.get_flights(path_for_destination[current_index], path_for_destination[current_index+1], date_of_trip, stops + i)
                        if(len(more_flights)>0):
                            specific_flight = None
                            for flight in more_flights:
                                specific_flight = more_flights[flight]
                                split_time_of_flight = "0:00 am"
                                if(flight_meet_time > 0):
                                    split_time_of_flight = specific_flight['time_of_flight'].split("–")[0]
                                else:
                                    split_time_of_flight = specific_flight['time_of_flight'].split("–")[1]
                                am_time = re.search("^(.*)am", split_time_of_flight)
                                if(am_time!= None):
                                    am_time = am_time.group()
                                pm_time = re.search("^(.*)pm", split_time_of_flight)
                                
                                if(pm_time!= None):
                                    pm_time = pm_time.group()
                                
                                time = 0
                                
                                if(am_time != None and pm_time == None):
                                    time_split = am_time.split(":")
                                    if(int(time_split[0]) == 12):
                                        hours = 0
                                    else:
                                        hours = int(time_split[0])*100
                                    minutes = int(time_split[1][:2])
                                    time = hours + minutes
                                
                                elif(am_time == None and pm_time != None):
                                    time_split = pm_time.split(":")
                                    if(int(time_split[0]) == 12):
                                        hours = 1200
                                    else:
                                        hours = int(time_split[0])*100 + 1200
                                    minutes = int(time_split[1][:2])
                                    time = hours + minutes
                                
                                if(time > flight_meet_time):
                                    flights.append(specific_flight)
                                    flight_meet_time = time
                                    truth_value = False
                                    break
                                i+=1
                        else:
                            i+=1
                            if(i > 3):
                                truth_value = False

            else:
                i = 1
                truth_value = True
                while(truth_value):
                    more_flights = self.get_flights(path_for_destination[current_index], path_for_destination[current_index+1], date_of_trip, stops+i)
                    if(len(more_flights)>0):
                        specific_flight = None
                        for flight in more_flights:
                            specific_flight = more_flights[flight]
                            split_time_of_flight = "0:00 am"
                            if(flight_meet_time > 0):
                                split_time_of_flight = specific_flight['time_of_flight'].split("–")[0]
                            else:
                                split_time_of_flight = specific_flight['time_of_flight'].split("–")[1]
                            if(re.search("^(.*)+1",split_time_of_flight) != None):
                                continue
                            am_time = re.search("^(.*)am", split_time_of_flight)
                            if(am_time!= None):
                                am_time = am_time.group()
                            pm_time = re.search("^(.*)pm", split_time_of_flight)
                            if(pm_time!= None):
                                pm_time = pm_time.group()
                                
                            time = 0
                            if(am_time != None and pm_time == None):
                                time_split = am_time.split(":")
                                if(int(time_split[0]) == 12):
                                    hours = 0
                                else:
                                    hours = int(time_split[0])*100
                                minutes = int(time_split[1][:2])
                                time = hours + minutes
                            elif(am_time == None and pm_time != None):
                                time_split = pm_time.split(":")
                                if(int(time_split[0]) == 12):
                                    hours = 1200
                                else:
                                    hours = int(time_split[0])*100 + 1200
                                minutes = int(time_split[1][:2])
                                time = hours + minutes

                            if(time > flight_meet_time):
                                flights.append(specific_flight)
                                flight_meet_time = time
                                truth_value = False
                                break
                            i+=1
                    else:
                        i+=1
                        if(i > 3):
                            truth_value = False
            
            current_index+=1
            if (counter_per_day % 2 == 0):
                flights_with_dates[date_of_trip] = flights
                flights = []
                count_number_of_days+=1
                date_of_trip = date_dictionary[count_number_of_days]
                counter_per_day +=1
                flight_meet_time = 0
                
            else:
                if(len(path_for_destination) == 2):
                    flights_with_dates[date_of_trip] = flights
                counter_per_day+=1
            
        
        return flights_with_dates

    

class AdjacenyList:

    def __init__(self, dataframe_of_flights, important_factors):
        self.data = dataframe_of_flights
        self.airport_numbers_to_codes,self.airport_codes_to_numbers = self.get_and_define_airport_symbols()
        self.important_factors = important_factors
        self.adjacency_list = self.create_adjacency_list()
        

    def get_and_define_airport_symbols(self):
        unique_departure_airports = self.data.ORIGIN.unique()
        unique_arrival_airports = self.data.DEST.unique()
        all_airports = None
        if(len(unique_arrival_airports) != len(unique_departure_airports)):
            aiports_not_in_departure_already = [airport for airport in unique_arrival_airports if airport not in unique_departure_airports]
            all_airports = unique_departure_airports + aiports_not_in_departure_already
        else:
            all_airports = unique_departure_airports

        i = 0
        airport_dict_1 = {}
        airport_dict_2 = {}
        for airport in all_airports:
            airport_dict_1[i] = airport
            airport_dict_2[airport] = i
            i+=1
        
        return airport_dict_1, airport_dict_2
        

    def create_adjacency_list(self):
        number_of_airports = len(self.airport_codes_to_numbers)
        i = 0
        matrix = [[-1 for i in range(number_of_airports)] for j in range(number_of_airports)]

        weights_dictionary = {1: "DEPARTURE_DELAY", 2 : "ARRIVAL_DELAY", 3: "ACTUAL_ELAPSED_TIME", 4: "AIR_TIME", 5: "DISTANCE"}

        the_list = []

        i = 0
        while (i < number_of_airports):
            the_list.append({})
            i+=1

        if (self.important_factors != 6):

            weight_item = weights_dictionary[self.important_factors]

            for index, row in self.data.iterrows():
                departure_airport =  row['ORIGIN']
                arrival_airport = row['DEST']
                index_for_departure = self.airport_codes_to_numbers[departure_airport]
                index_for_arrival = self.airport_codes_to_numbers[arrival_airport]
                the_list[index_for_departure][index_for_arrival] = row[weight_item]

        elif(self.important_factors == 6):
            data_to_normalize = self.data[["DEPARTURE_DELAY", "ARRIVAL_DELAY", "ACTUAL_ELAPSED_TIME", "AIR_TIME", "DISTANCE"]]
            for column_name in ["DEPARTURE_DELAY", "ARRIVAL_DELAY", "ACTUAL_ELAPSED_TIME", "AIR_TIME", "DISTANCE"]:
                min_val = min(list(data_to_normalize[column_name]))
                max_val = max(list(data_to_normalize[column_name]))
                data_to_normalize[column_name] = [(x - min_val) / max_val for x in data_to_normalize[column_name]]

            for index, row in data_to_normalize.iterrows():
                arrival_airport = self.data.iloc[index]['ORIGIN']
                departure_airport = self.data.iloc[index]['DEST']
                index_for_departure = self.airport_codes_to_numbers[departure_airport]
                index_for_arrival = self.airport_codes_to_numbers[arrival_airport]

                total_value = 0

                for value in weights_dictionary.values():
                    total_value += row[value]

                if (total_value != 0):
                    the_list[index_for_departure][index_for_arrival] = total_value

        return the_list
    

class Dijkstras:

    def __init__(self, adjacency_list):
        self.adjacency_list = adjacency_list

    def run_dijkstras(self, departure_index, arrival_index):
        distances = {airport_number: float('inf') for airport_number in range(len(self.adjacency_list))}
        distances[departure_index] = 0
        values_to_pop = [(0, departure_index)]
        visited = set()
        paths = {}

        while values_to_pop:
            (direct_distance, current_airport) = heapq.heappop(values_to_pop)
            
            if current_airport in visited:
                continue
            visited.add(current_airport)

            if (current_airport == arrival_index):
                return paths
            
            for airport, weights in self.adjacency_list[current_airport].items():
           
                distance = direct_distance + weights
                
                if distance < distances[airport]:
                    distances[airport] = distance
                    paths[airport] = current_airport
                    heapq.heappush(values_to_pop, (distance, airport))
        
        return paths
    
    def get_dikstras_path(self, departure_index, arrival_index, airport_code_conversion):

        path = self.run_dijkstras(departure_index, arrival_index)
        shortest_path = [arrival_index]
        while shortest_path[-1] != departure_index:
            shortest_path.append(path[shortest_path[-1]])
        shortest_path.reverse()
        for i in range(len(shortest_path)):
            shortest_path[i] = shortest_path[i]

        shortest_path_airport_codes = []

        for item in shortest_path:
            shortest_path_airport_codes.append(airport_code_conversion[item])
        
        return shortest_path_airport_codes


flight_data = pd.read_csv('FinalFlightDataForProject.csv')

flight_data = flight_data.drop(columns=['OP_CARRIER'])

final_flight_data = flight_data.groupby(['ORIGIN', 'DEST'], as_index=False).agg({'DEP_DELAY' : 'mean', 'ARR_DELAY' : 'mean', 'ACTUAL_ELAPSED_TIME': 'mean', 'AIR_TIME': 'mean', 'DISTANCE': 'mean'})

for index, row in final_flight_data.iterrows():
    if(row['DEP_DELAY'] < 0):
        final_flight_data.at[index, 'DEPARTURE_DELAY'] = 0
    else:
        final_flight_data.at[index, 'DEPARTURE_DELAY'] = row['DEP_DELAY']
    
    if(row['ARR_DELAY'] < 0):
        final_flight_data.at[index, 'ARRIVAL_DELAY'] = 0
    else:
        final_flight_data.at[index, 'ARRIVAL_DELAY'] = row['ARR_DELAY']

final_flight_data = final_flight_data.drop(columns=['DEP_DELAY', 'ARR_DELAY'])

adjacency_list = AdjacenyList(final_flight_data, int(value_on_flight))

index_for_departure = adjacency_list.airport_codes_to_numbers[departure_airport]
index_for_arrival = adjacency_list.airport_codes_to_numbers[arrival_airport]

dijkstras = Dijkstras(adjacency_list.adjacency_list)

results_going = dijkstras.get_dikstras_path(index_for_departure, index_for_arrival, adjacency_list.airport_numbers_to_codes)
results_coming_back = dijkstras.get_dikstras_path(index_for_arrival, index_for_departure, adjacency_list.airport_numbers_to_codes)

flights = Flights()

flights_to_destination = flights.get_flights_chronologically_on_path(start_date_of_trip, results_going)

flights_from_destination = flights.get_flights_chronologically_on_path(end_date_of_trip, results_coming_back)


print("\nHere is the Final Flight Schedule that you should follow to get from " + departure_airport + " to " + arrival_airport + " starting from " + start_date_of_trip + " (Max 2 Flights Per Travel Day). The final flight path calculated for you was :", "->".join(results_going))

for value in flights_to_destination:
    print("\nThese are the flights you will take on " + value + ":")
    specific_date_flights = flights_to_destination[value]
    i = 1
    for specific_flight in specific_date_flights:
        print("\n" + str(i) + ". You will take a flight by " + specific_flight['airline'] + " from " + specific_flight['airports'] + " during " + specific_flight['time_of_flight'] + " which will take you a total time of " + specific_flight['length_of_flight'] + " long and costs " + specific_flight['price'])
        i+=1


print("\nHere is the Final Flight Schedule that you should follow to get from " + arrival_airport + " to " + departure_airport + " starting from " + end_date_of_trip + " (Max 2 Flights Per Travel Day). The final flight path calculated for you was :", "->".join(results_coming_back))

for value in flights_from_destination:
    print("\nThese are the flights you will take on " + value + ":")
    specific_date_flights = flights_from_destination[value]
    i = 1
    for specific_flight in specific_date_flights:
        print("\n" + str(i) + ". You will take a flight by " + specific_flight['airline'] + " from " + specific_flight['airports'] + " during " + specific_flight['time_of_flight'] + " which will take you a total time of " + specific_flight['length_of_flight'] + " long and costs " + specific_flight['price'])
        i+=1