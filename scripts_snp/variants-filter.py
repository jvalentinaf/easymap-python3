# This script is used to filter polymorphism data in VA files according to a number of criteria determined by arguments from the workflow.
# The STEP argument is used to distinguish different types of filtering that are needed during the analysis
# 	STEP = 1: Normal argument-driven filtering
# 	STEP = 2: Candidate region filtering
# 	STEP = 3: Initial filtering + eliminates indels from the first VA files + eliminates variants from contigs shorter than 1 MB
# 	STEP = 4: Candidate region filtering for indels

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a", action="store", dest="input")
parser.add_argument("-b", action="store", dest="output")
parser.add_argument("-fasta", action="store", dest="fasta")
parser.add_argument("-chr", action="store", dest="chr", default="*", nargs="+")
parser.add_argument(
    "-mut_type", action="store", dest="mut_type", default="all"
)  # / EMS
parser.add_argument("-qual_min", action="store", dest="qual_min", default=0)
parser.add_argument("-dp_min", action="store", dest="dp_min", default=0)
parser.add_argument("-dp_max", action="store", dest="dp_max", default=8000)
parser.add_argument("-af_min", action="store", dest="af_min", default=0)
parser.add_argument("-af_max", action="store", dest="af_max", default=2)
parser.add_argument("-pos_min", action="store", dest="pos_min", default=0)
parser.add_argument("-pos_max", action="store", dest="pos_max", default=1000000000)
parser.add_argument("-step", action="store", dest="step")
parser.add_argument("-cand_reg_file", action="store", dest="cand_reg_file")
parser.add_argument("-in_format", action="store", dest="in_format", default="fastq")

args = parser.parse_args()

# Input
input = args.input
f1 = open(input, "r")
lines = f1.readlines()

# Output
output = args.output
f2 = open(output, "w")
step = args.step

# _________________________________CANDIDATE REGION FILTER___________________________________________________________________________________
regs = [[args.chr, args.pos_min, args.pos_max]]
if step == "1" or step == "5":
    pass
elif step == "2" or step == "4":
    f3 = open(args.cand_reg_file, "r")
    f3lines = f3.readlines()
    regs = list()
    for i, line in enumerate(f3lines):
        if line.startswith("?"):
            sp = line.split()
            args.chr = sp[1].strip(">")
            args.pos_min = int(float(sp[2].strip()))
            args.pos_max = int(float(sp[3].strip()))
            regs.append([args.chr, args.pos_min, args.pos_max])

# __________________________________________________________________________________________________________________________________________
if args.in_format == "fastq":

    def limits():
        global selector
        selector = 0
        if (
            (int(args.pos_min) < int(sp[1].strip()) < int(args.pos_max))
            and float(sp[4].strip()) > float(args.qual_min)
            and int(args.dp_min)
            < (int(sp[6].strip()) + int(sp[5].strip()))
            < int(args.dp_max)
            and float(args.af_min)
            < (
                (
                    float(sp[6].strip())
                    / ((float(sp[6].strip())) + (float(sp[5].strip())))
                )
            )
            < float(args.af_max)
        ):
            selector = 1
        else:
            selector = 0
        return [selector]


if args.in_format == "vcf":

    def limits():
        global selector
        selector = 0
        if (int(args.pos_min) < int(sp[1].strip()) < int(args.pos_max)) and float(
            sp[4].strip()
        ) > float(args.qual_min):
            selector = 1
        else:
            selector = 0
        return [selector]


# __________________________________________________________________________________________________________________________________________

for reg in regs:
    try:
        chromosome = reg[0]
        args.pos_min = reg[1]
        args.pos_max = reg[2]
    except:
        pass
    if step == "1" or step == "2" or step == "4" or step == "5":
        for i, line in enumerate(lines):
            if not line.startswith("#"):
                sp = line.split("\t")
                ref_b = sp[2]
                alt_b = sp[3]

                if args.mut_type.strip() == "EMS" and (
                    (str(sp[0].strip()) in chromosome) or (chromosome[0] == "*")
                ):
                    limits()
                    if (selector == 1) and (
                        (ref_b.strip() == "G" and alt_b.strip() == "A")
                        or (ref_b.strip() == "C" and alt_b.strip() == "T")
                    ):
                        if step != "4" and step != "5":
                            f2.write(line)

                elif args.mut_type.strip() == "all" and (
                    (str(sp[0].strip()) in chromosome) or (chromosome[0] == "*")
                ):
                    limits()
                    if selector == 1 and step == "2":
                        f2.write(line)
                    if selector == 1 and step == "1":
                        f2.write(line)
                    if selector == 1 and step == "4":
                        if len(ref_b) > 1 or len(alt_b) > 1:
                            f2.write(line)
                    if selector == 1 and step == "5":
                        if len(ref_b) > 1 or len(alt_b) > 1:
                            f2.write(line)

    if step == "3":
        # Function to parse fasta file (based on one of the Biopython IOs)
        def read_fasta(fp):
            name, seq = None, []
            for line in fp:
                line = line.rstrip()
                if line.startswith(">"):
                    if name:
                        yield (name, "".join(seq))
                    name, seq = line, []
                else:
                    seq.append(line)
            if name:
                yield (name, "".join(seq))

        # Read contig fasta file
        contig_lengths = list()
        contig_source = args.fasta
        with open(contig_source) as fp:
            fastalist = list()
            for name_contig, seq_contig in read_fasta(fp):
                innerlist = list()
                innerlist.append(name_contig.strip(">"))
                innerlist.append(len(seq_contig))
                fastalist.append(innerlist)

        large_contigs = list()
        for contig in fastalist:
            if int(contig[1]) > 2000000:
                large_contigs.append(contig[0].lower())

        # Filter
        for i, line in enumerate(lines):
            if not line.startswith("#"):
                sp = line.split("\t")
                if len(sp[2].strip()) == 1 and len(sp[3].strip()) == 1:
                    if str(sp[0]).strip().lower() in large_contigs:
                        if args.mut_type.strip() == "EMS" and (
                            (str(sp[0].strip()) in chromosome) or (chromosome[0] == "*")
                        ):
                            limits()
                            ref_b = sp[2]
                            alt_b = sp[3]
                            if (selector == 1) and (
                                (ref_b.strip() == "G" and alt_b.strip() == "A")
                                or (ref_b.strip() == "C" and alt_b.strip() == "T")
                            ):
                                f2.write(line)

                        elif args.mut_type.strip() == "all" and (
                            (str(sp[0].strip()) in chromosome) or (chromosome[0] == "*")
                        ):
                            limits()
                            if selector == 1:
                                f2.write(line)

f2.close()