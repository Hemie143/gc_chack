import hashlib
import sqlite3
import os

table_filename = 'rainbow.sqlite'
max_value = 99999

try:
    os.remove(table_filename)
except:
    pass

conn = sqlite3.connect(table_filename)
c = conn.cursor()
c.execute("CREATE TABLE rainbow (code text, hash text)")
c.execute("CREATE UNIQUE INDEX idx_hash ON rainbow (hash)")
conn.commit()

for i in range(max_value+1):
    if i % 500 == 0:
        print(f'Index {i}')
    text = f'{i:05}'
    hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    c.execute("INSERT INTO rainbow VALUES (?, ?)", (text, hash))
    conn.commit()

conn.close()

conn = sqlite3.connect(table_filename)
c = conn.cursor()
c.execute("SELECT * from rainbow where code=:text", {"text": "38575"})
print(c.fetchall())
t = ("00012",)
c.execute("SELECT * from rainbow WHERE code=?", t)
print(c.fetchall())

m = hashlib.md5()
m.update(b'38575')
print(m.hexdigest())

m = hashlib.md5()
m.update(b'38575')
print(m.hexdigest())

m = hashlib.md5(b'38575').hexdigest()
print(m)

conn.close()

# 38575
# d145f7efd8e7183b2cbc586ccfb1d0ec