
import paramiko, time, socket, re, uuid, sys, os, getpass
import PySimpleGUI as sg
import clipboard


class switch_lookup:
    ssh = None
    def __init__(self, mac="", ip=""):
        self.mac = mac
        self.ip = ip

    def login(self, usr, pwd, ip):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=usr, password=pwd)
            self.ssh = ssh
            channel = ssh.invoke_shell()
            out = channel.recv(9999)
            return channel, out
        except:
            print("something went wrong")
    def close_connection(self):
        self.ssh.close()

    def ssh_cmd(self,channel, out, command):
        #print("ssh_cmd")
        channel.send(command)
        #this while loop makes sure the script won't move on until the output is fully spit out of the terminal so we don't have any information loss
        while not channel.recv_ready():
            time.sleep(1)
        #basically this takes the last 9999 characters displayed on the terminal. Later it is decode into ascii characters for readability.
        out = channel.recv(9999)

        #time.sleep(1)
        return out

    def get_info(self, out, channel):
        # print("get info")
        # out = channel.recv(9999)
        # print("out")
        out = self.ssh_cmd(channel, out, 'terminal length 0\n')

        out = self.ssh_cmd(channel, out, 'show ip device tracking all\n')
        #print(out.decode("ascii"))
        i = 0
        capture_text = False
        info_list = []
        for o in out.decode("ascii").splitlines():
           # print(o, i)
            i += 1
            if i == 9:
                capture_text = True    

            if 'Total number' in o:
                capture_text = False

            if capture_text and '-' not in o:
                info_list.append(o)
        return info_list


    def mac_in(self, mac_list):
        user_mac = self.mac
        info = ": not found"
        user_mac = user_mac.lower()
        #print(user_mac)
        for t in mac_list:
            if user_mac in t:
                #print(t)
                info = t
        return_list = []
        for i in info.split():
            print(i)
            return_list.append(i)
        return return_list

    
    def ip_in(self, ip_list):
        user_ip = self.ip
        info = None
        user_ip = user_ip.lower()
        #print(user_ip)
        for t in ip_list:
            if user_ip in t:
               # print(t)
                info = t
        return info






output_list = []
for i in range(100):
    output_list.append('10.10.25.' + str(i))


layout = [
    [sg.Text('Switch', size=(25,2)), sg.T(' ' * 24),sg.Text('Search Parameter',size=(25,2))],
    [sg.InputCombo(values=output_list, size=(25,1), key='_ADDRESS_'), sg.T(' ' * 25), sg.Input('Enter search value', size=(25,1), key='_SEARCH_')],
    [sg.Button('Search', size=(20,1))],
    [sg.Text('Error Handling'), sg.Text('', size=(50,1),key='_OUT_')],
    [sg.Text('MAC' + ' ' * 10), sg.Text('', size=(25,1), key='_MAC_', text_color="black"), sg.Button('<-copy MAC')],
    [sg.Text('IP' + ' ' * 13), sg.Text('', size=(25,1), key='_IP_'), sg.Button('<-copy IP')],
    [sg.Text('Status' + ' ' * 8), sg.Text('',size=(25,1), key='_STATUS_')],
    [sg.Text('Port' + ' ' * 11), sg.Text('',size=(25,1), key='_PORT_') ],
    [ sg.Text('VLAN #' + ' ' * 7), sg.Text('',size=(25,1), key='_VLAN_')],
    [sg.T(' ' * 120), sg.Button('  Exit  ')]





]

window = sg.Window('Window Title', layout)
window.Size = 250,250
window.Refresh()

while True:                 # Event Loop
  mac_address = ""
  ip_address = ""
  event, values = window.Read()  
  print("EVENTS: ",event)
  print("VALUES: ",values)
  if event is None or event == '  Exit  ':  
      break
  elif event == 'Search':
    try:
        search_param = values.get('_SEARCH_')
        search_param = str(search_param)
        #search_param = lower(search_param)

        address_param = values.get('_ADDRESS_')
        address_param = str(address_param)
        #address_param = lower(address_param)
        #   print("SP: ", search_param)
        device_lines = []    
        
        sw = switch_lookup(mac=search_param)    

        ch, out = sw.login('matthewabbott','test',address_param)
        print("logging in... ")
        device_lines = sw.get_info(out, ch)
        tmp_list = sw.mac_in(device_lines)
        if len(tmp_list) == 5:
            ip_address = tmp_list[0]
            #ip_address.replace(" ", "")
            mac_address = tmp_list[1]
            #mac_address.replace(" ","")
            vlan_num = tmp_list[2]
            #vlan_num.replace(" ","")
            port_name = tmp_list[3]
            #port_name.replace(" ","")
            lease_status = tmp_list[4]
            #lease_status.replace(" ","")

            window.Element('_IP_').Update(ip_address)
            window.Element('_MAC_').Update(mac_address)
            window.Element('_VLAN_').Update(vlan_num)
            window.Element('_PORT_').Update(port_name)
            window.Element('_STATUS_').Update(lease_status)
        



        else:
            window.Element('_OUT_').Update(search_param + ": not found")
        
        print("closing connection...")
        sw.close_connection()
    except:
        window.Element('_OUT_').Update("Error could not connect to: " + str(address_param))


    
  elif event == '<-copy MAC':
      clipboard.copy(mac_address)
  elif event == '<-copy IP':
      clipboard.copy(ip_address)

      


window.Close()
