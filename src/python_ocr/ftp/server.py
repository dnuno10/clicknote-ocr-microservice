import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from ..core.config import settings

def run_ftp_server():
    ftp_directory = os.path.join(os.getcwd(), settings.UPLOAD_DIR)
    os.makedirs(ftp_directory, exist_ok=True)
    
    print(f"FTP server will store files in: {ftp_directory}")
    
    authorizer = DummyAuthorizer()
    authorizer.add_user(
        settings.FTP_USER, 
        settings.FTP_PASS, 
        ftp_directory, 
        perm="elradfmw"
    )
    
    handler = FTPHandler
    handler.authorizer = authorizer
    
    server = FTPServer((settings.FTP_HOST, settings.FTP_PORT), handler)
    print(f"FTP Server running on ftp://{settings.FTP_HOST}:{settings.FTP_PORT}")
    print(f" -> user='{settings.FTP_USER}' pass='{settings.FTP_PASS}'")
    server.serve_forever()

def start_ftp_in_background():
    thread = threading.Thread(target=run_ftp_server, daemon=True)
    thread.start()
    return thread