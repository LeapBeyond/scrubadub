from .base import Filth


class UrlFilth(Filth):
    type = 'url'

    # This allows you to keep the domain
    keep_domain = False

    # this can be used to customize the output, particularly when
    # keep_domain=True
    url_placeholder = type.upper()

    @property
    def placeholder(self):
        if self.keep_domain:
            return self.match.group('domain') + self.url_placeholder
        return self.url_placeholder
