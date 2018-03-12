from IPy import IP
from .base import RegexDetector
from ..filth.ip import FilthyIP


class IPv4Detector(RegexDetector):
    filth_cls = FilthyIP

    def iter_filth(self, text):
        for word in text.split(' '):
            if word and len(word.split('.')) == 4 or len(word.split(':')) > 2:
                try:
                    IP(str(word))  # inputs are unicode and most python2.X lib's prefer ascii
                except:
                    continue
                else:
                    index = text.find(word)
                    if index != -1:  # this should never happen but ill validate just in case
                        yield FilthyIP(beg=index, end=(index + len(word)), text=word)
