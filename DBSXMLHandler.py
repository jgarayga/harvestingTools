# These we need to communicate with DBS global DBSAPI
from DBSAPI.dbsApi import DbsApi
import DBSAPI.dbsException
import DBSAPI.dbsApiException
# and these we need to parse the DBS output.
global xml
global SAXParseException
import xml.sax
from xml.sax import SAXParseException

class DBSXMLHandler(xml.sax.handler.ContentHandler):
    """XML handler class to parse DBS results.

    The tricky thing here is that older DBS versions (2.0.5 and
    earlier) return results in a different XML format than newer
    versions. Previously the result values were returned as attributes
    to the `result' element. The new approach returns result values as
    contents of named elements.

    The old approach is handled directly in startElement(), the new
    approach in characters().

    NOTE: All results are returned in the form of string values of
          course!

    """

    # This is the required mapping from the name of the variable we
    # ask for to what we call it ourselves. (Effectively this is the
    # mapping between the old attribute key name and the new element
    # name.)

    mapping = {
        "dataset"        : "PATH",
        "dataset.tag"    : "PROCESSEDDATASET_GLOBALTAG",
        "datatype.type"  : "PRIMARYDSTYPE_TYPE",
        "run"            : "RUNS_RUNNUMBER",
        "run.number"     : "RUNS_RUNNUMBER",
        "file.name"      : "FILES_LOGICALFILENAME",
        "file.numevents" : "FILES_NUMBEROFEVENTS",
        "algo.version"   : "APPVERSION_VERSION",
        "site"           : "STORAGEELEMENT_SENAME",
        }
    
    def __init__(self, tag_names):
        # This is a list used as stack to keep track of where we are
        # in the element tree.
        self.element_position = []
        self.tag_names = tag_names
        self.results = {}

    def startElement(self, name, attrs):
        self.element_position.append(name)

        self.current_value = []

        #----------

        # This is to catch results from DBS 2.0.5 and earlier.
        if name == "result":
            for name in self.tag_names:
                key = DBSXMLHandler.mapping[name]
                value = str(attrs[key])
                try:
                    self.results[name].append(value)
                except KeyError:
                    self.results[name] = [value]

        #----------

    def endElement(self, name):
        assert self.current_element() == name, \
               "closing unopenend element `%s'" % name

        if self.current_element() in self.tag_names:
            contents = "".join(self.current_value)
            if self.results.has_key(self.current_element()):
                self.results[self.current_element()].append(contents)
            else:
                self.results[self.current_element()] = [contents]

        self.element_position.pop()

    def characters(self, content):
        # NOTE: It is possible that the actual contents of the tag
        # gets split into multiple pieces. This method will be called
        # for each of the pieces. This means we have to concatenate
        # everything ourselves.
        if self.current_element() in self.tag_names:
            self.current_value.append(content)

    def current_element(self):
        return self.element_position[-1]

    def check_results_validity(self):
        """Make sure that all results arrays have equal length.

        We should have received complete rows from DBS. I.e. all
        results arrays in the handler should be of equal length.

        """

        results_valid = True

        res_names = self.results.keys()
        if len(res_names) > 1:
            for res_name in res_names[1:]:
                res_tmp = self.results[res_name]
                if len(res_tmp) != len(self.results[res_names[0]]):
                    results_valid = False

        return results_valid

    # End of DBSXMLHandler.
