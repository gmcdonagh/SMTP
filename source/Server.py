from re import match
import sys
from socket import *

def parseReceiptToCmd(string, current_place, string_length):
    if(string_length < 4):
        try:
            connectionSocket.send("500 Syntax error: command unrecognized")
        except:
            print "Failed to send message"
            return 0                    
        return 0  
    token = string[:4]    
    if (token == "RCPT"):                                                   # Checks if first text is "RCPT"
        current_place = current_place + 4                                   #
        pass                                                                #
    else:                                                                   #                                                                   #
        if(bool(match('MAIL(( )|(\t))+FROM:', string))):                    # # Checks for other commands to see if sequence
            try:                                                            # # error exists
                connectionSocket.send("503 Bad sequence of commands")
            except:
                print "Failed to send message"
                return 0                          
            return 0                                                        # #
        elif(bool(match('DATA(( )|(\t))*$', string))):                      # #
            try:
                connectionSocket.send("503 Bad sequence of commands")
            except:
                print "Failed to send message"
                return 0                           
            return 0                                                        # #
        else:                                                               #
            try:
                connectionSocket.send("500 Syntax error: command unrecognized")
            except:
                print "Failed to send message"
                return 0               #
            return 0                                                        #
    
    for x in range(current_place,string_length):                            # Allows any whitespace between "RCPT" and "TO:"
        if (string[x] == " " or string[x] == "\t"):                         # Also checks to if text after "rcpt"
            pass                                                            # starts with "T" in "TO:"
        elif (string[x] == "T"):                                            #
            current_place = x                                               #
            break                                                           #
        else:                                                               #
            try:
                connectionSocket.send("500 Syntax error: command unrecognized")
            except:
                print "Failed to send message"
                return 0                #
            return 0                                                        #  
    
    token = string[current_place:current_place+3]                           # Verifies "TO:", case-insensitive
    if(token == "TO:"):                                                     #
        current_place = current_place+3                                     #
        pass                                                                #
    else:                                                                   #
        try:
            connectionSocket.send("500 Syntax error: command unrecognized")
        except:
            print "Failed to send message"
            return 0                
        return 0                                                            #
    
    for x in range(current_place, string_length):                           # Takes null space into effect and then locates
        if (string[x] == " " or string[x] == "\t"):                         # start of path token
            pass                                    
        else:                                       
            current_place = x
            current_place = parsePath(string, current_place, string_length) # Next call
            if (current_place == 0):                                        # Error was deeper than rcpt-to-cmd so just return false
                return 0
            for x in range (current_place+1,string_length):                 # Allow nullspace afterwards
                if (string[x] == " " or string[x] == "\t"):
                    pass
                else:
                    try:                                                                
                        connectionSocket.send("501 Syntax error in parameters or arguments")
                    except:
                        print "Failed to send message"
                        return 0
                    return 0
            connectionSocket.send("250 OK")
            return 1
    try:                                                                
        connectionSocket.send("501 Syntax error in parameters or arguments")
    except:
        print "Failed to send message"
        return 0
    return 0

def parseDomain(string, current_place, string_length, least_2):                 
    letter_first = True                                                                                             # This variable used to ensure that the first character in every element is a letter 
    domain_length = 0                                                                                               # This variable is used to keep track of length                                                                         
    for x in range(current_place, string_length):                                                                   
        current_place = x
        if(string[x] == "."):                                                                                       # Periods specify start of new domain
            if(not least_2):
                try:                                                                
                    connectionSocket.send("501 Syntax error in parameters or arguments")
                except:
                    print "Failed to send message"
                    return 0  
                return 0 
            least_2 = False
            current_place = x
            if(current_place+2 > string_length):                                                                    # Makes sure it doesn't end on period
                try:                                                                
                    connectionSocket.send("501 Syntax error in parameters or arguments")
                except:
                    print "Failed to send message"
                    return 0
                return 0
            return parseDomain(string, current_place+1, string_length, least_2)                                     # Recursive call to check if elements come after periods. Any number of elements allowed.
        elif((ord(string[x]) > 64 and ord(string[x]) < 91) or (ord(string[x]) > 96 and ord(string[x]) < 123)        # Check to see if characters in elements are allowed
        or (ord(string[x]) > 47 and ord(string[x]) < 58)):                                                          
            if(letter_first):
                if(ord(string[x]) > 64 and ord(string[x]) < 91) or (ord(string[x]) > 96 and ord(string[x]) < 123):  # Letter check
                    letter_first = False
                    pass
                else:
                    try:                                                                
                        connectionSocket.send("501 Syntax error in parameters or arguments")
                    except:
                        print "Failed to send message"
                        return 0
                    return 0
            domain_length = domain_length +1                                                                        # Updating length
            if(domain_length >= 2):                                                                                 # Now long enough to be accepted
                least_2 = True
            pass 
        elif(string[current_place] == " "):                                                                         # Space needs to be explicitly checked as generally it is a different error
            try:                                                                
                connectionSocket.send("501 Syntax error in parameters or arguments")
            except:
                print "Failed to send message"
                return 0
            return 0
        else:
            if(least_2):
                current_place = x
                return current_place 
            else:
                try:                                                                
                    connectionSocket.send("501 Syntax error in parameters or arguments")
                except:
                    print "Failed to send message"
                    return 0   
                return 0
            
    if(least_2 == True and letter_first == False):
        return string_length-1
    else:
        try:                                                                
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0
        return 0
def parseLocalPart(string, current_place, string_length):
    local_part_length = 0
    for x in range(current_place, string_length):
        if (ord(string[x]) < 128 and ord(string[x]) != 32 and ord(string[x]) != 9 and ord(string[x]) != 34 and ord(string[x]) != 28     # Using asc2 values to identify if character in string
        and ord(string[x]) != 29 and ord(string[x]) != 9 and (ord(string[x]) > 60 or ord(string[x]) < 58)                               # is allowed in grammar
        and ord(string[x]) != 62 and ord(string[x]) != 64 and (ord(string[x]) > 93 or ord(string[x]) < 91)
        and ord(string[x]) != 40 and ord(string[x]) != 41 and ord(string[x]) != 46 and ord(string[x]) != 44):
            pass
            local_part_length = local_part_length +1
        
        elif(local_part_length > 0):                                                                                                    # Grammar specifies there has to be at 
                current_place = x                                                                                                       # least one character in local-part
                return current_place
        else:
            try:                                                                
                connectionSocket.send("501 Syntax error in parameters or arguments")
            except:
                print "Failed to send message"
                return 0
            return 0
    

def parseMailbox(string, current_place, string_length):
    current_place = parseLocalPart(string, current_place, string_length)            # Next call
    if(current_place == None):                                                      # Signifies string is over
        try:                                                                
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0
        return 0
    if(current_place == 0):
        return 0
    if(string[current_place] != "@"):                                               # @ check
        try:                                                                
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0
        return 0
    if(current_place+1 == string_length):                                           
        try:                                                                
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0                                                  
        return 0
    if(string[current_place+1] == " " or string[current_place+1] == "\t"):          # Simple check for a space, which is a mailbox error,
        try:                                                                
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0                        
        return 0
    least_2 = False                                                                 # This variable appears in parseDomain parameters to check if there is at least on character in an element
    current_place = parseDomain(string, current_place+1, string_length, least_2)    # Next call  
    if(current_place == 0):
        return 0
        
    return current_place                                                            # End of this tree
    

def parsePath(string, current_place, string_length):
    if(string[current_place] == "<"):                                       # < check                         
        current_place = current_place + 1
        pass
    else:
        try:                                                                
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0 
        return 0
    if(string[current_place] == " " or string[current_place] == "\t"):      # Simple check for whitespace after <, which would be a path error, whereas any other
        try:                                                                # character would be a local-part error and would be found later.      
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0                
        return 0                             
    current_place =  parseMailbox(string, current_place, string_length)     # Next call
    if(current_place == 0):
        return 0
    if(string[current_place] == ">"):                                       # > check
        return current_place
    else:
        try:
            connectionSocket.send("501 Syntax error in parameters or arguments")
        except:
            print "Failed to send message"
            return 0
        return 0


def parseMailFromCmd(string, current_place, string_length):
    if(string_length < 4):
        try:
            connectionSocket.send("500 Syntax error: command unrecognized")
        except:
            print "Failed to send message"
            return 0                    
        return 0
    token = string[:4]  
    if (token == "MAIL"):                                                   # Checks if first text is "MAIL"
        current_place = current_place + 4                                   #
        pass                                                                #
    else:                                                                   #
        if(bool(match('RCPT(( )|(\t))+TO:', string))):                      # # Checks for other commands to see if there
            try:
                connectionSocket.send("503 Bad sequence of commands")
            except:
                print "Failed to send message"
                return 0                            
            return 0                                                        # #
        elif(bool(match('DATA(( )|(\t))*$', string))):                      # #
            try:
                connectionSocket.send("503 Bad sequence of commands")
            except:
                print "Failed to send message"
                return 0                           
            return 0                                                        
        else:                                                               
            try:
                connectionSocket.send("500 Syntax error: command unrecognized")
            except:
                print "Failed to send message"
                return 0                 
            return 0                                                        #
        
    for x in range(current_place,string_length):                            # Allows any whitespace between "MAIL" and "FROM"
        if (string[x] == " " or string[x] == "\t"):                         # Also checks to see if the text after "MAIL"
            pass                                                            # starts with "F" in "FROM"
        elif (string[x] == "F"):                                            #
            current_place = x                                               #
            break                                                           #
        else:                                                               #
            try:
                connectionSocket.send("500 Syntax error: command unrecognized")
            except:
                print "Failed to send message"
                return 0                  
            return 0                                                        #                                 
    
    token = string[current_place:current_place+5]                           # Verifies "FROM:"
    if(token == "FROM:"):                                                   #
        current_place = current_place+5                                     #
        pass                                                                #
    else:                                                                   #
        try:
            connectionSocket.send("500 Syntax error: command unrecognized")
        except:
            print "Failed to send message"
            return 0                     
        return 0                                                            #
                                                    
    for x in range(current_place, string_length):                           # Takes null space into effect and then locates
        if (string[x] == " " or string[x] == "\t"):                         # start of path token
            pass                                    
        else:                                       
            current_place = x
            current_place = parsePath(string, current_place, string_length) # Next call
            if (current_place == 0):                                        # Error was deeper than mail-from-cmd so just return false
                return 0
            for x in range (current_place+1,string_length):                 # Allows nullspace
                if (string[x] == " " or string[x] == "\t"):
                    pass
                else:
                    try:
                        connectionSocket.send("501 Syntax error in parameters or arguments")
                    except:
                        print "Failed to send message"
                        return 0
                    return 0
            try:
                connectionSocket.send("250 OK")
            except:
                print "Failed to send message"
                return 0
            return 1
    try:
        connectionSocket.send("501 Syntax error in parameters or arguments")
    except:
        print "Failed to send message"
        return 0
    return 0



if(len(sys.argv) == 2):                                                             # Checks to see if there is an argument so it knows to execute server
    connection_success = False                                                      # Loop component to keep trying until success                                              
    try:
        port = int(sys.argv[1])
    except:
        print "Invalid arguments"
        sys.exit()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    while (not connection_success):                                                 
        connection_success = True
        try:
            serverSocket.bind(('', port))
        except:
            port = port + 1                                                         # If port is busy, try port+1
            connection_success = False
    print("Started on port " + str(port))       
    serverSocket.listen(1)
    
    while True:                                                                     # Program never leaves this while loop
        valid_connection = True                                                     # Used to ensure connection to a client exists
        connectionSocket, addr = serverSocket.accept()                              # before processing starts
        try:
            connectionSocket.send(("220 " + getfqdn()))
        except:
            print "Failed to send message"
            connectionSocket.close()
            valid_connection = False
        state = "greeting"                                                          # variable to keep track of state
        appended_string = ""                                                        # string that will be appended to all rctp to files at end, gets built gradually during the program to encompass all needed text by the end
        rcpt_to_counter = 0                                                         # counts rcpt addresses,
        least_1_rcpt_to = False                                                     # has to be more than 1
        rcpt_to_list = []
        
        while (valid_connection): 
            need_next_line = False                                                  # true if the whole line has been dealt with and need to move on
            if (state != "data"):
                try:
                    string = connectionSocket.recv(1024)                    
                except:                                                             
                    print "Failed to receive message"
                    connectionSocket.close()
                    break                                                  
            current_place = 0                                                       # current_place is used in every method to iterate along string                              
            string_length = len(string) 
                      
            if (bool(match('QUIT(( )|\t)*$', string)) and state != "data" and state != "quit"):         #If client issues an unexpected quit, we close connection and wait
                connectionSocket.close()
                break
            if (state == "greeting" and(not need_next_line)):                       # Handles greeting stage with domain checking
                greeting_list = string.split()
                if (len(greeting_list) == 2 and greeting_list[0] == "HELO"):
                    success = parseDomain(greeting_list[1], current_place, len(greeting_list[1]), False)
                    if (success != 0):
                        try:
                            connectionSocket.send("250 OK " + greeting_list[1] + " please to meet you") # Responds with 250 if all valid
                        except:
                            print "Failed to send message"
                            connectionSocket.close()
                            break
                        state = "mf"
                        need_next_line = True
                    else:
                        connectionSocket.close()
                        break
                else:
                    try:
                        connectionSocket.send("500 Syntax error: command unrecognized")
                    except:
                        print "Failed to send message"
                        connectionSocket.close()
                        break
                    connectionSocket.close()
                    break
                    
            if (state == "mf" and (not need_next_line)):                                                            
                success = parseMailFromCmd(string, current_place, string_length)    # All productions in grammar have their own function to validate tokens within. The value returned by each is curent_place to continue iteration.                                                                                                    
                if(success == 1):                                                   # If a grammar error is ever found, the associated method prints the error name and then returns 0. At end, if current_place is 0 because it was sent up the chain, it knows to not validate string.
                    state = "rt"                                                    # mail from dealt with, now we move to rcpt to
                    need_next_line = True
                else:
                    connectionSocket.close() 
                    break                                      
            if (state == "rt" and (not need_next_line)):                                    
                if (bool(match('DATA(( )|(\t))*$', string)) and least_1_rcpt_to):   # Checks for data command to switch to that state
                    try:
                        connectionSocket.send("354 Start mail input; end with <CRLF>.<CRLF>")
                    except:
                        print "Failed to send message"
                        connectionSocket.close() 
                        break                 
                    state = "data" 
                    need_next_line = True
                else:                                                                   
                    success = parseReceiptToCmd(string, current_place, string_length)       # Not dealing with data command, so call to parse the rcpt to
                    if(success == 1):                                             
                        rcpt_to_counter = rcpt_to_counter + 1
                        least_1_rcpt_to = True
                        begin = string.find("@")
                        end = string.find(">")
                        rcpt_to_list.append(string[begin+1:end])                            # Add every path found in RCP TO commands to list
                    else:                                                                   # to use later
                        connectionSocket.close()
                        break
            if (state == "data" and (not need_next_line)):                                  # In data stage, append all lines that aren't "."
                string = ""
                while(string != "."):                                                       # This deals with the fact that TCP is a byte stream
                    string += connectionSocket.recv(1024)                                   # Will continuously process characters that come in
                    while (string.find("\n") != -1):                                        # until only a period is sent
                        appended_string += string[0:string.find("\n")+1]
                        string = string[string.find("\n")+1:]      
                try:
                    connectionSocket.send("250 OK")                                         # After period is received, send 250
                except:
                    print "Failed to send message"
                    connectionSocket.close()
                    break
                for x in range(0, rcpt_to_counter):                             # to locate the rcpt to addresses within rcpt to list
                    path_name = rcpt_to_list[x]            
                    file_name = path_name                                       
                    try:
                        with open(file_name, "a") as mail_file:                 # and all the text is written to each file
                            mail_file.write(appended_string)       
                    except:
                        print "Failed to locate mailbox"   
                        connectionSocket.close()
                        break      
                need_next_line = True
                state = "quit"
             
            if (state == "quit" and (not(need_next_line))):                     # We expect a quit command. Close connection either way
                if (bool(match('QUIT(( )|(\t))*$', string))):
                    connectionSocket.close()
                    break
                else:
                    print "Unrecognized command"
                    connectionSocket.close()
                    break             
else:
    print "Invalid arguments"