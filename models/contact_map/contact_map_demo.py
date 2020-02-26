#! /usr/bin/env python3

import matplotlib.pyplot as plt
from KaSaAn.core import KappaContactMap

my_contact_map = KappaContactMap('inputs.ka')
fig, ax = plt.subplots(figsize=(8, 8))

my_contact_map.move_agent_to('Fitz', 5, 5)
my_contact_map.move_agent_to('Foo', 10, 15)
my_contact_map.move_agent_to('Bar', 12.5, 5)
my_contact_map.move_agent_to('Baz', 0, 12.5)

my_contact_map.rotate_all_sites_of('Foo', 150)
my_contact_map.rotate_all_sites_of('Baz', -150)
my_contact_map.rotate_all_sites_of('Fitz', 30)
my_contact_map.rotate_all_sites_of('Bar', 30)

my_contact_map.draw(ax, draw_state_flagpole=True)
ax.axis('off')

fig.savefig('contact_map.png')
plt.show()
