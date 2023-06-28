import shodan
import folium
from tabulate import tabulate
import os

#set your shodan api key
API_KEY = 'IbL3g2JzBiRd2BYKVCCaYhdIS6WCpPlP'

#create an instance of the shodan api object
api = shodan.Shodan(API_KEY)


def print_banner(message):
    banner = '''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

 ______     ______     ______     __  __     _____     ______     ______     ______     ______   ______     ______    
/\  ___\   /\  __ \   /\  == \   /\ \/\ \   /\  __-.  /\  __ \   /\  __ \   /\  ___\   /\__  _\ /\  == \   /\  __ \   
\ \ \__ \  \ \  __ \  \ \  __<   \ \ \_\ \  \ \ \/\ \ \ \  __ \  \ \  __ \  \ \___  \  \/_/\ \/ \ \  __<   \ \  __ \  
 \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \____-  \ \_\ \_\  \ \_\ \_\  \/\_____\    \ \_\  \ \_\ \_\  \ \_\ \_\ 
  \/_____/   \/_/\/_/   \/_/ /_/   \/_____/   \/____/   \/_/\/_/   \/_/\/_/   \/_____/     \/_/   \/_/ /_/   \/_/\/_/ 
                                                                                                                      

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''
    print(banner)
    print(message)


#usage
message = ""
print_banner(message)

if not API_KEY:
    print("API key is empty. Please provide a valid Shodan API key.")
else:
    try:
        #prompt the user to select one input option
        print("Select an input option:")
        print("1. City")
        print("2. Geo location")
        print("3. Country(a 2-letter country code)")
        print("4. Organization")
        #error handling if user select wrong option
        while True:
            try:
                option = int(input("Enter your choice (1-4): "))
                if option in [1, 2, 3, 4]:
                    break
                else:
                    print("Invalid input option. Please select a valid option (1-4).")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

        #map the option to the corresponding field name
        fields = {
            1: "city",
            2: "geo",
            3: "country",
            4: "org"
        }

        #get the field name based on the selected option
        field = fields[option]

        #prompt the user for the value of the selected field
        value = input(f"Enter the {field}: ")
        print('[+]Searching For Cameras')

        #shodan camera dorks
        dorks = [
            'webcam 7',
            'webcamXP',
            'SQ-WEBCAM',
            'yawcam',
            'uc-httpd 1.0.0',
            'Surveillance',
            'Hikvision IP Camera',
            'title:camera',
            'webcam has_screenshot:true',
            'http.title:"WEB VIEW"',
            'http.title:"Webcam"',
            'D-Link Internet Camera',
            'Hipcam RealServer/V1.0',
            'title:camera',
            'cam'
        ]

        # perform shodan api search
        results = []

        for dork in dorks:
            query = f'{field}:{value} "{dork}"'
            dork_results = api.search(query)

            for result in dork_results['matches']:
                entry = [
                    result.get('ip_str', 'N/A'),
                    result.get('port', 'N/A'),
                    result.get('product', 'N/A'),
                    result.get('location', {}).get('country_name', 'N/A'),
                    result.get('location', {}).get('city', 'N/A'),
                    result.get('org', 'N/A'),
                    result.get('isp', 'N/A'),
                    result.get('asn', 'N/A'),
                    result.get('location', {}).get('latitude', None),
                    result.get('location', {}).get('longitude', None)
                ]
                results.append(entry)

        #print the results in a table format
        headers = ['IP Address', 'Port', 'Service', 'Country', 'City', 'Organization', 'ISP', 'ASN', 'Latitude', 'Longitude']
        table = tabulate(results, headers=headers, tablefmt="pipe")
        print(table)
        current_dir = os.getcwd()
        filename = input("Enter the text file name (e.g., result.txt): ")
        file_path = os.path.join(current_dir, filename)

        if filename:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(table)
            print(f"Results saved in {filename}")
        else:
            print("No file name provided. Results not saved.")



        #create a map and add markers for each IP address
        map_center = (results[0][8], results[0][9])  # Center the map on the first IP's location
        m = folium.Map(location=map_center, zoom_start=12)

        for result in results:
            ip_address = result[0]
            latitude = result[8]
            longitude = result[9]



            if latitude and longitude:
                marker = folium.Marker([latitude, longitude], popup=ip_address)
                marker.add_to(m)

        #save map to html file
        file_name = input("Enter the HTML file name (e.g., ip_map.html): ")


        if file_name:
            m.save(file_name)
            print(f"Map saved as '{file_name}'")
        else:
            print("No file name provided. Map not saved.")

    except shodan.APIError as e:
        if 'Invalid API key' in str(e):
            print("API key is invalid. Please provide a valid Shodan API key.")
        else:
            print(f"An error occurred: {str(e)}")
