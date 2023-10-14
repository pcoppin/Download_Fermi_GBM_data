# Download Fermi GBM data

### Step 1:
Download the CTIME data from all bursts; by running:
`python Download_ctime.py`

This script requires access to the GRBweb MySQL database. As such, it is necessary to set:
- a username and password to allow an ssh connection to pub.icecube.wisc.edu
- the password for the 'grbweb-ro' user on the MySQL database

Dependencies: _PyMySQL_ and _sshtunnel_ need to be installed through pip to enable the script

Burst data will be stored by default in the folder _Bursts_.<br />
The data/folder structure is analoguous to that of the HEASARC archive.<br />
An alternative location can be chosen by setting the variable _Fermi_data_loc_.


### Step 2:
Identify the 2 or 3 subdetectors that were triggered by the burst, and with the smallest angular separation to the burst; by running:
`Select_detectors.py`

The output of this script is a text file _Detectors_to_use.txt_ containing per line:
- the name of the burst
- the name of one of the selected subdetectors

Dependencies: _astropy_ needs to be installed through pip to enable the script

### Step 3:
Download the TTE data from the selected subdetectors; by running:
`Download_tte.py`

Again, burst data will be stored by default in the folder _Bursts_;<br />
and the data/folder structure is analoguous to that of the HEASARC archive.
