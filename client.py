
#importing the required libraries
import socket
import sys
import struct
import os
import time
import re
import fileinput
import sys
import ntpath
import threading
#import string
#clientname=""

class Client():
	clientname=""
#the important functions of the client are encapsulated in the client class
	def run(self,s):#this takes user inputs and based on user input calls the required function .
	#the code is based on the fact that every communication is initated by the client itself and server just responds
	#there are two infinite loop . the one till user logs in and the other after user has logged in 
		while not Client.clientname:
			data=raw_input("please enter 'login' to login , 'newLogin' to signup or 'quit' to quit")
			if data=="quit":
				self.quit(s)

			elif data=="login":
				self.login(s)	
			
			elif data=="newLogin":
				self.newLogin(s)

			elif data=="commit":
				self.commit(s)	
			elif data=="sendFile":
				self.senderFile(s)	
			else:
				s.send(data)
			print "name of client " + Client.clientname	
		while Client.clientname:
			data=raw_input("commit sendFile getFile listContent Download_Open_Repo quit#")
			if data=="quit":
				self.quit(s)	#closes the client
			elif data=="commit":
				self.commit(s)	
			elif data=="sendFile":
				self.senderFile(s)	#to push a file into one's repo
			elif data=="getFile":	
				self.getFile(s)	#to get a file of the desired version from the repository
			elif data=="listContent":
				self.listContent(s)#this function lists all the repo and its content for that particular user
			elif data=="Download_Open_Repo":
				self.Download_Open_Repo(s)	#to fork a particular repo into the current working directory of the client code
			else:
				s.send(data)
				print "wrong input\n"			
					
	def quit(self,s):
		s.send("quit")	#client can exit by typing 'quit'
		s.close()
		sys.exit()

	def listContent(self,s):
		s.send("listContent")	#initiates listContent 
		data=raw_input("enter subrepo- to know the sub-repos present viewContent-view content of a particular folder: ")
		s.send(data) #send the functionality taken above from the client
		check=s.recv(1024)
		print check
		print ('sending the clientname')
		s.send(Client.clientname)	#sending the client name to build the path for the repo
		chk=s.recv(1024)
		print chk
		if(data=='subrepo'):	#user wants to know the sub folders in the main repo
			l="asda"
			while (l != "stop"):				
				l=s.recv(1024)	#receives the names of the subfolders from the server side
				s.send("ack")	#sends an ACK everytime it receives data
				if l != "stop":
					print l #prints the data being received
		elif(data=='viewContent'):	#user wants to know the files and folders in the repo
			data=raw_input('specify the path of repo/sub-repo you want to know the content of: ')
			if (data!=Client.clientname):	#building the proper path for the input taken above
				send_this=Client.clientname+'/'+data
				s.send(send_this)	#Roughly,we are trying to avoid the user from typing one's client name in the
			else:					#path. So we check if the input is same as the client name.If yes,send it directly
				s.send(data)		#if no,append the client name with a '/' and then send to server.
			m="sadasd"
			while m!="stop":
							
				m=s.recv(1024)	#receiving the data from the server side
				#print m
				s.send("ack")	#sending ACK everytime data is received
				if m !="stop":
					print m 	#printing the incoming data
	def login(self,s):	#this function is called when the user types "login"
		s.send("login")#start the login procedure	
		data=s.recv(1024)	
		print data+"\n"
		user_name=raw_input("please enter your user name")
		s.send(user_name)	#asks for the user name
		data=s.recv(1024)
		print data+"\n"
		password=raw_input("password")	#asks for the password
		s.send(password)
		data=s.recv(1024)		#the authentication is done on the server side and the result is sent to the client
		if data=="success":		#which is being received and compared here.Depending on the message received from the server-
			print "succesfully logged in"	#-the authentication of the client is confirmed.
			Client.clientname=user_name	#storing the user name
			print clientname+"\n\n"
			data=False			
		elif data=="unsuccess":
			print "wrong credentials"
			self.login(s)
		else:
			print "error while logging in try again later"		
			self.login(s)	

	def newLogin(self,s):	#this method is called when a new user wants to register 
		s.send("newLogin")	#initiates the process
		data=s.recv(1024)
		print data+'/n'
		user_name=raw_input("please enter your user name")

		s.send(user_name)	#asks for the desired username
		data=s.recv(1024)	#based on the message received from the server, the registration of the new user is confirmed
		print data
		if data=="unique_user":
			password=raw_input("please enter passwprd \n")	#if user name is unique,then it prompts for a password
			s.send(password)
			Client.clientname=user_name	#storing the client name
			print clientname
		elif data=="user_exists":	
			print "user already exists .. please redo the procedure with a new username\n"
		else:
			print "some error occured\n"

	def commit(self,s):	
		print Client.clientname
		path= raw_input("please enter the exact path not including the folder itself\n")
		foldername=raw_input("please enter the exact folder name \n")
		#print clientname
		serverpath=Client.clientname+"/"+foldername
		input=raw_input("would u like to make this repo a open one yes for yes , no for no")
		#this is asked so as to know whether this repo is available for forking or not 
		s.send("UpdateOpenRepo")
		if input=="yes":
			print "its an open repo"
			s.send("yes")
			data=s.recv(1024)
			print data
			s.send(serverpath)
			data=s.recv(1024)
			print data
		elif input=="no":
			print "its not an open repo"
			s.send("no")

			data=s.recv(1024)
			print data 
		else:
			print "its a wrong input"
			s.send("error")
			data=s.recv(1024)
			print data			
		
		self.treeWalk(s,path,foldername,Client.clientname)

	def Download_Open_Repo(self,s):	#this method is called when the user wants to fork a repo
		s.send("Download_Open_Repo")
		fo=open("OpenRepoList.txt","w")
		data=self.recv_one_message(s)
		fo.write(data)
		fo.close()	
		print "a repo has been downloaded in the working directory of the client file"

		cur_Dir=os.getcwd()		#obtaining the current working directory of the client code


		repo_path=raw_input("please enter the repo path ")	#the path of the repo the user wants to fork
		s.send(repo_path)	#sends the path to the server
		data=s.recv(1024)
		print data 
		data=self.recv_one_message(s)
		print data	#this will print tree walk 
		while(data != "stop"):		#this keeps receiving the files until the value in the data equals 'stop'
			print "in while loop"
			data=self.recv_one_message(s)#this will recive folder or file or stop 
			if data=="folder":
				location=self.recv_one_message(s)#this will recive folder name
				self.send_one_message(s,"location received")
				location1=cur_Dir+"/"+location 
				self.CreateFolder_file(location1)	#creates a folder in the specified location
				data=self.recv_one_message(s)
				print data

			if data=="file":	#if the incoming data is a file
				location=self.recv_one_message(s)#this receives the location 
				self.send_one_message(s,"file location and name recived")#this sends the confiramtion of the recv. location
				location1=cur_Dir+"/"+location #builds the path of the file
				fo=open(location1,"a+")	#creates a file in that path if it doesn't exist
				content=self.recv_one_message(s)	#writes the content into the file
				fo.write(content)
				fo.close()
				self.send_one_message(s,"done with writing")

	def senderFile(self,s):	#this method takes in the path of the file on the client system,which is to be pushed and the 
		s.send("sendFile")	#path of the repo where it wants the file to be sent.These are then sent to 'sendfile' method
		client_path=raw_input("please enter client_path including file name: ")
		server_path=raw_input("please enter server path of the file excluding user name and / : ")
		server_path_final=Client.clientname+"/"+server_path#building the path for the file
		self.sendfile(s,client_path,server_path_final)

	def getFile(self,s):	#this method is called when the user wants to get a file from one's repo
		s.send('getFile')
		reqpath=raw_input('Specify the path of the file you want to get,excluding user name and / : ')
		reqpath_final=Client.clientname+"/"+reqpath
		vernum=raw_input('Give the version number you want and latest for the latest version: ')
			#asks for the version number of the file required
		self.getfile(s,reqpath_final,vernum)	#the parameters are then passed to the 'getfile' method
		print('The file will be downloaded in the current working directory of this client code: ')

	def recv_one_message(self,s):	#first receives the length of data and then the data itself
		lengthbuf=self.recvall(s,4)	
		length, =struct.unpack('!I',lengthbuf)
		return self.recvall(s,length)	#calls a helper method to read the content

	def recvall(self,s, count):
		buf = b''
		while count:
			newbuf = s.recv(count)
			if not newbuf: return None
			buf += newbuf
			count -= len(newbuf)
		return buf

	def send_one_message(self,c,data):	#first sends the length of the data to be sent and then sends the data
		length = len(data)
		c.sendall(struct.pack('!I',length))
		c.sendall(data)
#treeWalk is a helper function for commit. This function goes through all the sub-folders and files present in
#a given folder. We have replaced the abs. path of each folder with username/foldername
#for example .. If the folder is home/grep/root/project/CNS
#and if username is abc and he commit  cns then his server path would be 
#abc/CNS		

	def treeWalk(self,s,repo,foldername,username):
		print username
		#abspath=""
		repo_path=repo+'/'+foldername #this gives the path of the required folder 
		for folderName,subfolderList, fileList in os.walk(repo_path):
			print "this is the folder " + folderName + '\n' 
			finalfolderName=folderName.replace(repo,username)
			print finalfolderName
			s.send("NewFolder")	#initiates the newFolder request
			data = s.recv(1024)
			print data
			print (finalfolderName)
			s.send(finalfolderName)
			for fname in fileList:
				print (finalfolderName+'/'+fname)
				server_file_path=finalfolderName+'/'+fname#sends the foldername .. which includes desired location in the server
				client_file_path=folderName+'/'+fname
				s.send("sendFile")
				print "preparing to send "
				time.sleep(1)
				self.sendfile(s,client_file_path,server_file_path)	#calls a method for file transfer

	def sendfile(self,s,client_path,server_path):#client path include filename and serverpath also includes filename
		print client_path 
		print " "+server_path+"\n"
		self.send_one_message(s,server_path)		#sends the server_path to the server
		data=self.recv_one_message(s)		
		print data
		fo=open(client_path,"rb")		#open the flie existing at client path
		data=fo.read()		#reads the content
		self.send_one_message(s,data)	#sends the data being read
		fo.close()	#closes the file
		data=self.recv_one_message(s)
		print data

	def getfile(self,s,reqpath,vernum):
		#reqpath is the server path
		self.send_one_message(s,reqpath)	#sends the path from which the user wants the file
		data=self.recv_one_message(s)		#ack
		print data

		self.send_one_message(s,vernum)		#sends the version number of the file wanted
		data=self.recv_one_message(s)
		print data

		cur_Dir=os.getcwd()		#gets the current working directory
		self.send_one_message(s,cur_Dir)	#sends cur_Dir to the server
		data=self.recv_one_message(s)		
		print data

		data=self.recv_one_message(s)	#based on the message from the server, the client will get to know
		if data=="correct":				#if the path is correct
			self.recvfile(s)			#start the file transfer from the server to client using 'recvfile' method
		elif data=="incorrect":
			print "incorrect path  "	
		else:
			print "some error "	
		
	def recvfile(self,s):	
		print "path"
		path=self.recv_one_message(s)
		print path
		fo=open(path,"a")	#opens the file at the specified path
		self.send_one_message(s,"path received")	
		data=self.recv_one_message(s)
		fo.write(data)	#writes the data into the file
		fo.close()
		self.send_one_message(s,"done with file transfer")

	def CreateFolder_file(self,location):	#this method creates a new folder in the path given to it
		if not os.path.isdir(location):		#first,it checks if the folder is present at the given path or not
			os.makedirs(location)			#if no, then it creates one at the given path



class ClientThread(threading.Thread):
	def __init__(self):
		self.s= socket.socket()		#create a socket
		self.host=socket.gethostname()	
		self.counter=0
		threading.Thread.__init__(self)
		
	def run(self):
		while self.counter==0:
			#host=str(raw_input("please enter the ip of the server"))
			host='10.100.96.121'
			port=int(raw_input("please enter the port number of the server"))
			try:
				self.s.connect((host, port))
				self.counter=1
			except:
				print "error while connecting "
		data = self.s.recv(1024)		#This recceives from client "I have given you a new thread"
		self.s.send("Hi i am client")	#this will be simply printed on server terminal
		client=Client()	#make an object of the client class
		
		client.run(self.s)



if __name__=='__main__':		#program starts executing from here
	print "Hi I am client"
	#thread.start_new_thread (ClientThread)
	clientname=""	#initialise the clientname
	client_thread=ClientThread()
	client_thread.start()
	print "the thread has been started vooh"


