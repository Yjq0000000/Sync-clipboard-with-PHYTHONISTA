import qrcode,io,socket,clipboard
from PIL import Image
tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tmp.connect(('127.0.0.2',80))
ip=tmp.getsockname()[0]
#print(host)
port=100
while 1:
     port=port+1
     try:
	      s.bind(('',port))
     except Exception as err:
	      continue 
     break
#print(port)
img_qr = qrcode.make(ip+' '+str(port))
img_qr.show()
tmp.close()
s.listen(10)         #开始TCP监听
clipboard.set('')
conn,addr=s.accept()   #接受TCP连接，并返回新的套接字与IP地址
#print('Get',addr)   #输出客户端的IP地址
data_all=('').encode()
while 1:
       data=conn.recv(102400)  
       if(len(data)!=0):
       	     #print('0')
             conn.sendall('0'.encode())  
             data_all+=data
             # print(data.decode())
       else:
             #print('OVER') 
             conn.sendall(''.encode())  
             break
if data_all[0:1]=='0'.encode():
	wh=0
	hi=0
	for i in range(15):
		if(data_all[i:i+1]=='|'.encode()):
			wh=i
		if(data_all[i:i+1]=='&'.encode()):
			hi=i
	widge=int(data_all[0:wh].decode())
	height=int(data_all[wh+1:hi].decode())
	img_get=Image.new('RGBA',(widge,height))
	img_get=Image.open(io.BytesIO(data_all[hi+1:]))
	img_get.show()
	clipboard.set_image(img_get)
else:
	print(data_all[1:].decode())
	clipboard.set(data_all[1:].decode())
conn.close()     

