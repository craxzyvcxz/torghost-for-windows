import tkinter as tk
from tkinter import messagebox, simpledialog
import winreg as reg
import subprocess
import time
import os
import threading

class TorGhostVPN:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tor Ghost VPN v2.0 - Windows Edition")
        self.root.geometry("560x520")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)

        self.is_on = False
        self.tor_process = None
        self.rotate_thread = None
        self.stop_rotate = False
        self.killswitch_active = False

        self.show_instruction_and_start_tor()

        
        tk.Label(self.root, text="TOR GHOST VPN v2.0", 
                 font=("Arial", 28, "bold"), fg="#00ff41", bg="#0a0a0a").pack(pady=15)

        
        self.status_label = tk.Label(self.root, text="TOR: OFF", 
                                     font=("Arial", 26, "bold"), fg="red", bg="#0a0a0a")
        self.status_label.pack(pady=15)

        
        self.toggle_btn = tk.Button(self.root, text="TURN ON TOR GHOST VPN",
                                    font=("Arial", 16, "bold"), bg="#00cc00", fg="black",
                                    width=30, height=3, command=self.toggle_vpn)
        self.toggle_btn.pack(pady=20)

        
        self.killswitch_btn = tk.Button(self.root, text="ENABLE KILL SWITCH",
                                        font=("Arial", 12, "bold"), bg="#ff8800", fg="white",
                                        width=25, height=2, command=self.toggle_killswitch)
        self.killswitch_btn.pack(pady=8)

        
        self.rotate_btn = tk.Button(self.root, text="ROTATE TOR CIRCUIT",
                                    font=("Arial", 12, "bold"), bg="#0088ff", fg="white",
                                    width=25, height=2, command=self.start_rotation)
        self.rotate_btn.pack(pady=8)

        
        self.instruction_label = tk.Label(self.root,
            text="Make sure tor.exe is in the same folder as this script.\n"
                 "Kill Switch: If Tor dies, your internet gets cut immediately.\n"
                 "Rotate: Changes your Tor exit node on demand or automatically.",
            font=("Arial", 9), fg="#aaaaaa", bg="#0a0a0a", justify="left", wraplength=500)
        self.instruction_label.pack(pady=25, padx=20)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def show_instruction_and_start_tor(self):
        tor_path = "tor.exe"
        if os.path.exists(tor_path):
            try:
                self.tor_process = subprocess.Popen([tor_path], 
                                                    creationflags=subprocess.CREATE_NO_WINDOW)
                print("[TorGhost v2.0] tor.exe auto-started")
                time.sleep(5)  
            except Exception as e:
                print(f"[Error] Failed to start tor.exe: {e}")
        else:
            print("[TorGhost v2.0] tor.exe not found in folder!")

    def set_proxy(self, enable):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                              0, reg.KEY_SET_VALUE | reg.KEY_QUERY_VALUE)

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

            subprocess.run(['ipconfig', '/flushdns'], 
                           creationflags=subprocess.CREATE_NO_WINDOW, 
                           stdout=subprocess.DEVNULL)
            return True
        except Exception as e:
            messagebox.showerror("Admin Rights Required", 
                                 "Run Tor Ghost VPN as Administrator!\n\nError: " + str(e))
            return False

    def is_tor_alive(self):
        if not self.tor_process:
            return False
        return self.tor_process.poll() is None

    def kill_internet(self):
        try:
            subprocess.run('netsh interface set interface "Wi-Fi" admin=disabled', shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run('netsh interface set interface "Ethernet" admin=disabled', shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            print("[KILL SWITCH] Internet killed!")
        except:
            pass

    def restore_internet(self):
        try:
            subprocess.run('netsh interface set interface "Wi-Fi" admin=enabled', shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run('netsh interface set interface "Ethernet" admin=enabled', shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

    def toggle_killswitch(self):
        if not self.is_on:
            messagebox.showwarning("Kill Switch", "Turn ON the VPN first!")
            return

        self.killswitch_active = not self.killswitch_active
        if self.killswitch_active:
            self.killswitch_btn.config(text="KILL SWITCH: ACTIVE", bg="#ff0000")
            messagebox.showinfo("Kill Switch", "Kill Switch ENABLED\nIf Tor dies → Internet will be cut!")
        else:
            self.killswitch_btn.config(text="ENABLE KILL SWITCH", bg="#ff8800")
            messagebox.showinfo("Kill Switch", "Kill Switch disabled.")

    def monitor_tor(self):
        while self.is_on and self.killswitch_active:
            if not self.is_tor_alive():
                print("[KILL SWITCH TRIGGERED] Tor died → Killing internet!")
                self.kill_internet()
                messagebox.showerror("KILL SWITCH IS ON", 
                                     "Tor process died!\nInternet has been disconnected for your safety.")
                self.toggle_vpn()  # turn off vpn
                break
            time.sleep(3)

    def toggle_vpn(self):
        if not self.is_on:
            if self.set_proxy(True):
                self.is_on = True
                self.status_label.config(text="TOR GHOST VPN: ON", fg="#00ff41")
                self.toggle_btn.config(text="TURN OFF TOR GHOST VPN", bg="#cc0000")
                messagebox.showinfo("Success", "System traffic forced through Tor!\nYou are now ghosting ")

                # Start kill switch monitor if enabled
                if self.killswitch_active:
                    self.rotate_thread = threading.Thread(target=self.monitor_tor, daemon=True)
                    self.rotate_thread.start()
        else:
            if self.set_proxy(False):
                self.is_on = False
                self.status_label.config(text="TOR: OFF", fg="red")
                self.toggle_btn.config(text="TURN ON TOR GHOST VPN", bg="#00cc00")
                self.stop_rotate = True
                messagebox.showinfo("Tor Ghost VPN", "Normal connection restored.")

    def start_rotation(self):
        if not self.is_on:
            messagebox.showwarning("Not Active", "Turn ON the VPN first!")
            return

        
        num_str = simpledialog.askstring("Rotate Count", 
            "How many rotates?\n(Enter 'infinite' for endless rotation)", 
            initialvalue="infinite")

        if not num_str:
            return

        
        interval_str = simpledialog.askstring("Rotate Interval", 
            "How many seconds till each rotate?", 
            initialvalue="30")

        try:
            interval = int(interval_str)
            if interval < 5:
                interval = 5
        except:
            interval = 30

        self.stop_rotate = False

        if num_str.lower() == "infinite":
            threading.Thread(target=self.infinite_rotate, args=(interval,), daemon=True).start()
            messagebox.showinfo("Rotation Started", f"Infinite rotation started!\nNew circuit every {interval} seconds.")
        else:
            try:
                count = int(num_str)
                threading.Thread(target=self.do_rotates, args=(count, interval), daemon=True).start()
                messagebox.showinfo("Rotation Started", f"Will rotate {count} times.\nEvery {interval} seconds.")
            except:
                messagebox.showerror("Error", "Please enter a valid number or 'infinite'")

    def do_rotates(self, count, interval):
        for i in range(count):
            if self.stop_rotate or not self.is_on:
                break
            self.new_tor_circuit()
            time.sleep(interval)

    def infinite_rotate(self, interval):
        while not self.stop_rotate and self.is_on:
            self.new_tor_circuit()
            time.sleep(interval)

    def new_tor_circuit(self):
        try:
            
            
            if self.tor_process:
                self.tor_process.terminate()
                time.sleep(2)
                self.tor_process = subprocess.Popen(["tor.exe"], 
                                                    creationflags=subprocess.CREATE_NO_WINDOW)
                print(f"[TorGhost] New circuit requested - Tor restarted")
        except:
            print("[TorGhost] Failed to rotate circuit")

    def on_close(self):
        self.stop_rotate = True
        if self.is_on:
            self.set_proxy(False)
        if self.tor_process:
            try:
                self.tor_process.terminate()
            except:
                pass
        self.restore_internet()  
        self.root.destroy()

if __name__ == "__main__":
    print("Starting Tor Ghost VPN v2.0...")
    print("Make sure you run this as Administrator!")
    TorGhostVPN()
