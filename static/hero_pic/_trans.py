import os
import re

for s in os.listdir('.'):
    if s.find('icon0') == -1 and s.find('.png') > -1:
        s2 = s.replace('_', ' ')
        s2 = s2.replace('240px-', '')
        s2 = s2.replace(' icon', '')
        print(s, s2)
        os.rename(s, s2)