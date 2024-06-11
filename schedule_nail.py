import gspread
from datetime import datetime
import datetime as dt


gc = gspread.service_account(filename='nailbot-425314-c528aa53e119.json')
sh = gc.open("Расписание")
worksheet = sh.get_worksheet(0)


def get_info():
    date = worksheet.col_values(1)
    worksheet.get_all_records()
    index_start = get_index_day_start(date)

    true_data = list(worksheet.get_all_records()[index_start:])
    list_with_time = []

    for i in true_data:
        list_with_time.append(list(i.values()))

    list_with_time = get_days_and_times(list_with_time)
    return list_with_time


def get_index_day_start(days):
    now_time = dt.datetime.now()
    num_day = 0

    for day in days[1:]:
        if day == ("Время/место"):
            continue
        tek_time = datetime.strptime(day, "%d.%m.%Y")
        if (tek_time > now_time) or (tek_time == now_time):
            break
        num_day += 2
    return num_day


def get_days_and_times(list_with_time):
    list_time = list_with_time
    ready_times_list = []
    for times in range(1, len(list_time), 2):
        index = 0
        for time in list_time[times]:

            if (time != "") and (time != "Время/место"):
                list_time[times-1].pop(index)
                index -= 1
            index += 1
        ready_times_list.append(list_time[times-1])
    return ready_times_list


def get_dates():
    date = worksheet.col_values(1)
    worksheet.get_all_records()
    index_start = get_index_day_start(date)
    true_data = list(worksheet.get_all_records()[index_start:])
    list_with_time = []
    index = 0
    for i in true_data:
        if index % 2 == 0:
            list_with_time.append(list(i.values())[0])
        index += 1
    return list_with_time


def create_recording(day, time_service, text):
    try:
        cell = worksheet.find(day)
        row = cell.row
        worksheet.row_values(row)
        for time in range(0, len(worksheet.row_values(row))):
            if time_service == worksheet.row_values(row)[time]:
                worksheet.update_cell(row+1, time+1, text)
    except:
        return False
    return True
