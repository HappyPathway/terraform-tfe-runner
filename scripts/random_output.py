import random
import string
import json

random = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
print(json.dumps(dict(random=random)))