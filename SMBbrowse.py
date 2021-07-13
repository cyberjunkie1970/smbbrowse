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

root=Tk()
root.geometry("600x500")
root.title("Samba Share Browser")
tree=ttk.Treeview(root, height=20, selectmode='browse')
tree.pack(side=TOP, fill=BOTH, expand=1)
scrollbar = Scrollbar(tree)
scrollbar.pack(side = RIGHT, fill = Y)
tree.configure(yscrollcommand = scrollbar.set)
scrollbar.config(command = tree.yview)
iconSize=tkf.Font(font='TkDefaultFont').metrics('linespace')
serverIcon = Image.open('/usr/share/pixmaps/SMBbrowse/serverIcon.png')
resized=serverIcon.resize((iconSize, iconSize), Image.ANTIALIAS)
serverIcon=ImageTk.PhotoImage(resized)
folderIcon = Image.open('/usr/share/pixmaps/SMBbrowse/folderIcon.png')
resized=folderIcon.resize((iconSize, iconSize), Image.ANTIALIAS)
folderIcon=ImageTk.PhotoImage(resized)
result = subprocess.run(['nmblookup', '-S', 'WORKGROUP'], stdout=subprocess.PIPE)
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
            tree.configure(cursor='circle')
            root.update_idletasks()
            getShares(server)
            tree.item(server, open=True)
            tree.configure(cursor='')
def doubleClicked(event):
    selected=tree.focus()
    if '/' in selected:
        buttonText.set('Mount share smb://'+selected)
        result = subprocess.run(['xdg-open', 'smb://'+selected])
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
        result = subprocess.run(['xdg-open', buttonText.get()[12:len(buttonText.get())]])
def refresh():
    os.execl(sys.executable, sys.executable, *sys.argv)
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