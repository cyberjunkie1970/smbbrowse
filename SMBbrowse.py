#!/usr/bin/python

import subprocess
import os
import sys
from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkf
from tkinter.ttk import *
from tkinter import messagebox
from PIL import ImageTk, Image
from pathlib import Path

root=Tk()
root.geometry("600x500")
root.title("Samba Share Browser")
workgroupfile=str(Path.home())+"/.smbworkgroup"
Path(workgroupfile).touch()
file=open(workgroupfile, "r")
workgroup=file.readline()
file.close
if workgroup=="":
    workgroup="WORKGROUP"
def refresh():
    os.execl(sys.executable, sys.executable, *sys.argv)
def saveNewGroup(newworkgroup, popup):
    file=open(workgroupfile, "w")
    file.write(newworkgroup)
    file.close()
    popup.destroy()
    refresh()
def changeWorkgroup():
    popup=Tk()
    popup.geometry("300x100")
    popup.title("Change Workgroup")
    newworkgroup=StringVar(popup)
    newgrouptext=Label(popup, text="\nPlease enter the new workgroup name:\n")
    newgrouptext.pack()
    newgroupfield=Entry(popup, width=15, textvariable=newworkgroup)
    newgroupfield.pack()
    newgroupbutton=Button(popup, text="Apply", command= lambda: saveNewGroup(newworkgroup.get(), popup))
    newgroupbutton.pack(side=BOTTOM)
    newgroupfield.focus()
changegroup=ttk.Button(text='Workgroup: '+workgroup, command=changeWorkgroup)
changegroup.pack(side=TOP)
tree=ttk.Treeview(root, height=20, selectmode='browse')
tree.pack(side=TOP, fill=BOTH, expand=1)
scrollbar = Scrollbar(tree)
scrollbar.pack(side = RIGHT, fill = Y)
tree.configure(yscrollcommand = scrollbar.set)
scrollbar.config(command = tree.yview)
iconSize=tkf.Font(font='TkDefaultFont').metrics('linespace')
serverIcon = Image.open('/usr/share/pixmaps/smbbrowse/serverIcon.png')
resized=serverIcon.resize((iconSize, iconSize), Image.Resampling.BILINEAR)
serverIcon=ImageTk.PhotoImage(resized)
folderIcon = Image.open('/usr/share/pixmaps/smbbrowse/folderIcon.png')
resized=folderIcon.resize((iconSize, iconSize), Image.Resampling.BILINEAR)
folderIcon=ImageTk.PhotoImage(resized)
result = subprocess.run(['xdg-mime', 'query', 'default', 'inode/directory'], stdout=subprocess.PIPE)
output=result.stdout.decode('utf-8')
print (output)
fileManager=output[0:output.find('.')]
print (fileManager)
result = subprocess.run(['nmblookup', '-S', workgroup], stdout=subprocess.PIPE)
output=result.stdout.decode('utf-8')
server=''
servers=[]
x=0
while x<len(output):
    if output[x:x+10]=="Looking up":
        x=x+1
        while output[x:x+2]!='\n\t':
            x=x+1
        x=x+2
        startindex=x
        while output[x]!=" ":
            x=x+1
        servers.append(output[startindex:x])
    x=x+1
for server in servers:
    tree.insert(parent='', index='end', iid=server, text=' '+server, image=serverIcon)

def shareSelected(event):
    selected=tree.focus()
    if '/' in selected:
        buttonText.set('Mount share smb://'+selected)
    else:
        if not tree.get_children(selected):
            server=selected
            tree.configure(cursor='watch')
            root.update_idletasks()
            getShares(server)
            tree.item(server, open=True)
            tree.configure(cursor='')
def doubleClicked(event):
    selected=tree.focus()
    if '/' in selected:
        buttonText.set('Mount share smb://'+selected)
        result = subprocess.run([fileManager, 'smb://'+selected])
def getShares(server):
    cmd='smbclient -N -L '+server+' | grep Disk'
    result=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output=result.communicate()[0].decode('utf-8')
    shares=[]
    x=0
    while output.find('\t',x)!=-1:
        x=output.find('\t',x)+1
        startindex=x
        while output[x:x+2]!="  ":
            x=x+1
        shares.append(output[startindex:x])
    for share in shares:
        tree.insert(parent=server, index='end', iid=server+'/'+share, text=' '+share, image=folderIcon)
    root.update_idletasks()
def mountShare():
    if buttonText.get()!="No share selected":
        result = subprocess.run([fileManager, buttonText.get()[12:len(buttonText.get())]])
def showAbout():
    messagebox.showinfo("About", "SMB Browser 1.0\nCopyright 2021 Gary Streck\nLicense: MIT")
root.update_idletasks()
tree.bind('<<TreeviewSelect>>', shareSelected)
tree.bind('<Double-1>', doubleClicked)
buttonFrame = Frame(root)
buttonFrame.columnconfigure(0, weight=1)
buttonFrame.columnconfigure(1, weight=1)
buttonFrame.columnconfigure(2, weight=1)
buttonFrame.pack(side=BOTTOM, fill=X)
refreshText=StringVar()
refreshText.set("Refresh")
refreshButton=Button(buttonFrame, textvariable=refreshText, command=refresh).grid(column=0, row=0, pady=5, padx=5, sticky=W)
buttonText=StringVar()
buttonText.set("No share selected")
mountButton=Button(buttonFrame, textvariable=buttonText, command=mountShare).grid(column=1, row=0, pady=5, padx=5)
aboutText=StringVar()
aboutText.set("About")
aboutButton=Button(buttonFrame, textvariable=aboutText, command=showAbout).grid(column=2, row=0, pady=5, padx=5, sticky=E)
root.mainloop()
