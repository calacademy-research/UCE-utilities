
#/usr/bin/python

import os
import json

nex_headers = ('#NEXUS', 'begin', 'dimensions', 'format', 'matrix', ';', 'end', "\t")


UCE_list = []
for cur_filename in os.listdir('.'):
    #print cur_filename
    if cur_filename.endswith('.nexus'):
        #print cur_filename
        nexus_file = open(cur_filename, 'r')
        for cur_line in nexus_file:
            # if cur_line.find("angustus") > 0:
            #     print cur_line
            #     OTU = cur_line.split()
            #     print "first section:\'" + OTU[0] + "'"
            #     OTU = OTU[0]
            #     OTU = OTU.strip("'")
            #     print "OTU:\'" + OTU + "'"
            #print cur_line
            #if cur_line == 'uce*'
            #if cur_line.startswith("'uce"):
            if not cur_line.startswith(nex_headers):
                #print cur_line
                OTU = cur_line.split()
                #print OTU[0]
                OTU = OTU[0]
                OTU = OTU.strip("'")
                #print OTU
                # index_ = OTU.find('_')
                # OTU = OTU[ index_ + 1 : ]
                if OTU not in UCE_list:
                    UCE_list.append(OTU)
                    print "Appending: \'" + OTU + "\'"
                    # print OTU


# We now have all OTUs in a list.

prev_line = None
cur_species = None
species_to_OTU_dictionary = {}
for cur_line in UCE_list:
    #print cur_line
    # cur_line = cur_line.capitalize().strip()
    OTU = cur_line
    # print OTU
    unique_species = True
    OTU_list = cur_line.strip().split("_")
    if prev_line is not None:
        prev_OTU_list =  prev_line.strip().split("_")

        if  OTU_list[0] == prev_OTU_list[0] and  OTU_list[1] == prev_OTU_list[1]:
            unique_species = False

    if unique_species:
        # print ("unique species!")
        if (len(OTU_list) < 2):
            print "Bad data"
        cur_species = OTU_list[0] + "_" + OTU_list[1]
        #sp_list = []
        #for taxa in cur_species:
        #sp_list.append(taxa)

    #print cur_species + " = " + OTU
    #print sp_list
    #prev_line = cur_line

    #Species_dict = {cur_species: OTU}
    if cur_species in species_to_OTU_dictionary:
        OTUout_list = species_to_OTU_dictionary[cur_species]

    else:
        OTUout_list = []

    OTUout_list.append(OTU)
    print OTU  + ":" + cur_species
    species_to_OTU_dictionary[cur_species] = OTUout_list

#print json.dumps(species_to_OTU_dictionary,indent=4)

OTU_to_align={}
align_to_OTU={}
def OTU_from_align_tag(cur_line):
    #print cur_line
    #cur_line=cur_line.lower()
    OTU = cur_line.split()
    #print OTU[0]
    OTU = OTU[0]
    OTU = OTU.strip("'")
    #print OTU
    #index_ = OTU.find('_')
    #align = OTU[0:index_]
    #OTU = OTU[ index_ + 1 : ]

    #print align + " -> "+ OTU
    return OTU

for cur_filename in os.listdir('.'):
    #print cur_filename
    if cur_filename.endswith('.nexus'):
        #print cur_filename
        nexus_file = open(cur_filename, 'r')
        align = cur_filename.split('.')[0]
        for cur_line in nexus_file:
            #print cur_line
            #if cur_line == 'uce*'
            if not cur_line.startswith(nex_headers):

                OTU = OTU_from_align_tag(cur_line)

                #print align + " -> "+ OTU
                if OTU in OTU_to_align:
                    align_list = OTU_to_align[OTU]
                else:
                    align_list = []
                align_list.append(align)
                OTU_to_align[OTU] = align_list

                if align not in align_to_OTU:
                    align_to_OTU[align] = []
                align_to_OTU[align].append(OTU)


#print OTU_to_align

# species_to_OTU_dictionary
# OTU_to_align
#OTU_to_species = invert(species_to_OTU_dictionary)
# invert OTU_to_species dictionary
OTU_to_species = {}
for cur_species in species_to_OTU_dictionary:
    cur_OTU_list = species_to_OTU_dictionary[cur_species]
    for cur_OTU in cur_OTU_list:
#        OTU_to_species[cur_OTU.lower()]=cur_species.lower()
        OTU_to_species[cur_OTU]=cur_species

        # print "mapping otu to species: " + cur_OTU + " -> " + cur_species

#print "Done buildng dict"

# Which alignments have all species

# How many species are there?

species_count = len(species_to_OTU_dictionary.keys())
print "Species count:" + str(species_count)

# Which alignments have species_count species in them?
# For each species, do an aligntment count.  equals species_count, we print the alignment

# Which alignments contains at least one member of each species.


for cur_filename in os.listdir('.'):
    #print cur_filename
    if cur_filename.endswith('.nexus'):
        #print cur_filename
        nexus_file = open(cur_filename, 'r')
        alignment = cur_filename.split('.')[0]

        nexus_file_lines = nexus_file.readlines()
        sequence_length = None
        OTU_dictionary = {}
        output_list=[]
        for cur_line in nexus_file_lines:
            if not cur_line.startswith(nex_headers):

                line_list = cur_line.split()
                sequence_length = len(line_list[len(line_list)-1])
                OTU = OTU_from_align_tag(cur_line)
                OTU_dictionary[OTU]=None
                pre_sequence_length = len(line_list) + len(line_list[0])
        missing_species_dictionary = {}
        for cur_species in species_to_OTU_dictionary:
            missing_species_dictionary[cur_species] = None

        for cur_OTU in OTU_dictionary:
            cur_species = OTU_to_species[cur_OTU]
            if cur_species in missing_species_dictionary:
                del missing_species_dictionary[cur_species]

        for missing_species in missing_species_dictionary:
            sample_OTU = species_to_OTU_dictionary[missing_species][0]
            print "Missing species in alignment: " + alignment + " species: " + missing_species + " example OTU: " + sample_OTU
            hyphens=''
            write_string = sample_OTU
            for i in xrange(1,pre_sequence_length- len(write_string)):
                hyphens = hyphens + " "
            if(len(hyphens) < 1):
                hyphens = hyphens + " "

            for i in xrange(0,sequence_length):
                hyphens = hyphens + "-"
            write_string = write_string+hyphens+"\n"
            # print ("String: "+ write_string)
            output_list.append(write_string)
        nexus_file.close()
        try:
            os.stat('supplemented_files')
        except:
            os.mkdir('supplemented_files')
        ntax = int(nexus_file_lines[2].split()[1].split('=')[1])
        nchar = nexus_file_lines[2].split()[2].split('=')[1].replace(";", "")

        ntax = ntax + len(output_list)
        with open("./supplemented_files/"+cur_filename, "w") as outfile:
            for i in xrange(1,len(nexus_file_lines)-2):
                if i==2:
                    outfile.write("        dimensions ntax="+str(ntax)+" nchar="+nchar+";")
                else:
                    outfile.write(nexus_file_lines[i])
            for line in output_list:
                outfile.write(line)
            for i in xrange(len(nexus_file_lines)-2,len(nexus_file_lines)):
                outfile.write(nexus_file_lines[i])

    # Solegnathus_cf_hardwickii_Australia -> Solegnathus_hardwickii_cf_Australia
    # Corythoichthys_cf_intestinalis_NorthernMarianaIslands -> Corythoichthys_intestinalis_cf_NorthernMarianaIslands
    # Hippocampus_cf_mohnikei_Malaysia -> Hippocampus_mohnikei_cf_Malaysia
    # Doryrhamphus_cf_paulus_GulfCalifornia -> Doryrhamphus_paulus_cf_GulfCalifornia
    # Doryrhamphus_cf_californiensis_GulfCalifornia -> Doryrhamphus_californiensis_cf_GulfCalifornia

    # myfile.write
# for cur_align in align_to_OTU:
#     print ("Processing alignment: " + cur_align)
#     species_dict={}
#     cur_OTU_list = align_to_OTU[cur_align]
#     # print ("OTUs in this alignment: " + str(cur_OTU_list))
#     for cur_OTU in cur_OTU_list:
#         cur_species = OTU_to_species[cur_OTU]
#         # print ("Species:" + cur_species)
#         species_dict[cur_species]=None
#     print "in alignment: " + cur_align + " we have " + str(len(species_dict.keys()))
#     if len(species_dict.keys()) == species_count:
#         print "we have a winner."

