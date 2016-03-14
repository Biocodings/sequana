"""
Python script to filter a vcf-file generated by freebayes.
"""

import sys
import vcf

class VCF(vcf.Reader):
    def __init__(self, filename, **kwargs):
        """
        Filter vcf file with a dictionnary.
        It takes a vcf file as entry.
        """
        try:
            filin = open(filename, "r")
            vcf.Reader.__init__(self, fsock=filin, **kwargs)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))

    def _calcul_freq(self, vcf_line):
        alt_freq = [count/vcf_line.INFO["DP"] for count in vcf_line.INFO["AO"]]
        return alt_freq

    def _filter_info_field(self, info_value, threshold):
        if(threshold.startswith("<")):
            if(info_value < int(threshold[1:])):
                return False
        else:
            if(info_value > int(threshold[1:])):
                return False
        return True

    def _filter_line(self, vcf_line, filter_dict):
        if(vcf_line.QUAL < filter_dict["QUAL"]):
            return False
        alt_freq = self._calcul_freq(vcf_line)
        if(alt_freq[0] < filter_dict["FREQ"]):
            return False
        for key, value in filter_dict["INFO"].items():
            if(type(vcf_line.INFO[key]) != list):
                if(self._filter_info_field(vcf_line.INFO[key], value)):
                    return False
            else:
                if(self._filter_info_field(vcf_line.INFO[key][0], value)):
                    return False
        return True

    def filter_vcf(self, filter_dict, output):
        """
        Read the vcf file and write the filter vcf file.
        """
        with open(output, "w") as fp:
            vcf_writer = vcf.Writer(fp, self)
            for variant in self:
                if(self._filter_line(variant, filter_dict)):
                    vcf_writer.write_record(variant)