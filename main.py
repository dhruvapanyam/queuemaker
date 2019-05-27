from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
from bs4 import BeautifulSoup
from threading import Thread
import urllib.request
from tkinter import simpledialog
from tkinter import messagebox
import queue as Q
from tkinter import *
from tkinter.ttk import *
import time

#relief,focus_highlightcolor,cursor

def color_rgb(r,g,b):
    """r,g,b are intensities of red, green, and blue in range(256)
    Returns color specifier string for the resulting color"""
    return "#%02x%02x%02x" % (r,g,b)

#------------------------------------------------------------#-------------------------------GLOBALS-----------------------------------#------------------------------------------------------------            

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)     #For text like emojis, etc.

domain = "https://www.youtube.com"

driver_url = 'chromedriver_1.exe'

queue=[]
titles=[]
vidStatus = ''              # STRING TO SHOW STATUS ('Currently playing... ')

videoPlayerStatus = 0       # Whether driver has been launched or not

#------------------------------------------------------------#-----------------------------TKINTER STUFF-------------------------------#------------------------------------------------------------            

root = Tk()
#.option_add("*Font", "Courier")    #set default font

#style = Style()
#style.configure('TButton', font=('calibri',15,'bold','underline'),foreground='black',highlightcolor='black')
#style.map('TButton', highlightcolor = [('pressed','black')],
#                    foreground = [('active','!disabled', 'black')],
#                    background = [('active', color_rgb(145,152,163))],
#                    relief = [('pressed','sunken'),('active','raised')]) 

# --------------------------  Top Frame ---------------------------

topFrame = Frame(root)
topFrame.pack()
e = Entry(topFrame)
e.pack(side=LEFT)
e.focus_set()

var = IntVar()
button = Button(topFrame, text="Search YT", style='W.TButton',command=lambda: var.set(1))
button.pack(side=LEFT)

e2 = Entry(topFrame)
e2.pack(side=LEFT)

var2 = IntVar()
button2 = Button(topFrame, text="Add to Queue", command=lambda: var2.set(1))
button2.pack(side=LEFT)

label = Label(topFrame,text='')
label.pack(side=LEFT,fill=X)

varLoad = IntVar()
loadButton = Button(topFrame,text="Load Queue",command=lambda: varLoad.set(1))
loadButton.pack(side=LEFT)

varSave = IntVar()
saveButton = Button(topFrame,text="Save Queue",command=lambda: varSave.set(1))
saveButton.pack(side=LEFT)

varStart = IntVar()
startButton = Button(topFrame,text="Start Queue",command=lambda: varStart.set(1))
startButton.pack(side=LEFT)

# --------------------------  Bottom Frame ---------------------------
bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM , fill=X)

LABEL = Label(bottomFrame, text="<Queue>")
LABEL.pack()

varExit = IntVar()
exitBut = Button(bottomFrame,text='EXIT',command=lambda: varExit.set(1))
exitBut.pack(side=BOTTOM)

varStop = IntVar()
stopBut = Button(bottomFrame,text='Stop',command=lambda: varStop.set(1))
stopBut.pack(side=LEFT)

STATUS = Label(bottomFrame,text='<Video player is off.>')
STATUS.pack(side=LEFT)

varNext = IntVar()
nextButton = Button(bottomFrame,text='Next',command=lambda: varNext.set(1))
nextButton.pack(side=LEFT)

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            

                                                             #------------------FUNCTION DEFININTIONS---------------------#

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            


def queueEmpty():
    if len(queue)==0:
        messagebox.showinfo('Alert','No videos in queue')
        return 1 #empty
    return 0

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            

def loadQueue():

    loadPath = simpledialog.askstring('Input','Enter queue name',parent=root)
    try:
        f = open(loadPath+'.txt','r')
    except FileNotFoundError:
        print('file not found!')
        return 0
    lines = f.readlines()

    queue.clear()
    titles.clear()

    for i in range(len(lines)):
        if i%2==0:
            queue.append(lines[i][0:len(lines[i])-1])       #removing the \n from lines[i]
        else:
            titles.append(lines[i][0:len(lines[i])-1])       #removing the \n from lines[i]

    f.close()
    showQueue()

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            
    

def saveQueue():
    saveQ = simpledialog.askstring("Input", "Enter the name of the queue",parent=root)
    print(saveQ)

    f = open(saveQ+'.txt','w')

    for x in range(len(queue)):
        f.write(queue[x]+'\n')
        f.write(titles[x]+'\n')
    f.close()

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            

def showResults(s):
    root.update()
    label.config(text=s,justify='left')
    root.update()

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            

def showQueue(x=titles):

    root.update()
    s=''
    for q in x:
        s+=q+'\n'
    LABEL.config(text="Current Queue: \n"+s)

    root.update()

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------

def getResults(search):
    
    rootString=''

    if search==None:
        
        srch = input("YouTube search/link: ")
        if srch == "\\":
            return 0

    else:
        srch = search

    #print()
    #print()
    

    query=''
    for c in srch:
        if c==' ':
            query+='+'
        else:
            query+=c

    url = "https://www.youtube.com/results?search_query="+query         #getting the query url

    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    htmltxt = mystr
    soup = BeautifulSoup(htmltxt,'lxml')    #parsing the html

    tags = soup.find_all('a')           #finding all <a href=...> tags

    vids = {}
    channels={}

    for t in tags:
        att = t.attrs
        if 'watch' in att['href']:
            if 'radio' not in att['href']:  #no playlists
                vids[att['href']]=t.text
        if 'user' in att['href']: # or 'channel' in att['href']:
            channels[att['href']]=t

    #print('-----------------------------------------')
    rootString+='-----------------------------------------\n'
    #print('TOP VIDEO RESULTS:')
    rootString+='TOP VIDEO RESULTS:\n'
    #print('-----------------------------------------')
    rootString+='-----------------------------------------\n'
    

    watch = []
    user = []
    counter=1

    for v in vids:
     #   print(str(counter)+'.',vids[v].translate(non_bmp_map))
        rootString+=str(counter)+'. '+vids[v].translate(non_bmp_map)+'\n'
        #print()
        watch.append(v)
        counter+=1

    numVids = counter-1

    #print()
    rootString+='\n'
    
    #print('-----------------------------------------')    
    rootString+='-----------------------------------------\n'
    #print("Best Channel results:")
    rootString+="Best Channel results:\n"
    #print('-----------------------------------------')
    rootString+='-----------------------------------------\n'
            

    res=0
    for c in channels:
        if 1==1:                            #srch.lower() in str(channels[c]).lower():  I might as well show all the channels I find

            res=1
     #       print(str(counter)+'.',channels[c].text,end=' ')
            rootString+=str(counter)+'. '+channels[c].text+' '
            user.append(c)
            counter+=1

            if channels[c].find('span'):
                if channels[c].find('span').attrs['title']=='Verified':
      #              print('(Verified)')
                    rootString+='(Verified)\n'
       #     print()
            rootString+='\n'
    
    if res==0:
        #print('No channel found')
        rootString+='No channel found\n'
    
    #print('_____________________________________________')
    rootString+='_____________________________________________\n'

    return (rootString,vids,watch)
    
#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            
   

def addToQueue(vids,watch, queueStatus='hide', browse=None):
    status='browse'

    if status=='browse':
        #print('BROWSE: ',browse)
        #input()
        if browse==None:
            browse = input('\nEnter numbers to add videos to the queue: ')
        if browse=='\\':
            return 1
        
        for temp in browse.split(' '):
            if temp!='':
                index = int(temp)
                if index>len(watch):
     #               print('Cannot add channel to "watch queue"')
                    rootString+='Cannot add channel to "watch queue"\n'
            
                else:
                    queue.append(domain+watch[index-1])
                    titles.append(vids[watch[index-1]])

        if queueStatus == 'show':
            showQueue(titles)
    #return rootString

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            

def playVideo(x,driver,nextQueue):

    watchURL = queue[x]
    driver.get(watchURL)
    player_status=1
    

    while player_status:
        
        player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")

        if nextQueue.empty()==0:
            temp = nextQueue.get()
            player_status = 0

        if videoPlayerStatus == 0:

            player_status = 0
            

        time.sleep(1)               # Checking every second whether the video is over
    
    if player_status==0:
        print("VIDEO OVER (status)=",player_status)

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------            

def signIn(loginDetails):

    driver = webdriver.Chrome(driver_url)

    driver.get("https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den-GB%26next%3D%252F&hl=en-GB")

    userD = driver.find_element_by_id('identifierId')
    userD.send_keys(loginDetails['username'])
    
    driver.find_element_by_id('identifierNext').send_keys(Keys.ENTER)

    originalPwd = driver.current_url

    while True:
        
        time.sleep(1)
        
        passD = driver.find_element_by_name('password')
        passD.send_keys(loginDetails['password'])
        
        driver.find_element_by_id('passwordNext').send_keys(Keys.ENTER)

        newD = driver.current_url
        time.sleep(7)
        
        if newD!=domain+'/':         # Check if we're still on the password page
            
            print('password element found')
            print('ERROR! Wrong password...')
            print("Password: ")
            pwd = simpledialog.askstring('Input','Wrong password! Enter password again',parent=root)
            loginDetails['password']=pwd
            
        else:
            break
    return driver

#------------------------------------------------------------#------------------------------------------------------------#------------------------------------------------------------                
            
def startQueue(login,driver,vidQueue,nextQueue):
    global videoPlayerStatus
    
    if not login:
        driver = webdriver.Chrome(driver_url)

    videoPlayerStatus = 1
    x=0
    while x<len(queue) and videoPlayerStatus:
        global vidStatus
        vidStatus = ''
        #print('player_status: ',player_status)
        vidStatus+='Currently playing... ' + titles[x]+'\n'
        #print("\nCurrently playing... ",titles[x])
        if x+1 != len(queue):
            vidStatus+='Next up...            '+titles[x+1]+'\n'
            #print("Next up...           ",titles[x+1])

        #print()

        vidQueue.put(1)

        #STATUS.config(text=vidStatus)
        playVideo(x,driver,nextQueue)
        #time.sleep(5)
        x+=1

    #driver.get(domain)
    driver.quit()

    videoPlayerStatus = 0

#------------------------------------------------------------#------------------------------------MAIN FUNCTION----------------------------------------#-----------------------------            

def main():

    global videoPlayerStatus
    
    vidQueue = Q.Queue()
    nextQueue = Q.Queue()
    Driver = Q.Queue()
    vids={}
    watch=[]
    while True:

        if var.get():
            query=e.get()
            res = getResults(query)
            display = res[0]
            showResults(display)                        # Display results on GUI

            vids = res[1]
            watch = res[2]

            var.set(0)
            
        if var2.get():
            browse=e2.get()
            addToQueue(vids,watch,'hide',browse)   # Add 'browse' links to queue
            showQueue(titles)
            var2.set(0)

        if varLoad.get():

            #queue=[]            # Resetting queue (will add a 'Do you want to save your current queue first?')
            #titles=[]            
            loadQueue()
            varLoad.set(0)
            
        if varSave.get():
            if not queueEmpty():
                saveQueue()
            varSave.set(0)

        if varStart.get():
            if videoPlayerStatus:
                messagebox('Alert','Video player is already running')
            else:
                if not queueEmpty():
                    print('Starting queue...')
                    login = False       #messagebox.askyesno("Input", "Would you like to login to YouTube?",parent=root)                NEED TO FIX LOGIN

                    loginDetails={}
                    if login:
                         loginDetails['username'] = simpledialog.askstring("Input", "Enter username",parent=root)
                         loginDetails['password'] = simpledialog.askstring("Input", "Enter password",parent=root)

                         dvr = signIn(loginDetails)

                    else:
                        dvr = None
                        
                    play = Thread(target=startQueue,args=(login,dvr,vidQueue,nextQueue,))
                    play.start()
            varStart.set(0)

        if varNext.get():
            if videoPlayerStatus:
                print('skipping to next video')
                nextQueue.put(1)
            varNext.set(0)
            
        if varStop.get():
            videoPlayerStatus = 0
            varStop.set(0)

        if varExit.get():
            
            if videoPlayerStatus:
                messagebox.showinfo('Alert','Stop the video player before exiting...')
                
            else:
                root.destroy()
                return 1
            varExit.set(0)
                
        if vidQueue.empty()==0:

            if videoPlayerStatus:

                #print('vidQueue is not empty!')

                temp = vidQueue.get()
                STATUS.config(text=vidStatus)
                root.update()
            else:
                STATUS.config(text='<Video player is off.>')
                root.update()

        root.update()


#------------------------------------------------------------#------------------------END OF FUNCTIONS------------------------------------#------------------------------------------------------------            

main()
root.quit()

