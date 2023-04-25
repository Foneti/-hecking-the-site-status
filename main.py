from discord_webhook import DiscordWebhook
import requests
from time import sleep

URL = 'discord-webhook-url-here'
MST_URL = 'https://mst.foneti.ru/'
DID_URL = 'https://did.foneti.ru/'
ALLOK, ALLDOWN, MSTDOWN, DIDDOWN = range(4)
STATUS = ALLOK

def sendWebhook(text: str) -> requests.Response:
    '''Отправляет вебхук'''
    webhook = DiscordWebhook(url=URL, content=text)
    response = webhook.execute()
    return response


def checkStatus(url: str) -> int:
    '''Делает запрос к сайту и возвращает код статуса'''
    r = requests.get(url)
    return r.status_code


def checkStatusCode(code: int, service: str):
    '''Проверяет код статуса сервиса и отправляет webhook'''
    global STATUS
    didTextDown = f'<:offline:1015539695301697537>Нет ответа от **Detective Investigation Database**.\nКод ошибки: **{code}**.'
    mstTextDown = f'<:offline:1015539695301697537>Нет ответа от **METRO/SOD Terminal**.\nКод ошибки: **{code}**.'
    didTextOk = f'<:online:1015539696840998935>Получен ответ от **Detective Investigation Database**.'
    mstTextOk = f'<:online:1015539696840998935>Получен ответ от **METRO/SOD Terminal**.'
    #Проверяем код статуса. Если он не равен 200, то:
    if code != 200:
        #Если все сервисы были в порядке:
        if STATUS == ALLOK:
            #Отправляет вебхук упавшего сервиса и меняем статус сервисов на упавший
            sendWebhook(didTextDown if service == 'did' else mstTextDown)
            STATUS = DIDDOWN if service == 'did' else  MSTDOWN
            return
        #Если ранее упал DID и мы проверяем MST:
        if STATUS == DIDDOWN and service == 'mst':
            #Отправляет вебхук и меняем статус сервисов на всё упало
            sendWebhook(mstTextDown)
            STATUS = ALLDOWN
            return
        #Если ранее упал MST и мы проверяем DID:
        if STATUS == MSTDOWN and service == 'did':
            #Отправляет вебхук и меняем статус сервисов на всё упало
            sendWebhook(didTextDown)
            STATUS = ALLDOWN
            return
    #Если код статуса равен 200:
    else:
        #Если ранее упал DID и мы проверяем DID: отправляем DID окей
        if STATUS == DIDDOWN and service == 'did':
            STATUS = ALLOK
            sendWebhook(didTextOk)
            return
        #Если ранее упал MST и мы проверяем MST: отправляем MST окей
        if STATUS == MSTDOWN and service == 'mst':
            STATUS = ALLOK
            sendWebhook(mstTextOk)
            return
        if STATUS == ALLDOWN:
            #Отправляет вебхук упавшего сервиса и меняем статус сервисов на упавший
            sendWebhook(didTextOk if service == 'did' else mstTextOk)
            STATUS = MSTDOWN if service == 'did' else  DIDDOWN
            return


def main():
    while True:
        checkStatusCode(checkStatus(MST_URL), 'mst')
        checkStatusCode(checkStatus(DID_URL), 'did')
        sleep(120)

if __name__ == "__main__":
    main()