from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt5.QtCore import QThread , pyqtSignal
import time
import pickle
import os

class BotWorker(QThread): 
    isfinished = pyqtSignal()  # Signal to indicate the bot finished
    error_signal = pyqtSignal(str)  # Signal to pass error messagespip
    status_signal = pyqtSignal(str)

    def __init__(self,email,password,posts,comments,message,timer , times):
        super().__init__()
        self.driver = None
        self.email=email
        self.password=password
        self.posts=posts
        self.comments=comments
        self.message=message
        self.timer=timer
        self.times=times
        self._is_running=True

    def run(self):
        try:
            if self._is_running:
                self.status_signal.emit("Bot Starting...")
                self.start_Browser()
                self.login(self.email , self.password)
            if self._is_running:
                self.switching()
                self.replying(self.posts , self.comments , self.message)
        except Exception as e:
            return self.error_signal.emit(str(e))
        finally:
            self.status_signal.emit("The finally point")
            if self._is_running:
                for _ in range(self.times):
                    if not self._is_running:
                        break
                    time.sleep(self.timer)
                    self.status_signal.emit("The replying again")
                    self.replying(self.posts , self.comments , self.message)
            self.isfinished.emit()
            if self.driver:
                self.driver.quit()
                self.status_signal.emit("Browser closed, bot finished.")


    def start_Browser(self):
        options = Options()
        options.add_argument("--disable-notifications")
        #options.add_argument("--headless")  # Run in headless mode
        #options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        #options.add_argument('--disable-extensions')  # Disable extensions for faster load
        #options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(options=options)
        self.status_signal.emit('The browser has been opened ...')


    def stop(self):
        self._is_running = False
        if self.driver:
            self.driver.quit()
            self.status_signal.emit("Browser closed, bot finished.")


    # Save cookies to a file
    def save_cookies(self):
        COOKIES_FILE = "cookies.pkl"
        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)
        self.status_signal.emit("Cookies saved ...")

    # Load cookies from a file
    def load_cookies(self):
        COOKIES_FILE = "cookies.pkl"
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.status_signal.emit("Cookies loaded ...")
            self.driver.refresh()

    def login(self, email, password):
        try:
            self.driver.get('https://www.facebook.com/login')
            time.sleep(5)
            COOKIES_FILE = "cookies.pkl"

            # Load cookies if they exist
            if os.path.exists(COOKIES_FILE):
                self.load_cookies()
                time.sleep(5)
                # Check if we are already logged in after loading cookies
                if "facebook.com/login" not in self.driver.current_url:
                    self.status_signal.emit("Logged in using cookies.")
                    return

            # Enter login credentials
            username_box = self.driver.find_element(By.ID, 'email')
            username_box.send_keys(email)
            password_box = self.driver.find_element(By.ID, 'pass')
            password_box.send_keys(password)
            password_box.send_keys(Keys.RETURN)

            if "checkpoint" in self.driver.current_url:
                time.sleep(60)

            # Check if login was successful by verifying the URL or a specific logged-in element
            if "facebook.com/login" not in self.driver.current_url:  # Ensure we're not on the login page
                self.save_cookies()  # Save cookies after confirming login
                self.status_signal.emit("Successfully logged in and cookies saved.")
            else:
                self.status_signal.emit("Login failed: Incorrect credentials or other issues.")
            time.sleep(10)  # Wait for the page to load after login

        except Exception as e:
            return self.error_signal.emit(f"Login failed: {str(e)}")
            
            


    def scrolling(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5) 
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                    break
            last_height = new_height
        self.All_Comments()


    def All_Comments(self):
        try:
            allcommetns = self.driver.find_element(By.CSS_SELECTOR , 'div[class="html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x78zum5 x13a6bvl"]')
            time.sleep(5)
            allcommetns.find_element(By.XPATH , ".//div[@role='button']").click()
            time.sleep(5)
            self.scrolling()
        except:
            return


    def has_replies(self,comments):
        counter = 0
        unanswered_comments = []
        for comment in comments:
            try:
                comment.find_element(By.XPATH, "./div[2]/div")
                continue
            except:
                counter += 1
                unanswered_comments.append(comment)
        self.status_signal.emit(f'There are {counter} unreplyed comments.')
        return unanswered_comments
    


    def replying(self ,posts, comments , message):
        try:
            for post,Y_comment,Y_message in zip(posts , comments , message):
                self.driver.get(post)
                time.sleep(5)
                self.scrolling()
                time.sleep(5)
                comments = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="x169t7cy x19f6ikt"]')
                self.status_signal.emit(f"Found {len(comments)} comments ...")
                unanswered_comments = self.has_replies(comments)
                counter = 0
                for comment in unanswered_comments:
                    try:
                        self.reply_for_comment(comment , Y_comment),
                        time.sleep(2)
                        self.send_message_for_comment(comment,Y_message)
                        counter +=1
                    except Exception as e:
                        self.status_signal.emit(f"Error : not replyed on this comment")
                        continue
                self.status_signal.emit(f"{counter} comments were successfully replyed.")
        except Exception as e:
            return self.status_signal.emit(f'Error : {(str(e))}')
            
    def reply_for_comment(self , comment , reply):
        #replying comment
        ActionChains(self.driver).move_to_element(comment).perform()
        time.sleep(2)
        reply_button = comment.find_element(By.XPATH, ".//div[@role='button' and contains(text(), 'Reply')]")
        reply_button.click()
        time.sleep(2)
        comment_box = comment.find_element(By.XPATH, ".//div[@role='textbox']")
        comment_box.send_keys(reply)
        comment_box.send_keys(Keys.RETURN)
        time.sleep(5)
    
    def send_message_for_comment(self,comment,message):
        #sending message
        ActionChains(self.driver).move_to_element(comment).perform()
        comment.find_element(By.XPATH, './/div[@role="button" and contains(text(), "Send message")]').click()
        time.sleep(7)
        self.driver.find_element(By.XPATH , './/div[@role="textbox" and starts-with(@aria-placeholder, "Send a message as")]').send_keys(message)
        time.sleep(5)
        self.driver.find_element(By.XPATH , '//div[@role="button" and @aria-label="Send message"]').click()
        time.sleep(5)

    def switching(self):
        profile = self.driver.find_element(By.CSS_SELECTOR, 'div[class="x78zum5 x1n2onr6"]')
        profile.find_element(By.XPATH, ".//div[@role='button' and @aria-label='Your profile']").click()
        time.sleep(3)
        switch = self.driver.find_element(By.CSS_SELECTOR, 'div[class="x1ok221b"]')
        switch.find_element(By.XPATH, ".//div//div//span[1]//div").click()
        time.sleep(7)
