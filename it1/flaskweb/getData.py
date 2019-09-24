from flaskweb import db
import datetime

def meanRating(services):
    for j in services:
        length = len(j['Rating'])
        if length == 0:
            j['meanRating'] = 0
        else:
            sum1 = sum(j['Rating'])
            meanRating = sum1 / length
            meanRating = round(meanRating, 1)
            j['meanRating'] = meanRating
    services = sorted(services, key=lambda k: -(k.get('meanRating')))
    return services

def getServices(name):
    cursor = db.Services.find({'Type':name})
    services = []
    for i in cursor:
        services.append(i)
    services = meanRating(services)
    return services

def getInfo(name, id_):
    data = getServices(name)
    for i in data:
        if str(i.get('id_')) == id_:
            return i

def updateRating(name, id_, rating):
    alist = db.Services.find_one({'Type': name, 'id_': int(id_)}).get('Rating')
    alist.append(int(rating))
    db.Services.update_one(
        {'Type': name, 'id_': int(id_)},
        {'$set': {
            'Rating': alist
        }}
    )

def updateFavorite(email, service_name, service_id):
    alist = db.user.find_one({'email': email}).get('favorite')
    service_id = str(service_id)
    service = getInfo(service_name, service_id)
    if service not in alist:
        alist.insert(0, service)
        db.user.update_one(
            {'email': email},
            {'$set': {
                'favorite': alist
            }}
        )
        return 'success'
    else:
        return 'fail'

def getFavorite(email):
    alist = db.user.find_one({'email': email}).get('favorite')
    return alist


def pass_today():
    dic = {'0':'Monday', '1':'Tuesday', '2':'Wednesday', '3':'Thursday',
           '4':'Friday', '5':'Saturday', '6':'Sunday'}
    day = datetime.datetime.today().weekday()
    return dic[str(day)]
