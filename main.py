from google_images_download import google_images_download
from multiprocessing import Process, Queue, current_process
import queue
from googletrans import Translator


def get_keywords():
    with open('keyword.txt', 'rt') as keywords:
        query = []
        for keyword in keywords:
            query.append(keyword.rstrip())

        return query


def get_languages():
    with open('languages.txt', 'rt') as languages:
        languages_array = []
        for language in languages:
            languages_array.append(language.rstrip())
        return languages_array


def run(keyword):
    translator = Translator()
    languages = get_languages()
    response = google_images_download.googleimagesdownload()
    for language in languages:
        query = translator.translate(keyword, src='en', dest=language).text

        arguments = {"keywords": query, "limit": 700, "print_urls": False, 'image_directory': keyword,
                     'size': 'large', 'prefix': 'large -', 'no_numbering': True}
        response.download(arguments)

        arguments['size'] = 'medium'
        arguments['prefix'] = 'medium -'
        response.download(arguments)


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
            print('Keyword >>>>>>>>>>>>>>>>>>>>>>>>>>>>> : ' + task)
            run(task)
            tasks_that_are_done.put(task + ' is done by ' + current_process().name)
    return True


def main():
    query_list = get_keywords()
    number_of_process = 2
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    for i in range(len(query_list)):
        tasks_to_accomplish.put(query_list[i])

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
