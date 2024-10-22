
'''
    def send_message_for_account(self , comment):
            icon_profile = comment.find_element(By.CSS_SELECTOR, 'div[class="x1rg5ohu x1n2onr6 x3ajldb x1ja2u2z"]')
            ActionChains(self.driver).move_to_element(icon_profile).perform()
            time.sleep(5)
            self.driver.find_element(By.XPATH , ".//div[@aria-label='Message' and @role='button']").click()
            time.sleep(6)
            message_box = self.driver.find_element(By.CSS_SELECTOR , 'div[class="x5yr21d x1uvtmcs"]')
            text_box = message_box.find_element(By.XPATH , './/div[@role="textbox" and @aria-label="Message" and starts-with(@aria-describedby, "Write to")]')
            text_box.send_keys(Y_message)
            text_box.send_keys(Keys.ENTER)
            time.sleep(3)
            text_box.send_keys(Keys.ESCAPE)
'''