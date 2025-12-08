import shlex
import subprocess
import shutil
import os


##Finish help menu
def help_menu():
    print("cd <directory>\t-\t Changes the current working directory to <directory>")
    print("pwd\t-\t Prints the current working directory")
    print("cat <file>\t-\t Prints the contents of text file <file>")
    print("cp <src> <dst>\t-\t Copies <src> to <dst>")
    print("exit or quit\t-\t Exits the program")

def annotate_trace(trace_output: str):
    lines = trace_output.splitlines()
    annotated = []
    
    for line in lines:
        if "execve(" in line:
            annotated.append("\n--- PROGRAM START ---")
        if "openat(" in line and '"/lib' in line:
            annotated.append("\n--- LOADING SHARED LIBRARIES ---")
        if "getdents64" in line:
            annotated.append("\n--- READING DIRECTORY CONTENTS ---")
        if "write(1" in line:
            annotated.append("\n--- WRITING OUTPUT TO STDOUT ---")
        if "exit_group" in line:
            annotated.append("\n--- PROGRAM EXIT ---")
        annotated.append(line)
    return "\n".join(annotated)
    


def trace_command(cmd_line: str):
    args = shlex.split(cmd_line)
    
    #If user input is empty, try again
    if not args:
            return
            
    #Try check for specific builtins (cd, pwd). //ADD ANY ADDITIONAL COMMANDS HERE// 
    try:
        if args[0].lower() == "cd":
            try:
                before = os.getcwd()
                os.chdir(args[1])
                after = os.getcwd()
                if before == after: # If before == after, then directory didn't change
                    print(f"No directory {args[1]} exists")
                else:
                    print(f"Changed directory to {args[1]}")
            except IndexError:
                print("Usage: cd <directory>")

            return 
        if args[0].lower() == "pwd":
            print(os.getcwd())
            return
        if args[0].lower() == "cat":
                if len(args) < 2:
                    print("Usage: cat <file>")
                    return
                try:
                    with open(args[1], "r") as f:
                            print(f.read())
                except FileNotFoundError:
                    print(f"File not found: {args[1]}")
                return
        if args[0].lower() == "cp":
            if len(args) < 3:
                print("Usage: cp <src> <dst>")
                return
            try:
                shutil.copy(args[1], args[2])
                print(f"Copied {args[1]} -> {args[2]}")
            except FileNotFoundError:
                print(f"File not found: {args[1]}")
            return
    #Catch exception if user input is not a valid command
    except FileNotFoundError as e:
        print(f"Invalid directory: {args[1]}")
        return
        
    #Try check for executables
    try:
        
        #Checks each directory in $PATH. Returns the full path of the first match if found. 
        #If user input is not a valid executable, returns None and prints the invalid command
        if shutil.which(args[0]) is None:
            print(f"Invalid command: {args[0]}")
            return
        full_cmd = ["strace", "-f", "-tt", "-T"] + args


        #Store strace output
        result = subprocess.run(
            full_cmd,
            text=True,
            capture_output=True
        )
        
        #Print normal output
        print("=== STDOUT ===")
        print(result.stdout)

        #Print strace output
        print("=== SYSCALL TRACE ===")
        annotated = annotate_trace(result.stderr)
        print(annotated)
    except FileNotFoundError as e:
        print(f"invalid command: {e.filename}")

def main():
    print("Trace Shell (Linux): Enter 'quit' or 'exit' to exit the program.")
    print("For a list of supported builtins, enter 'help'.")
    while True:
        cmd = input("trace> ")
        if cmd.lower() in ("exit", "quit"):
            break
        if cmd.lower() in ("help"):
            help_menu()
            continue
        trace_command(cmd)
        

if __name__ == "__main__":
    main()
