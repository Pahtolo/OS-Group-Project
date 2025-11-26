import shlex
import subprocess
import shutil

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
    try:
        args = shlex.split(cmd_line)
        if not args:
            return
        if shutil.which(args[0]) is None:
            print(f"invalid command: {args[0]}")
            return
        full_cmd = ["strace", "-f", "-tt", "-T"] + args

        result = subprocess.run(
            full_cmd,
            text=True,
            capture_output=True
        )

        print("=== STDOUT ===")
        print(result.stdout)

        print("=== SYSCALL TRACE ===")
        annotated = annotate_trace(result.stderr)
        print(annotated)
    except FileNotFoundError as e:
        print(f"invalid command: {e.filename}")

def main():
    print("Trace Shell (Linux): Enter 'quit' or 'exit' to exit the program.")
    while True:
        cmd = input("trace> ")
        if cmd.lower() in ("exit", "quit"):
            break
        trace_command(cmd)

if __name__ == "__main__":
    main()
