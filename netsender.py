import requests
from shutil import copyfile
from requests.auth import HTTPBasicAuth

import os

config = configparser.ConfigParser()
config.read('iridium.ini')
bin_files=config['FOLDERS']['bin_files']
sent_files=config['FOLDERS']['sent_files']




#at = 'http://192.168.50.232'	


def send_file( file_name ):
	at = config['AT']['ip']
	to = config['AT']['to']
	login = config['AT']['login']
	pass = config['AT']['pass']
	fullname = os.path.join(bin_files, file_name)
        try:	
            f = open(fullname, 'br')
	    raw_data = f.read()
	    f.close()
        except:
            return False
	msg = file_name.encode()
	b_to = to.encode()
	dt = b'&to='+b_to + b'&urgency=0&chSv=1&subj=file&kvs=000&msg=' + msg + b'\x00' + raw_data
        try:	
            r = requests.post(at + '/sendmsg2.xip', data=dt, auth=HTTPBasicAuth('admin', 'nimda'))
        except:
            return False
        print(r)
        return True

def send_file_t(fl):
	print ("file f%s was setn" % fl)
	return True

raw_data = b'ku-ku eto ja'
file_name = "123.txt"
to = "1301"
send_file(at, to, file_name, raw_data)


names = os.listdir(bin_files)
files=[]
for name in names:
	fullname = os.path.join(bin_files, name) # получаем полное имя
	if os.path.isfile(fullname):
		files.append(name)


for f in files:
	if os.path.exists( os.path.join(sent_files, f) ):
		print('already sent')
	else:
		if ( send_file_t(f) ):
			copyfile( os.path.join(bin_files, f), os.path.join(sent_files, f))
