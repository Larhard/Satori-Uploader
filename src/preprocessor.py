def process(file_name, data):
    # TODO sed preprocessors

    if re.search('\.java$', file_name):
        # remove package keyword
        data = re.sub("\A(?P<commentary>(^\s*//.*$[\n\r]*)*)(?P<package>^\s*package.*$)",
                      "\\g<commentary>//\\g<package>",
                      data,
                      flags=re.MULTILINE)

    if re.search('\.(c|cpp)$', file_name):
        # include local
        includes = re.finditer('^\s*#include\s*"([^"]*)"\s*$', data, re.MULTILINE)
        for i in includes:
            print(i.group(1))
            # open(i.group(1)).read()
            data = open(i.group(1)).read().join(data.split(i.group(0)))
            # data = open(i.group(1)).join()
            # data = re.sub(i.group(0), "---", data, re.MULTILINE)
    return data
