import sys
from dwadapter.transport import HttpTransportMixin, TcpTransportMixin, UdpTransportMixin
from dwadapter.check import CheckMetrics
import time

class DatawayBase:
    EVENT_MEASUREMENT = "keyevent"
    FLOW_MEASUREMENT  = "flow"
    def __call__(self, msg):
        self.hander(msg)
        return True

    def hander(self, msg):
        raise NotImplementedError("Class `{}` must implemente method `{}`.".format(self.__class__.__name__,

                                                                         sys._getframe().f_code.co_name))
    def WriteMetrics(self, measurement, timestamp, fields, tags=None):
        """
        :param measurement: 必需；字符串类型
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param fields: 必需；字典，key为字符串类型，value为字符串，整型，浮点型或者布尔型之一
        :param tags: 非必需；字典，key与value均为字符串类型
        :return: 成功返回True，失败返回False
        """
        raise NotImplementedError("Class `{}` must implemente method `{}`.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))

    def WriteKeyEvent(self, title, timestamp, des=None, link=None, source=None, tags=None):
        """
        :param title: 必需；字符串类型
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param des: 非必需；字符串类型
        :param link: 非必需；字符串类型
        :param source: 非必需；字符串类型
        :param tags: 非必需；字典，key与value均为字符串类型
        :return: 成功返回True，失败返回False
        """
        raise NotImplementedError("Class `{}` must implemente method `{}`.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))

    def WriteFlow(self, traceid, name, parent, flowtype, duration, timestamp, tags=None, fields=None):
        """
        :param traceid: 必需；字符串类型
        :param name: 必需；字符串类型
        :param parent: 必需；字符串类型
        :param flowtype: 必需；字符串类型
        :param duration: 必需；整型，毫秒单位
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param tags: 非必需；字典，key与value均为字符串类型
        :param fields: 非必需；字典，key为字符串类型，value为字符串，整型，浮点型或者布尔型之一
        :return: 成功返回True，失败返回False
        """
        raise NotImplementedError("Class `{}` must implemente method `{}`.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))

    def _ConvFiledValToStr(self, value):
        type_str = type(value).__name__
        if type_str == "int":
            return "{}i".format(value)
        elif type_str == "str":
            return '"{}"'.format(value)
        else:
            return "{}".format(value)

    def MakeLineProtoData(self, measurement, tags, fields, timestamp):
        line_proto_data = ""
        line_proto_data += "{}".format(measurement)
        is_frist_field = True
        #tags可选
        if tags:
            for key, val in tags.items():
                line_proto_data += ",{}={}".format(key, val)
        # fields必填
        for key, val in fields.items():
            if is_frist_field:
                prefix = " "
                is_frist_field = False
            else:
                prefix = ","

            line_proto_data += "{}{}={}".format(prefix, key, self._ConvFiledValToStr(val))

        line_proto_data += " {}".format(timestamp)
        line_proto_data += "\n"
        return line_proto_data

    def MakeMetricsStr(self, measurement, tags, fields, timestamp):
        if not CheckMetrics(measurement, tags, fields, timestamp):
            return None

        return self.MakeLineProtoData(measurement, tags, fields, timestamp)

    def MakeEventStr(self, measurement, title, des, link, source, tags, timestamp):
        if tags is None:
            tags = {}
        if not isinstance(tags, dict):
            return None
        # source类型由CheckMetrics检查
        if source is not None:
            tags["source"] = source

        fields = {}
        # title字段必填且为字符串
        if title is None or type(title).__name__ != "str":
            return None
        fields["title"] = title
        # des为选填，若填则必为字符串类型
        if des is not None:
            if type(des).__name__ != "str":
                return None
            fields["des"] =des
        # des为选填，若填则必为字符串类型
        if link is not None:
            if type(link).__name__ != "str":
                return None
            fields["link"] = link

        if not CheckMetrics(measurement, tags, fields, timestamp):
            return None

        return self.MakeLineProtoData(measurement, tags, fields, timestamp)


    def MakeFlowStr(self, measurement, traceid, name, parent, flowtype, duration, tags, fields, timestamp):
        if tags is None:
            tags = {}
        if not isinstance(tags, dict):
            return None
        tags["traceId"] = traceid
        tags["name"]    = name
        tags["parent"]  = parent
        tags["type"]    = flowtype

        if fields is None:
            fields = {}
        if not isinstance(fields, dict):
            return None
        if type(duration).__name__ != "int":
            return None
        fields["duration"] = duration

        if not CheckMetrics(measurement, tags, fields, timestamp):
            return None

        return self.MakeLineProtoData(measurement, tags, fields, timestamp)


class DatawayAdapter(DatawayBase):
    def WriteMetrics(self, measurement, timestamp, fields, tags=None):
        r = 0
        data = self.MakeMetricsStr(measurement, tags, fields, timestamp)
        if data:
            r = self.transport(data)
        return r == 200


    def WriteKeyEvent(self, title, timestamp, des=None, link=None, source=None, tags=None):
        r = 0
        data = self.MakeEventStr(self.EVENT_MEASUREMENT, title, des, link, source, tags, timestamp)
        if data:
            r = self.transport(data)
        return r == 200

    def WriteFlow(self, traceid, name, parent, flowtype, duration, timestamp, tags=None, fields=None):
        r = 0
        data = self.MakeFlowStr(self.FLOW_MEASUREMENT, traceid, name, parent, flowtype, duration, tags, fields, timestamp)
        if data:
            r = self.transport(data)
        return r == 200


class DatawayHttpAdapter(DatawayAdapter, HttpTransportMixin):

    def __init__(self, **kwargs):
        HttpTransportMixin.__init__(self, **kwargs)


class DatawayTcpAdapter(DatawayAdapter, TcpTransportMixin):

    def __init__(self, **kwargs):
        HttpTransportMixin.__init__(self, **kwargs)


class DatawayUdpAdapter(DatawayAdapter, UdpTransportMixin):

    def __init__(self, **kwargs):
        HttpTransportMixin.__init__(self, **kwargs)
