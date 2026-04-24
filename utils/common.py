
import hashlib


def get_md5(content):
    if isinstance(content, str):
        content = content.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(content)
    return md5.hexdigest()
