#!/usr/bin/env python
# coding: utf-8

# Requires: pip install astropy

import numpy as np
import re
import sys, os
import glob

from astropy.io import fits

Fermi_data_loc = "Bursts"

def Angular_seperation(pos_1, pos_2, ra_dec=False, degrees=True):
    """
    Compute the angular seperation between point A & B on a sphere
    theta & phi can be arrays, allowing one function call to calculate the seperation between multiple points

    :type   pos_1: array or list
    :param  pos_1: (theta, phi) in spherical coordinates of point A OR (dec, ra)

    :type   pos_2: array or list
    :param  pos_2: (theta, phi) in spherical coordinates of point B OR (dec, ra)

    :type   ra_dec: boolean
    :param  ra_dec: False if pos_1/2 are in spherical coordinates, True if they are in ra & dec

    :type   degrees: boolean
    :param  degrees: False if pos_1/2 are in degrees, True if they are radians
    """
    def Spherical_to_cartesion(theta, phi):
        x = np.sin(theta)*np.cos(phi)
        y = np.sin(theta)*np.sin(phi)
        z = np.cos(theta)
        return x, y ,z
    
    if( degrees ):
        theta_1, phi_1 = np.radians(pos_1)
        theta_2, phi_2 = np.radians(pos_2)
    else:
        theta_1, phi_1 = np.array(pos_1)
        theta_2, phi_2 = np.array(pos_2)
    
    if( ra_dec ):
        theta_1 = 0.5*np.pi - theta_1
        theta_2 = 0.5*np.pi - theta_2
    
    x1, y1, z1 = Spherical_to_cartesion(theta_1, phi_1)
    x2, y2, z2 = Spherical_to_cartesion(theta_2, phi_2)
    inproduct = x1*x2+y1*y2+z1*z2
    inproduct = np.clip(inproduct, -1, 1) # Account for numerical precision
    ang_sep = np.arccos(inproduct)
    if( degrees ):
        return np.degrees(ang_sep)
    else:
        return ang_sep

burst_name_re = re.compile(r"/(bn.{9})/")

# Chosen by looking at the ctime light curves
Manually_selected_detectors = {"bn080905499": ('n3', 'n4', 'n6'),
                               "bn081024851": ('n3', 'n4', 'n5'),
                               "bn081209981": ('n7', 'n8', 'nb'),
                               "bn090227772": ('n0', 'n1', 'n2'),
                               "bn090617208": ('n0', 'n1', 'n3'),
                               "bn090621447": ('n6', 'n7'),
                               "bn090717111": ('n3', 'n7', 'n8'),
                               "bn090719063": ('n6', 'n7', 'n8'),
                               "bn090814368": ('n6', 'n9', 'na'),
                               "bn090819607": ('n6', 'n7', 'n8'),
                               "bn090907808": ('n6', 'n7', 'n9'),
                               "bn091012783": ('n9', 'na', 'nb'),
                               "bn091223191": ('n6', 'n7'),
                               "bn141022087": ('na', 'nb')}

# Numerical values taken from https://iopscience.iop.org/article/10.1088/0004-637X/702/1/791
Orientation_na_dets = {} # (azimuth, zenith) in spacecraft coordinates, in degrees
Orientation_na_dets[0]  = (45.9,  20.6) 
Orientation_na_dets[1]  = (45.1,  45.3)
Orientation_na_dets[2]  = (58.4,  90.2)
Orientation_na_dets[3]  = (314.9, 45.2)
Orientation_na_dets[4]  = (303.2, 90.3)
Orientation_na_dets[5]  = (3.4,   89.8)
Orientation_na_dets[6]  = (224.9, 20.4)
Orientation_na_dets[7]  = (224.6, 46.2)
Orientation_na_dets[8]  = (236.6, 90.0)
Orientation_na_dets[9]  = (135.2, 45.6)
Orientation_na_dets[10] = (123.7, 90.4)
Orientation_na_dets[11] = (183.7, 90.3)

detector_names = ["n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "na", "nb"]  


# ## Select detectors based on whether they triggered the NA detectors & their angular distance to the GRB
tcat_files = sorted(glob.glob(Fermi_data_loc + "/20??/bn?????????/current/glg_tcat_all_bn?????????_v??.fit"))

det_angles  = []
output_text = ""

a, b = [], []
for f in tcat_files:
    # Burst has abnormal high bg rate
    if( "bn131028096" in f ):
        print("Skipping bn131028096 due to abnormally high background rate")
        continue
    burst_name = burst_name_re.search(f).group(1)
    fitfile    = fits.open(f)
    PRIMARY    = fitfile[0]
    GRB        = {}
    GRB["trigger_timescale"]    = PRIMARY.header["TRIGSCAL"]  # Trigger time scale in ms
    GRB["detector_mask"]        = PRIMARY.header["DET_MASK"]  # Mask of detectors which triggered: n0 n1 n2 n3 n4 n5 n6 n7 n8 n9 na nb b0 b1
    
    detectors = []
    if( "PHI" in PRIMARY.header ):
        GRB["trigger_significance"] = PRIMARY.header["TRIG_SIG"]  # Significance of the trigger
        GRB["direction"]            = (PRIMARY.header["PHI"], PRIMARY.header["THETA"]) # In degrees in spacecrash coordinates

        for i, det in enumerate(Orientation_na_dets):
            if( GRB["detector_mask"][i]=="1" ):# or True ):
                ang_sep = Angular_seperation(Orientation_na_dets[det], GRB["direction"])
                det_angles.append(ang_sep)
                detectors.append( (detector_names[i], ang_sep) )        

        detectors = sorted(detectors, key=lambda x: x[1])
        if( burst_name in Manually_selected_detectors ):
            detectors = [(det, np.nan) for det in Manually_selected_detectors[burst_name]]
        for d in detectors[:3]:
            output_text += "{} {} {:8.3f} {:8.3f} {:8.3f}\n".format(burst_name, d[0], d[1], GRB["trigger_significance"], GRB["trigger_timescale"])
            a.append(d[1])
    
    else:
        if( burst_name in Manually_selected_detectors ):
            detectors = Manually_selected_detectors[burst_name]
        else:
            for i, det in enumerate(detector_names):
                if( GRB["detector_mask"][i]=="1" ):
                    detectors.append( det )      
        for d in detectors[:3]:
            output_text += "{} {}\n".format(burst_name, d)

output_text_file = open("Detectors_to_use.txt", "w")
output_text_file.write(output_text)
output_text_file.close()

