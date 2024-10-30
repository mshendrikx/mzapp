
import mzcommon as mzc
import mzdeclaration as mzd
from datetime import datetime, timedelta

conn, cursor = mzc.db_connect()

time_now = mzc.time_now('')

date_from = time_now - timedelta(days=21)

day_from = int(date_from.strftime("%Y%m%d") + '0000')

day_to = int(time_now.strftime("%Y%m%d") + '0000')

sql = 'SELECT deadline FROM transfers WHERE deadline > %s AND deadline < %s;'
values = (day_from, day_to, )
cursor.execute(sql, values)

counter = {}
reorder_array = []

for transfer in cursor.fetchall():
    date_obj = datetime.strptime(str(transfer[0]), "%Y%m%d%H%M")
    weekday = date_obj.strftime("%A")
    ident =  weekday + ' ' + str(date_obj.hour)
    if ident in counter:
        counter[ident] += 1
    else:
        counter[ident] = 1

for item in counter:
    reorder_array.append([item, counter[item]])

reorder_array.sort(key=lambda x: (x[1]), reverse=True)

breakpoint
