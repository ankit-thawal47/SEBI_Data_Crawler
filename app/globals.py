import os


'''
legal_menu_and_sub_menu is dict to store the urls to access "Historical Data" from the legal menu.
It's hard to collect these links, hence need to hardcode.
'''
legal_menu_and_sub_menu = {
            "acts" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingLegal=yes&sid=1&ssid=1&smid=0",
            "rules" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingLegal=yes&sid=1&ssid=2&smid=0",
            "regulations" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingLegal=yes&sid=1&ssid=3&smid=0",
            "general_orders" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=4&smid=0",
            "guidelines" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=5&smid=0",
            "master_circulars" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=6&smid=0",
            "circulars" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7&smid=0",
            # Doubt ? => How is Circulars are Circular_archive are different?
            "circulars_archive" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingCirArchive=yes&sid=1&ssid=7&smid=0",
            "gazette_notification" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=82&smid=0",
            "online_application_portal" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=91&smid=0",
            "guidance_notes" : "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=85&smid=0",
        }


# '''DB CONSTANTS'''
DB_NAME = "sebi_data.sqlite3"


# '''Paths of Folders and CSV files''' 
home_page_url = "https://www.sebi.gov.in"

regChat_folder = r"D:\Educational\Sarvam AI\Python\SEBI_Ankit"
extraction_folder_name = "SEBI_Extracted_Data"

base_folder_path = os.path.join(regChat_folder,extraction_folder_name)

SEBI_data_extraction_base_folder = os.path.join(regChat_folder,extraction_folder_name)

urls_of_sebi_menu_csv_path = os.path.join(regChat_folder,"urls_of_menus_of_sebi.csv")
