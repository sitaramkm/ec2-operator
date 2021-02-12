import datetime
import croniter
import sys


# return true if the cron schedule falls between now and now+seconds
def time_to_action(ec2_schedule, time_now, seconds):
    try:
        cron = croniter.croniter(ec2_schedule, time_now)
        d1 = time_now + datetime.timedelta(0, seconds)
        if seconds > 0:
            d2 = cron.get_next(datetime.datetime)
            ret = (time_now < d2 < d1)
        else:
            d2 = cron.get_prev(datetime.datetime)
            ret = (d1 < d2 < time_now)
        print("now %s" % time_now)
        print("d1 %s" % d1)
        print("d2 %s" % d2)
    except:
        ret = False
    print("time_to_action %s" % ret)
    return ret


now = datetime.datetime.now()
print('Script exec time is ' + now.strftime("%m-%d-%Y, %H:%M:%S") + ' and python version used is ' + sys.version + '!')
s1 = "0 0 * * SAT"
s2 = "10 9 * * WED"
s3 = "44 21 * * FRI"
#print(time_to_action(s1, now, 31 * 60))
#print(time_to_action(s2, now, 31 * 60))
print(time_to_action(s2, now, 31 * 60))
# datetime(year, month, day, hour, minute, second, microsecond)

print(now)
# print(time_to_action(s3, now2, 31 * 60))
d = datetime.date(2021, 1, 22)

print(time_to_action(s3, d, 31 * 60))
