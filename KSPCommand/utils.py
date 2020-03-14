import os
PROVISIONING_SCRIPT = open(
    os.path.join(os.path.dirname(__file__), 'provision.sh')).read()

ASSET_URL = "https://raw.githack.com/dmadisetti/KSPCommand/master"


def split_int(i):
    if i < 4:
        return 1, i

    factors = sum([[
        k,
    ] * v for k, v in factorint(i).items()], [])
    if len(factors) == 1:
        return split_int(i + 1)

    a = b = 1
    while len(factors) > 0:
        if min(a, b) == a:
            a *= factors.pop()
        else:
            b *= factors.pop()
        factors.reverse()
    return a, b
