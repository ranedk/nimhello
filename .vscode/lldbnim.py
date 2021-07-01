import lldb
import os


def NimStringDesc_SummaryFormatter(valobj, internal_dict):
    s = '<error>'
    try:
        nonSynth = valobj.GetNonSyntheticValue()
        data = nonSynth.GetChildMemberWithName('data').AddressOf()
        data.SetFormat(lldb.eFormatCString)
        s = data.GetValue()
    except:
        pass
    return s

class NimSeqProvider:

    def __init__(self, valobj, dict):
        self.valobj = valobj

    def num_children(self):
        try:
            self.count = self.len.GetValueAsUnsigned(0)
            return self.count
        except:
            return None

    def get_child_at_index(self, index):
        try:
            offset = index * self.data_size
            return self.start.CreateChildAtOffset(
                '[' + str(index) + ']', offset, self.data_type)
        except:
            return None

    def get_child_index(self, name):
        try:
            return int(name.lstrip('[').rstrip(']'))
        except:
            return None

    def update(self):
        try:
            data = self.valobj.GetChildMemberWithName('data')
            self.start = data
            self.sup = self.valobj.GetChildMemberWithName('Sup')
            self.len = self.sup.GetChildMemberWithName('len')
            self.reserved = self.sup.GetChildMemberWithName('reserved')
            self.data_type = data.GetType().GetArrayElementType()
            self.data_size = self.data_type.GetByteSize()
        except:
            pass

    def has_children(self):
        return True

def NimSeq_SummaryFormatter(valobj, internal_dict):
    s = '<error>'
    try:
        nonSynth = valobj.GetNonSyntheticValue()
        sup = nonSynth.GetChildMemberWithName('Sup')
        len = sup.GetChildMemberWithName('len')
        reserved = sup.GetChildMemberWithName('reserved')
        s = "{ len=" + str(len.GetValueAsSigned()) + ", reserved=" + str(reserved.GetValueAsSigned()) + " }"
    except:
        pass
    return s

def NimArray_SummaryFormatter(valobj, internal_dict):
    s = '<error>'
    try:
        arrayType = valobj.GetType()
        elemType = arrayType.GetArrayElementType()
        size = int(arrayType.GetByteSize() / elemType.GetByteSize())
        s = "{ size=" + str(size) + " }"
    except:
        pass
    return s

class NimTableProvider:

    def __init__(self, valobj, dict):
        self.valobj = valobj

    def num_children(self):
        try:
            return len(self.ary)
        except:
            return None

    def get_child_at_index(self, index):
        try:
            return self.ary[index]
        except:
            return None

    def get_child_index(self, name):
        try:
            key = int(name.lstrip('[').rstrip(']'))
            return self.table.get(key)
        except:
            return None

    def num_elem_children(self):
        try:
            self.seqCount = self.len.GetValueAsUnsigned(0)
            if self.seqCount < 0 or self.seqCount > 1000000:
                self.seqCount = 0
            return self.seqCount
        except:
            return None

    def get_elem_at_index(self, index):
        try:
            offset = index * self.data_size
            return self.start.CreateChildAtOffset(
                '[' + str(index) + ']', offset, self.data_type)
        except:
            return None

    def update(self):
        try:
            self.seq = self.valobj.GetChildMemberWithName('data').GetNonSyntheticValue()
            data = self.seq.GetChildMemberWithName('data')
            self.start = data
            self.sup = self.seq.GetChildMemberWithName('Sup')
            self.len = self.sup.GetChildMemberWithName('len')
            self.reserved = self.sup.GetChildMemberWithName('reserved')
            self.data_type = data.GetType().GetArrayElementType()
            self.data_size = self.data_type.GetByteSize()
            self.table = {}
            self.ary = []
            count = self.num_elem_children()
            if count > 1000:
                count = 1000
            for i in range(self.num_elem_children()):
                elem = self.get_elem_at_index(i)
                field0 = elem.GetChildMemberWithName('Field0')
                hash = field0.GetValueAsUnsigned()
                if hash != 0:
                    field1 = elem.GetChildMemberWithName('Field1')
                    key = field1.GetSummary()
                    if key is None:
                        key = str(field1.GetValue())
                    field2 = elem.GetChildMemberWithName('Field2').GetNonSyntheticValue()
                    value = field2.CreateValueFromAddress(key, field2.GetLoadAddress(), field2.GetType())
                    self.table[key] = len(self.ary)
                    self.ary.append(value)
        except:
            pass

    def has_children(self):
        return True

def NimTable_SummaryFormatter(valobj, internal_dict):
    s = '<error>'
    try:
        nonSynth = valobj.GetNonSyntheticValue()
        counter = nonSynth.GetChildMemberWithName('counter')
        s = "{ counter=" + str(counter.GetValueAsSigned()) + " }"
    except:
        pass
    return s

def __lldb_init_module(debugger, internal_dict):

    print("Initializing LLDB Nim helper")
    category = debugger.GetDefaultCategory()
    category.SetEnabled(True)

    category.AddTypeSynthetic(\
        lldb.SBTypeNameSpecifier("NimStringDesc"),\
        lldb.SBTypeSynthetic.CreateWithClassName("lldbnim.NimSeqProvider",
                                                 lldb.eTypeOptionCascade))

    category.AddTypeSummary(lldb.SBTypeNameSpecifier('NimStringDesc'), \
        lldb.SBTypeSummary.CreateWithFunctionName('lldbnim.NimStringDesc_SummaryFormatter'))

    category.AddTypeSynthetic(\
        lldb.SBTypeNameSpecifier("^tySequence__.*$", True),\
        lldb.SBTypeSynthetic.CreateWithClassName("lldbnim.NimSeqProvider",
                                                 lldb.eTypeOptionCascade))

    category.AddTypeSummary(\
        lldb.SBTypeNameSpecifier("^tySequence__.*$", True),\
        lldb.SBTypeSummary.CreateWithFunctionName('lldbnim.NimSeq_SummaryFormatter'))

    category.AddTypeSummary(\
        lldb.SBTypeNameSpecifier("^tyArray__.*$", True),\
        lldb.SBTypeSummary.CreateWithFunctionName('lldbnim.NimArray_SummaryFormatter'))

    category.AddTypeSynthetic(\
        lldb.SBTypeNameSpecifier("^tyObject_Table__.*$", True),\
        lldb.SBTypeSynthetic.CreateWithClassName("lldbnim.NimTableProvider",
                                                 lldb.eTypeOptionCascade))

    category.AddTypeSummary(\
        lldb.SBTypeNameSpecifier("^tyObject_Table__.*$", True),\
        lldb.SBTypeSummary.CreateWithFunctionName('lldbnim.NimTable_SummaryFormatter'))
