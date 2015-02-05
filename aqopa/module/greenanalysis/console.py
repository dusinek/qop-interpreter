#!/usr/bin/env python

import sys
from aqopa.simulator.state import Hook

"""
@file       console.py
@author     Katarzyna Mazur
"""

class PrintResultsHook(Hook):

    def __init__(self, module, simulator, output_file=sys.stdout):
        """ """
        self.module = module
        self.simulator = simulator
        self.output_file = output_file

    def execute(self, context, **kwargs):
        """ """

        self.output_file.write('-'*20)
        self.output_file.write('\n')
        self.output_file.write('Module\tCarbon Dioxide Emissions Analysis (pounds of CO2 produced per kWh)')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n' % self.simulator.context.version.name)

        # temp default value
        pounds_of_co2_per_kWh = 1.85

        emissions = self.module.get_all_emissions(self.simulator)