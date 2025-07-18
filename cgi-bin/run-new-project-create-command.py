#!src/Python-3.12.3/.localpython/bin/python3

import cgi, cgitb, subprocess
cgitb.enable()

arguments = cgi.FieldStorage()

print('Content-type:text/html\r\n\r\n')

#Gff bypass
if arguments['gff_file'].value == "None": gff_input="n/p"
else: gff_input = arguments['gff_file'].value

cmdString = str(arguments['program'].value) + ' ' + \
			str(arguments['project_name'].value) + ' ' + \
			str(arguments['workflow'].value) + ' ' + \
			str(arguments['data_source'].value) + ' ' + \
			str(arguments['ref_seq'].value) + ' ' + \
			str(arguments['ins_seq'].value) + ' ' + \
			str(gff_input) + ' ' + \
			str(arguments['ann_file'].value) + ' ' + \
			str(arguments['read_s'].value) + ' ' + \
			str(arguments['read_f'].value) + ' ' + \
			str(arguments['read_r'].value) + ' ' + \
			str(arguments['lib_type_sample'].value) + ' ' + \
			str(arguments['read_s_ctrl'].value) + ' ' + \
			str(arguments['read_f_ctrl'].value) + ' ' + \
			str(arguments['read_r_ctrl'].value) + ' ' + \
			str(arguments['lib_type_ctrl'].value) + ' ' + \
			str(arguments['is_ref_strain'].value) + ' ' + \
			str(arguments['cross_type'].value) + ' ' + \
			str(arguments['snp_analysis_type'].value) + ' ' + \
			str(arguments['control_parental'].value) + ' ' + \
			str(arguments['sim_mut'].value) + ' ' + \
			str(arguments['sim_recsel'].value) + ' ' + \
			str(arguments['sim_seq'].value) + ' ' + \
			str(arguments['stringency'].value) + ' ' + \
            str(arguments['exp_mut_type'].value) + ' ' + \
			str(arguments['n_threads'].value) + ' ' + \
			str(arguments['preprocessing'].value)

processedCmdString = cmdString.replace('~', '+');
print(processedCmdString)

# For testing only
#cmdString = './easymap.sh test ins sim nano pbinprok2.fa complete.gff TAIR10_gene_info.txt n/p n/p n/p se n/p n/p n/p se n/p n/p n/p n/p 1+li n/p 10+100,0+500,100+1+50+se n/p'

subprocess.Popen(processedCmdString, cwd=r'./', shell=True, stdout=subprocess.PIPE)



