import tkinter as tk
import os
import re
import sys
import zipfile

class TerminalEmulator:
    def __init__(self, vfs_path, script_path):
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs = None
        self.current_vfs_path = "/"
        
        if os.path.exists(vfs_path):
            self.vfs = zipfile.ZipFile(vfs_path, 'r')
        
        self.root = tk.Tk()
        username = os.getenv('USER') or os.getenv('USERNAME')
        hostname = os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME')
        self.root.title(f"Эмулятор - [{username}@{hostname}]")
        
        self.text_area = tk.Text(self.root, bg='black', fg='white', insertbackground='white')
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        self.prompt = f"[{username}@{hostname}]$ "
        self.text_area.insert(tk.END, self.prompt)
        
        self.text_area.bind('<Return>', self.execute_command)
        self.text_area.bind('<Key>', self.on_key_press)
        
        self.start_index = self.text_area.index("end-1c")
        
        self.execute_startup_script()
    
    def execute_startup_script(self):
        if os.path.exists(self.script_path):
            with open(self.script_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#'):
                        self.text_area.insert(tk.END, line)
                        self.execute_command(None, line.strip())
    
    def expand_variables(self, text):
        return re.sub(r'\$(\w+)', lambda m: os.getenv(m.group(1)) or m.group(0), text)
    
    def on_key_press(self, event):
        if event.keysym == 'BackSpace':
            cursor_pos = self.text_area.index(tk.INSERT)
            if self.text_area.compare(cursor_pos, "<=", self.start_index):
                return "break"
        return None
    
    def get_vfs_listing(self, path):
        if not self.vfs:
            return "VFS not mounted\n"
        
        result = []
        for name in self.vfs.namelist():
            if name.startswith(path.lstrip('/')) and name != path.lstrip('/'):
                rel_path = name[len(path.lstrip('/')):].lstrip('/')
                if '/' in rel_path:
                    dir_name = rel_path.split('/')[0] + '/'
                    if dir_name not in result:
                        result.append(dir_name)
                else:
                    result.append(rel_path)
        return "\n".join(result) + "\n" if result else "\n"
    
    def conf_dump(self):
        config = {
            "vfs_path": self.vfs_path,
            "script_path": self.script_path,
            "prompt": self.prompt.strip(),
            "working_directory": os.getcwd(),
            "user": os.getenv('USER') or os.getenv('USERNAME'),
            "hostname": os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME'),
            "vfs_mounted": bool(self.vfs),
            "current_vfs_path": self.current_vfs_path
        }
        
        result = "Configuration dump:\n"
        for key, value in config.items():
            result += f"  {key}: {value}\n"
        return result
    
    def execute_command(self, event, command_line=None):
        if command_line is None:
            last_line_index = self.text_area.index("end-1c linestart")
            command_text = self.text_area.get(last_line_index, "end-1c")
            command_line = command_text[len(self.prompt):].strip()
        
        expanded_line = self.expand_variables(command_line)
        cmd = expanded_line.split()
        
        self.text_area.insert(tk.END, "\n")
        
        if not cmd:
            self.text_area.insert(tk.END, self.prompt)
            self.text_area.mark_set(tk.INSERT, tk.END)
            self.text_area.see(tk.END)
            self.start_index = self.text_area.index("end-1c")
            return "break"
        
        if cmd[0] == "exit" and len(cmd) == 1:
            self.root.quit()
        elif cmd[0] == "echo":
            self.text_area.insert(tk.END, " ".join(cmd[1:]) + "\n")
        elif cmd[0] == "ls":
            self.text_area.insert(tk.END, " ".join(cmd) + "\n")
        elif cmd[0] == "cd":
            self.text_area.insert(tk.END, " ".join(cmd) + "\n")
        elif cmd[0] == "conf-dump":
            self.text_area.insert(tk.END, self.conf_dump())
        else:
            self.text_area.insert(tk.END, "Wrong command!\n")
        
        self.text_area.insert(tk.END, self.prompt)
        self.text_area.mark_set(tk.INSERT, tk.END)
        self.text_area.see(tk.END)
        self.start_index = self.text_area.index("end-1c")
        return "break"
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self.vfs:
                self.vfs.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Wrong params count")
        sys.exit(1)
    
    vfs_path = sys.argv[1]
    script_path = sys.argv[2]
    
    terminal = TerminalEmulator(vfs_path, script_path)
    terminal.run()