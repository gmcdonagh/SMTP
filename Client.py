from re import match
import sys
from socket import *

def parseReceiptToCmd(string, current_place, string_length):
    if(string_length < 4):
        print "500 Syntax error: command unrecognized"                      
        return 0  
    token = string[:4]    
    if (token == "RCPT"):                                                   # Checks if first text is "RCPT"
        current_place = current_place + 4                                   #
        pass                                                                #
    else:                                                                   #                                                                   #
        if(bool(match('MAIL(( )|(\t))+FROM:', string))):                    # # Checks for other commands to see if sequence
            print "503 Bad sequence of commands"                            # # error exists
            return 0                                                        # #
        elif(bool(match('DATA(( )|(\t))*$', string))):                      # #
            print "503 Bad sequence of commands"                            # #
            return 0                                                        # #
        else:                                                               #
            print "500 Syntax error: command unrecognized"                  #
            return 0                                                        #
    
    for x in range(current_place,string_length):                            # Allows any whitespace between "RCPT" and "TO:"
        if (string[x] == " " or string[x] == "\t"):                         # Also checks to if text after "rcpt"
            pass                                                            # starts with "T" in "TO:"
        elif (string[x] == "T"):                                            #
            current_place = x                                               #
            break                                                           #
        else:                                                               #
            print "500 Syntax error: command unrecognized"                  #
            return 0                                                        #  
    
    token = string[current_place:current_place+3]                           # Verifies "TO:", case-insensitive
    if(token == "TO:"):                                                     #
        current_place = current_place+3                                     #
        pass                                                                #
    else:                                                                   #
        print "500 Syntax error: command unrecognized"                      #
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
                    print "501 Syntax error in parameters or arguments"
                    return 0
            print "250 OK"
            return 1
    print "501 Syntax error in parameters or arguments"
    return 0

def parseDomain(string, current_place, string_length, least_2):                 
    letter_first = True                                                                                             # This variable used to ensure that the first character in every element is a letter 
    domain_length = 0                                                                                               # This variable is used to keep track of length                                                                         
    for x in range(current_place, string_length):                                                                   
        current_place = x
        if(string[x] == "."):                                                                                       # Periods specify start of new domain
            if(not least_2):
                print "Invalid address"    
                return 0 
            least_2 = False
            current_place = x
            if(current_place+2 > string_length):                                                                    # Makes sure it doesn't end on period
                print "Invalid address"
                return 0
            return parseDomain(string, current_place+1, string_length, least_2)                                     # Recursive call to check if elements come after periods. Any number of elements allowed.
        elif((ord(string[x]) > 64 and ord(string[x]) < 91) or (ord(string[x]) > 96 and ord(string[x]) < 123)        # Check to see if characters in elements are allowed
        or (ord(string[x]) > 47 and ord(string[x]) < 58)):                                                          
            if(letter_first):
                if(ord(string[x]) > 64 and ord(string[x]) < 91) or (ord(string[x]) > 96 and ord(string[x]) < 123):  # Letter check
                    letter_first = False
                    pass
                else:
                    print "Invalid address"
                    return 0
            domain_length = domain_length +1                                                                        # Updating length
            if(domain_length >= 2):                                                                                 # Now long enough to be accepted
                least_2 = True
            pass 
        elif(string[current_place] == " "):                                                                         # Space needs to be explicitly checked as generally it is a different error
            print "Invalid address"    
            return 0
        else:
            if(least_2):
                current_place = x
                return current_place 
            else:
                print "Invalid address"    
                return 0
    return string_length-1
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
            print "Invalid address"
            return 0
    

def parseMailbox(string, current_place, string_length):
    current_place = parseLocalPart(string, current_place, string_length)            # Next call
    if(current_place == None):                                                      # Signifies string is over
        print "Invalid address"
        return 0
    if(current_place == 0):
        return 0
    if(string[current_place] != "@"):                                               # @ check
        print "Invalid address"
        return 0
    if(current_place+1 == string_length):                                           
        print "Invalid address"                                                    
        return 0
    if(string[current_place+1] == " " or string[current_place+1] == "\t"):          # Simple check for a space, which is a mailbox error,
        print "Invalid address"                         # whereas any other invalid character is a domain error and checked later
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
        print "Invalid address"
        return 0
    if(string[current_place] == " " or string[current_place] == "\t"):      # Simple check for whitespace after <, which would be a path error, whereas any other
        print "Invalid address"                 # character would be a local-part error and would be found later.
        return 0                             
    current_place =  parseMailbox(string, current_place, string_length)     # Next call
    if(current_place == 0):
        return 0
    if(string[current_place] == ">"):                                       # > check
        return current_place
    else:
        print "Invalid address"
        return 0


def parseMailFromCmd(string, current_place, string_length):
    if(string_length < 4):
        print "500 Syntax error: command unrecognized"                      
        return 0
    token = string[:4]  
    if (token == "MAIL"):                                                   # Checks if first text is "MAIL"
        current_place = current_place + 4                                   #
        pass                                                                #
    else:                                                                   #
        if(bool(match('RCPT(( )|(\t))+TO:', string))):                      # # Checks for other commands to see if there
            print "503 Bad sequence of commands"                            # # is a sequence error
            return 0                                                        # #
        elif(bool(match('DATA(( )|(\t))*$', string))):                      # #
            print "503 Bad sequence of commands"                            # #
            return 0                                                        # #
        else:                                                               #
            print "500 Syntax error: command unrecognized"                  #
            return 0                                                        #
        
    for x in range(current_place,string_length):                            # Allows any whitespace between "MAIL" and "FROM"
        if (string[x] == " " or string[x] == "\t"):                         # Also checks to see if the text after "MAIL"
            pass                                                            # starts with "F" in "FROM"
        elif (string[x] == "F"):                                            #
            current_place = x                                               #
            break                                                           #
        else:                                                               #
            print "500 Syntax error: command unrecognized"                  #
            return 0                                                        #                                 
    
    token = string[current_place:current_place+5]                           # Verifies "FROM:"
    if(token == "FROM:"):                                                   #
        current_place = current_place+5                                     #
        pass                                                                #
    else:                                                                   #
        print "500 Syntax error: command unrecognized"                      #
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
                    print "501 Syntax error in parameters or arguments"
                    return 0
            print "250 OK"
            return 1
    print "501 Syntax error in parameters or arguments"
    return 0



# Initial user interaction to help build mail message. If addresses entered are erroneous, client tell user the address was invalid
# and re-prompts them for a correct one
if(len(sys.argv) == 3):                                                     # Cursory check for number of inputs
    formed = False                                                          # Endless user mistakes are possible so loop is dependent on well-formed message or not
    state = "from"                                                          # Variable for state within loop
    lines = ""                                                              # This is gradually built up to encompass all text the user enters, excluding subject which is added later
    to_error = False                                                        # If one to address is invalid, treat all as invalid and re-prompt                    
    while(not(formed)):
        if(state == "from"):                                                # Handling from address
            from_address = raw_input("From: ")
            from_address = "<" + from_address.strip() + ">"                 # Simple hack to allow for original parsing code to still work
            string_length = len(from_address)
            current_place = 0
            success = parsePath(from_address, current_place, string_length) 
            if(success == 0):
                lines = ""
                state = "from"
            else:
                lines+= "From: " + from_address + "\n"
                state = "to"
        if(state == "to"):                                                  # Handling to address
                to_error = False
                to_address_list = raw_input("To: ").split(",")              # List of all to addresses is created and then all are parsed
                for to_address in to_address_list:
                    to_address = "<" + to_address.strip() + ">"             # Simple hack to allow for original parsing code to still work
                    string_length = len(to_address)
                    current_place = 0
                    success = parsePath(to_address, current_place, string_length)
                    if(success == 0):                                       # Throw away all to addresses as a mistake was found
                        to_error = True
                    else:
                        lines+= "To: " + to_address.strip() + "\n"
                if(not(to_error)):
                            state = "subject"        
        if(state == "subject"):                                             # Handling subject
            subject = raw_input("Subject: ")
            state = "message"
        if(state == "message"):                                             # Handling message body
            message_line = raw_input("Message: ")
            while(not(message_line == ".")):
                lines += message_line + "\n"
                message_line = raw_input()  
            formed = True                                                   # The variable lines now encompasses all user text in a format that allows earlier
                                                                            # client code to parse it and issue commands to the server based
                                                                            # on what is inside
            
# User interaction completed, begin TCP and message processing. If a TCP error is ever encountered, connection is closed if
# it exists and program terminates. Same for any formatting errors encountered in message processing. TCP error presence is checked for
# every time a connection is used. 
    hostname = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except:
        print "Invalid arguments"
        sys.exit()
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((hostname, port))                  # Connects to server
    except:
        print "Connection failed"
        sys.exit()
        
    quit_flag = False                                           # used only in beginning in some places for cleaner termination of program than sys.exit()
    try:                                                        
        reply = clientSocket.recv(1024)
    except:
        print "Failed to receive message through socket"
        clientSocket.close()
        sys.exit
    print >> sys.stderr, reply
    if(bool(match("220", reply))):                              # Checks first received message for 220 code
        domain = getfqdn()                                      #
        domain = domain[domain.find(".")+1:len(domain)]         #
        try:                                                    #
            clientSocket.send("HELO " + domain)                 # Responds with HELO command if success
        except:
            print "Failed to send message through socket"
            clientSocket.close()
            sys.exit 
        try:
            reply = clientSocket.recv(1024)
        except:
            print "Failed to receive message through socket"
            clientSocket.close()
            sys.exit
        print >> sys.stderr, reply
        if(bool(match("250", reply))):                          # If HELO is responded to with 250, enters message processing
            pass                                                # and command send sequence
        else:
            print "Invalid HELO command"
            clientSocket.close()
            quit_flag = True
    else:
        print "Failed to receive greeting"
        clientSocket.close()
        quit_flag = True
        
    if(not(quit_flag)):               
        file_lines = lines.split("\n")                                      # Splits the 'lines' text from the user input stage
        file_lines.pop(-1)                                                  # Removes last line of lines which is an empty string and an artifact of how lines was processed
        state = "from"                                                      # Keeps track of state
        error = False                                                       # Keeps track of whether an error is thrown or not
        for line in file_lines:                                             # This loop runs through every line of text and depending on what it is, handles it in one of a number ways
            need_next_line = False                                          # Signals to move to next line once a line has been dealt with
            if(state == "from" and not(need_next_line)):                    # This condition specifies we expect a from address
                if(line[0:5] == "From:"): 
                    from_path_begin = line.find("<")                        # Locates from address        
                    from_path_end = line.find(">")                          #
                    from_path = line[from_path_begin:from_path_end+1]       #
                    try:                                                    #
                        clientSocket.send("MAIL FROM: " + from_path)        # Issues mail from command      
                    except: 
                        print "Failed to send message through socket"
                        clientSocket.close()
                        sys.exit()
                    try:
                        reply = clientSocket.recv(1024)                      
                    except:
                        print "Failed to receive message through socket"
                        clientSocket.close()
                        sys.exit()
                    print >> sys.stderr, reply                               
                    if(bool(match("250", reply))):                          # Only continues if the the response to MAIL FROM is a 250
                        state = "to"                                        #
                        need_next_line = True                               #
                    else:                                                   #
                        print "Invalid MAIL FROM command"                   #
                        clientSocket.close()                                #
                        sys.exit()                                          #
                else:                                                       # If text isn't "From:" , an error is thrown
                    print "Invalid MAIL FROM command"                       #
                    clientSocket.close()                                    #
                    sys.exit()                                              #
                   
            elif(state == "to" and not(need_next_line)):                    # This condition specifies we expect a to address
                if (line[0:3] == "To:"):                                    # However, as any number of to addresses are allowed,
                    empty_body = True                                       # we have to keep going until we get a non-to address string and handle that
                    to_path_begin = line.find("<")                          # Locates to address     
                    to_path_end = line.find(">")                            #
                    to_path = line[to_path_begin:to_path_end+1]             # 
                    try:
                        clientSocket.send("RCPT TO: " + to_path)            # Issues rcpt to command
                    except:
                        print "Failed to send message through socket"
                        clientSocket.close()
                        sys.exit
                    try:
                        reply = clientSocket.recv(1024)                      
                    except:
                        print "Failed to receive message through socket"
                        clientSocket.close()
                        sys.exit
                    print >> sys.stderr, reply                              # Only continues if response to RCPT TO is a 250
                    if(bool(match("250", reply))):                          #
                        state = "to"                                        #
                        need_next_line = True                               #
                    else:                                                   #
                        print "Invalid RCPT TO command"                     #
                        clientSocket.close()                                #
                        sys.exit()                                          #
                else:                                                       #  
                    try:                                                    # When we expect a to address, but get a line of body message instead,
                        clientSocket.send("DATA")                           # we have dealt with all the to addresses and now need to
                    except:                                                 # process text. So we send the DATA command
                        print "Failed to send message through socket"
                        clientSocket.close()
                        sys.exit
                    try:
                        reply = clientSocket.recv(1024)                     
                    except:
                        print "Failed to receive message through socket"
                        clientSocket.close()
                        sys.exit
                    print >> sys.stderr, reply                               
                    if(bool(match("354", reply))):                                                  # Once we get the 354, we send the from address,               
                        try:                                                                        # the to addresses, and the subject immediately
                            clientSocket.send("From: " + from_path[1:len(from_path) - 1] + "\n")    #
                        except:                                                                     #
                            print "Failed to send message through socket"                           #
                            clientSocket.close()                                                    #
                            sys.exit                                                                #
                                                                                                    #
                        for path in to_address_list:                                                #
                            try:                                                                    #
                                clientSocket.send("To: " + path.strip() + "\n")                     #
                            except:                                                                 #
                                print "Failed to send message through socket"                       #
                                clientSocket.close()                                                #
                                sys.exit                                                            #
                                                                                                    #
                        try:                                                                        #
                            clientSocket.send("Subject: " + subject + "\n" + "\n")                  #               
                        except:                                                                     #
                            print "Failed to send message through socket"                           #
                            clientSocket.close()                                                    #
                            sys.exit                                                                #
                                                       
                        state = "text"                                      
                    else:                                                   
                        print "Invalid DATA command"                        
                        clientSocket.close()                                
                        sys.exit()                                          
                        
                    try:
                        clientSocket.send(line + '\n')                      # When we get a valid 354, we output that one body message line
                    except:                                                 # and switch to a state that only deals with body text
                        print "Failed to send message through socket"
                        clientSocket.close()
                        sys.exit
                    empty_body = False
                    state= "text"                                           
                    need_next_line = True
                
            elif(state == "text" and not(need_next_line)):                  # State that only deals with body message.              
                try:                                                    
                    clientSocket.send(line + '\n')                          # Simply send the body message line to server               
                except:
                    print "Failed to send message through socket"
                    clientSocket.close()
                    sys.exit  
                   
                empty_body = False                                      # This signals if the message body is totally empty for formatting
                need_next_line = True                                   # later
            
        if(not(error)):                                                     # If no error was made, then we know the file ended with the
            if(empty_body):                                                 # last line of a message body. So we do different things depending
                try:                                                        # on if the message body was empty or not
                    clientSocket.send("DATA")                              
                except:
                    print "Failed to send message through socket"
                    clientSocket.close()
                    sys.exit
                try:
                    reply = clientSocket.recv(1024)                          
                except:
                    print "Failed to receive message through socket"
                    clientSocket.close()
                    sys.exit
                print >> sys.stderr, reply                                   
                if(bool(match("354", reply))):                                                  # There was an empty body so we send the from, tos,            
                    try:                                                                        # and subject out with a period to denote end of body
                        clientSocket.send("From: " + from_path[1:len(from_path) - 1] + '\n')    #
                    except:                                                                     #
                        print "Failed to send message through socket"                           #
                        clientSocket.close()                                                    #
                        sys.exit                                                                #
                                                                                                #
                    for path in to_address_list:                                                #
                        try:                                                                    #
                            clientSocket.send("To: " + path.strip() + '\n')                     #
                        except:                                                                 #
                            print "Failed to send message through socket"                       #
                            clientSocket.close()                                                #
                            sys.exit                                                            #     
                                                                                                #
                    try:                                                                        #
                        clientSocket.send("Subject: " + subject + '\n' + '\n')                  #
                    except:                                                                     #
                        print "Failed to send message through socket"                           #
                        clientSocket.close()                                                    #
                        sys.exit                                                                #
                                                                                                #
                    try:                                                                        #
                        clientSocket.send(".")                                                  #
                    except:                                                                     #
                        print "Failed to send message through socket"                           #
                        clientSocket.close()                                                    #
                        sys.exit                                                                #                                                                                                                                
                else:                                                       
                    print "Invalid DATA command"                            
                    clientSocket.close()
                    sys.exit
            else:
                try:                                                           
                    clientSocket.send(".")                          # There wasn't an empty body so we know the from,tos, and subject
                except:                                             # were already sent, so we end the message
                    print "Failed to send message through socket"
                    clientSocket.close()
                    sys.exit                                                  
            try:
                reply = clientSocket.recv(1024)
            except:
                print "Failed to receive message through socket"
                clientSocket.close()
                sys.exit
            print >> sys.stderr, reply                                      
            if(bool(match("250", reply))):                          # Signals reception of entire email message upon which we send quit command                 
                try:
                    clientSocket.send("QUIT")   
                except:
                    print "Failed to send message through socket"
                    clientSocket.close()
                    sys.exit 
                clientSocket.close()   
                sys.exit()                               
            else:                                                           
                print "Email message not successfully received"
                clientSocket.close()
                sys.exit 
else:
    print "Invalid arguments"