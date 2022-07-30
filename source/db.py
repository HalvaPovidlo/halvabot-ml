import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('halvabot-firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


def get_song_titles():
    docs = db.collection(u'songs').stream()
    titles = []
    for doc in docs:
        titles.append(doc.to_dict()['title'])
    return titles
