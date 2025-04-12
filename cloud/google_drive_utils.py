import os
import pickle
import mimetypes
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import GoogleAuthError
import logging
logging.basicConfig(level=logging.DEBUG)


SCOPES = ['https://www.googleapis.com/auth/drive']


def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            with open('token.pickle', 'wb') as f:
                pickle.dump(creds, f)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("OAuth Error", f"Google OAuth thất bại!\n\nChi tiết lỗi:\n{str(e)}")
            os._exit(1)  # dừng toàn bộ ứng dụng nếu lỗi xác thực

    return build('drive', 'v3', credentials=creds)


def upload_to_drive(filepath, folder_name):
    service = get_service()
    folder_id = get_or_create_folder(service, folder_name)
    media = MediaFileUpload(filepath, mimetype=mimetypes.guess_type(filepath)[0])
    metadata = {'name': os.path.basename(filepath), 'parents': [folder_id]}
    service.files().create(body=metadata, media_body=media).execute()
    print(f"📤 Uploaded {filepath} to {folder_name} successfully!")

def upload_log_to_drive(reason, timestamp, folder_name="FaceMonitorLogs"):
    log_data = {
        "type": reason,
        "timestamp": timestamp
    }
    os.makedirs("temp", exist_ok=True)
    path = f"temp/log_{timestamp}.json"
    with open(path, 'w') as f:
        json.dump(log_data, f)
    upload_to_drive(path, folder_name)
    print(f"📤 Uploaded log {path} to {folder_name} successfully!")

def get_or_create_folder(service, name):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    folders = service.files().list(q=q).execute().get('files')
    if folders: return folders[0]['id']
    return service.files().create(body={'name': name, 'mimeType': 'application/vnd.google-apps.folder'}).execute()['id']
