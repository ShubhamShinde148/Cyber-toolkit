import firebase_admin
from firebase_admin import credentials, firestore

# Firebase service account key
cred = credentials.Certificate("darkweb-monitor-fee1c-firebase-adminsdk-fbsvc-be2b34d535.json")

firebase_admin.initialize_app(cred)

# Firestore database
db = firestore.client()