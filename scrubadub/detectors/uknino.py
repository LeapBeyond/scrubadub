import re, scrubadub


class NewNINODetector(scrubadub.detectors.Detector):
    name = 'NewNINODetector'
    filth_cls = scrubadub.filth.Filth.UkNino
    regex = re.compile(r"(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}([A-D]|\s)", re.IGNORECASE)
    scrubber = scrubadub.Scrubber()
    scrubber.add_detector(NewNINODetector())
    text = u"This url will be found https://example.com, NINO: ZB 79 53 67 A"
    scrubber.clean(text)