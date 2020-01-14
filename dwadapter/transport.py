import sys
import requests
import gzip

class TransportMixinBase:

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

    transport_required_name = ["dataway_url"]
    hearders = {"Content-Encoding":"gzip", "X-Datakit-UUID":"xxxxxxx"}

    def __init__(self, **kwargs):
        self.transport_kwargs = dict()

        for name in self.transport_required_name:
            assert name in kwargs.keys(), (
                "Expected a `{}` key-word parameter in Class `{}`, but it missed.".format(name, self.__class__.__name__)
            )
            self.transport_kwargs[name] = kwargs.pop(name)

    def create(self):
        pass

    def transport(self, data):
        compress_data = gzip.compress(data.encode())
        pesponse = requests.post(url = self.transport_kwargs.get("dataway_url"), headers = self.hearders,
                                 data = compress_data)
        return pesponse.status_code

    def close(self):
        pass


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







