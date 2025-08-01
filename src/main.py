# imports
import sys
import datetime
import dateparser

from pathlib import Path
from rich.console import Console


# initializations and constants
rich = Console()

HOME = Path.home()
TASK_FILE = f"{HOME}/.dot/dotfile"
HISTORY_FILE = f"{HOME}/.dot/dothistory"

# defintions

def help():
    rich.print("[reverse bold] dot [/reverse bold] todo list")
    rich.print("\nby [bright_blue underline]https://github.com/AbyssWalker240\n")

    rich.print("Available operations[bright_green bold]:\n")
    
    rich.print("[bright_white]  dot add [bright_green bold]<message> [not bold white]\\[@one @or @more @tags] \\[-d [green]<date>[/green]]")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] add a new entry")
    rich.print("[bright_white]  dot done [bright_green bold]<id>")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] complete an entry and move to history")
    rich.print("[bright_white]  dot delete [bright_green bold]<id>")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] delete an entry")
    rich.print("[bright_white]  dot edit [bright_green bold]<id> <message> [not bold white]\\[@one @or @more @tags] \\[-d [green]<date>[/green]]")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] edit details of an entry")
    rich.print("[bright_white]  dot [not bold white]list \\[all|done|due|overdue] \\[@one @or @more @tags]")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] list entries based on details\n")

    rich.print("[bright_white]  dot history restore [bright_green bold]<id>")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] restore/uncomplete an entry")
    rich.print("[bright_white]  dot history delete [bright_green bold]<id>")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] delete an entry from history")
    rich.print("[bright_white]  dot history [not bold white]list \\[all|on-time|overdue] \\[@one @or @more @tags]")
    rich.print("[white]    [bright_green bold]-[/bright_green bold] list entry history based on details\n")

    rich.print("[bright_yellow bold]Note: [bright_white not bold]no message or tag may contain a pipe [b]|[/b] symbol\n")
    

def error(message):
    message = message+"\n'list help' for help"
    rich.print(f"[bright_red bold]{message}")
    sys.exit(1)

def getItem(listv, index):
    try:
        return listv[index]
    except IndexError:
        error("Not enough arguments")
        
def getItemContinue(listv, index, default):
    try:
        return listv[index]
    except IndexError:
        return default
        

operationIn: str = ""
idIn: int = 0
messageIn: str = ""
tagsIn: list = []
dueIn: str = ""
listIn: str = ""
isList: bool = False
isHistoryList: bool = False
listOperation: str = ""
def parse():
    global operationIn
    global idIn
    global messageIn
    global tagsIn
    global dueIn
    global listIn
    global isList
    global isHistoryList
    global listOperation
    
    args = sys.argv

    # parse and remove optional arguments
    for i in range(len(args) - 1, -1, -1):
        if(args[i].startswith("@")):
            tagsIn.append(args[i])
            del args[i]
        elif(args[i] == "-d"):
            dueIn = getItem(args,i+1)
            del args[i:i+2]
    tagsIn.reverse()
        
    
    # list if no arguments
    if(len(args) == 1):
        operationIn = "list"
        isList = True
        listOperation = "all"
        return
    

    # parse operation
    if(getItem(args,1) == "history"):
        operationIn = f"{args[1]} {getItemContinue(args,2,"list")}"
        del args[1:3]
    else:
        operationIn = args[1]
        del args[1]

    match operationIn:
        case "help":
            help()
            sys.exit(0)
        case "add":
            messageIn = getItem(args,1)
            del args[1]
        case "done":
            idIn = getItem(args,1)
            del args[1]
        case "delete":
            idIn = getItem(args,1)
            del args[1]
        case "edit":
            idIn = getItem(args,1)
            messageIn = getItem(args,2)
            del args[1:3]
        case "list":
            isList = True
            listOperation = getItemContinue(args,1,"all")
            if(len(args) > 1):
                del args[1]
        case "history restore":
            idIn = getItem(args,1)
            del args[1]
        case "history delete":
            idIn = getItem(args,1)
            del args[1]
        case "history list":
            isHistoryList = True
            listOperation = getItemContinue(args,1,"all")
            if(len(args) > 1):
                del args[1]
        case _:
            error("Invalid operation")


    # parse list operation
    if isList:
        match listOperation:
            case "all":
                listIn = "all" # same as dot
            case "done":
                listIn = "done" # same as dot history list (all) or dot history
            case "due":
                listIn = "due" # due soon
            case "overdue":
                listIn = "overdue" # past due but not completed
            case _:
                error("Invalid list operation")
    elif isHistoryList:
        match listOperation:
            case "all":
                listIn = "all" # same as dot list done or dot history
            case "on-time":
                listIn = "on-time" # all completed tasks that were on time
            case "overdue":
                listIn = "overdue" # all completed tasks that were overdue
            case _:
                error("Invalid list operation")


def parseDate(string):
    if(string == ""):
        return "NONE"
        
    date = dateparser.parse(string)
    if date:
        return date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        error("Could not parse date")


def validateData():
    global messageIn
    global tagsIn

    if not (type(messageIn) is str and type(tagsIn) is list):
        error("Incorrect argument types")

    if("|" in messageIn):
        error("Reserved character '|' used")

    for tag in tagsIn:
        if("|" in tag):
            error("Reserved character '|' used")


def readFile(file):
    with open(file, 'r') as f:
        return f.readlines()


def writeFile(file,buffer):
    with open(file, 'w') as f:
        f.writelines(buffer)


def valIDate(file,id):
    lines = readFile(file)
    
    try:
        id = int(id)
    except TypeError:
        error("Invalid type, id must be an integer")

    if(id <= len(lines) and id > 0):
        return id
    else:
        error("Invalid id")


def editEntry(file,id,message,tags,due):
    id = valIDate(file, id)
    due = parseDate(due)
    buffer = readFile(file)

    id = id - 1
    buffer[id] = f"{message}|{tags}|{due}\n"

    writeFile(file,buffer)


def deleteEntry(file,id):
    id = valIDate(file,id)
    buffer = readFile(file)

    id = id - 1
    del buffer[id]

    writeFile(file,buffer)


def parseLine(line):
    return line


def completeEntry(file,historyFile,id):
    id = valIDate(file,id)
    buffer = readFile(file)

    deleteEntry(file,id)

    print(parseLine(buffer[id-1])) # parseLine() parses the line and gathers message, tags, and due


def addEntry(file,message,tags,due):
    due = parseDate(due)
    buffer = f"{message}|{tags}|{due}\n"

    with open(file, 'a') as f:
        f.write(buffer)


# framework

parse()

validateData()

rich.print(f"[green]operation {operationIn}\nid {idIn}\ntags {tagsIn}\ndue {dueIn}\nlist {listIn}")
rich.print(f"[bright_green]message {messageIn}")
# print(isList)
# print(isHistoryList)
# print(listOperation)

match operationIn:
    case "add":
        addEntry(TASK_FILE,messageIn,tagsIn,dueIn)
    case "done":
        completeEntry(TASK_FILE,HISTORY_FILE,idIn)
    case "delete":
        deleteEntry(TASK_FILE,idIn)
    case "edit":
        editEntry(TASK_FILE,idIn,messageIn,tagsIn,dueIn)
