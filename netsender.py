import requests
import sys
import configparser
from requests.auth import HTTPBasicAuth
import os
import time
import shutil
from datetime import datetime


settings_file='netsender.ini'
if (os.path.isfile('netsender.ini')) != True:
	print("\n\tERROR! Settings file %s not exists." % (settings_file))
	sys.exit(1)

config = configparser.ConfigParser()
config.read('netsender.ini')
bin_files = config['FOLDERS']['bin_files']
sent_files = config['FOLDERS']['sent_files']
bin_files = os.path.join(os.getcwd(), bin_files)
sent_files = os.path.join(os.getcwd(), sent_files)

if ( os.path.exists(bin_files)==False):
	print("DIR %s not exists" % bin_files)
	sys.exit(1)

if ( not os.path.exists( sent_files ) ):
	try:	
		print("Creating quitance folder: %s" % sent_files)
		os.mkdir(sent_files)
	except:
		print("Cant create quitance folder: %s" % sent_files)
		sys.exit(1)

def loger(ln):
	l = open('log.txt', 'aw')
	date_line=datetime.strftime(datetime.now() ,"%d_%H-%M-%S")
	l.writeln(date_line + ' > ' +ln)
	l.close()

def send_file( file_name ):
	at=config['AT']['at']
	to=config['AT']['to']
        channel=int(config['AT']['channel'])	
        login=config['AT']['login']
	password=config['AT']['password']
	fullname = os.path.join(bin_files, file_name)
	print('send_file> fullname %s' % fullname)	
	try:	
		f = open(fullname, 'br')
		raw_data = f.read()
		print(raw_data)
		f.close()
		msg = file_name.encode()
		b_to = to.encode()
                b_ch= channel.encode()
		dt = b'&to='+b_to + b'&urgency=0&chSv='+b_ch +'&subj=file&kvs=000&msg=' + msg + b'\x00' + raw_data
		print(dt)
			
		try:	
			at=at+'sendmsg2.xip'
			print('AT: %s' % at)
			
			r = requests.post(at, data=dt, auth=HTTPBasicAuth(login, password) )
			#print("login: %s  pass: %s" % (login, password))
			print(r)
			print(r.status_code)
			if (r.status_code == 200):
				print('CODE 200')
				return True
			else:
				print('CODE %s ' %r.status_code)		
				return False
		except requests.exceptions.RequestException as e:
			print (e)
			return False
		return True;
		#except:
		print('sending request failure')
		#return False
	except:
		print('open error')
		return False
	return True



while True:
	names = os.listdir(bin_files)
	files=[]
	for name in names:
		fullname = os.path.join(bin_files, name) # получаем полное имя
		if os.path.isfile(fullname):
			files.append(name)
	for f in files:
		if os.path.exists( os.path.join(sent_files, f) ):
			print("file %s already sent" % f)
		else:
			print("try to send %s " % f)
			if ( send_file(f) ):
				print("sent %s success" % f)
				try:	
					shutil.move( os.path.join(bin_files, f), os.path.join(sent_files, f))
				except:
					sys.exit(1)	
			else:
				print('sent file ' + f +  ' failed')
	time.sleep(5)
