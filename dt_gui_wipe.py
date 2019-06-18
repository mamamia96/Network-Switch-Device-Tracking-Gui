# TO DO:
# be able to put in address manually. Just run seperate function if len(_ADDRESS_) is less than 14
# change get_info function to work with newer switches 'show device-tracking database' instead of 'show ip device tracking all'
# prettify username and password entry
# custom taskbar icon
import paramiko, time, socket, re, uuid, sys, os, xlrd, clipboard
import PySimpleGUI as sg

class switch_lookup:
    ssh = None
    def __init__(self, mac="", ip=""):
        self.mac = mac
        self.ip = ip

    def login(self, usr, pwd, ip):
        print("ADDRESS: ",ip)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=usr, password=pwd)
            self.ssh = ssh
            channel = ssh.invoke_shell()
            out = channel.recv(9999)
            return channel, out
        except:
            print("I tried address: ",ip)
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
        
        out = self.ssh_cmd(channel, out, 'show device-tracking database | b Network\n')
        out = out.decode("ascii")
        capture_bool = False
        info_list = []
        for x in out.splitlines():
            #print("X: ",x)
            if not capture_bool:
                for ele in x.split():
                    if ele == 'left':
                        capture_bool = True
            else:
                if not x:
                    capture_bool = False
                else:
                    info_list.append(x)
        #print("INFOLIST: ",info_list)
        
        return info_list


    def mac_in(self, mac_list):
        user_mac = self.mac
        info = ": not found"
        user_mac = user_mac.lower()
        user_mac = user_mac.replace(':','')
        user_mac = user_mac.replace('.','')
        user_mac = user_mac.replace('-','')
        #print(user_mac)
        for t in mac_list:
            if user_mac in t:
                print(t)
                info = t
        return_list = []
        for i in info.split():
            print(i)
            return_list.append(i)
        return return_list


    def add_splitter(self, s):
        address = ""
        add_bool = False
        for ele in s:
            if ele == ':':
                add_bool = True
                continue
            
            if add_bool:
                address += ele
        
        address = address.replace(' ','')

        return address


class data:
    def __init__(self):
        print("reading excel data...")
    
    def cty_splicer(self,s):
        name = ""
        for i in range(4):
            name += s[i]

        return name

    def info_splicer(self,s):
        info = ""
        for i in range(5,len(s)):
            info += s[i]
            

        return info

    def sheet_create(self):
        try:
            loc = ("cisco_devices.xls") 
  
            # To open Workbook 
            wb = xlrd.open_workbook(loc) 
            sheet = wb.sheet_by_index(0) 
            print("accessing: ", loc)
            return sheet
        except:
            print("could not find: ", loc)
            return None

    def dict_create(self):
        city_dict = {}
        city_names = []
        sheet = self.sheet_create()
        if sheet != None:
            for i in range(357):
               # print(sheet.cell_value(i,0))
                #print(sheet.cell_value(i,0) + ": " + sheet.cell_value(i,1))
                tmp = self.cty_splicer(sheet.cell_value(i,0))
               # print(tmp)
                city_names.append(tmp)
                
                the_scoop = self.info_splicer(sheet.cell_value(i,0)) + ": " + sheet.cell_value(i,1)

                if city_dict.get(tmp) == None:
                    city_dict[tmp] = [the_scoop]
                else:
                    city_dict[tmp].append(the_scoop)
            
            return city_dict
        else:
            return {}



# d = data()
# cty_names = []
# cty_dict = d.dict_create()
# for ele in cty_dict:
#     cty_names.append(ele)


layout = [
    [sg.Text('Switch', size=(25,2)), sg.T(' ' * 50),sg.Text('Search Parameter',size=(25,2))],
    [sg.Text('City              '), sg.InputCombo(values=['redacted'], change_submits=True, key='_CTY_',size=(5,1), readonly=True)],
    [sg.Text('Switch Name'),sg.InputCombo(values=['enter ip here'], size=(30,1), key='_ADDRESS_'), sg.T(' ' * 25), sg.Input('Enter search value', size=(25,1), key='_SEARCH_')],
    [sg.Button('Search', size=(20,1))],
    [sg.Text('Error Handling'), sg.Text('', size=(50,1),key='_OUT_')],
    [sg.Text('MAC' + ' ' * 10), sg.Text('', size=(25,1), key='_MAC_', text_color="black"), sg.Button('<-copy MAC')],
    [sg.Text('IP' + ' ' * 13), sg.Text('', size=(25,1), key='_IP_'), sg.Button('<-copy IP')],
    [sg.Text('Status' + ' ' * 8), sg.Text('',size=(25,1), key='_STATUS_')],
    [sg.Text('Port' + ' ' * 11), sg.Text('',size=(25,1), key='_PORT_') ],
    [ sg.Text('VLAN #' + ' ' * 7), sg.Text('',size=(25,1), key='_VLAN_')],
    [sg.Text('username'), sg.Text(' ' * 60),sg.Text('password')],
    [sg.Input('', key='_USR_'), sg.Input('', key='_PWD_', password_char='*********')],
    [sg.T(' ' * 120), sg.Button('  Exit  ')]





]

window = sg.Window('Switch Info Lookup', layout)
window.Size = 250,250
window.Refresh()

while True:                 # Event Loop
  mac_address = ""
  ip_address = ""
  event, values = window.Read()
  #window.Element('_ADDRESS_').Update(values=cty_dict.get(values.get('_CTY_')))
#   print("EVENTS: ",event)
#   print("VALUES: ",values)
  if event is None or event == '  Exit  ':  
      break
  elif event == 'Search':
    try:
        print("SEARCHING")
        search_param = values.get('_SEARCH_')
        search_param = str(search_param)
        #search_param = lower(search_param)

        sw = switch_lookup(mac=search_param)

        address_param = values.get('_ADDRESS_')
        address_param = str(address_param)
        if len(address_param) > 16:
            address_param = sw.add_splitter(address_param)
        
        #address_param = lower(address_param)
        #   print("SP: ", search_param)
        device_lines = []  
        print("address: ",address_param)  
        
        

        ch, out = sw.login(values.get('_USR_'),values.get('_PWD_'),address_param)
        print("logging in to ",address_param)
        device_lines = sw.get_info(out, ch)
        tmp_list = sw.mac_in(device_lines)

        if len(tmp_list) > 5:
            ip_address = tmp_list[1]

            mac_address = tmp_list[2]

            vlan_num = tmp_list[4]

            port_name = tmp_list[3]

            lease_status = tmp_list[7]


            window.Element('_IP_').Update(ip_address)
            window.Element('_MAC_').Update(mac_address)
            window.Element('_VLAN_').Update(vlan_num)
            window.Element('_PORT_').Update(port_name)
            window.Element('_STATUS_').Update(lease_status)
        



        if mac_address == None:
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
