from objc_util import *
from ctypes import c_void_p
import ui
import sound
import sys,socket,clipboard,threading,io
from PIL import Image
import time

found_codes = set()
main_view = None

AVCaptureSession = ObjCClass('AVCaptureSession')
AVCaptureDevice = ObjCClass('AVCaptureDevice')
AVCaptureDeviceInput = ObjCClass('AVCaptureDeviceInput')
AVCaptureMetadataOutput = ObjCClass('AVCaptureMetadataOutput')
AVCaptureVideoPreviewLayer = ObjCClass('AVCaptureVideoPreviewLayer')
dispatch_get_current_queue = c.dispatch_get_current_queue
dispatch_get_current_queue.restype = c_void_p

def captureOutput_didOutputMetadataObjects_fromConnection_(_self, _cmd, _output, _metadata_objects, _conn):
	objects = ObjCInstance(_metadata_objects)
	for obj in objects:
		s = str(obj.stringValue())
		if s not in found_codes:
			found_codes.add(s)
			sound.play_effect('digital:PowerUp7')
		main_view['label'].text = 'Last scan: ' + s
	#	time.sleep(0.3)
		main_view.close()

MetadataDelegate = create_objc_class('MetadataDelegate', methods=[captureOutput_didOutputMetadataObjects_fromConnection_], protocols=['AVCaptureMetadataOutputObjectsDelegate'])

@on_main_thread
def scan():
	global main_view
	delegate = MetadataDelegate.new()
	main_view = ui.View(frame=(0, 0, 400, 400))
	main_view.name = 'Barcode Scanner'
	session = AVCaptureSession.alloc().init()
	device = AVCaptureDevice.defaultDeviceWithMediaType_('vide')
	_input = AVCaptureDeviceInput.deviceInputWithDevice_error_(device, None)
	if _input:
		session.addInput_(_input)
	else:
		print('Failed to create input')
		return
	output = AVCaptureMetadataOutput.alloc().init()
	queue = ObjCInstance(dispatch_get_current_queue())
	output.setMetadataObjectsDelegate_queue_(delegate, queue)
	session.addOutput_(output)
	output.setMetadataObjectTypes_(output.availableMetadataObjectTypes())
	prev_layer = AVCaptureVideoPreviewLayer.layerWithSession_(session)
	prev_layer.frame = ObjCInstance(main_view).bounds()
	prev_layer.setVideoGravity_('AVLayerVideoGravityResizeAspectFill')
	ObjCInstance(main_view).layer().addSublayer_(prev_layer)
	label = ui.Label(frame=(0, 0, 400, 30), flex='W', name='label')
	label.background_color = (0, 0, 0, 0.5)
	label.text_color = 'white'
	label.text = 'Nothing scanned yet'
	label.alignment = ui.ALIGN_CENTER
	main_view.add_subview(label)
	session.startRunning()
	main_view.present('sheet')
	main_view.wait_modal()
	session.stopRunning()
	delegate.release()
	session.release()
	output.release()
	if found_codes:
		#print('All scanned codes:\n' + '\n'.join(found_codes))
		return str('\n'.join(found_codes))
	return ''
def recieve(s):
	while 1:
		data = s.recv(1024)
		if(len(data.decode())==0):
			break
	#print('OVER')
def getimg(s):
	img=clipboard.get_image(idx=0)
	img_bytes=io.BytesIO()
	widge,height=img.size
	img.save(img_bytes,format='PNG')
	img_bytes='0'.encode()+str(widge).encode()+'|'.encode()+str(height).encode()+'&'.encode()+img_bytes.getvalue()
#	img.show()
	i=0
	if(len(img_bytes)>1024):
			while 1:
				end=900+i
				if(end>len(img_bytes)):
					s.sendall(img_bytes[i:])
					break
				s.sendall(img_bytes[i:end])
				i=end	
	else:
		s.send(img_bytes)
#	print(1)
def gettext(s):
		 	#print('this is text')
	 	text='1'.encode()+clipboard.get().encode()
	 	i=0
	 	end=0
	 	if(len(text)>1024):
	 		while 1:
	 			end=800+i
	 			for ii in range(200):
	 				if(end+ii<len(text) and text[end+ii]=='\n'):
	 					end+=ii
	 					break
	 			if(end>len(text)):
	 				s.sendall(text[i:])
	 				break
	 			s.sendall(text[i:end])
	 			i=end
	 	else:
	 		s.send(text)
if __name__ == '__main__':
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	tmp=scan().split()
	s.connect((tmp[0],int(tmp[1])))
	p=threading.Thread(target=recieve, args=(s,))
	p.start()
	try:
		getimg(s)
	except Exception as err:
		#print(err)
		gettext(s)
	s.shutdown(socket.SHUT_WR)
	p.join()
	s.close()
	
