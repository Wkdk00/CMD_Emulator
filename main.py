import tkinter as tk
import os
import re

class TerminalEmulator:
    def __init__(self):
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
    
    def expand_variables(self, text):
        return re.sub(r'\$(\w+)', lambda m: os.getenv(m.group(1)) or m.group(0), text)
    
    def on_key_press(self, event):
        if event.keysym == 'BackSpace':
            cursor_pos = self.text_area.index(tk.INSERT)
            if self.text_area.compare(cursor_pos, "<=", self.start_index):
                return "break"
        return None
    
    def execute_command(self, event):
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
        elif cmd[0] == "ls":
            self.text_area.insert(tk.END, " ".join(cmd) + "\n")
        elif cmd[0] == "cd":
            self.text_area.insert(tk.END, " ".join(cmd) + "\n")
        else:
            self.text_area.insert(tk.END, "Wrong command!\n")
        
        self.text_area.insert(tk.END, self.prompt)
        self.text_area.mark_set(tk.INSERT, tk.END)
        self.text_area.see(tk.END)
        self.start_index = self.text_area.index("end-1c")
        return "break"
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    terminal = TerminalEmulator()
    terminal.run()
