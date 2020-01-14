import nsq


class NsqAgent:
    nsq_required_name = ["nsq_url", "topic", "channel", "handler"]

    def __init__(self, **kwargs):
        self.nsq_kwargs = dict()

        for name in self.nsq_required_name:
            assert name in kwargs.keys(), (
                "Expected a `{}` key-word parameter in Class `{}`, but it missed.".format(name, self.__class__.__name__)
            )
            self.nsq_kwargs[name] = kwargs.pop(name)


    def start(self):
        nsq.Reader(message_handler = self.nsq_kwargs["handler"],
                                 lookupd_http_addresses = [self.nsq_kwargs["nsq_url"]],
                                 topic = self.nsq_kwargs["topic"],
                                 channel = self.nsq_kwargs["channel"], max_in_flight=9)
        nsq.run()
