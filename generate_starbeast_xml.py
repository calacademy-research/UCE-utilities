#/usr/bin/python

import os
import textwrap
nex_headers = ('#NEXUS', 'begin', 'dimensions', 'format', 'matrix', ';', 'end', "\t")

def indent(string,indent_level, keep_newlines=True):
    num_spaces = indent_level * 4
    string_list = string.splitlines(keep_newlines)
    ret_string=""
    for cur_string in string_list:
        ret_string = ret_string + num_spaces * " " + cur_string
    return ret_string

def build_UCE_id_list_from_nexus_files(directory):

    UCE_id_list = []
    for cur_filename in os.listdir(directory):

        if cur_filename.endswith('.nexus'):
            #print cur_filename
            UCE_id_list.append(cur_filename.split(".")[0])
    return UCE_id_list


def build_UCE_list_from_nexus_files(directory):
    UCE_list = []
    for cur_filename in os.listdir(directory):
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
                #if cur_line == 'uce*'
                #if cur_line.startswith("'uce"):
                if not cur_line.strip().startswith(nex_headers):
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
                        names = OTU.split("_")
                        if len(names) <= 2:
                            print ("WARNING - binomial OTU")
                            print cur_filename+":"+"'"+OTU+"'"
    return UCE_list



def build_UCE_length_map(directory):
    UCE_length_map = {}
    for cur_filename in os.listdir(directory):
        #print cur_filename
        if cur_filename.endswith('.nexus'):
            #print cur_filename
            nexus_file = open(cur_filename, 'r')
            for cur_line in nexus_file:
                if cur_line.strip().startswith("dimensions"):
                    length = cur_line.strip().split()[2].split('=')[1]
            UCE = cur_filename.split('.')[0]
            UCE_length_map[UCE] = length.rstrip(';')
    return UCE_length_map


def build_species_to_OTU_dictionary_from_nexus_files(directory):
    UCE_list = build_UCE_list_from_nexus_files(directory)
    species_to_OTU_dictionary = {}
    prev_line = None
    cur_species = None
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
                print "Bad data: " + str(OTU_list) +":"+ cur_line

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
        # print OTU  + ":" + cur_species
        species_to_OTU_dictionary[cur_species] = OTUout_list

    return species_to_OTU_dictionary

def reverse_dictionary(dictionary):
    output_dictionary = {}
    for cur_key in dictionary:
        cur_value_list = dictionary[cur_key]
        for value in cur_value_list:
            output_dictionary[value]=cur_key
    return output_dictionary

def generate_uce_header(uce_name,indent_level):
    return indent("<data id=\""+uce_name+"\" name=\"alignment\">",indent_level)

def generate_uce_trailer(indent_level):
    return indent("</data>",indent_level)

def process_nexus_file(filename,UCE_length_map,outfile,indent_level):
    nexus_file = open(filename, 'r')
    UCE = filename.split(".")[0]

    for cur_line in nexus_file:
        #print cur_line
        #if cur_line == 'uce*'
        #if cur_line.startswith("'uce"):
        prev_length= None
        if not cur_line.strip().startswith(nex_headers):
            uce = filename.split(".")[0]
            input_array = cur_line.split()
            OTU = input_array[0]
            sequence = input_array[1]
            if prev_length is None:
                prev_length = len(sequence)
            if len(sequence) != prev_length:
                print ("Warning: mismatched alignemnt length")
            if len(sequence) != int(UCE_length_map[UCE]):
                print ("Reported alignemnt length does not match actual alighment length in UCE: " + UCE + " reported: " +  UCE_length_map[UCE] + " Counted:" + str(len(sequence)))
                print ("  Alignment: " + sequence)

            # species = OTU_to_species_dictionary[OTU]
            outfile.write(indent("<sequence",indent_level))
            outfile.write(" id=\""+OTU+uce+"\"")
            outfile.write(" taxon=\""+OTU+"\"")
            outfile.write(" totalcount=\"4\"")
            outfile.write(" value=\""+sequence+"\"")
            outfile.write("/>\n")


def get_map_names(indent_level):
    return indent(textwrap.dedent("""\
        <map name="Uniform" >beast.math.distributions.Uniform</map>
        <map name="Exponential" >beast.math.distributions.Exponential</map>
        <map name="LogNormal" >beast.math.distributions.LogNormalDistributionModel</map>
        <map name="Normal" >beast.math.distributions.Normal</map>
        <map name="Beta" >beast.math.distributions.Beta</map>
        <map name="Gamma" >beast.math.distributions.Gamma</map>
        <map name="LaplaceDistribution" >beast.math.distributions.LaplaceDistribution</map>
        <map name="prior" >beast.math.distributions.Prior</map>
        <map name="InverseGamma" >beast.math.distributions.InverseGamma</map>
        <map name="OneOnX" >beast.math.distributions.OneOnX</map>
        """) ,indent_level)

def get_mcmc_header(indent_level):
    return indent(textwrap.dedent("""\
        <run id="mcmc" spec="MCMC" chainLength="100000000" storeEvery="50000">
         """),indent_level)

def write_start_state(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
            <state id="state" storeEvery="5000">
        """),indent_level))

def write_end_state(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
            </state>
        """),indent_level))

def write_start_statenode(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
            <stateNode id="Tree.t:Species" spec="starbeast2.SpeciesTree">
        """),indent_level))

def write_end_statenode(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        </stateNode>
        """),indent_level))

def process_all_nexus_files(directory,UCE_length_map,outfile,indent_level):
    for cur_filename in os.listdir(directory):
        #print cur_filename
        if cur_filename.endswith('.nexus'):
            #print cur_filename
            outfile.write( generate_uce_header(cur_filename.split(".")[0],indent_level) +"\n")
            process_nexus_file(cur_filename,UCE_length_map,outfile,indent_level+1)
            outfile.write(generate_uce_trailer(indent_level) +"\n")

def write_taxonset_xml(outfile,species_to_OTU_dictionary,indent_level):
    outfile.write(indent(textwrap.dedent("""\
            <taxonset id="taxonsuperset" spec="starbeast2.StarBeastTaxonSet">
        """),indent_level))


    for cur_species in species_to_OTU_dictionary:
        string = indent(textwrap.dedent("""\
            <taxon id="XXXXX" spec="TaxonSet">
        """),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_species))

        for cur_OTU in species_to_OTU_dictionary[cur_species]:
            string = indent(textwrap.dedent("""\
            <taxon id="XXXXX" spec="Taxon"/>
            """),indent_level+2)
            outfile.write(string.replace("XXXXX",cur_OTU))

        outfile.write(indent(textwrap.dedent("""</taxon>\n"""),indent_level))


    outfile.write(indent(textwrap.dedent("""</taxonset>\n"""),indent_level))


    # for cur_species in species_to_OTU_dictionary:
    #     outfile.write(indent ("""<taxon id=""",4,False))
    #     outfile.write("\""+cur_species + "\"")
    #     outfile.write(""" spec="TaxonSet">\n""")
    #     for cur_OTU in species_to_OTU_dictionary[cur_species]:
    #         outfile.write(indent ("""<taxon id=""",5,False))
    #         outfile.write("\""+cur_OTU + "\"")
    #         outfile.write(""" spec="Taxon">\n""")
    #     outfile.write(indent ("""</taxon>\n""",indent_level))
    #
    # outfile.write(indent (textwrap.dedent("""\
    #     </taxonset>
    #     """),indent_level) )



def write_tree_and_parameter_xml(UCE_id_list,outfile,indent_level):
    for UCE_id in UCE_id_list:
        string = indent (textwrap.dedent("""\
            <tree id="Tree.t:XXXXX" name="stateNode">
                <taxonset id="TaxonSet.XXXXX" spec="TaxonSet">
                    <alignment idref="XXXXX"/>
                </taxonset>
            </tree>
            <parameter id="mutationRate.s:XXXXX" name="stateNode">1.0</parameter>
            <parameter id="kappa.s:XXXXX" lower="0.0" name="stateNode">2.0</parameter>
        """),indent_level)
        outfile.write(string.replace("XXXXX",UCE_id))

def write_single_parameters_xml(outfile,indent_level):
    string = indent (textwrap.dedent("""\
            <parameter id="constPopSizes.Species" lower="0.0" name="stateNode" upper="2.0">1.0</parameter>
            <parameter id="constPopMean.Species" lower="0.0" name="stateNode">1.0</parameter>
            <parameter id="netDiversificationRate.t:Species" lower="0.0" name="stateNode" upper="10000.0">1.0</parameter>
            <parameter id="ExtinctionFraction.t:Species" lower="0.0" name="stateNode" upper="1.0">0.5</parameter>

        """),indent_level)
    outfile.write(string)

def write_init_block(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <init id="SBI" spec="starbeast2.StarBeastInitializer" birthRate="@netDiversificationRate.t:Species" estimate="false" speciesTree="@Tree.t:Species">
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="Tree.t:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""\
            <populationModel id="popModelBridge.Species" spec="starbeast2.PassthroughModel">
                <childModel id="constPopModel.Species" spec="starbeast2.ConstantPopulations" populationSizes="@constPopSizes.Species" speciesTree="@Tree.t:Species"/>
            </populationModel>
        </init>
        """),indent_level))



def write_start_posterior_distribution(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="posterior" spec="util.CompoundDistribution">
        """),indent_level))

def write_end_posterior_distribution(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
            </distribution>
        """),indent_level))

def write_coalescent_distributions_block(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="speciescoalescent" spec="starbeast2.MultispeciesCoalescent">
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<distribution id="geneTree.t:XXXXX" spec="starbeast2.GeneTree" populationModel="@popModelBridge.Species" speciesTree="@Tree.t:Species" tree="@Tree.t:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</distribution>\n"""),indent_level))


def write_compound_distributions_block(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="prior" spec="util.CompoundDistribution">
            <distribution id="BirthDeathModel.t:Species" spec="beast.evolution.speciation.BirthDeathGernhard08Model" birthDiffRate="@netDiversificationRate.t:Species" relativeDeathRate="@ExtinctionFraction.t:Species" tree="@Tree.t:Species"/>
            <prior id="ExtinctionFractionPrior.t:Species" name="distribution" x="@ExtinctionFraction.t:Species">
                <Uniform id="Uniform.27" name="distr"/>
            </prior>
            <prior id="constPopMeanPrior.Species" name="distribution" x="@constPopMean.Species">
                <OneOnX id="OneOnX.25" name="distr"/>
            </prior>
            <prior id="constPopSizesPrior.Species" name="distribution" x="@constPopSizes.Species">
                <Gamma id="Gamma.0" beta="@constPopMean.Species" mode="ShapeMean" name="distr">
                    <parameter id="constPopShape.Species" estimate="false" lower="0.0" name="alpha">2.0</parameter>
                </Gamma>
            </prior>
            <prior id="netDiversificationRatePrior.t:Species" name="distribution" x="@netDiversificationRate.t:Species">
                <Uniform id="Uniform.36" name="distr" upper="10000.0"/>
            </prior>
        """),indent_level))
    first = True
    for cur_UCE in UCE_id_list:
        if(first):
            string = indent (textwrap.dedent("""
                <prior id="KappaPrior.s:XXXXX" name="distribution" x="@kappa.s:XXXXX">
                    <LogNormal id="LogNormalDistributionModel.20" name="distr">
                        <parameter id="RealParameter.20" estimate="false" name="M">1.0</parameter>
                        <parameter id="RealParameter.21" estimate="false" name="S">1.25</parameter>
                    </LogNormal>
                </prior>
            """),indent_level+1)
            first=False
        else:
            string = indent (textwrap.dedent("""
            <prior id="KappaPrior.s:XXXXX" name="distribution" x="@kappa.s:XXXXX">
                <LogNormal id="LogNormalDistributionModel.20.XXXXX" name="distr">
                    <parameter id="RealParameter.20.XXXXX" estimate="false" name="M">1.0</parameter>
                    <parameter id="RealParameter.21.XXXXX" estimate="false" name="S">1.25</parameter>
                </LogNormal>
            </prior>
            """),indent_level+1)
        first = False
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</distribution>\n"""),indent_level))

def write_compound_likelyhood_distributions_block(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="likelihood" spec="util.CompoundDistribution">
        """),indent_level))
    first = True
    first_string = None
    for cur_UCE in UCE_id_list:
        if first:
            string = indent (textwrap.dedent("""
                <distribution id="treeLikelihood.XXXXX" spec="TreeLikelihood" data="@XXXXX" tree="@Tree.t:XXXXX">
                    <siteModel id="SiteModel.s:XXXXX" spec="SiteModel" mutationRate="@mutationRate.s:XXXXX">
                        <parameter id="gammaShape.s:XXXXX" estimate="false" name="shape">1.0</parameter>
                        <parameter id="proportionInvariant.s:XXXXX" estimate="false" lower="0.0" name="proportionInvariant" upper="1.0">0.0</parameter>
                        <substModel id="hky.s:XXXXX" spec="HKY" kappa="@kappa.s:XXXXX">
                            <frequencies id="empiricalFreqs.s:XXXXX" spec="Frequencies" data="@XXXXX"/>
                        </substModel>
                    </siteModel>
                    <branchRateModel id="StrictClock.c:XXXXX" spec="beast.evolution.branchratemodel.StrictClockModel">
                        <parameter id="strictClockRate.c:XXXXX" estimate="false" lower="0.0" name="clock.rate">0.001</parameter>
                    </branchRateModel>
                </distribution>
            """),indent_level+1)
            first = False
            first_string = cur_UCE
        else:
            string = indent (textwrap.dedent("""
            <distribution id="treeLikelihood.XXXXX" spec="TreeLikelihood" branchRateModel="@StrictClock.c:YYYYY" data="@XXXXX" tree="@Tree.t:XXXXX">
                <siteModel id="SiteModel.s:XXXXX" spec="SiteModel" mutationRate="@mutationRate.s:XXXXX">
                    <parameter id="gammaShape.s:XXXXX" estimate="false" name="shape">1.0</parameter>
                    <parameter id="proportionInvariant.s:XXXXX" estimate="false" lower="0.0" name="proportionInvariant" upper="1.0">0.0</parameter>
                    <substModel id="hky.s:XXXXX" spec="HKY" kappa="@kappa.s:XXXXX">
                        <frequencies id="empiricalFreqs.s:XXXXX" spec="Frequencies" data="@XXXXX"/>
                    </substModel>
                </siteModel>
            </distribution>
            """),indent_level+1)
            string = string.replace("YYYYY",first_string)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</distribution>\n"""),indent_level))


def write_operator_Reheight(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="Reheight.t:Species" spec="starbeast2.NodeReheight2" taxonset="@taxonsuperset" tree="@Tree.t:Species" weight="75.0">
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="geneTree.t:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),indent_level))


def write_operator_coordinatedUniform(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="coordinatedUniform.t:Species" spec="starbeast2.CoordinatedUniform" speciesTree="@Tree.t:Species" weight="15.0">
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="Tree.t:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),indent_level))


def write_operator_coordinatedExponential(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="coordinatedExponential.t:Species" spec="starbeast2.CoordinatedExponential" speciesTree="@Tree.t:Species" weight="15.0">
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="Tree.t:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),indent_level))

def write_operator_updownAll(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="updownAll:Species" spec="UpDownOperator" scaleFactor="0.75" weight="6.0">
            <up idref="netDiversificationRate.t:Species"/>
            <down idref="Tree.t:Species"/>
            <down idref="constPopSizes.Species"/>
            <down idref="constPopMean.Species"/>
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<down idref="Tree.t:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),indent_level))

    #             <parameter idref="mutationRate.s:uce-975"/>
    # <parameter idref="mutationRate.s:uce-976"/>
    # <parameter idref="mutationRate.s:uce-979"/>
    # <parameter idref="mutationRate.s:uce-98"/>
    # <parameter idref="mutationRate.s:uce-982"/>
    # <parameter idref="mutationRate.s:uce-986"/>
    # <parameter idref="mutationRate.s:uce-987"/>
    # <parameter idref="mutationRate.s:uce-99"/>
    # <parameter idref="mutationRate.s:uce-990"/>
    # <parameter idref="mutationRate.s:uce-993"/>

    # <weightvector id="weightparameter" spec="parameter.IntegerParameter" dimension="10" estimate="false" lower="0" upper="0">327 322 324 316 326 322 333 340 308 327 318 335 305 321 318 314 327 313 337 322 325 324 336 334 304 318 300 316 324 314 302 318 326 329 315 327 322 320 314 327 335 333 305 316 322 326 333 314 309 321 331 306 338 315 344 313 323 329 316 336 314 339 319 322 309 334 331 314 329 319 325 317 336 339 341 311 336 330 309 317 329 311 323 315 307 325 326 332 312 317 334 309 318 321 327 311 312 337 343 348 331 344 318 320 316 337 336 322 328 345 332 330 338 315 340 325 318 304 320 322 312 326 305 337 322 321 311 312 315 319 314 326 330 321 337 306 331 332 322 322 312 329 324 330 335 317 327 338 326 309 333 328 334 305 329 312 314 311 333 315 329 339 306 315 335 311 336 327 319 328 338 318 317 339 309 323 331 318 323 323 321 309 314 320 323 319 309 320 324 320 311 319 318 334 322 323 322 330 328 338 305 328 315 330 326 339 321 325 305 334 320 310 311 318 314 317 311 334 325 308 330 316 324 298 325 333 324 320 319 320 319 334 329 326 333 345 317 312 338 306 323 313 346 324 320 318 318 310 317 313 325 335 327 316 311 330 332 324 325 319 317 317 317 323 329 327 326 307 308 332 320 329 329 334 318 314 318 336 312 339 339 330 316 319 331 310 313 318 341 317 330 331 324 308 323 321 332 316 319 330 322 312 306 334 327 336 335 338 320 319 321 328 346 336 321 340 307 332 328 318 330 312 337 307 337 332 344 327 319 314 328 337 328 327 318 322 318 331 322 316 307 320 336 314 324 317 328 317 322 304 312 309 315 305 302 319 327 315 336 327 331 330 320 334 328 325 314 335 324 328 308 341 328 317 307 336 323 338 309 340 317 308 325 341 322 319 306 334 314 318 319 330 325 311 319 324 310 317 338 314 313 332 314 324 321 329 334 329 324 332 303 323 317 314 317 329 319 315 339 323 326 320 308 313 329 329 325 320 326 334 312 323 318 328 304 312 326 329 326 328 342 339 333 316 306 333 340 304 328 331 320 311 307 321 309 320 305 333 341 336 320 323 321 322 306 327 309 339 333 327 316 309 312 334 321 328 326 311 326 327 303 313 319 313 322 326 321 328 331 330 340 314 315 324 305 338 319 339 332 314 328 346 340 335 324 323 316 325 307 324 328 311 328 315 319 337 329 318 313 319 319 334 329 322 323 332 321 312 326 328 336 315 344 313 308 316 326 312
    # 311 325 320 322 316 331 315 3371</weightvector>


def write_operator_FixMeanMutationRatesOperator(UCE_id_list,UCE_length_map,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
    <operator id="FixMeanMutationRatesOperator" spec="DeltaExchangeOperator" delta="0.75" weight="11.0">
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<parameter idref="mutationRate.s:XXXXX"/>\n"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))
    # outfile.write(indent(textwrap.dedent("""<weightvector id="weightparameter" spec="parameter.IntegerParameter" dimension="10" estimate="false" lower="0" upper="0">154 214 252 127 188 172 151 174 229 336</weightvector>\n"""),indent_level))
    outfile.write(indent(textwrap.dedent("""<weightvector id="weightparameter" spec="parameter.IntegerParameter" dimension=\""""),indent_level+1))
    outfile.write(str(len(UCE_id_list)))
    outfile.write("""" estimate="false" lower="0" upper="0">""")
    first = True
    for cur_UCE in UCE_id_list:
        length = UCE_length_map[cur_UCE].strip()
        if first:
            outfile.write(length)
            first = False
        else:
            outfile.write(" " + length)

    outfile.write(textwrap.dedent("""</weightvector>\n"""))

    outfile.write(indent(textwrap.dedent("""</operator>\n"""),indent_level))


def write_operator_singles(UCE_id_list,outfile,indent_level):
    for cur_UCE in UCE_id_list:
        string = indent(textwrap.dedent("""\
            <operator id="TreeScaler.t:XXXXX" spec="ScaleOperator" scaleFactor="0.95" tree="@Tree.t:XXXXX" weight="3.0"/>
            <operator id="TreeRootScaler.t:XXXXX" spec="ScaleOperator" rootOnly="true" scaleFactor="0.7" tree="@Tree.t:XXXXX" weight="3.0"/>
            <operator id="UniformOperator.t:XXXXX" spec="Uniform" tree="@Tree.t:XXXXX" weight="15.0"/>
            <operator id="SubtreeSlide.t:XXXXX" spec="SubtreeSlide" size="0.002" tree="@Tree.t:XXXXX" weight="15.0"/>
            <operator id="Narrow.t:XXXXX" spec="Exchange" tree="@Tree.t:XXXXX" weight="15.0"/>
            <operator id="Wide.t:XXXXX" spec="Exchange" isNarrow="false" tree="@Tree.t:XXXXX" weight="15.0"/>
            <operator id="WilsonBalding.t:XXXXX" spec="WilsonBalding" tree="@Tree.t:XXXXX" weight="15.0"/>
            <operator id="clockUpDownOperator.c:XXXXX" spec="UpDownOperator" scaleFactor="0.95" weight="3.0">
                <down idref="Tree.t:XXXXX"/>
            </operator>

        """),indent_level)

        outfile.write(string.replace("XXXXX",cur_UCE))

def write_operator_KappaScaler(UCE_id_list,outfile,indent_level):
    for cur_UCE in UCE_id_list:
        string = indent(textwrap.dedent("""\
            <operator id="KappaScaler.s:XXXXX" spec="ScaleOperator" parameter="@kappa.s:XXXXX" scaleFactor="0.75" weight="1.0"/>
        """),indent_level)

        outfile.write(string.replace("XXXXX",cur_UCE))


def write_operator_unique(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="constPopSizesSwap.Species" spec="starbeast2.RealCycle" k="2" optimise="false" parameter="@constPopSizes.Species" weight="3.0"/>
        <operator id="constPopSizesScale.Species" spec="ScaleOperator" parameter="@constPopSizes.Species" scaleFactor="0.5" weight="3.0"/>
        <operator id="constPopMeanScale.Species" spec="ScaleOperator" parameter="@constPopMean.Species" scaleFactor="0.75" weight="1.0"/>

        <operator id="netDiversificationRateScale.t:Species" spec="ScaleOperator" parameter="@netDiversificationRate.t:Species" scaleFactor="0.5" weight="1.0"/>
        <operator id="ExtinctionFractionScale.t:Species" spec="ScaleOperator" parameter="@ExtinctionFraction.t:Species" scaleFactor="0.5" weight="0.5"/>
        <operator id="ExtinctionFractionUniform.t:Species" spec="UniformOperator" parameter="@ExtinctionFraction.t:Species" weight="0.5"/>
        <operator id="bdSubtreeSlide.t:Species" spec="SubtreeSlide" size="0.002" tree="@Tree.t:Species" weight="15.0"/>
        <operator id="bdWilsonBalding.t:Species" spec="WilsonBalding" tree="@Tree.t:Species" weight="15.0"/>
        <operator id="bdWide.t:Species" spec="Exchange" isNarrow="false" tree="@Tree.t:Species" weight="15.0"/>
        <operator id="bdNarrow.t:Species" spec="Exchange" tree="@Tree.t:Species" weight="15.0"/>
        <operator id="bdUniformOperator.t:Species" spec="Uniform" tree="@Tree.t:Species" weight="15.0"/>
        <operator id="bdTreeRootScaler.t:Species" spec="ScaleOperator" rootOnly="true" scaleFactor="0.7" tree="@Tree.t:Species" weight="3.0"/>
        <operator id="bdTreeScaler.t:Species" spec="ScaleOperator" scaleFactor="0.95" tree="@Tree.t:Species" weight="3.0"/>
        <operatorschedule id="operatorSchedule" spec="OperatorSchedule">
            <subschedule id="operatorSubschedule" spec="OperatorSchedule" operatorPattern="^.*Species$" weight="20.0" weightIsPercentage="true"/>
        </operatorschedule>
         """),indent_level))


def write_tracelog(UCE_id_list,outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <logger id="tracelog" fileName="starbeast.log" logEvery="5000" model="@posterior" sort="smart">

            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
            <log idref="speciescoalescent"/>
            <log id="TreeHeight.Species" spec="beast.evolution.tree.TreeHeightLogger" tree="@Tree.t:Species"/>
            <log id="TreeLength.Species" spec="starbeast2.TreeLengthLogger" tree="@Tree.t:Species"/>
            <log idref="constPopMean.Species"/>
            <log idref="BirthDeathModel.t:Species"/>
            <log idref="netDiversificationRate.t:Species"/>
            <log idref="ExtinctionFraction.t:Species"/>
        """),indent_level))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""
            <log idref="treeLikelihood.XXXXX"/>
            <log id="TreeHeight.t:XXXXX" spec="beast.evolution.tree.TreeHeightLogger" tree="@Tree.t:XXXXX"/>
            <log idref="mutationRate.s:XXXXX"/>
            <log idref="kappa.s:XXXXX"/>"""),indent_level+1)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</logger>\n"""),indent_level))


def write_logger_singles(outfile,indent_level):
    outfile.write(indent(textwrap.dedent("""\
        <logger id="speciesTreeLogger" fileName="species.trees" logEvery="5000" mode="tree">
            <log id="SpeciesTreeLoggerX" spec="starbeast2.SpeciesTreeLogger" populationmodel="@constPopModel.Species" speciesTree="@Tree.t:Species"/>
        </logger>

        <logger id="screenlog" logEvery="5000" model="@posterior">
            <log idref="posterior"/>
            <log id="ESS.0" spec="util.ESS" arg="@posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
        </logger>
         """),indent_level))


def write_treelog(UCE_id_list,outfile,indent_level):

    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""
            <logger id="treelog.t:XXXXX" fileName="$(tree).trees" logEvery="5000" mode="tree">
                <log id="TreeWithMetaDataLogger.t:XXXXX" spec="beast.evolution.tree.TreeWithMetaDataLogger" tree="@Tree.t:XXXXX"/>
            </logger>
        """),indent_level)
        outfile.write(string.replace("XXXXX",cur_UCE))


def write_loggers(UCE_id_list,outfile,indent_level):
    write_tracelog(UCE_id_list,outfile,indent_level)
    write_logger_singles(outfile,indent_level)
    write_treelog(UCE_id_list,outfile,indent_level)




with open ("./auto-generated-starbeast.xml","w") as outfile:
    species_to_OTU_dictionary = build_species_to_OTU_dictionary_from_nexus_files(".")
    OTU_to_species_dictionary = reverse_dictionary(species_to_OTU_dictionary)
    UCE_id_list = build_UCE_id_list_from_nexus_files(".")
    UCE_length_map = build_UCE_length_map(".")
# Hippocampus_angustus_Australia2
    outfile.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
    outfile.write('<beast beautitemplate=\'StarBeast2\' beautistatus=\'noAutoSetClockRate\' namespace="beast.core:beast.evolution.alignment:beast.evolution.tree.coalescent:beast.core.util:beast.evolution.nuc:beast.evolution.operators:beast.evolution.sitemodel:beast.evolution.substitutionmodel:beast.evolution.likelihood" required="starbeast2 v0.14.0" version="2.4">\n')
    process_all_nexus_files(".",UCE_length_map,outfile,1)
    outfile.write (get_map_names(1))
    outfile.write (get_mcmc_header(1))
    write_start_state(outfile,2)
    write_start_statenode(outfile,3)
    write_taxonset_xml(outfile,species_to_OTU_dictionary,4)
    write_end_statenode(outfile,3)
    write_tree_and_parameter_xml(UCE_id_list,outfile,3)
    write_single_parameters_xml(outfile,3)

    write_end_state(outfile,2)
    write_init_block(UCE_id_list,outfile,2)
    write_start_posterior_distribution(outfile,2)
    write_coalescent_distributions_block(UCE_id_list,outfile,3)
    write_compound_distributions_block(UCE_id_list,outfile,3)
    write_compound_likelyhood_distributions_block(UCE_id_list,outfile,3)
    write_end_posterior_distribution(outfile,3)
    write_operator_Reheight(UCE_id_list,outfile,2)
    write_operator_coordinatedUniform (UCE_id_list,outfile,2)
    write_operator_coordinatedExponential(UCE_id_list,outfile,2)
    write_operator_updownAll(UCE_id_list,outfile,2)
    write_operator_singles(UCE_id_list,outfile,2)
    write_operator_FixMeanMutationRatesOperator(UCE_id_list,UCE_length_map,outfile,2)
    write_operator_KappaScaler(UCE_id_list,outfile,2)
    write_operator_unique(outfile,2)
    write_loggers(UCE_id_list,outfile,2)
    outfile.write(indent(textwrap.dedent("""\
            </run>
        </beast>
         """),0))
