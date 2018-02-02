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

def generate_uce_header(uce_name):
    return "    <data id=\""+uce_name+"\" name=\"alignment\">"

def generate_uce_trailer():
    return "    </data>"

def process_nexus_file(filename,OTU_to_species_dictionary,outfile):
    nexus_file = open(filename, 'r')
    for cur_line in nexus_file:
        #print cur_line
        #if cur_line == 'uce*'
        #if cur_line.startswith("'uce"):

        if not cur_line.strip().startswith(nex_headers):
            uce = filename.split(".")[0]
            input_array = cur_line.split()
            OTU = input_array[0]
            sequence = input_array[1]
            species = OTU_to_species_dictionary[OTU]
            outfile.write("        <sequence")
            outfile.write(" id=\""+OTU+uce+"\"")
            outfile.write(" taxon=\""+OTU+"\"")
            outfile.write(" totalcount=\"4\"")
            outfile.write(" value=\""+sequence+"\"")
            outfile.write("/>\n")


def get_map_names():
    return textwrap.dedent("""\
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
        """)

def get_mcmc_header():
    return textwrap.dedent("""\
        <run id="mcmc" spec="MCMC" chainLength="100000000" storeEvery="50000">
         """)

def write_start_state(outfile):
    outfile.write(indent(textwrap.dedent("""\
            <state id="state" storeEvery="5000">
        """),1))

def write_end_state(outfile):
    outfile.write(indent(textwrap.dedent("""\
            </state>
        """),1))

def write_start_statenode(outfile):
    outfile.write(indent(textwrap.dedent("""\
            <stateNode id="Tree.t:Species" spec="starbeast2.SpeciesTree">
        """),2))

def write_end_statenode(outfile):
    outfile.write(indent(textwrap.dedent("""\
        </stateNode>
        """),2))

def process_all_nexus_files(directory,OTU_to_species_dictionary,outfile):
    for cur_filename in os.listdir(directory):
        #print cur_filename
        if cur_filename.endswith('.nexus'):
            #print cur_filename
            outfile.write(generate_uce_header(cur_filename.split(".")[0]) +"\n")
            process_nexus_file(cur_filename,OTU_to_species_dictionary,outfile)
            outfile.write(generate_uce_trailer() +"\n")

def write_taxonset_xml(outfile,species_to_OTU_dictionary):
    outfile.write(indent(textwrap.dedent("""\
            <taxonset id="taxonsuperset" spec="starbeast2.StarBeastTaxonSet">
        """),3))


    for cur_species in species_to_OTU_dictionary:
        string = indent(textwrap.dedent("""\
            <taxon id="XXXXX" spec="TaxonSet">
        """),3)
        outfile.write(string.replace("XXXXX",cur_species))

        for cur_OTU in species_to_OTU_dictionary[cur_species]:
            string = indent(textwrap.dedent("""\
            <taxon id="XXXXX" spec="Taxon"/>
            """),4)
            outfile.write(string.replace("XXXXX",cur_OTU))

        outfile.write(indent(textwrap.dedent("""</taxon>\n"""),3))


    outfile.write(indent(textwrap.dedent("""</taxonset>\n"""),3))


    # for cur_species in species_to_OTU_dictionary:
    #     outfile.write(indent ("""<taxon id=""",4,False))
    #     outfile.write("\""+cur_species + "\"")
    #     outfile.write(""" spec="TaxonSet">\n""")
    #     for cur_OTU in species_to_OTU_dictionary[cur_species]:
    #         outfile.write(indent ("""<taxon id=""",5,False))
    #         outfile.write("\""+cur_OTU + "\"")
    #         outfile.write(""" spec="Taxon">\n""")
    #     outfile.write(indent ("""</taxon>\n""",4))
    #
    # outfile.write(indent (textwrap.dedent("""\
    #     </taxonset>
    #     """),3) )



def write_tree_and_parameter_xml(UCE_id_list,outfile):
    for UCE_id in UCE_id_list:
        string = indent (textwrap.dedent("""\
            <tree id="Tree.t:XXXXX" name="stateNode">
                <taxonset id="TaxonSet.XXXXX" spec="TaxonSet">
                  <alignment idref="XXXXX"/>
                </taxonset>
            </tree>
            <parameter id="mutationRate.s:XXXXX" name="stateNode">1.0</parameter>
            <parameter id="kappa.s:XXXXX" lower="0.0" name="stateNode">2.0</parameter>
        """),2)
        outfile.write(string.replace("XXXXX",UCE_id))

def write_single_parameters_xml(outfile):
    string = indent (textwrap.dedent("""\
            <parameter id="constPopSizes.Species" lower="0.0" name="stateNode" upper="2.0">1.0</parameter>
            <parameter id="constPopMean.Species" lower="0.0" name="stateNode">1.0</parameter>
            <parameter id="netDiversificationRate.t:Species" lower="0.0" name="stateNode" upper="10000.0">1.0</parameter>
            <parameter id="ExtinctionFraction.t:Species" lower="0.0" name="stateNode" upper="1.0">0.5</parameter>

        """),2)
    outfile.write(string)

def write_init_block(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <init id="SBI" spec="starbeast2.StarBeastInitializer" birthRate="@netDiversificationRate.t:Species" estimate="false" speciesTree="@Tree.t:Species">
        """),1))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="Tree.t:XXXXX"/>\n"""),2)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""\
            <populationModel id="popModelBridge.Species" spec="starbeast2.PassthroughModel">
                <childModel id="constPopModel.Species" spec="starbeast2.ConstantPopulations" populationSizes="@constPopSizes.Species" speciesTree="@Tree.t:Species"/>
            </populationModel>
        </init>
        """),1))



def write_start_posterior_distribution(outfile):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="posterior" spec="util.CompoundDistribution">
        """),1))

def write_end_posterior_distribution(outfile):
    outfile.write(indent(textwrap.dedent("""\
            </distribution>
        """),1))

def write_coalescent_distributions_block(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="speciescoalescent" spec="starbeast2.MultispeciesCoalescent">
        """),2))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<distribution id="geneTree.t:XXXXX" spec="starbeast2.GeneTree" populationModel="@popModelBridge.Species" speciesTree="@Tree.t:Species" tree="@Tree.t:XXXXX"/>\n"""),3)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</distribution>\n"""),2))


def write_compound_distributions_block(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="prior" spec="util.CompoundDistribution">
            <distribution id="BirthDeathModel.t:Species" spec="beast.evolution.speciation.BirthDeathGernhard08Model" birthDiffRate="@netDiversificationRate.t:Species" relativeDeathRate="@ExtinctionFraction.t:Species" tree="@Tree.t:Species"/>
            <prior id="ExtinctionFractionPrior.t:Species" name="distribution" x="@ExtinctionFraction.t:Species">
                <Uniform id="Uniform.13" name="distr"/>
            </prior>
            <prior id="constPopMeanPrior.Species" name="distribution" x="@constPopMean.Species">
                <OneOnX id="OneOnX.11" name="distr"/>
            </prior>
            <prior id="constPopSizesPrior.Species" name="distribution" x="@constPopSizes.Species">
                <Gamma id="Gamma.0" beta="@constPopMean.Species" mode="ShapeMean" name="distr">
                    <parameter id="constPopShape.Species" estimate="false" lower="0.0" name="alpha">2.0</parameter>
                </Gamma>
            </prior>
            <prior id="netDiversificationRatePrior.t:Species" name="distribution" x="@netDiversificationRate.t:Species">
                <Uniform id="Uniform.12" name="distr" upper="10000.0"/>
            </prior>
        """),2))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""
            <prior id="KappaPrior.s:XXXXX" name="distribution" x="@kappa.s:XXXXX">
                <LogNormal id="LogNormalDistributionModel.20.XXXXX" name="distr">
                    <parameter id="RealParameter.20.XXXXX" estimate="false" name="M">1.0</parameter>
                    <parameter id="RealParameter.21.XXXXX" estimate="false" name="S">1.25</parameter>
                </LogNormal>
            </prior>
        """),3)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</distribution>\n"""),2))

def write_compound_likelyhood_distributions_block(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <distribution id="likelihood" spec="util.CompoundDistribution">
        """),2))
    first = True
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
            """),3)
            first = False
        else:
            string = indent (textwrap.dedent("""
                <distribution id="treeLikelihood.XXXXX" spec="TreeLikelihood" data="@XXXXX" tree="@Tree.t:XXXXX">
                    <siteModel id="SiteModel.s:XXXXX" spec="SiteModel" mutationRate="@mutationRate.s:XXXXX">
                        <parameter id="gammaShape.s:XXXXX" estimate="false" name="shape">1.0</parameter>
                        <parameter id="proportionInvariant.s:XXXXX" estimate="false" lower="0.0" name="proportionInvariant" upper="1.0">0.0</parameter>
                        <substModel id="hky.s:XXXXX" spec="HKY" kappa="@kappa.s:XXXXX">
                            <frequencies id="empiricalFreqs.s:XXXXX" spec="Frequencies" data="@XXXXX"/>
                        </substModel>
                    </siteModel>
                </distribution>
            """),3)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</distribution>\n"""),2))


def write_operator_Reheight(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="Reheight.t:Species" spec="starbeast2.NodeReheight2" taxonset="@taxonsuperset" tree="@Tree.t:Species" weight="75.0">
        """),2))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="geneTree.t:XXXXX"/>\n"""),2)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),1))


def write_operator_coordinatedUniform(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="coordinatedUniform.t:Species" spec="starbeast2.CoordinatedUniform" speciesTree="@Tree.t:Species" weight="15.0">
        """),2))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="Tree.t:XXXXX"/>\n"""),2)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),1))


def write_operator_coordinatedExponential(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="coordinatedExponential.t:Species" spec="starbeast2.CoordinatedExponential" speciesTree="@Tree.t:Species" weight="15.0">
        """),2))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<geneTree idref="Tree.t:XXXXX"/>\n"""),2)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),1))

def write_operator_updownAll(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
        <operator id="updownAll:Species" spec="UpDownOperator" scaleFactor="0.75" weight="6.0">
            <up idref="netDiversificationRate.t:Species"/>
            <down idref="Tree.t:Species"/>
            <down idref="constPopSizes.Species"/>
            <down idref="constPopMean.Species"/>
        """),2))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<down idref="Tree.t:XXXXX"/>\n"""),2)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),1))

def write_operator_FixMeanMutationRatesOperator(UCE_id_list,outfile):
    outfile.write(indent(textwrap.dedent("""\
    <operator id="FixMeanMutationRatesOperator" spec="DeltaExchangeOperator" delta="0.75" weight="11.0">
        """),1))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""<parameter idref="mutationRate.s:XXXXX"/>\n"""),2)
        outfile.write(string.replace("XXXXX",cur_UCE))
    outfile.write(indent(textwrap.dedent("""<weightvector id="weightparameter" spec="parameter.IntegerParameter" dimension="10" estimate="false" lower="0" upper="0">154 214 252 127 188 172 151 174 229 336</weightvector>
\n"""),2))
    outfile.write(indent(textwrap.dedent("""</operator>\n"""),1))


def write_operator_singles(UCE_id_list,outfile):
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

        """),1)

        outfile.write(string.replace("XXXXX",cur_UCE))

def write_operator_KappaScaler(UCE_id_list,outfile):
    for cur_UCE in UCE_id_list:
        string = indent(textwrap.dedent("""\
            <operator id="KappaScaler.s:XXXXX" spec="ScaleOperator" parameter="@kappa.s:uce-1" scaleFactor="0.75" weight="1.0"/>
        """),1)

        outfile.write(string.replace("XXXXX",cur_UCE))


def write_operator_unique(outfile):
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
         """),1))


def write_tracelog(UCE_id_list,outfile):
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
        """),1))
    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""
            <log idref="treeLikelihood.XXXXX"/>
            <log id="TreeHeight.t:XXXXX" spec="beast.evolution.tree.TreeHeightLogger" tree="@Tree.t:XXXXX"/>
            <log idref="mutationRate.s:XXXXX"/>
            <log idref="kappa.s:XXXXX"/>
        """),2)
        outfile.write(string.replace("XXXXX",cur_UCE))

    outfile.write(indent(textwrap.dedent("""</logger>\n"""),1))


def write_logger_singles(outfile):
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
         """),1))


def write_treelog(UCE_id_list,outfile):

    for cur_UCE in UCE_id_list:
        string = indent (textwrap.dedent("""
            <logger id="treelog.t:XXXXX" fileName="$(tree).trees" logEvery="5000" mode="tree">
                <log id="TreeWithMetaDataLogger.t:XXXXX" spec="beast.evolution.tree.TreeWithMetaDataLogger" tree="@Tree.t:uce-13"/>
            </logger>
        """),1)
        outfile.write(string.replace("XXXXX",cur_UCE))


def write_loggers(UCE_id_list,outfile):
    write_tracelog(UCE_id_list,outfile)
    write_logger_singles(outfile)
    write_treelog(UCE_id_list,outfile)


with open ("./auto-generated-starbeast.xml","w") as outfile:
    species_to_OTU_dictionary = build_species_to_OTU_dictionary_from_nexus_files(".")
    OTU_to_species_dictionary = reverse_dictionary(species_to_OTU_dictionary)
    UCE_id_list = build_UCE_id_list_from_nexus_files(".")
# Hippocampus_angustus_Australia2
    outfile.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?><beast beautitemplate=\'StarBeast2\' beautistatus=\'noAutoSetClockRate\' namespace="beast.core:beast.evolution.alignment:beast.evolution.tree.coalescent:beast.core.util:beast.evolution.nuc:beast.evolution.operators:beast.evolution.sitemodel:beast.evolution.substitutionmodel:beast.evolution.likelihood" required="starbeast2 v0.14.0" version="2.4">\n')
    process_all_nexus_files(".",OTU_to_species_dictionary,outfile)
    outfile.write (get_map_names())
    outfile.write (get_mcmc_header())
    write_start_state(outfile)
    write_start_statenode(outfile)
    write_taxonset_xml(outfile,species_to_OTU_dictionary)
    write_end_statenode(outfile)
    write_tree_and_parameter_xml(UCE_id_list,outfile)
    write_single_parameters_xml(outfile)

    write_end_state(outfile)
    write_init_block(UCE_id_list,outfile)
    write_start_posterior_distribution(outfile)
    write_coalescent_distributions_block(UCE_id_list,outfile)
    write_compound_distributions_block(UCE_id_list,outfile)
    write_compound_likelyhood_distributions_block(UCE_id_list,outfile)
    write_end_posterior_distribution(outfile)
    write_operator_Reheight(UCE_id_list,outfile)
    write_operator_coordinatedUniform (UCE_id_list,outfile)
    write_operator_coordinatedExponential(UCE_id_list,outfile)
    write_operator_updownAll(UCE_id_list,outfile)
    write_operator_singles(UCE_id_list,outfile)
    write_operator_FixMeanMutationRatesOperator(UCE_id_list,outfile)
    write_operator_KappaScaler(UCE_id_list,outfile)
    write_operator_unique(outfile)
    write_loggers(UCE_id_list,outfile)
    outfile.write(indent(textwrap.dedent("""\
        </run>
        </beast>
         """),0))
