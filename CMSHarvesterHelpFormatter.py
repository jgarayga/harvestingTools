import optparse
from harvester import twiki_url, __author__, __version__

class CMSHarvesterHelpFormatter(optparse.IndentedHelpFormatter):
    """Helper class to add some customised help output to cmsHarvester.

    We want to add some instructions, as well as a pointer to the CMS
    Twiki.

    """

    def format_usage(self, usage):

        usage_lines = []

        sep_line = "-" * 60
        usage_lines.append(sep_line)
        usage_lines.append("Welcome to the CMS harvester V%s, a (hopefully useful)" % __version__)
        usage_lines.append("tool to create harvesting configurations.")
        usage_lines.append("For more information please have a look at the CMS Twiki:")
        usage_lines.append("  %s" % twiki_url)
        usage_lines.append("or contact the author:")
        usage_lines.append("  %s" % __author__)
        usage_lines.append(sep_line)
        usage_lines.append("")

        # Since we only add to the output, we now just append the
        # original output from IndentedHelpFormatter.
        usage_lines.append(optparse.IndentedHelpFormatter. \
                           format_usage(self, usage))

        formatted_usage = "\n".join(usage_lines)
        return formatted_usage

    # End of CMSHarvesterHelpFormatter.
