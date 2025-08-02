# imports
import sys
import datetime
import dateparser
import contextlib

from pathlib import Path
from rich.console import Console


# initializations and constants
rich = Console()

HOME = Path.home()
TASK_FILE = f"{HOME}/.dot/dotfile"
HISTORY_FILE = f"{HOME}/.dot/dothistory"

# defintions

def help():
    rich.print("\n[reverse bold] dot [/reverse bold] todo list")
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
    rich.print("[bright_white]  dot history [not bold white]list \\[all|ontime|overdue] \\[@one @or @more @tags]")
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
listOperation: str = ""
compact: bool = False
def parse():
    global operationIn
    global idIn
    global messageIn
    global tagsIn
    global dueIn
    global listIn
    global listOperation
    global compact
    
    isList = False
    isHistoryList = False
    
    args = sys.argv

    # parse and remove optional arguments
    for i in range(len(args) - 1, -1, -1):
        if(args[i].startswith("@")):
            tagsIn.append(args[i])
            del args[i]
        elif(args[i] == "-d"):
            dueIn = getItem(args,i+1)
            del args[i:i+2]
        elif(args[i] == "-c"):
            compact = True
            del args[i]
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
                operationIn = "history list"
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
            case "ontime":
                listIn = "ontime" # all completed tasks that were on time
            case "overdue":
                listIn = "overdue" # all completed tasks that were overdue
            case _:
                error("Invalid list operation")


def parseDate(string):
    if(string == "" or string == "NONE"):
        return "NONE"

    with contextlib.redirect_stderr(None): # ignore error I dont understand
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


def encodeTags(tags):
    return ",".join(tags)

def decodeTags(tagsString):
    return tagsString.split(",")


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
    tags = encodeTags(tags)
    due = parseDate(due)
    buffer = readFile(file)

    id = id - 1 # adjust index to be zero indexed
    buffer[id] = f"{message}|{tags}|{due}||\n"

    writeFile(file,buffer)


def deleteEntry(file,id):
    id = valIDate(file,id)
    buffer = readFile(file)

    id = id - 1 # adjust index to be zero indexed
    del buffer[id]

    writeFile(file,buffer)


def parseLine(line):
    buffer = line.split("|")
    buffer[1] = decodeTags(buffer[1])
    return buffer


def completeEntry(file,historyFile,id,isRestore):
    id = valIDate(file,id)
    buffer = readFile(file)

    deleteEntry(file,id)

    parsed = parseLine(buffer[id-1])

    message = parsed[0]
    tags = parsed[1]
    due = parsed[2]

    if isRestore:
        completed = ""
    else:
        completed = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    addEntry(historyFile,message,tags,due,completed)


def addEntry(file,message,tags,due,completed):
    tags = encodeTags(tags)
    due = parseDate(due)
    buffer = f"{message}|{tags}|{due}|{completed}|\n"

    with open(file, 'a') as f:
        f.write(buffer)


def printLine(parsedData,line,compact,dueLevel):
    parsedData[1] = " ".join(parsedData[1])

    match dueLevel:
        case 0:
            compactLine = f"[bright_black not bold]Due: {parsedData[2]}"
            normalLine = f"[bright_green bold] -[bright_white not bold] {parsedData[0]}  [bright_black not bold]Due: {parsedData[2]}\n"
        case 1:
            compactLine = f"[bright_black not bold]Due: [yellow italic]{parsedData[2]}"
            normalLine = f"[bright_green bold] -[bright_white not bold] {parsedData[0]}  [bright_black not bold]Due: {parsedData[2]} [italic yellow]SOON\n"
        case 2:
            compactLine = f"[bright_black not bold]Due: [red italic]{parsedData[2]}"
            normalLine = f"[bright_green bold] -[bright_white not bold] {parsedData[0]}  [red not bold]Due: {parsedData[2]} [bright_red bold italic]OVERDUE\n"
    
    if compact:
        rich.print(f"[bright_yellow bold]{line}) [bright_white not bold]{parsedData[0]}  [green not bold]{parsedData[1]}")
        rich.print(compactLine)
    else:
        rich.print(f"[bright_yellow bold]{line}) [bright_black not bold]Tags: [green not bold]{parsedData[1]}")
        rich.print(normalLine)


def printHistoryLine(parsedData,line,compact,dueLevel):
    parsedData[1] = " ".join(parsedData[1])

    match dueLevel:
        case 0:
            compactLine = f" [bright_green not bold]Completed: {parsedData[3]} [bright_black not bold]Due: {parsedData[2]}"
            normalLine = f"[bright_green not bold]   Completed: {parsedData[3]}\n"
        case 1:
            compactLine = f" [bright_green not bold]Completed: {parsedData[3]} [bright_black not bold]Due: {parsedData[2]}"
            normalLine = f"[bright_green not bold]   Completed: {parsedData[3]}\n"
        case 2:
            compactLine = f" [bright_green not bold]Completed: {parsedData[3]} [red italic]Due: {parsedData[2]}"
            normalLine = f"[bright_green not bold]   Completed: {parsedData[3]} [red italic]Late\n"
    
    if compact:
        rich.print(f"[bright_yellow bold]{line}) [bright_white not bold]{parsedData[0]}")
        rich.print(compactLine)
        rich.print(f" [bright_black not bold]Tags: [green not bold]{parsedData[1]}")
    else:
        rich.print(f"[bright_yellow bold]{line}) [bright_black not bold]Tags: [green not bold]{parsedData[1]}")
        rich.print(f" [bright_green bold]-[bright_white not bold] {parsedData[0]}  [bright_black not bold]Due: {parsedData[2]}")
        rich.print(normalLine)


def dotList(file,filter,operation,compact):
    buffer = readFile(file)

    now = datetime.datetime.now()
    in24hours = now + datetime.timedelta(hours=24)
    
    if compact:
        rich.print(f"[reverse bold] dot [/reverse bold] {operation}\n")
    else:
        rich.print(f"\n[reverse bold] dot [/reverse bold] {operation}\n")

    match filter:
        case "all":
            for i in range(0,len(buffer)):
                if(operation == "list"):
                    if(not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") <= now):
                        printLine(parseLine(buffer[i]),i+1,compact,2)
                    elif(not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") <= in24hours):
                        printLine(parseLine(buffer[i]),i+1,compact,1)
                    else:
                        printLine(parseLine(buffer[i]),i+1,compact,0)
                else:
                    if(not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") <= datetime.datetime.strptime(parseLine(buffer[i])[3], "%Y-%m-%d %H:%M:%S")):
                        printHistoryLine(parseLine(buffer[i]),i+1,compact,2)
                    else:
                        printHistoryLine(parseLine(buffer[i]),i+1,compact,0)

        case "done":
            for i in range(0,len(buffer)):
                printHistoryLine(parseLine(buffer[i]),i+1,compact,0)

        case "due":
            for i in range(0,len(buffer)):
                if(not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") <= now):
                    printLine(parseLine(buffer[i]),i+1,compact,2)
                elif(not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") <= in24hours):
                    printLine(parseLine(buffer[i]),i+1,compact,1)

        case "overdue":
            for i in range(0,len(buffer)):
                if(not parseLine(buffer[i])[2] == "NONE" and operation == "list" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") < now):
                    printLine(parseLine(buffer[i]),i+1,compact,2)
                elif(not parseLine(buffer[i])[2] == "NONE" and operation == "history list" and not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") < datetime.datetime.strptime(parseLine(buffer[i])[3], "%Y-%m-%d %H:%M:%S")):
                    printHistoryLine(parseLine(buffer[i]),i+1,compact,2)

        case "ontime":
            for i in range(0,len(buffer)):
                if(not parseLine(buffer[i])[2] == "NONE" and datetime.datetime.strptime(parseLine(buffer[i])[2], "%Y-%m-%d %H:%M:%S") >= datetime.datetime.strptime(parseLine(buffer[i])[3], "%Y-%m-%d %H:%M:%S")):
                    printHistoryLine(parseLine(buffer[i]),i+1,compact,0)


# framework

parse()

validateData()

# rich.print(f"[green]operation {operationIn}\nid {idIn}\ntags {tagsIn}\ndue {dueIn}\nlist {listIn}")
# rich.print(f"[bright_green]message {messageIn}")
# print(isList)
# print(isHistoryList)
# print(listOperation)

match operationIn:
    case "add":
        addEntry(TASK_FILE,messageIn,tagsIn,dueIn,"")
    case "done":
        completeEntry(TASK_FILE,HISTORY_FILE,idIn,False)
    case "delete":
        deleteEntry(TASK_FILE,idIn)
    case "edit":
        editEntry(TASK_FILE,idIn,messageIn,tagsIn,dueIn)
    case "list":
        dotList(TASK_FILE,listOperation,operationIn,compact)
    case "history restore":
        completeEntry(HISTORY_FILE,TASK_FILE,idIn,True)
    case "history delete":
        deleteEntry(HISTORY_FILE,idIn)
    case "history list":
        dotList(HISTORY_FILE,listOperation,operationIn,compact)
