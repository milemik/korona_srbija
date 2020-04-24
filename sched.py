import schedule
from time import sleep

def job():
    print('HELLO')


schedule.every(1).minute.do(job)

while True:
    schedule.run_pending()
    sleep(1)
