# imports
import sys

from rich.console import Console


# initializations
rich = Console()


# defintions

def help():
    print("help!")

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
    rich.print(f"[bright_black]{args}")

    # parse all tags and dates
    
    if(getItem(args,1) == "history"):
        operationIn = f"{args[1]} {getItem(args,2)}"
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
        case "history add":
            messageIn = getItem(args,1)
            del args[1]
        case "history restore":
            idIn = getItem(args,1)
            del args[1]
        case "history delete":
            idIn = getItem(args,1)
            del args[1]
        case "history edit":
            idIn = getItem(args,1)
            messageIn = getItem(args,2)
            del args[1:3]
        case "history list":
            isHistoryList = True
            listOperation = getItemContinue(args,1,"all")
            if(len(args) > 1):
                del args[1]
        case _:
            error("Invalid operation")

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

    # while(len(args) > 1):
    #     match args[1]:
    #         case tag if tag.startswith("@"):
    #             tagsIn.append(tag)
    #             del args[1]
    #         case "-d":
    #             dueIn = getItem(args,2)
    #             del args[1:3]
    #         case _:
    #             error("Unrecognized flag")


# framework

parse()

rich.print(f"[green]operation {operationIn}\nid {idIn}\ntags {tagsIn}\ndue {dueIn}\nlist {listIn}")
rich.print(f"[bright_green]message {messageIn}")
