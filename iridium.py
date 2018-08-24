import serial
import sys
from datetime import datetime

com_port ='COM3'
bin_folder='C:/IRIDIUM/'
#устанавливаем com порт
ser = serial.Serial(port = 'COM3', baudrate = 19200, timeout = 30)
print(ser.name)

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

def checksum(bf):
	sum_size = 2
	data = bf[0:len(bf)-sum_size]
	cs_byte=bf[-2:]
	calc_cs = sum(data)
	#print(len(buff))
	#print(data)
	#print(len(data))
	#print("CALC_CS %s" % hex(calc_cs))
	cs_int = int(cs_byte[0]) * 256 + int( cs_byte[1] )
	#print(hex(calc_cs))
	#print(hex(cs_int))
	if calc_cs == cs_int:
		return True
	else:
		return False  


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
			#print("SBDD2")
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
			print(buff)
			#выделяем символы между BDWB= и символом \r это размер данных
			len_s = buff.find(b'BDWB=')
			len_e = buff.find(b'\r')
			#print( "START LENGTH: %s" % str(len_s+5) )
			#print( "END LENGTH: %s" % str(len_e) )
			# тут всегда будет верно, а len_s нам нужно для вырезания длины сообщения, надо бы переписать
			if len_s != -1:
				#сколько символов занимает длина пакета
                                #len_s +5  -- позиция после знака равно в команде BDWB 
				#
				length_data = len_e - len_s - 5
				#print( "DATA LENGTH%s" % str(length_data) )
				length_read=buff[len_s+5:len_e]
				#print(length_read)
				#длина сообщения есть параметр команды BDWB и еще 2 байта
				msg_len = int(length_read)  + 2
				print ("--> READY\n")
				ser.write(b'READY\r')
				#читаем сколько нужно байт и еще два для CRC
				raw = ser.read( msg_len)
				print("length raw %s" % len(raw))
				s=''
				z=0
				for b in raw:
					s = s + str(z) + ':' + str(hex(b)) + ' '
					z = z + 1 
				print(s)
				#сохраняем в файл
				ff=datetime.strftime(datetime.now() ,"%Y-%m-%d_%H-%M-%S")
				filename = bin_folder+ff+'.bin';

				f=open(filename, 'bw')
				f.write( raw )
				f.close();
				if checksum(raw):
					print("CHECKSUM CORRECT")
					ser.write(b'0\rOK\r')
				else:
					print("CHECKSUM INCORRECT")
					ser.write(b'2\rOK\r')
		#обнуляем глобальную переменную буфер		
		buff = b''               