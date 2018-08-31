import serial
import sys
import configparser
import os
import getopt
opts,args = getopt.getopt(sys.argv[1:], "f:",["config_file="])
config_file='iridium.ini'
for o, a in opts:
	if o in ( "-f", "--config_file"):
		print("Using users config file %s" % config_file)
		config_file=a	
from datetime import datetime


if ( os.path.isfile(config_file) != True):
	print("Config file %s not exists." % config_file)
	sys.exit(1)


config = configparser.ConfigParser()

config.read(config_file)

com_port = config['SERIAL']['com_port']
com_baudrate = 19200
com_timeout = 300
if config.has_option('SERIAL', 'baudrate'):
	com_baudrate = int(config['SERIAL']['baudrate'])

if config.has_option('SERIAL', 'timeout'):
	com_timeout  = int(config['SERIAL']['timeout'])

bin_files = config['STORAGE']['bin_files']
write_checksum = config['DATA']['write_checksum']

if (write_checksum == 'ON'):
	write_checksum=1
else:
	write_checksum=0


id=config['AFTOGRAPH']['id']
print("Listening:\t%s port " % com_port )
print("Com speed:\t%s baud " % com_baudrate )
print("Com timeout:\t%s msec " % com_timeout )
if (write_checksum):
	print("Cheksum:\tON")
else:
	print("Checksum:\tOFF")
exit

bin_files = os.path.join(os.getcwd(), bin_files)
if (os.path.exists(bin_files)==False):
	print("Binary file storage %s not exists " % bin_files)
	try:
		print("Binary file storage created %s " % bin_files)
		os.mkdir(bin_files)
	except:
		print("Cant create binary storage %s" % bin_files)
		sys.exit(1)
print("Binary file storage %s " % bin_files)

#устанавливаем com порт
ser = serial.Serial(port = com_port, baudrate = com_baudrate, timeout = com_timeout)

#буффер где аккумулируются считываемые данные из ком порта
buff = b''
buff_size = 0

#константы для обнаружения команд
CSQ_C = 1
SBDWB_C = 2
ATE0_C = 3
AT_C = 4
SBDD2_C = 5
SBDD0_C = 6
SBDIX_C = 7
SBDSX_C = 8

def log():
	f = open('iridium.log', 'w>')
	
def checksum(bf):
	return True
	sum_size = 2
	data = bf[0:len(bf)-sum_size]
	cs_byte=bf[-2:]
	calc_cs = sum(data)
	cs_int = int(cs_byte[0]) * 256 + int( cs_byte[1] )
	if calc_cs == cs_int:
		return True
	else:
		return False  

def buff_to_file(raw_buf, write_checksum, id):
	#сохраняем в файл
	dt=datetime.strftime(datetime.now(), "%y%m%d-%H%M%S")
	#ff=datetime.strftime(datetime.now() ,"%Y%m%d-%H-%M-%S")
	f = str(id)+'-'+dt+'.bin'
	filename = os.path.join(bin_files,f) ;
	f=open(filename, 'bw')
	if (write_checksum == 0):	
		f.write( raw_buf[0:len(raw_buf)-2] )
	else:
		f.write(raw_buf)	
	f.close();
def write_ok():
	ser.write(b'OK\r')
def show_buff(raw):
	s=''
	z=0
	for b in raw:
		s = s + str(z) + ':' + str(hex(b)) + ' '
		z = z + 1 
	print(s)
	
#ищем в символьном буфере сигнатуру команды
def cmd_type():
	AT = buff.find(b'AT\r')
	CSQ = buff.find(b'AT+CSQ')
	SBDWB = buff.find(b'AT+SBDWB=')
	ATE0 = buff.find(b'ATE0')
	SBDD2 = buff.find(b'SBDD2')
	SBDD0 = buff.find(b'SBDD0')
	SBDIX = buff.find(b'SBDIX')
	SBDSX = buff.find(b'SBDSX')
	if CSQ != -1:
		return CSQ_C
	if SBDWB != -1:
		return SBDWB_C
	if ATE0 != -1:
		return ATE0_C
	if SBDD2 != -1:
		return SBDD2_C
	if SBDD0 != -1:
		return SBDD0_C
	if SBDIX != -1:
		return SBDIX_C
	if SBDSX != -1:
		return SBDSX_C
	if AT != -1:
		return AT_C
while True:
	#считали один байт
	s = ser.read(1)
	buff = buff + s
	#нет ли у нас спецсимвола в буфере который говорит о приеме команды?
	k = buff.find(b'\r')
	#если спецсимвол обнаружен, выделяем команду
	if k!=-1:
		print('<-- %s' % buff)
		cmd = cmd_type()
		
		if cmd == CSQ_C:
			print("-->  +CSQ:5\r")
			ser.write(b'+CSQ:5\r')
			
		if cmd == AT_C:
			print("--> OK\n")
			ser.write(b'OK\r')
		if cmd == SBDD2_C:
			print("--> OK\n")
			ser.write(b'0\rOK\r')
		if cmd == SBDD0_C:
			print("--> OK")
			ser.write(b'0\rOK\r')    		
		if cmd == SBDIX_C:
			print("--> +SBDIX: 0, 495, 0, 0, 0, 0 OK")
			ser.write(b'+SBDIX: 0, 495, 0, 0, 0, 0\rOK\r')
		if cmd == SBDSX_C:
			print("--> +SBDSX: 0, 495, 0, 0, 0, 0 OK")
			ser.write(b'+SBDSX: 0, 495, 0, 0, 0, 0\rOK\r')
		if cmd == SBDWB_C:
			#print(buff)
			#выделяем символы между BDWB= и символом \r это размер данных
			
			cmd_length = len('BDWB=')
			position_s = buff.find(b'BDWB=')
			position_e = buff.find(b'\r')
			length_data = position_e - position_s - cmd_length
			#print( "DATA LENGTH%s" % str(length_data) )
			length_read=buff[position_s + cmd_length : position_e]
			#длина сообщения есть параметр команды BDWB и еще 2 байта
			CRC_LEN = 2
			msg_len = int(length_read)  + CRC_LEN
			print ("--> READY\n")
			ser.write(b'READY\r')
			#читаем сколько нужно байт и еще два для CRC
			raw = ser.read( msg_len)
			#print("length raw %s" % len(raw))
			buff_to_file(raw, 0, id)
			show_buff(raw)
			if checksum(raw):
				print("CHECKSUM CORRECT")
				ser.write(b'0\r')
				write_ok()
			else:
				print("CHECKSUM INCORRECT")
				ser.write(b'2\r')
				write_ok()
		#обнуляем глобальную переменную буфер		
		buff = b''               
