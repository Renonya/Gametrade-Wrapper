# Gametrade-Wrapper
gametrade.jp wrapper for python.


# requirements
```
tls_client
BeautifulSoup
capmonster_python
```
capmonster apikey


# example
```
Gametrade = Gametrade("Capmonster_ApiKey")

create account  
print(Gametrade.create_account("nickname","abcd1234@gmail.com","123456789!"))
print(Gametrade.verify_mail(input("enter verify_url: ")))

login
remember_token = Gametrade.login("abcd1234@gmail.com","123456789!")

favorite and unfavorite
print(Gametrade.favorite(remember_token,"https://gametrade.jp/fortnight/exhibits/1145141919"))
print(Gametrade.unfavorite(remember_token,"https://gametrade.jp/fortnight/exhibits/1145141919"))

sms verify
phone_number = input("enter phone_number(09012345678): ")
print(Gametrade.sms_verify(phone_number, remember_token))
