#########################################################################################################################
# Download the new ctime files for all GRBs
#########################################################################################################################
### Execute with the command below, to re-run the script if it fails. Also set the passwords before running
# function retry { python3 Download_ctime.py && echo "success" || (echo "fail" && sleep 20 && retry) }; retry

# Requires: pip install PyMySQL  and   pip install pip install sshtunnel

from ftplib import FTP_TLS
from sshtunnel import SSHTunnelForwarder
import urllib.request
import pymysql as MySQLdb
import re
import sys, os
import glob

ssh_user = 
ssh_pass = 
SQL_pass = 
Fermi_data_loc = "Bursts"

server = SSHTunnelForwarder(('pub.icecube.wisc.edu', 22), ssh_password=ssh_pass, ssh_username=ssh_user, remote_bind_address=('dbs3.icecube.wisc.edu', 3306))
server.start()
db = MySQLdb.connect(host='localhost', port=server.local_bind_port, user='grbweb-ro', passwd=SQL_pass)
c  = db.cursor()
c.execute("USE grbweb2")
c.execute("SELECT trigger_name, GRB_name_Fermi FROM Fermi_GBM;")
GBM_trigger_and_GRB_names_Fermi = list(c.fetchall())
GBM_trigger_and_GRB_names_Fermi.sort(key=lambda x: x[0])
GBM_trigger_and_GRB_names_Fermi.sort(key=lambda x: x[1])
GBM_trigger_names, GRB_names_Fermi = list(zip(*GBM_trigger_and_GRB_names_Fermi))
c.close()
db.close()
server.stop()
server.close()

#GBM_trigger_names = ["bn091024380"]
#GRB_names_Fermi = ["bn091024380"]

ftp_webpage  = "heasarc.gsfc.nasa.gov"
ftp          = FTP_TLS(ftp_webpage, timeout=1)
ftp.login("anonymous", "")
#ftp.set_pasv(False)
ftp.prot_p()

if( not os.path.isdir( Fermi_data_loc ) ):
    raise Exception("Fermi data not found on disk: {}".format(Fermi_data_loc))

ctime_files_on_disk = glob.glob(Fermi_data_loc + "/20??/bn?????????/current/glg_ctime_??_bn?????????_v??.pha")
tcat_files_on_disk = glob.glob(Fermi_data_loc + "/20??/bn?????????/current/glg_tcat_all_bn?????????_v??.fit")
print("{:d} ctime files found already ({:d} bursts)".format(len(ctime_files_on_disk), int(len(ctime_files_on_disk)/14)) )
for trigger_name, GRB_name_Fermi in zip(GBM_trigger_names, GRB_names_Fermi):
    if( sum([trigger_name in fit_file for fit_file in ctime_files_on_disk])!=14 or sum([trigger_name in fit_file for fit_file in tcat_files_on_disk])==0 ):
        year         = 2000 + int(trigger_name[2:4])
        data_webpage = "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/" + str(year) + "/" + trigger_name + "/current/"
        if( True ):#year in range(2019, 2020) ):
            try:
                page_source = urllib.request.urlopen(data_webpage).read().decode('utf-8')
            except:
                print("\t\t{}, {} not found on Fermi ftp server despite being a 'Fermi-GBM' GRB in the GRBweb catalogue?!".format(trigger_name, GRB_name_Fermi))
            else:
                try:
                    ctime_file_names = re.findall(r'(glg_ctime_.*\.pha)">glg_ctime', page_source)
                    tcat_file_names = re.findall(r'(glg_tcat_.*\.fit)">glg_tcat', page_source)
                except:
                    print("\t\tNo ctime or tcat files available/found for %s"%GRB_name_Fermi)
                else:
                    print("Downloading the ctime & tcat files for %s"%GRB_name_Fermi)
                    sys.stdout.flush()
                    output_dir = Fermi_data_loc + "/" + str(year) + "/" + trigger_name + "/current/"
                    if( not os.path.isdir( output_dir ) ):
                        os.makedirs( output_dir )
                    #for file_name in (ctime_file_names + tcat_file_names):
                    for file_name in (tcat_file_names+ctime_file_names):
                        print("\tDownloading {}".format(file_name))
                        sys.stdout.flush()
                        loc_file  = "/" + str(year) + "/" + trigger_name + "/current/" + file_name
                        file_path = Fermi_data_loc + loc_file
                        try:
                            file      = open(file_path, 'wb')
                            ftp.retrbinary("RETR " + "/FTP/fermi/data/gbm/bursts" + loc_file, file.write)
                            file.close()
                        except Exception as error:
                            os.system("rm {}".format(file_path))
                            raise error

ftp.quit()
