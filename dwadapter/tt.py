from dwadapter.adapater import DatawayAdapter

d = DatawayAdapter()

tags = {"city":"bj",
        # "bj":2
        }

fields = {"int":10,
          "float":6.4,
          "str":"abc",
          # "a":[],
          "tf":True}
timestamp = 1234567890123456789
# print(d.MakeMetricsStr("SDK", tags=tags, fields=fields, timestamp=timestamp))

# WriteKeyEvent(self, title, timestamp, des=None, link=None, source=None, tags=None):
# print(d.MakeEventStr("keyevent", title="提交", timestamp=1, des="des", link="link", source="source", tags=tags))
#
print(d.MakeFlowStr("Flow", traceid="trace1234", name="提交", parent="直接负责人", flowtype="请假", duration=200, tags=None,  fields= None, timestamp=timestamp))