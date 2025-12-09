import shlex
import subprocess
import shutil
import os


##Finish help menu
def help_menu():
    print("cd <directory>\t-\tChanges the current working directory to <directory> ('..' moves backwards)")
    print("ls\t-\tPrints the contents of the current working directory")
    print("pwd\t-\tPrints the current working directory")
    print("mkdir\t-\tCreates <directory>")
    print("rmdir\t-\tRemoves <directory> only if it is empty")
    print("mv <src> <dst>\t-\tMoves <src> to <dst>")
    print("cat <file>\t-\tPrints the contents of <file>")
    print("touch <file>\t-\tCreates <file>, if it already exists, then update its date modified")
    print("cp <src> <dst>\t-\tCopies <src> to <dst>")
    print("mk <file>\t-\tCreates <file> only if it does not already exist")
    print("rm <file>\t-\tRemoves <file>")

    print("help\t-\t Prints this list of available commands")
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
            if len(args) < 2:
                print("Usage: cd <directory>")
                return

            if not os.path.exists(args[1]):
                print(f"No such directory: {args[1]}")
                return

            os.chdir(args[1])
            print(f"Changed directory to: {args[1]}")
            return
        if args[0].lower() == "ls":
            print("Current directory contents:")
            print(os.listdir(os.getcwd()))
            return
        if args[0].lower() == "pwd":
            print("Current working directory: ", os.getcwd())
            return
        if args[0].lower() == "mkdir":
            if len(args) < 2:
                print("Usage: mkdir <directory>")
                return

            if os.path.exists(args[1]):
                print(f"Directory already exists: {args[1]}")
            else:
                os.mkdir(args[1])
                print(f"Created directory: {args[1]}")

            return
        if args[0].lower() == "rmdir":
            if len(args) < 2:
                print("Usage: rmdir <directory>")
                return

            if not os.path.exists(args[1]):
                print(f"Directory does not exist: {args[1]}")
                return

            if len(os.listdir(args[1])) == 0:
                os.rmdir(args[1])
                print(f"Directory removed: {args[1]}")
            else:
                print(f"Directory not empty: {args[1]}")

            return
        if args[0].lower() == "mv":
            if len(args) < 3:
                print("Usage: mv <src> <dst>")
                return

            if not os.path.exists(args[1]):
                print(f"File not found: {args[1]}")
                return

            if not os.path.exists(args[2]):
                print(f"No such directory: {args[2]}")
                return

            shutil.move(args[1], args[2])
            print(f"Moved {args[1]} -> {args[2]}")
            return
        if args[0].lower() == "cat":
            if len(args) < 2:
                print("Usage: cat <file>")
                return

            try:
                with open(args[1], "r") as file:
                    print(file.read())
                    file.close()
            except FileNotFoundError:
                print(f"File not found: {args[1]}")

            return
        if args[0].lower() == "touch":
            if len(args) < 2:
                print("Usage: touch <file>")
                return
            if not os.path.exists(args[1]):
                with open(args[1], "x"):
                    os.utime(args[1], None)
                    print(f"{args[1]} created")
                return
            os.utime(args[1], None)
            print(f"Touched: {args[1]}")
            return
        if args[0].lower() == "cp":
            if len(args) < 3:
                print("Usage: cp <src> <dst>")
                return

            if not os.path.exists(args[1]):
                print(f"File not found: {args[1]}")
                return

            if not os.path.exists(args[2]):
                print(f"No such directory: {args[2]}")
                return

            shutil.copy(args[1], args[2])
            print(f"Copied {args[1]} -> {args[2]}")
            return
        if args[0].lower() == "mk":
            if len(args) < 2:
                print("Usage: mk <file>")
                return
            if os.path.exists(args[1]):
                print(f"File already exists: {args[1]}")
                return
            open(args[1], "x").close()
            print(f"Created file: {args[1]}")
            return
        if args[0].lower() == "rm":
            if len(args) < 2:
                print("Usage: rm <file>")
                return
            if not os.path.exists(args[1]):
                print(f"File does not exist: {args[1]}")
                return
            os.remove(args[1])
            print(f"File removed: {args[1]}")


    #Catch exception if user input is not a valid command
    except FileNotFoundError:
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
        print(f"Invalid command: {e.filename}")

def main():
    print("Trace Shell (Linux): Enter 'quit' or 'exit' to exit the program.")
    print("For a list of supported builtins, enter 'help'.")
    while True:
        cmd = input("trace> ")
        if len(cmd) == 0:
            continue
        if cmd.lower() in ("exit", "quit"):
            break
        if cmd.lower() in "help":
            help_menu()
            continue
        trace_command(cmd)
        

if __name__ == "__main__":
    main()
