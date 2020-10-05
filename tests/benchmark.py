import re
import sys
import faker
import random
import timeit


def make_fake_document(paragraphs=20, seed=1234):
    fake = faker.Faker()

    fake_functions = [
        fake.phone_number,
        fake.name,
        fake.address,
        fake.url,
        fake.email,
    ]

    faker.Faker.seed(seed)
    random.seed(seed)

    doc = ""
    for i_paragraph in range(paragraphs):
        for i_sentance_group in range(random.randint(1,10)):
            text = fake.text()
            matches = list(re.finditer(r'[\s.]', text))
            position = random.choice(matches)
            pii_function = random.choice(fake_functions)
            doc += (
                text[:position.start()] +
                position.group() +
                pii_function() +
                position.group() +
                text[position.end():]
            )
        doc += "\n\n"
    return doc.strip()


def main():
    doc = make_fake_document(paragraphs=20, seed=1234)
    variables = {'doc': doc}
    setup_cmd = 'import scrubadub; scrubber = scrubadub.Scrubber()'
    cmd = 'scrubber.clean(doc)'

    print("Timing '{}':".format(cmd))
    repeats = 100
    timer = timeit.Timer(cmd, setup=setup_cmd, globals=variables)
    try:
        time = timer.timeit(number=repeats)
    except Exception:
        timer.print_exc()
        sys.exit(1)
    else:
        print("{: >8.4f}s total runtime".format(time))
        print("{: >8.4f}s per iteration".format(time/repeats))
    sys.exit(0)


if __name__ == "__main__":
    main()
