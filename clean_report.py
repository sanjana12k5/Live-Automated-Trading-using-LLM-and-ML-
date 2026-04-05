import codecs
import re

with codecs.open('final_report.txt', 'r', 'utf-16') as f:
    text = f.read()

# Replace all \r with newline if it's acting weird, or just split by \r
lines = text.replace('\r', '\n').split('\n')
lines = [l.strip() for l in lines if l.strip() and not l.startswith('Processed candle')]

print('\n'.join(lines[-40:]))
