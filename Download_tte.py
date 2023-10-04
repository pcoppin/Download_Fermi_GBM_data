#########################################################################################################################
# Download new TTE files for detectors which are significantly above their threshold (up-to-date to 03/2019)
#########################################################################################################################

from ftplib import FTP_TLS
import urllib.request
import re
import sys, os
import glob
import numpy as np

Fermi_data_loc = "Bursts"

ftp_webpage  = "heasarc.gsfc.nasa.gov"
ftp          = FTP_TLS(ftp_webpage, timeout=10000)
ftp.login("anonymous", "")
ftp.prot_p()

if( not os.path.isdir( Fermi_data_loc ) ):
    raise Exception("Fermi data not found on disk: {}".format(Fermi_data_loc))
    
Detectors_to_use = open("Detectors_to_use.txt", "r")

#TTE_files_on_disk = []
TTE_files_on_disk = sorted(glob.glob(Fermi_data_loc + "/20??/bn?????????/current/glg_tte_??_bn?????????_v??.fit"))
print("{:d} tte files found already".format(len(TTE_files_on_disk)))

for line in Detectors_to_use:
    trigger_name, detector = line.split()[:2]   
    year         = 2000 + int(trigger_name[2:4])
    OUTPUT_dir = Fermi_data_loc + "/" + str(year) + "/" + trigger_name + "/current/"
    TTE_string = "glg_tte_{}_{}_".format(detector, trigger_name)
    if( not any([TTE_string in TTE_file for TTE_file in TTE_files_on_disk]) ):
        data_webpage = "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/" + str(year) + "/" + trigger_name + "/current/"
        if( True ):
        #if( year==2014 ):
            page_source = urllib.request.urlopen(data_webpage).read().decode('utf-8')
            try:
                TTE_file_name =  re.search(r'(glg_tte_{}_{}_.*\.fit)">glg_tte'.format(detector, trigger_name), page_source).group(1)
            except:
                print("TTE file {} not found!".format(TTE_string))
            else:
                print("\tDownloading {}".format(TTE_file_name))
                sys.stdout.flush()
                loc_file  = "/" + str(year) + "/" + trigger_name + "/current/" + TTE_file_name
                file_path = Fermi_data_loc + loc_file
                try:
                    file      = open(file_path, 'wb')
                    ftp.retrbinary("RETR " + "/FTP/fermi/data/gbm/bursts" + loc_file, file.write)
                    file.close()
                except Exception as error:
                    os.system("rm {}".format(file_path))
                    raise error

ftp.quit()

