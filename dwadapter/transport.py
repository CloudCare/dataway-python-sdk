import sys
import requests
import gzip
import datetime
import hashlib
import hmac
import base64


class TransportMixinBase:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self):
        raise NotImplementedError("Class {} must implemente method {}.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))


    def transport(self, data):
        raise NotImplementedError("Class {} must implemente method {}.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))


    def close(self):
        raise NotImplementedError("Class {} must implemente method {}.".format(self.__class__.__name__,
                        sys._getframe().f_code.co_name))


class HttpTransportMixin(TransportMixinBase):
    transport_required_para = ["dataway_url"]
    transport_authen_para   = ["pk","sk"]
    content_type   = "application/json"
    content_coding = "gzip"
    uuid = "default_uuid"

    def __init__(self, **kwargs):
        self.transport_kwargs = dict()
        self._authenticate = True

        for name in self.transport_required_para:
            assert name in kwargs.keys(), (
                "Expected a `{}` key-word parameter in Class `{}`, but it missed.".format(name, self.__class__.__name__)
            )
            self.transport_kwargs[name] = kwargs.pop(name)

        for name in self.transport_authen_para:
            if name not in kwargs.keys():
                self._authenticate = False
                break
            self.transport_kwargs[name] = kwargs.pop(name)

        if "uuid" in kwargs.keys():
            self.transport_kwargs["uuid"] = kwargs.pop("uuid")
        else:
            self.transport_kwargs["uuid"] = self.uuid

        super().__init__(**kwargs)


    def create(self):
        pass

    def transport(self, data):
        compress_data = gzip.compress(data.encode())
        header = self._build_http_heraer(compress_data)
        pesponse = requests.post(url = self.transport_kwargs.get("dataway_url"), headers = header,
                                 data = compress_data)
        return pesponse.status_code

    def close(self):
        pass


    def _build_http_heraer(self, data):
        header = {}
        date = self._http_date()
        header["Content-Encoding"] = self.content_coding
        header["Content-Type"]     = self.content_type
        header["X-Datakit-UUID"]   = self.transport_kwargs["uuid"]
        header["Date"]             = date

        if self._authenticate:
            header["Authorization"] = self._makeAuthorization(data, date)
        return header


    def _makeAuthorization(self, data, date):
        signature = "DWAY " + self.transport_kwargs["pk"] + ":"
        cont_md5 = hashlib.md5(data).digest()
        cont_md5 = base64.standard_b64encode(cont_md5).decode()
        s = "POST" + "\n" + cont_md5 + "\n" + self.content_type + "\n" + date
        return signature + self._hash_hmac(self.transport_kwargs["sk"], s)


    def _hash_hmac(self, key, code):
        hmac_code = hmac.new(key.encode(), digestmod=hashlib.sha1)
        hmac_code.update(code.encode())
        bs = hmac_code.digest()
        return base64.standard_b64encode(bs).decode()


    def _http_date(self):
        dt = datetime.datetime.utcnow()
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "{}, {:02d} {} {:4d} {:02d}:{:02d}:{:02d} GMT".format(weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)


class TcpTransportMixin(TransportMixinBase):

    def create(self):
        pass

    def transport(self, data):
        pass

    def close(self):
        pass


class UdpTransportMixin(TransportMixinBase):

    def create(self):
        pass

    def transport(self, data):
        pass

    def close(self):
        pass







