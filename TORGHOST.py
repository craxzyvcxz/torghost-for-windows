import tkinter as tk
from tkinter import messagebox
import winreg as reg
import subprocess
import time
import os

class VPN012:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tor Ghost (windows edtion no one made it so i made it) VPN")
        self.root.geometry("520x420")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)
        
        self.is_on = False
        self.tor_process = None
        
        
        self.show_instruction_label()
        
        
        tk.Label(self.root, text="tor ghost VPN", font=("Arial", 26, "bold"), fg="#00ff41", bg="#0a0a0a").pack(pady=15)
        
        self.status_label = tk.Label(self.root, text="TOR: OFF", 
                                     font=("Arial", 24, "bold"), fg="red", bg="#0a0a0a")
        self.status_label.pack(pady=20)
        
        self.toggle_btn = tk.Button(self.root, text="TURN ON Tor ghost VPN", 
                                    font=("Arial", 15, "bold"), bg="#00cc00", fg="black", 
                                    width=28, height=3, command=self.toggle_vpn)
        self.toggle_btn.pack(pady=25)
        
        self.instruction_label = tk.Label(self.root, 
            text="Before using Tor ghost VPN you have to put tor.exe in the same folder.\n"
                 "If you don't have it:\n"
                 "1. Install Tor Browser\n"
                 "2. Go to search bar and type \"tor.exe\"\n"
                 "3. Copy the tor.exe file into this folder\n"
                 "4. Open tor.exe → wait until it says Bootstrapped 100%\n"
                 "5. Close this script and reopen it",
            font=("Arial", 10), fg="#aaaaaa", bg="#0a0a0a", justify="left", wraplength=480)
        self.instruction_label.pack(pady=20, padx=20)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def show_instruction_label(self):
        
        tor_path = "tor.exe"
        if os.path.exists(tor_path):
            try:
                self.tor_process = subprocess.Popen([tor_path], creationflags=subprocess.CREATE_NO_WINDOW)
                print("[012 VPN] tor.exe auto-started from same folder")
                time.sleep(4)
            except:
                pass
        else:
            print("[tor ghost VPN] tor.exe not found in folder")
    
    def set_proxy(self, enable):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                              r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                              0, reg.KEY_SET_VALUE)
            if enable:
                reg.SetValueEx(key, "ProxyEnable", 0, reg.REG_DWORD, 1)
                reg.SetValueEx(key, "ProxyServer", 0, reg.REG_SZ, "socks=127.0.0.1:9050")
            else:
                reg.SetValueEx(key, "ProxyEnable", 0, reg.REG_DWORD, 0)
                try:
                    reg.DeleteValue(key, "ProxyServer")
                except:
                    pass
            reg.CloseKey(key)
            subprocess.run(['ipconfig', '/flushdns'], creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL)
            return True
        except:
            messagebox.showerror("Error", "Run tor ghost VPN as Administrator!")
            return False
    
    def toggle_vpn(self):
        if not self.is_on:
            if self.set_proxy(True):
                self.is_on = True
                self.status_label.config(text="Tor ghost VPN: ON ", fg="#00ff41")
                self.toggle_btn.config(text="TURN OFF TOR GHOST VPN", bg="#cc0000")
                messagebox.showinfo("Tor ghost VPN", "System traffic forced through Tor!\nCheck your IP now.")
        else:
            if self.set_proxy(False):
                self.is_on = False
                self.status_label.config(text="TOR: OFF", fg="red")
                self.toggle_btn.config(text="TURN ON TOR GHOST VPN", bg="#00cc00")
                messagebox.showinfo("TOR GHOST VPN", "Normal connection restored.")
    
    def on_close(self):
        if self.is_on:
            self.set_proxy(False)
        if self.tor_process:
            try:
                self.tor_process.terminate()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    print("Starting Torghost VPN...")
    VPN012()