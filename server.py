#importing libraries 
#Its a multi threaded server in which whenever a client connects to the server it is given a new thread . hence each thread is assigned a #socket id. The communication is always initiated by the client and is appropriatley ack. and serverd by the server 
import socket
import threading
import os
import struct
import ntpath
import re
import fileinput
import sys


host="0.0.0.0"
port = 12367

class ClientThread(threading.Thread):
	def __init__(self,(conn,addr),counter,sock):#this is client thread constructor. This initializes few variables and thread itself 
		self.conn=conn
		self.addr=addr
		self.counter=counter
		self.sock=sock
		threading.Thread.__init__(self)

	def run(self):
		self.conn.send("I have given you a new thread")
		while True:
			data =  self.conn.recv(1024)#this is where server recv. data from the client and responds appropriatley 

			if data:
				print "Its data from thread "+str(self.counter)+" "+data
				if data=="login":#to initiate login 
					print "In login"
					self.login()
				elif data=="quit":#for quit 
					self.quit()	
				elif data=="newLogin":#for new user
					self.newLogin()	
				elif data=="NewFolder":#to create a new folder 
					#call a function called CreateFolder_file with desired location 
					self.NewFolder()
				elif data=="sendFile":#it recv. file and stores it at appropriate location
					print "in send file checker"
					self.recverfile()
				elif data=="getFile":#it gives file to the server which might be latest or some previous version
					print "getFile starting..."
					self.giveFile()	
				elif data=="UpdateOpenRepo":#it is used to update the text file of open repo whenever a commit takes place
					print "in update open repo"
					self.UpdateOpenRepo()	
				elif data=="listContent":#for listing the content of the folder or the given repo
					print "listContent"
					self.listContent()	
				elif data=="Download_Open_Repo":#for forkin
					print "in Download_Open_Repo"
					self.Download_Open_Repo()	
	def listContent(self):
#IT FIRST builds the exact location or path 
#Depending on the input given,this method gives the client the list of folders present in the main repo or the list of files and folders in
#a given folder path
#the logic to send data is .. send data .. and at client side there is a while loop which keeps on recv. and checking . When we are done with 
#data transfer send a "stop" which will exit the loop
		print('in listContent')
		cur=os.getcwd()#prints the current working directory 
		print cur	#working
		inp=self.conn.recv(1024)	
		print inp	#working
		self.conn.send('got the input')
		name=self.conn.recv(1024)
		self.conn.send('got the name')
		key=cur+'/'+name
		print key	#working
		if(inp=='subrepo'):#this prints all the repo of the client 
			print "in subrepo"		
			if os.path.exists(key):
				print ('path exists in server home directory')
				l=os.walk(key).next()[1]#this is a list of all the folder 
				print ('list obtained')
				if(len(l)!=0):
					for k in l:#take one folder from the list .. send it and wait for ack.
						print k
						k=k+" "
						self.conn.send(k)#sends the name 
						data=self.conn.recv(1024)#recv. the ack
					print ('list sent')
					self.conn.send("stop")#indicating end of list
				else:
					self.conn.send('no folders in the main repository')
					self.conn.send("stop")
		elif(inp=='viewContent'):#this list the content of the  folder 
			rec=self.conn.recv(1024)
			print rec
			key1=cur+'/'+rec#builds the required path 
			print key1
			if os.path.exists(key1):
				m=os.listdir(key1)#a list of the content in the folder 
				print ('list obtained')
				length=str(len(m))
				if(len(m)!=0):
					for i in m:#take each element and send it and at end send an "stop" bit 
						print i
						i=i+" "
						self.conn.send(i)
						ack=self.conn.recv(1024)
						print ack
						
					print ('list sent')
					self.conn.send("stop")					
				else:			
					self.conn.send('no content in this folder')
					self.conn.send("stop")
	def login(self):# a login system .In which first client sends "Login" after which username and password is recv. If the password.
#the string is concat. with a space and serched through the LoginLookUp.txt and then the client is replied accordingly 
		print("Give me your login name")
		self.conn.send("user_name")#code for asking user name is 10
		name=self.conn.recv(1024)
		print("Give me your password")
		self.conn.send("password")#code for asking user name is 11
		password=self.conn.recv(1024)
		util=utility()
		lookup_return=util.lookup(name,password)#a helper function which goes through the name+" "+password and returns  accordingly
		if lookup_return:
			self.conn.send("success")#sends success for correct login 
		else:
			print "incorrect combination"#sends unsuccess for incorrect login 
			self.conn.send("unsuccess")


	def newLogin(self):#a new user login system. A file called user is present. Whenever a request for new login comes the username is 
#searched through the file to check uniqueness and if it is unique .. append the name and return accordingly
#it also makes a new folder for the user which will be the main repo of the client  
		self.conn.send("Give me your login name")
		name=self.conn.recv(1024)
		util=utility()
		name_return=util.nameLookup(name)
		if name_return:
			fo = open("UserName.txt", "a+")
			temp=name+"\n"#a new line is added so that the next user comes in .It goes at the end 
			fo.write(temp)#append the unique user name 
			fo.close()
			self.conn.send("unique_user")#send an ack 
			print "please enter password ()" 
			password=self.conn.recv(1024)
			fo = open("LoginLookUp.txt", "a+")#apeend the name + " " +password in loginLookUp.txt 
			temp=name+" "+password+'\n'
			fo.write(temp)
			fo.close()
			print "A new user has been created and u have been logged in "
			util=utility()
			util.CreateFolder_file(name)


		else:
			print "user_exists"
			self.conn.send("user_exists")

			#self.newLogin()

	def quit(self):#a function which which prints whenever the socket is closed 
		print "client"+str(self.counter)+" quits"
		#self.conn.close()	

	def UpdateOpenRepo(self):#this function updates the OpenRepo file whenever a open source repo is formed 
		print "in the function "
		data=self.conn.recv(1024)
		print data	
		self.conn.send("input received ")
		if data=="yes":
			serverpath=self.conn.recv(1024)
			self.conn.send("received path")#the path is recv. here 
			fo=open("OpenRepo.txt","a+")
			serverpath=serverpath+'\n'
			fo.write(serverpath)
			fo.close

	def Download_Open_Repo(self):#whenever a user asks for a open repo . First a file is sent to the user which is downloaded 
#in the current orking directory of the client.The client selects a particular folder to be forked. 
#the path is then recived by the server and then with that path this calls tree walk
		fo=open("OpenRepo.txt","a+")
		data=fo.read()
		util=utility()
		util.send_one_message(self.conn,data)
		serverpath=self.conn.recv(1024)
		print "the server path is "+serverpath
		self.conn.send("path receive")
		self.TreeWalk(serverpath)
		#now i have to create a new tree walk .. thats it 

	def TreeWalk(self,serverpath):#this function sends name and the files assocaited with a folder and the content of each subfolder
		util=utility()

		util.send_one_message(self.conn,"treewalk")#telling client that a tree walk has to be intitated 
		for folderName,subfolderList, fileList in os.walk(serverpath):
			print "this is the folder " + folderName + '\n'#this prints the folder name 
			util.send_one_message(self.conn,"folder")
			util.send_one_message(self.conn,folderName)#this folder name is recv. by the client and there it calls a new foder to #create the given path 
			data=util.recv_one_message(self.conn)#this will recive confirmation ie location received s
			print data#now fname will print all the files .. but we just need log.txt and then read each and very line
			#send the name and 
			for fname in fileList:
				server_file_path=folderName+'/'+fname
				print server_file_path
				util.send_one_message(self.conn,"file")
				util.send_one_message(self.conn,server_file_path)
				confirm=util.recv_one_message(self.conn)#this will recv the confiramtion 
				print confirm
				fo=open(server_file_path,"r")
				contenet=fo.read()
				util.send_one_message(self.conn,contenet)#send the contenet
				fo.close()
				confirm=util.recv_one_message(self.conn)
				print confirm

		util.send_one_message(self.conn,"stop")		


	def NewFolder(self):
		self.conn.send("preparing to receive path .. pls send the path ")
		data=self.conn.recv(1024)	#receives the path in which the folder needs to be built
		print "client sent this " + data +'\n'
		util=utility()
		util.CreateFolder_file(data)	#calls the helper method to create a folder in the given path
#this is working 
	def recverfile(self):
		util=utility()
		util.recvfile(self.conn)	
	
	def giveFile(self):
		util=utility()
		util.getfile(self.conn)

class utility():

	def lookup(self,name,password):	#this method checks the username and password is the right combination or not
		lookupString=name+" "+password	#combines both the parameters 

		fo = open("LoginLookUp.txt", "r+")	#here, LoginookUp.txt stores the username and password combination separated
		fo_line=open("LoginLookUp.txt", "r+")	#by a space
		while(fo.read()):
			for line in fo_line:	#compares every line in the file 'LoginLookUp.txt' with the lookupString
				line=line[:-1]	#if found,it means that the credentials are right
				if(line==lookupString):
					fo.close()
					fo_line.close()
					return "found"
			fo.close()
			fo_line.close()
			return False	#else, it returns false

	def nameLookup(self,name):	#this method is called when the newLogin is called, 
		lookupString=name	#it opens the file 'UserName.txt' which has a list of all the user names 
		fo = open("UserName.txt", "r+")
		fo_line=open("UserName.txt", "r+")
		while(fo.read()):	#this method compares the lookupString with every user name in the file 
			for line in fo_line:	#to check if the user name which the user is requesting is unique or not
				line=line[:-1]	#if unique,it returns 'unique name'
				if(line==lookupString):
					fo.close()
					fo_line.close()
					return 
		fo.close()
		fo_line.close()
		return "unique name"

	def CreateFolder_file(self,location):	#creates a folder in the given location if it does not exist
		if not os.path.isdir(location):
			os.mkdir(location)
			log_Location=location+'/'+'log.txt'
			fo_log=open(log_Location,"a+")	#creates a file 'log.txt' in every folder it creates 
	
#this is working
	def send_one_message(self,c,data):	#sends the length of the message and then the data
		length = len(data)
		c.sendall(struct.pack('!I',length))
		c.sendall(data)		
#this is working	
	def recvall(self,s, count):	#reads the content of the data being sent
		buf = b''
		while count:
			newbuf = s.recv(count)
			if not newbuf: return None
			buf += newbuf
			count -= len(newbuf)
		return buf	
#this is working
	def recv_one_message(self,s):			#one needs to send self.conn here
		lengthbuf=self.recvall(s, 4)
		length, =struct.unpack('!I', lengthbuf)	#receives the length of the content and then the content
		return self.recvall(s,length)	

	def sendfile(self,s,client_path,server_path,filename):#client path include filename and serverpath also includes filename
		print client_path
		print " "+server_path+"\n"

		self.send_one_message(s,client_path)	#gets the path from the client side where the file should be sent
		data=self.recv_one_message(s)
		print data
		fo=open(server_path,"rb")	#opens the file in the server_path and reads it in the binary format
		data=fo.read()
		self.send_one_message(s,data)	#sends the data which is being read
		fo.close()			#closes the file once it is done
		data=self.recv_one_message(s)
		print data
#this is working
	def recvfile(self,s): 
		print "path"
		path=self.recv_one_message(s)
		print path
		version_num=self.setversion_Num(s,path)	#calls a method to set the version number of the incoming file
		print "the returned version number is " + str(version_num)
		print "sending to modified path "

		modpath=self.savefileAs(s,path,version_num)#version is integer here 
		#building the path for the file to be sent
		print "the modified path is " + modpath +'\n'
		print path


		fo=open(modpath,"a")	#opens a file at the specified path
		self.send_one_message(s,"path received")
		data=self.recv_one_message(s)	#writes the data into it and then closes the file
		fo.write(data)
		fo.close()
		head,tail=ntpath.split(path)	#head=path excluding filename and tail=filename+extension
		pathforLog=head+'/'+'log.txt'	#path for the log.txt file for that particular folder
										#so this updates the log file 
		print "the pathforlog is " + pathforLog
		print "the path to be recorded in the file is " + path
		print "the version number is" + str(version_num)  
		self.updatelogFile(s,pathforLog,path,version_num)
		self.send_one_message(s,"done with file transfer")


	
	def updatelogFile(self,s,pathforLog,path,version_num): #this is used to update log file
#whenever a new file is sent to the server. This will update the log file . The log file stores the latest version of the file . If a new file #comes the latest version has to be replaced. this function does the replacing part. If there is no enetry this function also updates the log #file  with the latest entry. it is stored in the form of path+'-_-_-'+str(version_num)+'\n'   
		print "in log file\n"
		
		enterinLog=path+'-_-_-'+str(version_num)+'\n'
		print "the log to be entered is " + enterinLog
		temp_counter = 0 					
		file=pathforLog
		print "the file variable is " + pathforLog
		for line in fileinput.input(file, inplace=1):
			#line=line[:-1]
			#print line
			Path,ver_Num=re.split('-_-_-',line)	#FYI : we are using -_-_- as the delimiter
			if(Path==path):
				line = line.replace(line,enterinLog)
				temp_counter=temp_counter+1
			sys.stdout.write(line)

		print temp_counter	
		if temp_counter==0:
			print "in temp_counter "
			f1=open(pathforLog,'a+')	
			f1.write(enterinLog)
			f1.close()	#if it's the first entry then make a entry in log.txt
		
		#f.close()

		return 'changes made in the log file'			

	
	def getfile(self,s):#this is used to get an apprpriate version of the file.	
		reqpath=self.recv_one_message(s)
		self.send_one_message(s,"Got the required path")
		#reqpath is the server path 

		nameOfFile=os.path.basename(reqpath)

		vernum=self.recv_one_message(s)
		self.send_one_message(s,"Got the version number")
		print "the vernum is " + vernum

		if vernum=="latest":
			print "in latest and the vernum is " + vernum
			vernum=self.return_vernum(s,reqpath)
			print "the latest vernum is " + vernum + "\n" 


		pathtoSend=self.searcher_setter(s,reqpath,vernum)
		base=os.path.basename(reqpath)


		#print "the path to send is " + pathtoSend
		req_dir=self.recv_one_message(s)
		self.send_one_message(s,"Got the path to send ")


		clientpath=req_dir+'/'+nameOfFile#we need to append it with name of file or ask client to append it with name of client
		print "the clientpath is " + clientpath
		#print "the server path is " + pathtoSend

		if pathtoSend:
			self.send_one_message(s,"correct")
			self.sendfile(s,clientpath,pathtoSend,base)
		else :
			self.send_one_message(s,"incorrect")
				

	def searcher_setter(self,s,server_path,version_num):#this is used to set the path of the file 
		properpath=self.savefileAs(s,server_path,version_num) 
		print "the properpath is " + properpath

		if os.path.exists(properpath):
			print "in if condition "
			return properpath
		return	

	def return_vernum(self,s,server_path):#this returns the latest version of the file or the asked or required version
		version="0"
		print "in return_latest"
		head,tail=ntpath.split(server_path)
		pathforLog=head+'/'+'log.txt'
		f0=open(pathforLog,'a+')
		f1=open(pathforLog,'a+')
		while(f0.read()):
			for line in f1:
				line=line[:-1]
				Path,ver_Num=re.split('-_-_-',line)
				print "the path is " + Path
				print "the version is in return_vernum " + ver_Num 
				if(Path==server_path):
					version=ver_Num#here version is string
					print "in file checker if loop " + version+'\n'


		f0.close()
		f1.close()
		return str(version)			





	def searchforFile(self,s,reqpath,vernum):	#not tested yet; searches for the required version of the file in corresponding log.txt
		print "in search for file "
		head,tail=ntpath.split(reqpath)	#head=path excluding filename and tail=filename+extension
		pathforLog=head+'/'+'log.txt'	#path for the log.txt file for that particular folder
		stringto_Search=reqpath+"-_-_-"+str(vernum)#pran/time1.py-_-_-2
		f0=open(pathforLog,'a+')
		f1=open(pathforLog,'a+')		
		while(f0.read()):
			for line in f1:
				line=line[:-1]
				if(line==stringto_Search):
					sendback_Path=self.getfileAs(s,stringto_Search,vernum)	#preparing the path to be sent to server to get the 
			#f0.close()							#latest version of the file
			#f1.close()
		f0.close()
		f1.close()
		return sendback_Path

	
	def getfileAs(self,s,reqpath,vernum):
		fileName,fileExt=os.path.splitext(reqpath)	#gets the path and extension separately
		head,tail=ntpath.split(reqpath)	#head=path excluding filename and tail=filename+extension
		pathforLog=head+'/'+'log.txt'	#path for the log.txt file for that particular folder
		f=open(pathforLog,'a+')		#opens the file
		f1=open(pathforLog,'a+')
		while(f.read()):		#reading the file
			for line in f1:		#for every line in the file
				#line=line[:-1]	#exclude the \n
				Path,ver_Num=re.split('-_-_-',line)	#split the line using double space as delimiter
				print "the path is " + Path		
				print "the ver_Num is p" + ver_Num+"p"	
				if(Path==path):	#checking 
					sendthis_Path=fileName+"-_-_-"+str(vernum)+fileExt	#prepare the path to be sent
			f.close()
			f1.close()
		f.close()
		f1.close()
		return sendthis_path

						
	def savefileAs(self,s,path,vernum):	#does the appending the filename stuff- this works smoooth
		print "In saveFileAs\n"
		base=os.path.basename(path)
		num=self.setversion_Num(s,path)
		print base	#gives the filename along with extension

		fileName,fileExt=os.path.splitext(path)
		print fileName	#gives the total path without extension
		print fileExt	#gives the extension only
		properpath=fileName+"-_-_-"+str(vernum)+fileExt
		print "from savefileAs" + properpath +'\n'

		return properpath	
	
	def setversion_Num(self,s,path):	#this is probably working ... Not so sure.. but it assigns the first version properly
		new_versionNum=1				#this method decides the version number to be maintained for the given file
		head,tail=ntpath.split(path)	#head=path excluding filename and tail=filename+extension
		pathforLog=head+'/'+'log.txt'	#path for the log.txt file for that particular folder
		f=open(pathforLog,'r')
		f1=open(pathforLog,'r')
		while(f.read()):
			for line in f1:
				line=line[:-1]
				print "the line is " + line
				Path,ver_Num=re.split('-_-_-',line)
				print "the path is " + Path
				print "the ver_Num is p" + ver_Num+"p"

				if(Path==path):	#checking for the previous latest version
					new_versionNum=int(ver_Num)+1
		
		f.close()
		f1.close()
		return new_versionNum
class Server():
	counter= 0
	def __init__(self):
		self.sock= socket.socket()
		self.sock.bind((host,port))
		print "U have been initialized"



	def run(self):
		self.sock.listen(5)#it listens to the new incoming connection 
		#Server.counter=Server.counter+1
		print Server.counter
		print "you can enter here"
		while True:
			Server.counter=Server.counter+1
			client=ClientThread(self.sock.accept(),Server.counter,self.sock)#it calls client class constructor which intiilizes a #new thread
			client.daemon=True#this is set true if the thread is running in infinite loop
			client.start()#This will call the run function in class ClientThread

	def stop(self):
		self.sock.close()
	 		

#the code starts from here after importing libraries 
if __name__=='__main__':
	print "file transfer server is about to start\n"
	print "A new or existing lookUP table"
	fo=open("LoginLookUp.txt","a+")#a text file which stores information for login like username password 
#whenever server runs its either created and if it exists then it just opens and close 
	fo.close()
	fo=open("UserName.txt","a+")#a text file to store username . Same logic as above 
	fo.close()
	fo=open("OpenRepo.txt","a+")#a text file which stores all the open repo. used at the time of forking 
	fo.close()
	temp_sock=socket.socket()
	temp_sock.connect(("8.8.8.8",80))
	print "the ip of the server is " + temp_sock.getsockname()[0]
	temp_sock.close()
	print "the port of the server is " + str(port)	
	s=Server()#calls the server class which binds the socket . Simply  a constructor 
	s.run()#calls the run method 
	print "hello people I am the server talking"
