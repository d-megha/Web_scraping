
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import csv,time,random
from datetime import datetime, timedelta
from fake_headers import Headers
from selenium.common.exceptions import NoSuchElementException
from stem import Signal
# from c 
# from torrequest import TorRequest
import threading
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import pymysql;

class Naukri:


    @staticmethod
    def init_driver(browser_name:str):
        def set_properties(browser_option):
                ua = Headers().generate()      #fake user agent
                # browser_option.add_argument('--headless')
                # browser_option.add_argument('--disable-extensions')
                # browser_option.add_argument('--incognito')
                # browser_option.add_argument('--disable-gpu')
                # browser_option.add_argument('--log-level=3')
                browser_option.add_argument(f'user-agent={ua}')
                # print(browser_option.add_argument(f'user-agent={ua}'))
                # browser_option.add_argument('--disable-notifications')
                # browser_option.add_argument('--disable-popup-blocking')            
                return browser_option



        # with TorRequest(proxy_port=9050, ctrl_port=9051, password='password') as tr:
        #         tr.ctrl.signal(Signal.NEWNYM)  # Request a new connection to the TOR network
        #         session = tr.session
        #         browser_option = FirefoxOptions()
        #         browser_option = set_properties(browser_option)
        #         driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=browser_option,proxy=Proxy({
        #             'proxyType': ProxyType.MANUAL,
        #             'httpProxy': 'socks5://127.0.0.1:9050',
        #             'ftpProxy': 'socks5://127.0.0.1:9050',
        #             'sslProxy': 'socks5://127.0.0.1:9050',
        #         }))
        #         return driver


        try:
            browser_name = browser_name.strip().title()
            print(browser_name)

            ua = Headers().generate()
            print(ua)      #fake user agent
            #automating and opening URL in headless browser
            if browser_name.lower() == "chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_option) #chromedriver's path in first argument
                driver.maximize_window()
            elif browser_name.lower() == "firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=browser_option)
                driver.maximize_window()
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)


            
    @staticmethod
    def scrap(browser_name,page_range):
        def is_fully_visible(driver, element):
            """Returns True if the element is fully visible on the screen, False otherwise."""
            # Get the element's bounding rectangle
            rect = element.rect

            # Get the viewport's size
            viewport_height = driver.execute_script("return Math.max( document.documentElement.clientHeight, window.innerHeight );")
            viewport_width = driver.execute_script("return Math.max( document.documentElement.clientWidth, window.innerWidth );")

            # Calculate the element's top and bottom coordinates relative to the viewport
            top_coord = rect["y"]
            bottom_coord = rect["y"] + rect["height"]

            # Return True if the element is fully visible, False otherwise
            return top_coord >= 0 and bottom_coord <= viewport_height

        #taking username and chrome as default browser
        random_values = [15,16,17,18,19,20] #for giving random number of waits
      
        pageno_strt = int(input("Enter starting page no: "))
        time.sleep(10)
        pageno_end = int(input("Enter ending page no: "))+1
        # pageno_strt = 1
        # pageno_end = 2
        time.sleep(15)
        for page_index in range(pageno_strt,pageno_end):#no of pages +1 should be given
            URL = f"https://www.naukri.com/jobs-in-all-india-{page_index}?jobPostType=1"
            header_row= ["SI","Company Name","Company Rating","Job title","Experience","Education-UG","Education-PG","Salary","Location","Description","Role","Industry Type","Functional Area","Employment Type","Role Categoty","Must have skills","Other skills","Posted","Openings","Job views","Applicants","URL"]
            with open(f"new/Data{page_index}.csv", 'w') as f:
                csvwriter = csv.writer(f) 
                csvwriter.writerow(header_row)
                f.close()
            driver = Naukri.init_driver(browser_name)
            try:
                driver.get(URL)
                time.sleep(random.choice(random_values))

            except AttributeError:
            
                print("Driver is not set")
                exit()

            time.sleep(random.choice(random_values))
            count= driver.find_element('xpath',"//span[@class='fleft count-string mr-5 fs12']").text
            counter = count.split("-")[0]
            counter = int(counter)

            new_counter = counter-1
                
            for result_index in range(1,21):#range 1,21 since 20 result in one page.
                result_Si =new_counter+result_index
                p = driver.current_window_handle
                parent = driver.window_handles[0]
                driver.switch_to.window(parent)
                driver.implicitly_wait(20)
                time.sleep(5)
                
                job_post = driver.find_element("xpath",f"//div[@class='list']//article[{result_index}]")
                if not is_fully_visible(driver, job_post):
                    driver.execute_script("arguments[0].scrollIntoView();", job_post)

           
                time.sleep(6)
                WebDriverWait(driver,20)
                time.sleep(random.choice(random_values))
                webdriver.ActionChains(driver).move_to_element(job_post).click(job_post).perform()
                time.sleep(random.choice(random_values))
                child = driver.window_handles[1]
                driver.switch_to.window(child)
                company_url = driver.current_url 
                try:
                    try:
                        company_name = driver.find_element("xpath","//div[@class='jd-top-head']//div[@class='jd-header-comp-name']//a[@class='pad-rt-8']").text
                        rating = driver.find_element("xpath","//div[@class='jd-header-comp-name']//preceding::span[@class='amb-reviews pad-rt-4']//preceding::span[@class='amb-rating pad-rt-4']").text
                        job_title = driver.find_element("xpath","//h1[@class='jd-header-title']").text
                        experience = driver.find_element("xpath","//div[@class='exp']//span").text
                        salary = driver.find_element("xpath","//div[@class='salary']//span").text
                        location = driver.find_element("xpath","//span[@class='location ']").text
                        x= 1 # first pattern
                    except NoSuchElementException:
                        pass
                    try:
                        company_name = driver.find_element("xpath","//p[@class='cpName f14']").text
                        rating = 'not provided'
                        job_title = driver.find_element("xpath","//h1").text
                        experience = driver.find_element("xpath","//span[@class='jobs-icon exp']").text
                        salary = driver.find_element("xpath","//span[@class='job-meta slide-meta-sal']").text
                        location = driver.find_element("xpath","//span[@class='jobs-icon loc']").text
                        x= 2 # second pattern
                    except NoSuchElementException:
                        pass
                    try:
                        company_name = driver.find_element("xpath","//div[@class='f14 lh18 alignJ'][1]").text
                        rating = 'not provided'
                        job_title = driver.find_element("xpath","//h1").text
                        experience = driver.find_element("xpath","//div[@class='jdSum ovh hLine pb20']//span[@class='icon exp']").text
                        salary = driver.find_element("xpath","//span[@class='naukicon naukicon-salary']").text
                        location = driver.find_element("xpath","//div[@class='jdSum ovh hLine pb20']//span[@class='fl disc-li']").text
                        x= 3 #third pattern
                    except NoSuchElementException:
                        pass
                    try:
                        company_name = driver.find_element("xpath","//div[@class='f14 lh18 alignJ'][1]").text
                        rating = 'not provided'
                        job_title = driver.find_element("xpath","//h1").text
                        experience = driver.find_element("xpath","//div[@class='slide-meta getExperience']//span[@class='slide-meta-exp pull-left']").text
                        salary1 = driver.find_element("xpath","//span[@class='job-meta slide-meta-sal']").text
                        salary = salary1.strip("From of experience").replace("year(s)", "years")
                        print(salary+"4")
                        location = driver.find_element("xpath","//span[@class='slide-meta-loc pull-left']").text
                        x= 5 #2 pattern
                    except NoSuchElementException:
                        pass
                except:
                    x=4


                if x==1: # first pattern web2652 elements
                    try:
                        role = driver.find_element("xpath","//div[@class='other-details']//label[(text()='Role')]//following-sibling::span").text
                    except NoSuchElementException:
                        role = "Not provided"
                    try:
                        industry_type=driver.find_element("xpath","//div[@class='other-details']//label[(text()='Industry Type')]//following-sibling::span").text
                    except NoSuchElementException:
                        industry_type = "Not provided"
                    try:
                        functional_area=driver.find_element("xpath","//div[@class='other-details']//label[(text()='Functional Area')]//following-sibling::span").text
                    except NoSuchElementException:
                        functional_area ="Not provided"
                    try:
                        employment_type=driver.find_element("xpath","//div[@class='other-details']//label[(text()='Employment Type')]//following-sibling::span").text
                    except NoSuchElementException:
                        employment_type= "Not provided"
                    try:
                        role_category=driver.find_element("xpath","//div[@class='other-details']//label[(text()='Role Category')]//following-sibling::span").text
                    except NoSuchElementException:
                        role_category = "Not provided"
                    try:
                        education_ug = driver.find_element("xpath","//div[@class='education']//div[@class='details']//following::span").text
                    except NoSuchElementException:
                        education_ug = "Not provided"
                    try:
                        education_pg = driver.find_element("xpath","//div[@class='education']//div[@class='details']//following::span//following::span").text
                    except NoSuchElementException:
                        education_pg = "Not provided"
                    try:
                        post = driver.find_element("xpath","//div[@class='jd-stats']//preceding::span[@class='stat']//span").text.split(" ")
                        if post[0].isdigit():
                            posted = int(post[0])
                            post_date = datetime.today() - timedelta(days=float(posted))
                            date_posted = (post_date.strftime('%d-%m-%Y'))
                            posted_on = str(date_posted)
                        else:
                            post_date = datetime.today()
                            date_posted = (post_date.strftime('%d-%m-%Y'))
                            posted_on = str(date_posted)
                    except NoSuchElementException:
                        posted_on = "Not provided"
                    try:
                        openings = driver.find_element("xpath","//div[@class='jd-stats']//following-sibling::span//span").text
                        job_views = "Not Available"
                        job_applicants = driver.find_element("xpath","//div[@class='jd-stats']//following-sibling::span//following-sibling::span//span").text        
                    except NoSuchElementException:
                        openings = "Not provided"
                        job_views = "Not Available"
                        job_applicants = driver.find_element("xpath","//div[@class='jd-stats']//following-sibling::span//span").text
                    try:#must have skills
                        skills_1 = driver.find_elements("xpath","//div[@class='key-skill']//div[text()='Key Skills']//following-sibling::div[1]/*")
                        skill_list_1 = []
                        for i in range(len(skills_1)):
                            my_skills_1 =''
                            my_skills_1 = skills_1[i].get_attribute("innerText")   
                            skill_list_1.append(my_skills_1)          
                        if skill_list_1 is None:
                            print("Not Mentioned")
                    except:#other skills
                        skill_list_1 = "not mentioned"

                    try:
                        skills_2 = driver.find_elements("xpath","//div[@class='key-skill']//div[text()='Key Skills']//following-sibling::div[2]/*")
                        skill_list_2 = []
                        for i in range(len(skills_2)):
                            my_skills_2 =''
                            my_skills_2 = skills_2[i].get_attribute("innerText")   
                            skill_list_2.append(my_skills_2) 
                        if skill_list_2 is None:
                            print("Not Mentioned")
                    except:
                        skill_list_2 = "not mentioned"

                    try:
                        description_items = driver.find_elements("xpath","//div[@class='dang-inner-html']")
                        description_dic = dict()
                        key = ""
                        value_total = ""
                        
                        for i in range(len(description_items)):
                            tags = description_items[i].tag_name
                            if tags.startswith("h") or tags.find("strong"):
                                if key:
                                    description_dic[key] = value_total
                                    key = ""
                                    value_total = ""
                                key = description_items[i].get_attribute("innerText")
                            if tags.startswith("p"):
                                value = description_items[i].get_attribute("innerText")
                                value_total = value_total + value
                            if tags.startswith("ul"):
                                li_tag_items = description_items[i].find_elements_by_tag_name('li')
                                for j in range(len(li_tag_items)):
                                    li_tag_item = li_tag_items[j].get_attribute("innerText")
                                    value_total = value_total + li_tag_item

                        description_direc= ''
                        for k, v in description_dic.items():
                            description_direc = description_direc + k + '\n' + v                 
                        if description_dic is not None:
                            description_direc = driver.find_element("xpath","//div[@class='dang-inner-html']").text
                    
                    except NoSuchElementException:
                        pass



                if x==2:# second pattern web elements
                    try:
                        role = driver.find_element("xpath","//p[@class='coPE getRoleLabel']//span").text
                    except NoSuchElementException:
                        role = "not provided"            
                    try:
                        industry_type=driver.find_element("xpath","//p[@class='coPE getIndustryLabel']//span//span").text
                    except NoSuchElementException:
                        industry_type= "not provided"          
                    try:
                        functional_area=driver.find_element("xpath","//p[@class='coPE getFareaLabel']//span//span").text
                    except NoSuchElementException:
                        functional_area= "not provided" 
                    try:
                        employment_type=driver.find_element("xpath","//p[@class='coPE getEmploymentType']//span").text
                    except NoSuchElementException:
                        employment_type = "not provided"
                    try:
                        role_category=driver.find_element("xpath","//p[@class='coPE getCategoryRoleLabel']//span").text
                    except NoSuchElementException:
                        role_category= "not provided"
                    try:
                        education_ug = driver.find_element("xpath","//p[@class='coPE getUGCourse']//span").text
                    except NoSuchElementException:
                        education_ug = "Not provided"
                    try:
                        education_pg = driver.find_element("xpath","//p[@class='coPE getPGCourse']//span").text
                    except NoSuchElementException:
                        education_pg = "Not provided"
                    try:
                        post = driver.find_element("xpath","//div[@class='sumFoot']//strong").text.split(" ")
                        if post[0].isdigit():
                            posted = int(post[0])
                            post_date = datetime.today() - timedelta(days=float(posted))
                            date_posted = (post_date.strftime('%d-%m-%Y'))
                            posted_on = str(date_posted)
                        else:
                            post_date = datetime.today()
                            date_posted = (post_date.strftime('%d-%m-%Y'))
                            posted_on = str(date_posted)
                    except NoSuchElementException:
                        posted_on = "Not provided"
                    try:
                        job_views = driver.find_element("xpath","//span[@class='jViews']//strong").text
                        openings = "Not available"
                        job_applicants = driver.find_element("xpath","//span[@class='jApplys']//strong").text        
                    except NoSuchElementException:
                        job_views = "Not provided"
                        job_applicants = "not provided"
                        openings = "Not available"
                        
                
                    try:
                        description_items = driver.find_elements("xpath","//div[@class='clearboth description']")
                        description_dic = dict()
                        key = ""
                        value_total = ""

                        for i in range(len(description_items)):
                            tags = description_items[i].tag_name
                            if tags.startswith("h") or tags.find("strong"):
                                if key:
                                    description_dic[key] = value_total
                                    key = ""
                                    value_total = ""
                                key = description_items[i].get_attribute("innerText")
                            if tags.startswith("p"):
                                value = description_items[i].get_attribute("innerText")
                                value_total = value_total + value
                            if tags.startswith("ul"):
                                li_tag_items = description_items[i].find_elements_by_tag_name('li')
                                for j in range(len(li_tag_items)):
                                    li_tag_item = li_tag_items[j].get_attribute("innerText")
                                    value_total = value_total + li_tag_item

                        description_direc = ''
                        for k, v in description_dic.items():
                            description_direc = description_direc + k + '\n' + v
                        if description_dic is not None:
                            description_direc = driver.find_element("xpath","//div[@class='clearboth description']").text
                    except NoSuchElementException:
                        pass
                
                    try:#must have skills
                        skills_1 = driver.find_elements("xpath","//div[@class='getJobKeySkillsSection key-skill']//div[text()='Key Skills']//following-sibling::div[1]/*")
                        skill_list_1 = [] 
                        for i in range(len(skills_1)):
                            my_skills_1 =''
                            my_skills_1 = skills_1[i].get_attribute("innerText")   
                            skill_list_1.append(my_skills_1)          
                        if skill_list_1 is None:
                            print("Not Mentioned")
                    except:
                        skill_list_1 = "Not mentioned"

                    try:#other skills
                        skills_2 = driver.find_elements("xpath","//div[@class='getJobKeySkillsSection key-skill']//div[text()='Key Skills']//following-sibling::div[2]/*")
                        skill_list_2 = []
                        for i in range(len(skills_2)):
                            my_skills_2 =''
                            my_skills_2 = skills_2[i].get_attribute("innerText")   
                            skill_list_2.append(my_skills_2) 
                        if skill_list_2 is None:
                            print("Not Mentioned")
                    except:
                        skill_list_2 = "Not mentioned"

                



                    if x==3:# second pattern web elements
                        try:
                            role_1 = driver.find_element("xpath",'//*[@id="apply_career"]/div[1]/div[2]/text()[4]').text
                            role =role_1.split(":")[1]
                        except NoSuchElementException:
                            role = "not provided"            
                        try:
                            industry_type=driver.find_element("xpath",'//*[@id="apply_career"]/div[1]/div[2]/text()[2]//following-sibling::a[1]').text
                        except NoSuchElementException:
                            industry_type= "not provided"          
                        try:
                            functional_area=driver.find_element("xpath",'//*[@id="apply_career"]/div[1]/div[2]/text()[2]//following-sibling::a[2]').text
                        except NoSuchElementException:
                            functional_area= "not provided" 
                        try:
                            employment_type_1=driver.find_element("xpath",'//*[@id="apply_career"]/div[1]/div[2]/text()[5]').text
                            employment_type = employment_type_1.split(':')[1]
                        except NoSuchElementException:
                            employment_type = "not provided"
                        try:
                            role_category_1=driver.find_element("xpath",'//*[@id="apply_career"]/div[1]/div[2]/text()[4]').text
                            role_category = role_category_1.split(':')[1]
                        except NoSuchElementException:
                            role_category= "not provided"
                        try:
                            education_ug_1 = driver.find_element("xpath",'//*[@id="apply_career"]/div[4]/div/text()[1]').text
                            education_ug = education_ug_1.split("-")[1]
                        except NoSuchElementException:
                            education_ug = "Not provided"
                        try:
                            education_pg_1 = driver.find_element("xpath",'//*[@id="apply_career"]/div[4]/div/text()[2]').text
                            education_pg = education_pg_1.split("-")[1]
                        except NoSuchElementException:
                            education_pg = "Not provided"
                        try:
                            post = driver.find_element("xpath","//div[@class='sumFoot']//span[1]").text.split(" ")
                            if post[0].isdigit():
                                posted = int(post[0])
                                post_date = datetime.today() - timedelta(days=float(posted))
                                date_posted = (post_date.strftime('%d-%m-%Y'))
                                posted_on = str(date_posted)
                            else:
                                post_date = datetime.today()
                                date_posted = (post_date.strftime('%d-%m-%Y'))
                                posted_on = str(date_posted)
                        except NoSuchElementException:
                            posted_on = "Not provided"
                        try:
                            job_views = driver.find_element("xpath","//span[@class='fr jViews']//strong").text
                            openings = "Not available"
                            job_applicants = driver.find_element("xpath","//span[@class='fr jApplys']//strong").text        
                        except NoSuchElementException:
                            job_views = "Not provided"
                            job_applicants = "not provided"
                            openings = "Not available"
                            

                        try:
                            description_items = driver.find_elements("xpath",'//*[@id="apply_career"]/div[1]/div[1]/h2')
                            description_dic = dict()
                            key = ""
                            value_total = ""

                            for i in range(len(description_items)):
                                tags = description_items[i].tag_name
                                if tags.startswith("h") or tags.find("strong"):
                                    if key:
                                        description_dic[key] = value_total
                                        key = ""
                                        value_total = ""
                                    key = description_items[i].get_attribute("innerText")
                                if tags.startswith("p"):
                                    value = description_items[i].get_attribute("innerText")
                                    value_total = value_total + value
                                if tags.startswith("ul"):
                                    li_tag_items = description_items[i].find_elements_by_tag_name('li')
                                    for j in range(len(li_tag_items)):
                                        li_tag_item = li_tag_items[j].get_attribute("innerText")
                                        value_total = value_total + li_tag_item

                            description_direc = ''
                            for k, v in description_dic.items():
                                description_direc = description_direc + k + '\n' + v
                            if description_dic is not None:
                                description_direc = driver.find_element("xpath","//div[@class='clearboth description']").text
                        except NoSuchElementException:
                            pass

                        try:#must have skills
                            skills_1 = driver.find_elements("xpath",'//*[@id="apply_career"]/div[2]/div[2]/div')
                            skill_list_1 = [] 
                            for i in range(len(skills_1)):
                                my_skills_1 =''
                                my_skills_1 = skills_1[i].get_attribute("innerText")   
                                skill_list_1.append(my_skills_1)          
                            if skill_list_1 is None:
                                print("Not Mentioned")
                        except:
                            skill_list_1 = "Not mentioned"

                        try:#other skills
                            skills_2 = driver.find_elements("xpath",'//*[@id="apply_career"]/div[3]/div[2]/div')
                            skill_list_2 = []
                            for i in range(len(skills_2)):
                                my_skills_2 =''
                                my_skills_2 = skills_2[i].get_attribute("innerText")   
                                skill_list_2.append(my_skills_2) 
                            if skill_list_2 is None:
                                print("Not Mentioned")
                        except:
                            skill_list_2 = "Not mentioned"
                    
                    if x==5:# second pattern web elements
                        try:
                            role = driver.find_element("xpath","//p[@class='coPE getRoleLabel']//span").text
                        except NoSuchElementException:
                            role = "not provided"            
                        try:
                            industry_type=driver.find_element("xpath","//p[@class='coPE getIndustryLabel']//span//span").text
                        except NoSuchElementException:
                            industry_type= "not provided"          
                        try:
                            functional_area=driver.find_element("xpath","//p[@class='coPE getFareaLabel']//span//span").text
                        except NoSuchElementException:
                            functional_area= "not provided" 
                        try:
                            employment_type=driver.find_element("xpath","//p[@class='coPE getEmploymentType']//span").text
                        except NoSuchElementException:
                            employment_type = "not provided"
                        try:
                            role_category=driver.find_element("xpath","//p[@class='coPE getCategoryRoleLabel']//span").text
                        except NoSuchElementException:
                            role_category= "not provided"
                        try:
                            education_ug = driver.find_element("xpath","//p[@class='coPE getUGCourse']//span").text
                        except NoSuchElementException:
                            education_ug = "Not provided"
                        try:
                            education_pg = driver.find_element("xpath","//p[@class='coPE getPGCourse']//span").text
                        except NoSuchElementException:
                            education_pg = "Not provided"
                        try:
                            post = driver.find_element("xpath","//div[@class='sumFoot']//strong").text.split(" ")
                            if post[0].isdigit():
                                posted = int(post[0])
                                post_date = datetime.today() - timedelta(days=float(posted))
                                date_posted = (post_date.strftime('%d-%m-%Y'))
                                posted_on = str(date_posted)
                            else:
                                post_date = datetime.today()
                                date_posted = (post_date.strftime('%d-%m-%Y'))
                                posted_on = str(date_posted)
                        except NoSuchElementException:
                            posted_on = "Not provided"
                        try:
                            job_views = driver.find_element("xpath","//span[@class='jViews']//strong").text
                            openings = "Not available"
                            job_applicants = driver.find_element("xpath","//span[@class='jApplys']//strong").text        
                        except NoSuchElementException:
                            job_views = "Not provided"
                            job_applicants = "not provided"
                            openings = "Not available"
                            
                    
                        try:
                            description_items = driver.find_elements("xpath","//div[@class='clearboth description']")
                            description_dic = dict()
                            key = ""
                            value_total = ""

                            for i in range(len(description_items)):
                                tags = description_items[i].tag_name
                                if tags.startswith("h") or tags.find("strong"):
                                    if key:
                                        description_dic[key] = value_total
                                        key = ""
                                        value_total = ""
                                    key = description_items[i].get_attribute("innerText")
                                if tags.startswith("p"):
                                    value = description_items[i].get_attribute("innerText")
                                    value_total = value_total + value
                                if tags.startswith("ul"):
                                    li_tag_items = description_items[i].find_elements_by_tag_name('li')
                                    for j in range(len(li_tag_items)):
                                        li_tag_item = li_tag_items[j].get_attribute("innerText")
                                        value_total = value_total + li_tag_item

                            description_direc = ''
                            for k, v in description_dic.items():
                                description_direc = description_direc + k + '\n' + v
                            if description_dic is not None:
                                description_direc = driver.find_element("xpath","//div[@class='clearboth description']").text
                        except NoSuchElementException:
                            pass
                    
                        try:#must have skills
                            skills_1 = driver.find_elements("xpath","//div[@class='getJobKeySkillsSection key-skill']//div[text()='Key Skills']//following-sibling::div[1]/*")
                            skill_list_1 = [] 
                            for i in range(len(skills_1)):
                                my_skills_1 =''
                                my_skills_1 = skills_1[i].get_attribute("innerText")   
                                skill_list_1.append(my_skills_1)          
                            if skill_list_1 is None:
                                print("Not Mentioned")
                        except:
                            skill_list_1 = "Not mentioned"

                        try:#other skills
                            skills_2 = driver.find_elements("xpath","//div[@class='getJobKeySkillsSection key-skill']//div[text()='Key Skills']//following-sibling::div[2]/*")
                            skill_list_2 = []
                            for i in range(len(skills_2)):
                                my_skills_2 =''
                                my_skills_2 = skills_2[i].get_attribute("innerText")   
                                skill_list_2.append(my_skills_2) 
                            if skill_list_2 is None:
                                print("Not Mentioned")
                        except:
                            skill_list_2 = "Not mentioned"


                    if  x==4:
                        company_name,rating,job_title,experience,education_ug,education_pg,salary,location,description_direc,role,industry_type,functional_area,employment_type,role_category,skill_list_1,skill_list_2,posted_on,openings,job_views,job_applicants = "nil"



                field_row =[result_Si,company_name,rating,job_title,experience,education_ug,education_pg,salary,location,description_direc,role,industry_type,functional_area,employment_type,role_category,skill_list_1,skill_list_2,posted_on,openings,job_views,job_applicants,company_url]
                
                with open(f'new/Data{page_index}.csv', 'a', encoding="utf-8") as files:
                    csvwriter = csv.writer(files)
                    csvwriter.writerow(field_row)
                    files.close()
                      
     
            driver.close()  
        # lock.release()
    def create_threads():
        threads = []
        for i in range(6):
            t = threading.Thread(target=Naukri.scrap, args=('firefox', range(i*2+1, i*2+3)))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

if __name__ == '__main__':

    Naukri.create_threads()
            