import tls_client
from bs4 import BeautifulSoup
from capmonster_python import RecaptchaV3Task
import re

class Gametrade_exception(Exception):
    pass


class Gametrade():
    def __init__(self,capmonstar_api):
        self.capmonstar_api = capmonstar_api
        self.session = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://gametrade.jp',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }


    def solve_captcha(self,website_url, website_key):
        i = 0
        while True:
            try:
                if i==3:
                    raise Gametrade_exception("captcha_failed")
                i += 1
                capmonster = RecaptchaV3Task(self.capmonstar_api)
                task_id = capmonster.create_task(website_url, website_key)
                result = capmonster.join_task_result(task_id)
                return result.get("gRecaptchaResponse")
            except:
                print("error captcha unsolved try again...")


    def login(self,email,password):
        response = self.session.get("https://gametrade.jp/signin")
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        
        data = {
            'utf8': '✓',
            'authenticity_token': csrf_token,
            'session[email]': email,
            'session[password]': password,
            'g-recaptcha-response': self.solve_captcha("https://gametrade.jp/signin", "6Lckg8cZAAAAAB59DnqTKd5I21URI80QT5HuI5zx")
        }

        response = self.session.post('https://gametrade.jp/signin', headers=self.headers, data=data)
        if response.status_code == 302:
            cookies_dict = self.session.cookies.get_dict()
            remember_token = cookies_dict.get("remember_token")
            return remember_token
        else:
            raise Gametrade_exception("failed")

    def create_account(self,nickname,email,password):
        response = self.session.get("https://gametrade.jp/signup_info")
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        data = {
            'utf8': '✓',
            'authenticity_token': csrf_token,
            'user[nickname]': nickname,
            'user[email]': email,
            'user[password]': password,
            'invited_user[invite_code]': "",
            'g-recaptcha-response': self.solve_captcha("https://gametrade.jp/signup_info", "6Le806QeAAAAAPAPS1HufPdR-c4wvdJcgqif7cFO"),
        }
        response = self.session.post('https://gametrade.jp/users',data=data)
        if response.status_code == 302:
            return "success"
        else:
            raise Gametrade_exception("failed")


    def verify_mail(self,url):
        response = self.session.get(url)
        if response.status_code == 302:
            return "success"
        else:
            raise Gametrade_exception("failed")


    def sms_verify(self,phone_number,remember_token,twofactor=True): #default True
        if not len(remember_token) == 40:
            raise Gametrade_exception("no_remember_token")
        if not len(phone_number) == 11:
            raise Gametrade_exception("phone_number_error")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        
        response = self.session.get("https://gametrade.jp/sms",headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        if twofactor==True:  
            data = {
                'utf8': '✓',
                'authenticity_token': csrf_token,
                'mobile_number': phone_number,
                'mfa_enabled': [
                    '0',
                    '1',
                ],
            }
        elif twofactor==False:
            data = {
                'utf8': '✓',
                'authenticity_token': csrf_token,
                'mobile_number': phone_number,
                'mfa_enabled': '0',
            }
        else:
            return "2fa_not_setted"
        
        response = self.session.post('https://gametrade.jp/sms', data=data)
        
        verify_code = input("enter verify code: ")
        response = self.session.get("https://gametrade.jp/sms/verify")
        data = {
            'utf8': '✓',
            'authenticity_token': csrf_token,
            'token': verify_code,
            'g-recaptcha-response': self.solve_captcha("https://gametrade.jp/sms/verify","6LeOnwsfAAAAAH_V7pm-yJgN6rzXGIzkqex4yEEv")
        }
        response = self.session.post('https://gametrade.jp/sms/verify', headers=self.headers, data=data)
        if response.status_code == 302:
            return "success"
        else:
            raise Gametrade_exception("failed")


    def favorite(self, remember_token, URL):
        if not len(remember_token) == 40:
            raise Gametrade_exception("no_remember_token")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        response = self.session.get(URL)

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']


        input_tag = soup.find('input', {'name': '_method'})
        value = input_tag['value'] if input_tag else None
        if value=="delete":
            return "already_favorited"
        else:
            pass
        
        data = {
            'utf8': '✓',
            'submit': '',
        }

        headers = {
            'accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
            'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://gametrade.jp',
            'priority': 'u=1, i',
            'referer': URL,
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': csrf_token,
            'x-requested-with': 'XMLHttpRequest',
        }

        ID = str(URL).split("/")[5]

        response = self.session.post('https://gametrade.jp/exhibits/' + ID + '/thinkings', headers=headers, data=data)
        if response.status_code == 200:
            return "Success"
        else:
            raise Gametrade_exception("failed")


    def unfavorite(self, remember_token, URL):
        if not len(remember_token) == 40:
            raise Gametrade_exception("no_remember_token")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        response = self.session.get(URL)

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']


        input_tag = soup.find('input', {'name': '_method'})
        value = input_tag['value'] if input_tag else None
        if value=="delete":
            pass
        else:
            return "not_favorited"
        
        data = {
            'utf8': '✓',
            '_method': 'delete',
            'button': '',
        }

        headers = {
            'accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
            'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://gametrade.jp',
            'priority': 'u=1, i',
            'referer': URL,
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-csrf-token': csrf_token,
            'x-requested-with': 'XMLHttpRequest',
        }

        ID = str(URL).split("/")[5]

        response = self.session.post('https://gametrade.jp/exhibits/' + ID + '/thinkings', headers=headers, data=data)
        if response.status_code == 200:
            return "Success"
        else:
            raise Gametrade_exception("failed")
      

    def get_reviews(self,remember_token):
        if not len(remember_token) == 40:
            raise Gametrade_exception("remember_token_except")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")

        response = self.session.get("https://gametrade.jp/mypage", headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        very_good = soup.find("div", class_="very-good-score").text.strip()
        good = soup.find("div", class_="good-score").text.strip()
        bad = soup.find("div", class_="bad-score").text.strip()
        all_ = int(very_good) + int(good) + int(bad)

        return int(all_),int(very_good),int(good),int(bad)


    def get_nickname(self,remember_token):
        if not len(remember_token) == 40:
            raise Gametrade_exception("remember_token_except")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        response = self.session.get("https://gametrade.jp/mypage", headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        nickname = soup.find('p', class_='nickname').text
        return nickname

    def get_balance(self,remember_token):
        if not len(remember_token) == 40:
            raise Gametrade_exception("remember_token_except")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        response = self.session.get("https://gametrade.jp/mypage/sales_history", headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        amount = soup.find('div', class_='amount').text
        amount = int(amount.replace("¥",""))
        return amount

    def get_point(self,remember_token):
        if not len(remember_token) == 40:
            raise Gametrade_exception("remember_token_except")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        response = self.session.get("https://gametrade.jp/mypage/point_history", headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        amount = soup.find('div', class_='amount').text
        amount = int(amount.replace("¥","").replace("P",""))
        return amount

    def get_sms_verify_status(self,remember_token):
        if not len(remember_token) == 40:
            raise Gametrade_exception("remember_token_except")
        self.session.cookies.set("remember_token", remember_token, domain="gametrade.jp")
        response = self.session.get("https://gametrade.jp/sms",headers=self.headers, allow_redirects=False)
        if response.status_code == 302:
            return True
        elif response.status_code == 200:
            return False
        else:
            raise Gametrade_exception("failed")
