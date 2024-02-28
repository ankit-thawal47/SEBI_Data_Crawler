

           
class SEBIDataScraper:

    def __init__(self):
        print("SEBI Data Scrapper Object is created")
        # OLD => Create CSV files with menus, if they dont already exists
        # NEW => Create sqlitedb (if it doesn't exists) to store the the extracted text 
        if(not os.path.exists(pdf_links_of_all)):
            df = pd.DataFrame(columns=columns_for_pdf_links_of_all)
            df.to_csv(pdf_links_of_all, index=True)
            print(f"CSV file {pdf_links_of_all} with column names created successfully.")
        self.data = []

    

    def navigate_pagination_and_collect_links(self,url,type,sub_type):
        type = type.lower()
        sub_type = sub_type.lower()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        page_num = 0

        while(1):
            logging.basicConfig(filename='selenium_next_button.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
            logging.info(f'Entering navigate_pagination_and_collect_links method, {url}')

            try:

                time.sleep(1)
                ########### GEL HTML/PDF LINKS FROM THE TABLE ###########
                html_content = driver.page_source
                soup = BeautifulSoup(html_content,'html.parser')
                table = soup.find('table')
                if(table == None):
                    return
                no_of_rows = len(table.find_all('tr'))
                print(f"Page : {page_num} | No of rows: {no_of_rows}")

                # The html contains table which hold info - PDF Title, Data, PDF Viewer Link
                for row in table.find_all('tr'):
                    if(row == None):
                        continue
                    all_cells = row.find_all('td')
                    #Exclude the first row
                    if(len(all_cells) == 0):
                        continue

                    anchor_tag = all_cells[1].find('a')
                    date = all_cells[0].text
                    title = all_cells[1].text
                    href_link = anchor_tag.get('href')
                    new_row = {
                        "title" : title,
                        "date" : date,
                        "html_link" : href_link,
                        "pdf_link" : "",
                        "type": type,
                        "sub_type" : sub_type,
                        "file_name" : "",
                        "pdf_text" : ""
                    }

                    self.data.append(new_row)

                ############ ENDS HERE ############

                time.sleep(2)

                # Check if the page contains pagination or is it a single page
                try:
                    if not (driver.find_element(By.CLASS_NAME, "pagination_outer")):
                        return

                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "pagination_outer"))
                        # Check if the pagination_outer is loaded, so we can move on to next step
                    )
                except NoSuchElementException:
                    print("Exceptions occured!")
                    print(".paginatiom_outer is not present")

                # if we cant find the next_button, it means we are at the last page
                if not (driver.find_elements(By.XPATH, "//*[@title='Next']")):
                    return

                next_button = driver.find_element(By.XPATH, "//*[@title='Next']")
                time.sleep(2)

                next_button.click()
                logging.info('Clicked on Next Button')

                driver.implicitly_wait(5)
                logging.info('Waited for download to complete')
            except Exception as e:
                print("EXCEPTION occurred :",e)
                logging.error(f'An exception occurred: {str(e)}')
                return
            finally:
                #driver.quit()
                page_num += 1
                print("Exiting navigation_pagination_and_collect_links")
                logging.info('Exiting navigation_pagination_and_collect_links')

    # Function that collects html links from navigating to each menu links
    def collect_html_links(self,menu_to_scrape, submenu_to_scrape):
        print(f"Entering collect_html_links for [{menu_to_scrape}] | [{submenu_to_scrape}]")
        df = pd.read_csv(urls_of_sebi_menu_csv_path)
        
        for _,row in df.iterrows():
            menu = row['menu']
            submenu = row['submenu']
            url = row['url']
            # print(f"Creating list of urls using menu: {menu} and sub_menu: {submenu}")
            menu = menu.replace(" ","_")
            submenu = submenu.replace(" ","_")
            if(menu.lower() == menu_to_scrape.lower() and submenu.lower() == submenu_to_scrape.lower()):
                print(f"Accessing the link {url}")
                self.navigate_pagination_and_collect_links(url,menu,submenu)
            # print(f"Row added in CSV: {menu} | sub_menu: {submenu}")
    
    def collect_pdf_links(self,menu_to_scrape, submenu_to_scrape):
        print("xx")
        self.collect_html_links(menu_to_scrape, submenu_to_scrape)
        print(f"collecting pdf links for : [{menu_to_scrape}] | [{submenu_to_scrape}]")
        def soup_returner(url):
            soup = BeautifulSoup()
            try:
                session = requests.Session()
                retry = HTTPAdapter(max_retries=5)
                session.mount("http://", retry)
                session.mount("https://", retry)
                read = session.get(url,verify=False)
                html_content = read.text
                soup = BeautifulSoup(html_content,'html.parser')
            except Exception as e:
                print("URL ", url)
                print("Exception occured : ",e )
            return soup

        for row in self.data:
            url = row['html_link']
            soup = soup_returner(url)
            only_anchor_tags = soup.find_all('iframe')
            new_pdf_link = ""
            for link in only_anchor_tags:
                href_link = link.get('src')
                if href_link!=None and href_link.lower().endswith(".pdf"):
                    pdf_link = href_link
                    new_pdf_link = urljoin(home_page_url,pdf_link)
            row['pdf_link'] = new_pdf_link

            #storing the name of the pdf for the future use
            split_pdf_link = new_pdf_link.split("/")
            row['file_name'] = split_pdf_link[-1]
            
            # If thge pdf name is blank that means the content is html file
            if (new_pdf_link == ""):
                url_base64 = base64.b64encode(url.encode()).decode()
                row['file_name'] = url_base64+".html"

        df2 = pd.DataFrame(self.data)
        df2.to_csv(pdf_links_of_all, mode='a', index=True)

    # @staticmethod
    def download_pdf(self,url,download_path,file_name):
        logging.basicConfig(filename='selenium_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
        logging.info(f"Downloading {file_name} in {download_path}")
        print(f"Downloading {file_name} in {download_path}")

        if(not url.startswith("http")):
            logging.info("Not a valid url")
            return
        
        pdf_path = os.path.join(download_path,file_name)
        if(os.path.exists(pdf_path)):
            print(f"The pdf {file_name} already exists")
            logging.info(f"The pdf {file_name} already exists")
            return

        try:
            response = requests.get(url)
            logging.info(f'Status of url : {url} is {response.status_code}')
            if(response.status_code != 200):
                print(f"Status of {url} is {response.status_code}")
            options = webdriver.ChromeOptions()

            prefs = {
                "download.default_directory": download_path,
                'download.prompt_for_download': False,
                'plugins.always_open_pdf_externally': True
            }

            options.add_argument("--headless=new")

            options.add_experimental_option('prefs',prefs)

            driver = webdriver.Chrome(options=options)
            driver.get(url)
            logging.info(f'Navigated to URL: {url}')
            # Wait for some time to ensure the PDF is loaded
            #driver.implicitly_wait(10)

            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "download"))
            )

            #Find the DOWNLOAD Button from the pdfviewer using the id of button tag
            download_button = driver.find_element(By.ID, "download")
            time.sleep(3)
            download_button.click()
            logging.info('Clicked on PDF download Button')
            driver.implicitly_wait(10)
            logging.info('Waited for download to complete')
            time.sleep(6)

            # num = rename_most_recent_pdf(download_path,file_name,past_num_of_files_present)
            # past_num_of_files_present = num
            # print(f"Past num of files present : {past_num_of_files_present}")

        except Exception as e:
            print("EXCEPTION ",e)
            logging.error(f'An error occurred: {str(e)}')
        finally:
            #driver.quit()
            logging.info('Browser session closed')

    def download_pdf_new(self,row):
        url = row['pdf_link']
        html_url = row['html_link']
        title = row['title']
        type = row['type']
        sub_type = row['sub_type']
        file_name = row['file_name']
        
        type = type.replace(" ","_")
        sub_type = sub_type.replace(" ","_")
        # SEBI_data_extraction_base_folder = r"D:\Educational\Sarvam AI\Python\SEBI\SEBI_Extracted_Data"
        type_folder_path = os.path.join(SEBI_data_extraction_base_folder,type)
        sub_type_folder_path = os.path.join(type_folder_path,sub_type)
        download_path = sub_type_folder_path
        
        print("URL Accessing ",url)
        
        file_path = os.path.join(download_path, file_name)
        if(os.path.exists(file_path)):
            print(f"the file {file_path} already exists.")
            return
        
        try:
            response = requests.get(url)
            # logging.info(f'Status of url : {url} is {response.status_code}')
            if(response.status_code != 200):
                print(f"Status of {url} is {response.status_code}")
            options = webdriver.ChromeOptions()

            prefs = {
                "download.default_directory": download_path,
                'download.prompt_for_download': False,
                'plugins.always_open_pdf_externally': True
            }

            options.add_argument("--headless=new")

            options.add_experimental_option('prefs',prefs)

            driver = webdriver.Chrome(options=options)
            driver.get(url)
            # logging.info(f'Navigated to URL: {url}')
            
            # options = webdriver.ChromeOptions()
            # # options.add_argument("enable-automation")
            # options.add_argument("--headless=new")
            # options.add_argument('--no-sandbox')
            # options.add_argument("--disable-dev-shm-usage")
            # driver = webdriver.Chrome(options=options)
            
            
            # chrome_options = Options()
            # chrome_options.add_argument("--headless")  # Optional: Run browser in headless mode
            # driver = webdriver.Chrome(options=chrome_options)
            # options = webdriver.ChromeOptions()

            # prefs = {
            #     "download.default_directory": download_path,
            #     'download.prompt_for_download': False,
            #     'plugins.always_open_pdf_externally': True
            # }

            # options.add_experimental_option('prefs',prefs)

            # driver = webdriver.Chrome(options=options)
            # driver.get(url)
            # logging.info(f'Navigated to URL: {url}')
            # Wait for some time to ensure the PDF is loaded
            #driver.implicitly_wait(10)

            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "download"))
            )

            #Find the DOWNLOAD Button from the pdfviewer using the id of button tag
            download_button = driver.find_element(By.ID, "download")
            time.sleep(2)
            download_button.click()
            
            driver.implicitly_wait(10)
            # logging.info('Waited for download to complete')
            time.sleep(6)
            
            timeout = 25  # Maximum wait time in seconds
            start_time = time.time()
            while time.time() - start_time < timeout:
                print(str(time.time() - start_time))
                if os.path.isfile(os.path.join(download_path, file_name)):
                    print(f"Download complete! for {file_name} in {download_path}")
                    break
                time.sleep(1)  # Check every 1 second
        except NoSuchElementException:
            print(f"Download button not found for URL: {url}")
        finally:
            # driver.quit()
            print("Exiting download_pdf_new")
    
    # @staticmethod
    def download_html(self,url,download_path, file_name):
        print(f"Downloading {file_name} in {download_path}")
        response = requests.get(url)
        
        # filename_hashed = hashlib.sha256(url.encode('utf-8')).hexdigest()

        file_download_path = os.path.join(download_path,file_name)
        if(os.path.exists(file_download_path)):
            print(f"The file {file_name} already exists")
            logging.info(f"The file {file_name} already exists")
            return

        if response.status_code == 200:
            print(response.status_code)
            with open(file_download_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"{url} is downloaded into {download_path}")
        else:
            print("Failed to download HTML:", response.status_code)
            
    def download_html_new(self,row):
        # url = row['pdf_link']
        html_url = row['html_link']
        title = row['title']
        type = row['type']
        sub_type = row['sub_type']
        file_name = row['file_name']
        
        
        
        print(f" File : {file_name} and LENGTH : {len(file_name)}",file_name)
        
        
        type = type.replace(" ","_")
        sub_type = sub_type.replace(" ","_")
        type_folder_path = os.path.join(SEBI_data_extraction_base_folder,type)
        sub_type_folder_path = os.path.join(type_folder_path,sub_type)
        download_path = sub_type_folder_path
        
        file_path = os.path.join(download_path, file_name)
        if(os.path.exists(file_path)):
            print(f"the file {file_path} already exists.")
            return
        
        response = requests.get(html_url)

        if response.status_code == 200:
            print(response.status_code)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"{html_url} is downloaded into {download_path}")
        else:
            print("Failed to download HTML:", response.status_code)
    
    
    # def download_all_files(self):
    #     print("Downloading in...",SEBI_data_extraction_base_folder)
    #     for row in self.data:

    #         pdf_url = row['pdf_link']
    #         html_url = row['html_link']
    #         title = row['title']
    #         sub_type = row['type']
    #         sub_sub_type = row['sub_type']
    #         file_name = row['file_name']

    #         sub_type = sub_type.replace(" ","_")
    #         sub_sub_type = sub_sub_type.replace(" ","_")
            
    #         sub_type_folder_path = os.path.join(SEBI_data_extraction_base_folder,sub_type)
    #         sub_sub_type_folder_path = os.path.join(sub_type_folder_path,sub_sub_type)
    #         download_path = sub_sub_type_folder_path

    #         if (pdf_url == ""):
    #             self.download_html(html_url, download_path, file_name)
    #             continue
    #         self.download_pdf(pdf_url, download_path,file_name)
    
    def count_files(self, menu,submenu,file_type):
    # Ensure the folder exists

        folder_path = os.path.join(SEBI_data_extraction_base_folder,menu)
        folder_path = os.path.join(folder_path,submenu)
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return

        # Initialize the count
        file_count = 0
        total_files = 0
        # Iterate through all items in the folder
        for item in os.listdir(folder_path):
            # Check if the item is a file
            if os.path.isfile(os.path.join(folder_path, item)):
                # If it's a file, increment the count
                total_files += 1
                if(item.lower().endswith(file_type)):
                    file_count += 1

        return file_count,total_files
    
    def create_list_of_links(self,menu,submenu):

        df = pd.read_csv(pdf_links_of_all)
        pdf_link_list = []
        html_link_list = []
        total_pdf_count = 0
        total_html_count = 0
        
        print(f"Create list of links {menu} and {submenu}")
        
        i = 0
        
        for _,row in df.iterrows():
            
            pdf_link = row['pdf_link']
            html_url = row['html_link']
            title = row['title']
            type = row['type']
            sub_type = row['sub_type']
            file_name = row['file_name']
            flag = False
            
            
            if(pd.isna(row['pdf_link'])):
                flag = True
            if(pd.isna(html_url) or pd.isna(title) or pd.isna(type) or pd.isna(sub_type) or pd.isna(file_name)):
                print("Values are empty")
                continue
            
            def create_download_path(type, sub_type):
                type = type.replace(" ","_")
                sub_type = sub_type.replace(" ","_")
                
                type_folder_path = os.path.join(SEBI_data_extraction_base_folder,type)
                sub_type_folder_path = os.path.join(type_folder_path,sub_type)
                download_path = sub_type_folder_path
                return download_path
            
            download_path = create_download_path(type,sub_type)
            file_path = os.path.join(download_path,file_name)
            
            if(not pd.isna(pdf_link)):
                if(menu == str(row['type']) and submenu == str(row['sub_type'])):
                    # print("pdf_list udpated")
                    total_pdf_count += 1
            else:
                if(menu == str(row['type']) and submenu == str(row['sub_type'])):
                    # print("html list updated")
                    total_html_count += 1
            
            
            # print(f"TYPE : {type} SUBTYPE : {sub_type}")
            if(not pd.isna(pdf_link)):
                if(menu == str(row['type']) and submenu == str(row['sub_type'])):
                    # print("pdf_list udpated")
                    if(os.path.exists(file_path)):
                        print(f"Not adding to list, becoz The file {file_path} already exists")
                        continue
                    pdf_link_list.append(row)
            else:
                if(menu == str(row['type']) and submenu == str(row['sub_type'])):
                    # print("html list updated")
                    if(os.path.exists(file_path)):
                        print(f"Not adding to list, becoz The file {file_path} already exists")
                        continue
                    html_link_list.append(row)
                    
            # DELETE IT LATER
            if(len(pdf_link_list) == 4000):
                return pdf_link_list,html_link_list,total_pdf_count,total_html_count
                
        return pdf_link_list,html_link_list,total_pdf_count,total_html_count
    
    def download_files(self, menu, sub_menu):
        df = pd.read_csv(pdf_links_of_all)
        
        for _,row in df.iterrows():
            pdf_url = row['pdf_link']
            html_url = row['html_link']
            title = row['title']
            type = row['type']
            sub_type = row['sub_type']
            file_name = row['file_name']
            flag = False
            if(pd.isna(row['pdf_link'])):
                flag = True
            if(pd.isna(html_url) or pd.isna(title) or pd.isna(type) or pd.isna(sub_type) or pd.isna(file_name)):
                print("Values are empty.")
                continue
            
            type = type.replace(" ","_")
            sub_type = sub_type.replace(" ","_")
            
            type_folder_path = os.path.join(SEBI_data_extraction_base_folder,type)
            sub_type_folder_path = os.path.join(type_folder_path,sub_type)
            download_path = sub_type_folder_path
            
            if (sub_menu == None):
                if(menu == type.lower()):
                    if (flag):
                        file_name = row['file_name']
                        filename_hashed = hashlib.sha256(html_url.encode('utf-8')).hexdigest()
                        row['file_name'] = filename_hashed
                        self.download_html(html_url, download_path, filename_hashed)
                    else:
                        self.download_pdf(pdf_url, download_path,file_name)
            else:
                if(menu == type.lower() and sub_menu == sub_type.lower()):
                    if (flag):
                        file_name = row['file_name']
                        filename_hashed = hashlib.sha256(html_url.encode('utf-8')).hexdigest()
                        row['file_name'] = filename_hashed
                        self.download_html(html_url, download_path, filename_hashed)
                    else:
                        self.download_pdf(pdf_url, download_path,file_name)
                        
    def download_files2(self, row, menu, sub_menu):
        
        pdf_url = row['pdf_link']
        html_url = row['html_link']
        title = row['title']
        type = row['type']
        sub_type = row['sub_type']
        file_name = row['file_name']
        
        print(f"Downloading..... {html_url}")
        
        type = type.replace(" ","_")
        sub_type = sub_type.replace(" ","_")
        
        type_folder_path = os.path.join(SEBI_data_extraction_base_folder, type)
        sub_type_folder_path = os.path.join(type_folder_path, sub_type)
        download_path = sub_type_folder_path

        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        if (sub_menu == None):
            if(menu == type.lower()):
                if (pdf_url == ""):
                    self.download_html(html_url, download_path, file_name)
                else:
                    self.download_pdf(pdf_url, download_path,file_name)
            else:
                if(menu == type.lower() and sub_menu == sub_type.lower()):
                    if (pdf_url == ""):
                        self.download_html(html_url, download_path, file_name)
                    else:
                        self.download_pdf(pdf_url, download_path,file_name)
                        
    def download_files3(self,menu,submenu):
        print("inside download_files3")
        print(menu,submenu)
        pdf_urls = []
        html_urls = []
        pdf_urls,html_urls,total_pdf_count,total_html_count = self.create_list_of_links(menu,submenu)
        for row in pdf_urls:
            print(row)
            print(row['pdf_link'])
            print("-------------------")
        print("HTML Links ::: ")
        for row in html_urls:
            print(row['html_link'])
            print("-------------------") 
        
        print("List has been created, moving on to downloads")
        
        # Concurrently download PDFs
        round = 1
        file_count,total_files_downloaded = self.count_files(menu,submenu,"pdf")
        i = 0
        
        # for row in pdf_urls:
        #     self.download_pdf_new(row)
        #     print(f"Download completed : {i}/{len(pdf_urls)} ")
        #     i += 1
        while(1):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.download_pdf_new, pdf_urls)
            pdf_urls = []
            html_urls = []
            pdf_urls,html_urls,total_pdf_count,total_html_count = self.create_list_of_links(menu,submenu)
            
        ##########################      
        # while(total_files_downloaded < total_pdf_count):
        #     print(f"Round : {round}")
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
        #         executor.map(self.download_pdf_new, pdf_urls)
        #     # for row in pdf_urls:
        #     #     self.download_pdf_new(row)
        #     file_count,_ = self.count_files(menu,submenu,"pdf")
        #     print(f"File Count : {file_count}/{total_files_downloaded}")
        #     round += 1
        ####################
        
        # Concurrently download HTMLs
        round = 1
        i = 0
        file_count,total_files_downloaded = self.count_files(menu,submenu,"html")
        for row in html_urls:
            self.download_html_new(row)
            print(f"Download completed : {i}/{len(html_urls)} ")
            i += 1
        # while(total_files_downloaded < total_html_count):
        #     print(f"Round : {round}")
        #     # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     #     executor.map(self.download_html_new, html_urls)
        #     for row in html_urls:
        #         self.download_html_new(row)
        #     file_count,_ = self.count_files(menu,submenu,"html")
        #     print(f"File Count : {file_count}/{total_files_downloaded}")
        #     round += 1
        ###########################
        
        
        
        
        
    # def download_files_concurrently(self, menu, sub_menu):
    #     pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Use number of available CPUs
    #     func = lambda row: self.download_file(row, menu, sub_menu)
    #     df = pd.read_csv(pdf_links_of_all)
    #     pool.map(func, df.iterrows())
    #     pool.close()
    #     pool.join()
  