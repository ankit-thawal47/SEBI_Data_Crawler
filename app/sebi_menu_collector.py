import globals as globals
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

class SEBIMenuCollector:

        legal_menu_and_sub_menu = globals.legal_menu_and_sub_menu
        urls_of_sebi_menu_csv_path = globals.urls_of_sebi_menu_csv_path
        base_folder_path = globals.base_folder_path
        
        def dictify(self,ul):
            '''
            Create multi-level dictionary to store the menus and submenus
            
            Use? => to create nested folder and to maintain folder hierachy
            
            '''
            result = {}
            for li in ul.find_all("li", recursive=False):
                key = next(li.stripped_strings)
                url = ""
                a_tags = li.find_all('a')
                
                if(len(a_tags) == 1):
                    url = a_tags[0]['href']
                    
                ul = li.find("ul")
                
                if ul:
                    result[key] = self.dictify(ul)
                else:
                    if(not url.startswith("http")):
                        base_url = "https://www.sebi.gov.in"
                        joined_url = urljoin(base_url, url)
                        url = joined_url
                    result[key] = url
            return result
        
        def download_menus_js(self):
            menus_of_sebi = "D:\Educational\Sarvam AI\Python\SEBI_Ankit\menus_of_sebi.html"
            import requests
            menus_of_sebi = "https://www.sebi.gov.in/js/menu.js"
            response = requests.get(menus_of_sebi)
            html_content = response.text

            html_content = html_content.replace('document.write("',"")
            html_content = html_content.replace('");','')
            html_content = "<html>" + html_content + "</html>"
    
        def collect_menu_links(self):
            
            # OLD => saving menu of sebis into csv file
            # NEW => We will maintain CSV for Menu collection
            if(os.path.exists(self.urls_of_sebi_menu_csv_path)):
                return
            # OLD => manually downladed fileissues? 
            # NEW => instead of downloaded file, download the file from the server
            
            # OLD => reads a manually saved menus_of_sebi.html file and stores content into html_content
            # NEW => write a method that will get the data using requests.get and store into
            html_content = self.download_menus_js()
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Get the main list
            ul = soup.ul
            result = self.dictify(ul)

            # Example data dictionary
            data_dict = result

            # Initialize empty lists for each column
            menu_list, submenu_list, description_list, url_list = [], [], [], []

            # Iterate over the data dictionary and append values to the lists
            for menu, submenu_dict in data_dict.items():
                for submenu, details in submenu_dict.items():
                    if isinstance(details, dict):
                        for description, url in details.items():
                            menu_list.append(menu.lower())
                            submenu_list.append(submenu.lower())
                            description_list.append(description.lower())
                            url_list.append(url)
                    else:
                        menu_list.append(menu.lower())
                        submenu_list.append(submenu.lower())
                        description_list.append("")
                        url_list.append(details)

            # Create DataFrame from lists
            df = pd.DataFrame({
                'menu': menu_list,
                'submenu': submenu_list,
                'subsubmenu': description_list,
                'url': url_list
            })
            
            row_count = len(df)
            for i in range(row_count):
                row = df.iloc[i]
                menu = row['menu']
                submenu = row['submenu']
                subsubmenu = row['subsubmenu']
                print(menu, submenu, subsubmenu)
                df.at[i, 'menu'] = menu.replace(" ","_")
                df.at[i, 'submenu'] = submenu.replace(" ","_")
                df.at[i, 'subsubmenu'] = subsubmenu.replace(" ","_")
            print("replaced <space> with <_>")

            '''df2 maintains historical_data links'''
            df2 = pd.DataFrame(
                {
                    'menu': ["legal"] * len(self.legal_menu_and_sub_menu),
                    'submenu': list(self.legal_menu_and_sub_menu.keys()),
                    'subsubmenu': ["historical_data"] * len(self.legal_menu_and_sub_menu),
                    'url': list(self.legal_menu_and_sub_menu.values())
                }
            )

            final_df = pd.concat([df, df2], axis=0)
            
            # OLD => saved the data to csv file
            # NEW => No change its better to save the menus_data in csv file only
            final_df.to_csv(self.urls_of_sebi_menu_csv_path, mode='a')
            
            
        def create_folder_hierarchy(self):
            try:
                df = pd.read_csv(self.urls_of_sebi_menu_csv_path)

                # Base folder to store SEBI Extracted Data
                print("Creating Folder Hierarchy for : ",self.base_folder_path)
                if not os.path.exists(self.base_folder_path):
                    # Create the base folder if it doesn't exist
                    os.makedirs(self.base_folder_path)

                for _,row in df.iterrows():
                    menu = row['menu']
                    menu = menu.replace(" ","_")
                    menu = menu.lower()
                    print(menu)
                    menu_folder = os.path.join(self.base_folder_path,menu)
                    # Create the base folder if it doesn't exist
                    if not os.path.exists(menu_folder):
                        os.makedirs(menu_folder)
                    sub_menu = row['submenu']
                    sub_menu = sub_menu.lower()
                    sub_menu = sub_menu.replace(" ","_")
                    sub_menu_folder = os.path.join(menu_folder,sub_menu)
                    if not os.path.exists(sub_menu_folder):
                        os.makedirs(sub_menu_folder)
            except Exception as e:
                print(f"Exception occurred : {e}")
            finally:
                print("Folder Hierarchy Created")