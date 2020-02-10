import sys
from collections import OrderedDict
import json
import re
from dwadapter.transport import HttpTransportMixin, TcpTransportMixin, UdpTransportMixin
from dwadapter.check import check_metrics

class DatawayBase:
    EVENT_MEASUREMENT = "$keyevent"
    FLOW_MEASUREMENT  = "$flow"

    adapter_required_para = ["app"]
    def __init__(self, **kwargs):
        self.adapter_kwargs = dict()

        for name in self.adapter_required_para:
            assert name in kwargs.keys(), (
                "Expected a `{}` key-word parameter in Class `{}`, but it missed.".format(name, self.__class__.__name__)
            )
            self.adapter_kwargs[name] = kwargs.pop(name)

        if not self._check_app(self.adapter_kwargs["app"]):
            raise ValueError("app parameter error.")
        self.FLOW_MEASUREMENT += "_"+self.adapter_kwargs["app"]

        super().__init__(**kwargs)

    def _check_app(self, app):
        if not isinstance(app, str) or len(app) > 40:
            return False
        return re.search(r'[^\w-]', app) == None

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


    def WriteFlow(self, traceid, name, parent, duration, timestamp, tags=None, fields=None):
        """
        :param traceid: 必需；字符串类型
        :param name: 必需；字符串类型
        :param parent: 必需；字符串类型
        :param duration: 必需；整型，毫秒单位
        :param timestamp: 必需；整型，时间戳，纳秒单位
        :param tags: 非必需；字典，key与value均为字符串类型
        :param fields: 非必需；字典，key为字符串类型，value为字符串，整型，浮点型或者布尔型之一
        :return: 成功返回True，失败返回False
        """
        raise NotImplementedError("Class `{}` must implemente method `{}`.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))


    def _conv_field_str(self, value):
        type_str = type(value).__name__
        if type_str == "int":
            return "{}i".format(value)
        elif type_str == "str":
            return '"{}"'.format(value)
        else:
            return "{}".format(value)


    def make_proto_str(self, measurement, tags, fields, timestamp):
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

            line_proto_data += "{}{}={}".format(prefix, key, self._conv_field_str(val))


        line_proto_data += " {}".format(timestamp)
        line_proto_data += "\n"
        return line_proto_data


    def make_json_str(self, measurement, tags, fields, timestamp):
        tags_list = []
        fields_list = []

        if tags:
            for k, v in tags.items():
                tags_list.append({"k":k, "v":v})

        for k, v in fields.items():
            if isinstance(v, bool):
                fields_list.append({"k": k, "v": v, "t": "b"})
            elif isinstance(v, int):
                fields_list.append({"k":k, "v":v, "t":"i"})
            else:
                fields_list.append({"k": k, "v": v})

        d = [{
            "M": measurement,
            "T": tags_list,
            "F": fields_list,
            "TS": timestamp,
            # "TP": "ns"
        }]

        return json.dumps(d)



    def make_metrics_str(self, measurement, tags, fields, timestamp):
        if not check_metrics(measurement, tags, fields, timestamp):
            return None

        return self.make_json_str(measurement, tags, fields, timestamp)


    def make_event_str(self, measurement, title, des, link, source, tags, timestamp):
        if tags is None:
            tags = {}
        elif not isinstance(tags, dict) and not isinstance(tags, OrderedDict):
            return None
        tags = tags.copy()
        # source类型由check_metrics检查
        if source is not None:
            tags["$source"] = source

        fields = {}
        # title字段必填且为字符串
        if title is None or not isinstance(title, str):
            return None
        fields["$title"] = title
        # des为选填，若填则必为字符串类型
        if des is not None:
            if not isinstance(des, str):
                return None
            fields["$des"] =des
        # link为选填，若填则必为字符串类型
        if link is not None:
            if not isinstance(link, str):
                return None
            fields["$link"] = link

        if not check_metrics(measurement, tags, fields, timestamp):
            return None

        return self.make_json_str(measurement, tags, fields, timestamp)


    def make_flow_str(self, measurement, traceid, name, parent, duration, tags, fields, timestamp):
        if tags is None:
            tags = {}
        elif not isinstance(tags, dict) and not isinstance(tags, OrderedDict):
            return None
        tags = tags.copy()
        tags["$traceId"] = traceid
        tags["$name"]    = name
        tags["$parent"]  = parent

        if not isinstance(duration, int):
            return None

        if fields is None:
            fields = {}
        elif not isinstance(fields, dict) and not isinstance(fields, OrderedDict):
            return None
        fields = fields.copy()

        fields["$duration"] = duration

        if not check_metrics(measurement, tags, fields, timestamp):
            return None

        return self.make_json_str(measurement, tags, fields, timestamp)


class DatawayAdapter(DatawayBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def WriteMetrics(self, measurement, timestamp, fields, tags=None):
        r = 0
        data = self.make_metrics_str(measurement, tags, fields, timestamp)
        if data:
            r = self.transport(data)
        return r == 200


    def WriteKeyEvent(self, title, timestamp, des=None, link=None, source=None, tags=None):
        r = 0
        data = self.make_event_str(self.EVENT_MEASUREMENT, title, des, link, source, tags, timestamp)
        if data:
            print(data)
            r = self.transport(data)
        return r == 200


    def WriteFlow(self, traceid, name, parent, duration, timestamp, tags=None, fields=None):
        r = 0
        data = self.make_flow_str(self.FLOW_MEASUREMENT, traceid, name, parent, duration, tags, fields, timestamp)
        if data:
            print(data)
            r = self.transport(data)
        return r == 200


class DatawayHttpAdapter(DatawayAdapter, HttpTransportMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DatawayTcpAdapter(DatawayAdapter, TcpTransportMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DatawayUdpAdapter(DatawayAdapter, UdpTransportMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
