from google_images_download import google_images_download
from multiprocessing import Lock, Process, Queue, current_process
import queue
from bs4 import BeautifulSoup as bs
import requests


def get_keywords():
    with open('keyword.txt', 'rt') as keywords:
        query = []
        for keyword in keywords:
            query.append(keyword.rstrip())

        return query


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = bs(requests.get(url).content, "html.parser")
    proxies = []
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies


def run(query, proxy):
    response = google_images_download.googleimagesdownload()
    arguments = {
        "keywords": query,
        "limit": 700,
        "proxy": proxy,
        "print_urls": False
    }
    paths = response.download(arguments)


def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
        except queue.Empty:

            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            print('Keyword : ' + task[0])
            run(task[0], task[1])
            tasks_that_are_done.put(task[0] + ' is done by ' + current_process().name)
    return True


def main():
    query_list = get_keywords()
    proxy_list = get_free_proxies()
    number_of_process = 5
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    for i in range(len(query_list)):
        tasks_to_accomplish.put([query_list[i], proxy_list[i]])

    # creating process
    for w in range(number_of_process):
        p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

    return True


if __name__ == '__main__':
    main()
