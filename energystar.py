#!/usr/bin/env python
# -*- coding: utf-8; indent-tabs-mode: nil; tab-width: 4; c-basic-offset: 4; -*-
#
# Copyright (C) 2014 Canonical Ltd.
# Author: Shih-Yuan Lee (FourDollars) <sylee@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import math
import subprocess

def debug(msg):
    if args.debug:
        print("\033[93mDEBUG:\033[0m %s" % (msg))

def warning(msg):
    print("\033[91mWARNING:\033[0m %s" % (msg))

def question_str(prompt, length, validator):
    while True:
        s = raw_input(prompt + "\n>> ")
        if len(s) == length and set(s).issubset(validator):
            print('-'*80)
            return s
        print("The valid input '" + validator + "'.")

def question_bool(prompt):
    while True:
        s = raw_input(prompt + " [y/n]\n>> ")
        if len(s) == 1 and set(s).issubset("YyNn01"):
            print('-'*80)
            if s == 'Y' or s == 'y' or s == '1':
                return True
            else:
                return False

def question_int(prompt, maximum):
    while True:
        s = raw_input(prompt + "\n>> ")
        if set(s).issubset("0123456789"):
            try:
                num = int(s)
                if num <= maximum:
                    print('-'*80)
                    return num
            except ValueError:
                print("Please input a positive integer less than or equal to %s." % (maximum))
        print("Please input a positive integer less than or equal to %s." % (maximum))

def question_num(prompt):
    while True:
        s = raw_input(prompt + "\n>> ")
        try:
            num = float(s)
            print('-'*80)
            return num
        except ValueError:
            print "Oops!  That was no valid number.  Try again..."


class SysInfo:
    def __init__(self,
            auto=False,
            cpu_core=0,
            cpu_clock=0.0,
            mem_size=0.0,
            disk_num=0,
            diagonal=0,
            ep=False,
            width=0,
            height=0,
            product_type=0,
            computer_type=0,
            off=0,
            sleep=0,
            long_idle=0,
            short_idle=0,
            eee=0,
            discrete=False,
            switchable=False,
            power_supply='',
            max_power=0,
            more_discrete=False,
            media_codec=False,
            integrated_display=False):
        self.auto = auto
        self.cpu_core = cpu_core
        self.cpu_clock = cpu_clock
        self.mem_size = mem_size
        self.disk_num = disk_num
        self.width = width
        self.height = height
        self.diagonal = diagonal
        self.ep = ep
        self.product_type = product_type
        self.computer_type = computer_type
        self.eee = eee
        self.off = off
        self.sleep = sleep
        self.long_idle = long_idle
        self.short_idle = short_idle
        self.discrete = discrete
        self.switchable = switchable
        self.power_supply = power_supply
        self.max_power = max_power
        self.more_discrete = more_discrete
        self.media_codec = media_codec
        self.integrated_display = integrated_display

        if not auto:
            # Product type
            self.product_type = question_int("""Which product type would you like to verify?
 [1] Desktop, Integrated Desktop, and Notebook Computers
 [2] Workstations
 [3] Small-scale Servers
 [4] Thin Clients""", 4)

            if self.product_type == 1:
                # Computer type
                self.computer_type = question_int("""Which type of computer do you use?
 [1] Desktop
 [2] Integrated Desktop
 [3] Notebook""", 3)

                # GPU Information
                if question_bool("Does it have switchable graphics and automated switching enabled by default?"):
                    self.switchable = True
                    # Those with switchable graphics may not apply the Discrete Graphics allowance.
                    self.discrete = False
                else:
                    self.switchable = False
                    if question_bool("Is there a discrete graphics device?"):
                        self.discrete = True
                    else:
                        self.discrete = False

                # Screen size
                if self.computer_type != 1:
                    self.diagonal = question_num("What is the display diagonal in inches?")
                    self.ep = question_bool("Is there an Enhanced-perforcemance Integrated Display?")

                # Gigabit Ethernet
                self.eee = question_num("How many IEEE 802.3az­compliant (Energy Efficient Ethernet) Gigabit Ethernet ports?")

                # Power Supply
                if self.computer_type != 3:
                    self.power_supply = question_str("Does it use external power supply or internal power supply? [e/i]", 1, "ei")
                else:
                    self.power_supply = 'e'

                # Power Consumption
                self.off = question_num("What is the power consumption in Off Mode?")
                self.sleep = question_num("What is the power consumption in Sleep Mode?")
                self.long_idle = question_num("What is the power consumption in Long Idle Mode?")
                self.short_idle = question_num("What is the power consumption in Short Idle Mode?")
            elif self.product_type == 2:
                self.off = question_num("What is the power consumption in Off Mode?")
                self.sleep = question_num("What is the power consumption in Sleep Mode?")
                self.long_idle = question_num("What is the power consumption in Long Idle Mode?")
                self.short_idle = question_num("What is the power consumption in Short Idle Mode?")
                self.max_power = question_num("What is the maximum power consumption?")
                self.eee = question_num("How many IEEE 802.3az­compliant (Energy Efficient Ethernet) Gigabit Ethernet ports?")
            elif self.product_type == 3:
                self.off = question_num("What is the power consumption in Off Mode?")
                self.short_idle = question_num("What is the power consumption in Short Idle Mode?")
                self.eee = question_num("How many IEEE 802.3az­compliant (Energy Efficient Ethernet) Gigabit Ethernet ports?")
                if self.get_cpu_core() < 2:
                    self.more_discrete = question_bool("Does it have more than one discrete graphics device?")
            elif self.product_type == 4:
                self.off = question_num("What is the power consumption in Off Mode?")
                self.sleep = question_num("What is the power consumption in Sleep Mode?\n(You can input the power consumption in Long Idle Mode, if it lacks a discrete System Sleep Mode)")
                self.long_idle = question_num("What is the power consumption in Long Idle Mode?")
                self.short_idle = question_num("What is the power consumption in Short Idle Mode?")
                self.media_codec = question_bool("Does it support local multimedia encode/decode?")
                self.eee = question_num("How many IEEE 802.3az­compliant (Energy Efficient Ethernet) Gigabit Ethernet ports?")
                self.integrated_display = question_bool("Does it have integrated display?")
                if self.integrated_display:
                    self.computer_type = 2
                    self.diagonal = question_num("What is the display diagonal in inches?")
                    self.ep = question_bool("Is it an Enhanced-perforcemance Integrated Display?")

    def get_cpu_core(self):
        if self.cpu_core:
            return self.cpu_core

        try:
            subprocess.check_output('cat /proc/cpuinfo | grep cores', shell=True)
        except subprocess.CalledProcessError:
            self.cpu_core = 1
        else:
            self.cpu_core = int(subprocess.check_output('cat /proc/cpuinfo | grep "cpu cores" | sort -ru | head -n 1 | cut -d: -f2 | xargs', shell=True).strip())

        debug("CPU core: %s" % (self.cpu_core))
        return self.cpu_core

    def get_cpu_clock(self):
        if self.cpu_clock:
            return self.cpu_clock

        self.cpu_clock = float(subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | sort -u | cut -d: -f2 | cut -d@ -f2 | xargs | sed 's/GHz//'", shell=True).strip())

        debug("CPU clock: %s GHz" % (self.cpu_clock))
        return self.cpu_clock

    def get_mem_size(self):
        if self.mem_size:
            return self.mem_size

        for size in subprocess.check_output("sudo dmidecode -t 17 | grep 'Size:.*MB' | awk '{print $2}'", shell=True).split('\n'):
            if size:
                self.mem_size = self.mem_size + int(size)
        self.mem_size = self.mem_size / 1024

        debug("Memory size: %s GB" % (self.mem_size))
        return self.mem_size

    def get_disk_num(self):
        if self.disk_num:
            return self.disk_num

        self.disk_num = len(subprocess.check_output('ls /sys/block | grep sd', shell=True).strip().split('\n'))

        debug("Disk number: %s" % (self.disk_num))
        return self.disk_num

    def set_display(self, diagonal, ep):
        self.diagonal = diagonal 
        self.ep = ep

    def get_display(self):
        return (self.diagonal, self.ep)

    def get_resolution(self):
        if self.width == 0 or self.height == 0:
            (width, height) = subprocess.check_output("xrandr --current | grep current | sed 's/.*current \\([0-9]*\\) x \\([0-9]*\\).*/\\1 \\2/'", shell=True).strip().split(' ')
            self.width = int(width)
            self.height = int(height)
        debug("Resolution: %s x %s" % (self.width, self.height))
        return (self.width, self.height)

    def get_power_consumptions(self):
        return (self.off, self.sleep, self.long_idle, self.short_idle)

    def get_basic_info(self):
        return (self.get_cpu_core(), self.get_cpu_clock(), self.get_mem_size(), self.get_disk_num())

class EnergyStar52:
    """Energy Star 5.2 calculator"""
    def __init__(self, sysinfo):
        self.sysinfo = sysinfo

    def qualify_desktop_category(self, category, gpu_discrete, gpu_width):
        (core, clock, memory, disk) = self.sysinfo.get_basic_info()

        if category == 'D':
            if core >= 4:
                if memory >= 4:
                    return True
                elif gpu_width:
                    return True
        elif category == 'C':
            if core >= 2:
                if memory >= 2:
                    return True
                elif gpu_discrete:
                    return True
        elif category == 'B':
            if core == 2 and memory >= 2:
                return True
        elif category == 'A':
            return True
        return False

    def qualify_netbook_category(self, category, gpu_discrete, over_gpu_width):
        (core, clock, memory, disk) = self.sysinfo.get_basic_info()

        if category == 'C':
            if core >= 2 and memory >= 2:
                if gpu_discrete and over_gpu_width:
                    return True
        elif category == 'B':
            if gpu_discrete:
                return True
        elif category == 'A':
            return True
        return False

    def equation_one(self):
        """Equation 1: TEC Calculation (E_TEC) for Desktop, Integrated Desktop, and Notebook Computers"""
        (P_OFF, P_SLEEP, P_LONG_IDLE, P_SHORT_IDLE) = self.sysinfo.get_power_consumptions()
        P_IDLE = P_SHORT_IDLE

        if self.sysinfo.computer_type == 3:
            (T_OFF, T_SLEEP, T_IDLE) = (0.6, 0.1, 0.3)
        else:
            (T_OFF, T_SLEEP, T_IDLE) = (0.55, 0.05, 0.4)

        E_TEC = ((P_OFF * T_OFF) + (P_SLEEP * T_SLEEP) + (P_IDLE * T_IDLE)) * 8760 / 1000

        debug("T_OFF = %s, T_SLEEP = %s, T_IDLE = %s" % (T_OFF, T_SLEEP, T_IDLE))
        debug("P_OFF = %s, P_SLEEP = %s, P_IDLE = %s" % (P_OFF, P_SLEEP, P_IDLE))

        return E_TEC

    def equation_two(self, over_gpu_width):
        """Equation 2: E_TEC_MAX Calculation for Desktop, Integrated Desktop, and Notebook Computers"""

        (core, clock, memory, disk) = self.sysinfo.get_basic_info()

        result = []

        ## Maximum TEC Allowances for Desktop and Integrated Desktop Computers
        if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
            if disk > 1:
                TEC_STORAGE = 25.0 * (disk - 1)
            else:
                TEC_STORAGE = 0.0

            if self.qualify_desktop_category('A', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 148.0

                if memory > 2:
                    TEC_MEMORY = 1.0 * (memory - 2)
                else:
                    TEC_MEMORY = 0.0

                if over_gpu_width:
                    TEC_GRAPHICS = 50.0
                else:
                    TEC_GRAPHICS = 35.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('A', E_TEC_MAX))

            if self.qualify_desktop_category('B', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 175.0

                if memory > 2:
                    TEC_MEMORY = 1.0 * (memory - 2)
                else:
                    TEC_MEMORY = 0.0

                if over_gpu_width == 'y':
                    TEC_GRAPHICS = 50.0
                else:
                    TEC_GRAPHICS = 35.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('B', E_TEC_MAX))

            if self.qualify_desktop_category('C', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 209.0

                if memory > 2:
                    TEC_MEMORY = 1.0 * (memory - 2)
                else:
                    TEC_MEMORY = 0.0

                if over_gpu_width:
                    TEC_GRAPHICS = 50.0
                else:
                    TEC_GRAPHICS = 0.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('C', E_TEC_MAX))

            if self.qualify_desktop_category('D', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 234.0

                if memory > 4:
                    TEC_MEMORY = 1.0 * (memory - 4)
                else:
                    TEC_MEMORY = 0.0

                if over_gpu_width:
                    TEC_GRAPHICS = 50.0
                else:
                    TEC_GRAPHICS = 0.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('D', E_TEC_MAX))

        ## Maximum TEC Allowances for Notebook Computers
        else:
            if memory > 4:
                TEC_MEMORY = 0.4 * (memory - 4)
            else:
                TEC_MEMORY = 0.0

            if disk > 1:
                TEC_STORAGE = 3.0 * (disk - 1)
            else:
                TEC_STORAGE = 0.0

            if self.qualify_netbook_category('A', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 40.0
                TEC_GRAPHICS = 0.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('A', E_TEC_MAX))

            if self.qualify_netbook_category('B', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 53.0

                if over_gpu_width:
                    TEC_GRAPHICS = 3.0
                else:
                    TEC_GRAPHICS = 0.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('B', E_TEC_MAX))

            if self.qualify_netbook_category('C', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 88.5
                TEC_GRAPHICS = 0.0

                E_TEC_MAX = TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE
                result.append(('C', E_TEC_MAX))

        debug("TEC_BASE = %s, TEC_MEMORY = %s, TEC_STORAGE = %s, TEC_GRAPHICS = %s" % (TEC_BASE, TEC_MEMORY, TEC_STORAGE, TEC_GRAPHICS))
        debug("E_TEC_MAX = %s" % (E_TEC_MAX))

        return result

    def equation_three(self):
        """Equation 3: P_TEC Calculation for Workstations""" 
        (P_OFF, P_SLEEP, P_LONG_IDLE, P_SHORT_IDLE) = self.sysinfo.get_power_consumptions()
        P_IDLE = P_SHORT_IDLE

        (T_OFF, T_SLEEP, T_IDLE) = (0.35, 0.10, 0.55)
        P_TEC = (P_OFF * T_OFF) + (P_SLEEP * T_SLEEP) + (P_IDLE * T_IDLE) 

        return P_TEC

    def equation_four(self):
        """Equation 4: P_TEC_MAX Calculation for Workstations"""
        P_MAX = self.sysinfo.max_power
        N_HDD = self.sysinfo.disk_num

        P_TEC_MAX = 0.28 * (P_MAX + (N_HDD * 5))

        return P_TEC_MAX

    def equation_five(self, wol):
        """Equation 5: Calculation of P_OFF_MAX for Small-scale Servers"""
        (core, clock, memory, disk) = self.sysinfo.get_basic_info()

        P_OFF_BASE = 2.0
        if wol:
            P_OFF_WOL = 0.7
        else:
            P_OFF_WOL = 0
        if (core > 1 or self.sysinfo.more_discrete) and memory >= 1:
            category = 'B'
            P_IDLE_MAX = 65.0
        else:
            category = 'A'
            P_IDLE_MAX = 50.0
        P_OFF_MAX = P_OFF_BASE + P_OFF_WOL
        return (category, P_OFF_MAX, P_IDLE_MAX)

    def equation_six(self, wol):
        """Equation 6: Calculation of P_OFF_MAX for Thin Clients"""
        P_OFF_BASE = 2.0
        if wol:
            P_OFF_WOL = 0.7
        else:
            P_OFF_WOL = 0
        P_OFF_MAX = P_OFF_BASE + P_OFF_WOL
        return P_OFF_MAX

    def equation_seven(self, wol):
        """Equation 7: Calculation of P_SLEEP_MAX for Thin Clients"""
        P_SLEEP_BASE = 2.0
        if wol:
            P_SLEEP_WOL = 0.7
        else:
            P_SLEEP_WOL = 0
        P_SLEEP_MAX = P_SLEEP_BASE + P_SLEEP_WOL
        return P_SLEEP_MAX

class EnergyStar60:
    """Energy Star 6.0 calculator"""
    def __init__(self, sysinfo):
        self.sysinfo = sysinfo

    # Requirements for Desktop, Integrated Desktop, and Notebook Computers
    def equation_one(self):
        """Equation 1: TEC Calculation (E_TEC) for Desktop, Integrated Desktop, Thin Client and Notebook Computers"""
        (P_OFF, P_SLEEP, P_LONG_IDLE, P_SHORT_IDLE) = self.sysinfo.get_power_consumptions()
        if self.sysinfo.computer_type == 3:
            (T_OFF, T_SLEEP, T_LONG_IDLE, T_SHORT_IDLE) = (0.25, 0.35, 0.1, 0.3)
        else:
            (T_OFF, T_SLEEP, T_LONG_IDLE, T_SHORT_IDLE) = (0.45, 0.05, 0.15, 0.35)

        E_TEC = ((P_OFF * T_OFF) + (P_SLEEP * T_SLEEP) + (P_LONG_IDLE * T_LONG_IDLE) + (P_SHORT_IDLE * T_SHORT_IDLE)) * 8760 / 1000

        debug("T_OFF = %s, T_SLEEP = %s, T_LONG_IDLE = %s, T_SHORT_IDLE = %s" % (T_OFF, T_SLEEP, T_LONG_IDLE, T_SHORT_IDLE))
        debug("P_OFF = %s, P_SLEEP = %s, P_LONG_IDLE = %s, P_SHORT_IDLE = %s" % (P_OFF, P_SLEEP, P_LONG_IDLE, P_SHORT_IDLE))

        return E_TEC

    def equation_two(self, gpu_category):
        """Equation 2: E_TEC_MAX Calculation for Desktop, Integrated Desktop, and Notebook Computers"""
        (core, clock, memory, disk) = self.sysinfo.get_basic_info()

        P = core * clock
        debug("P = %s" % (P))

        if self.sysinfo.computer_type != 3:
            if P <= 3:
                TEC_BASE = 69.0
            elif self.sysinfo.switchable or self.sysinfo.discrete:
                if P <= 6:
                    TEC_BASE = 112.0
                elif P <= 7:
                    TEC_BASE = 120.0
                else:
                    TEC_BASE = 135.0
            else:
                if P <= 9:
                    TEC_BASE = 115.0
                else:
                    TEC_BASE = 135.0
        else:
            if P <= 2:
                TEC_BASE = 14.0
            elif self.sysinfo.switchable or self.sysinfo.discrete:
                if P <= 5.2:
                    TEC_BASE = 22.0
                elif P <= 8:
                    TEC_BASE = 24.0
                else:
                    TEC_BASE = 28.0
            else:
                if P <= 9:
                    TEC_BASE = 16.0
                else:
                    TEC_BASE = 18.0

        TEC_MEMORY = 0.8 * memory

        if self.sysinfo.switchable:
            if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
                TEC_SWITCHABLE = 0.5 * 36
            else:
                TEC_SWITCHABLE = 0
            TEC_GRAPHICS = 0
        else:
            TEC_SWITCHABLE = 0
            if self.sysinfo.discrete:
                if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
                    if gpu_category == 'G1':
                        TEC_GRAPHICS = 36
                    elif gpu_category == 'G2':
                        TEC_GRAPHICS = 51
                    elif gpu_category == 'G3':
                        TEC_GRAPHICS = 64
                    elif gpu_category == 'G4':
                        TEC_GRAPHICS = 83
                    elif gpu_category == 'G5':
                        TEC_GRAPHICS = 105 
                    elif gpu_category == 'G6':
                        TEC_GRAPHICS = 115 
                    elif gpu_category == 'G7':
                        TEC_GRAPHICS = 130 
                else:
                    if gpu_category == 'G1':
                        TEC_GRAPHICS = 14
                    elif gpu_category == 'G2':
                        TEC_GRAPHICS = 20
                    elif gpu_category == 'G3':
                        TEC_GRAPHICS = 26
                    elif gpu_category == 'G4':
                        TEC_GRAPHICS = 32
                    elif gpu_category == 'G5':
                        TEC_GRAPHICS = 42
                    elif gpu_category == 'G6':
                        TEC_GRAPHICS = 48
                    elif gpu_category == 'G7':
                        TEC_GRAPHICS = 60
            else:
                TEC_GRAPHICS = 0

        if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
            TEC_EEE = 8.76 * 0.2 * (0.15 + 0.35) * self.sysinfo.eee
        else:
            TEC_EEE = 8.76 * 0.2 * (0.10 + 0.30) * self.sysinfo.eee

        if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
            TEC_STORAGE = 26 * (disk - 1)
        else:
            TEC_STORAGE = 2.6 * (disk - 1)

        if self.sysinfo.computer_type != 1:
            (EP, r, A) = self.equation_three()

        if self.sysinfo.computer_type == 2:
            TEC_INT_DISPLAY = 8.76 * 0.35 * (1 + EP) * (4 * r + 0.05 * A)
        elif self.sysinfo.computer_type == 3:
            TEC_INT_DISPLAY = 8.76 * 0.30 * (1 + EP) * (2 * r + 0.02 * A)
        else:
            TEC_INT_DISPLAY = 0
        debug("TEC_BASE = %s, TEC_MEMORY = %s, TEC_GRAPHICS = %s, TEC_SWITCHABLE = %s, TEC_EEE = %s, TEC_STORAGE = %s, TEC_INT_DISPLAY = %s" % (TEC_BASE, TEC_MEMORY, TEC_GRAPHICS, TEC_SWITCHABLE, TEC_EEE, TEC_STORAGE, TEC_INT_DISPLAY))

        return TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE + TEC_INT_DISPLAY + TEC_SWITCHABLE + TEC_EEE

    def equation_three(self):
        """Equation 3: Calculation of Allowance for Enhanced-performance Integrated Displays"""
        (diagonal, enhanced_performance_display) = self.sysinfo.get_display()
        if enhanced_performance_display:
            if diagonal >= 27.0:
                EP = 0.75
            else:
                EP = 0.3
        else:
            EP = 0
        (width, height) = self.sysinfo.get_resolution()
        r = 1.0 * width * height / 1000000
        A =  1.0 * diagonal * diagonal * width * height / (width ** 2 + height ** 2)
        debug("EP = %s, r = %s, A = %s" % (EP, r, A))
        return (EP, r, A)

    def equation_four(self):
        """Equation 4: P_TEC Calculation for Workstations""" 
        (P_OFF, P_SLEEP, P_LONG_IDLE, P_SHORT_IDLE) = self.sysinfo.get_power_consumptions()
        (T_OFF, T_SLEEP, T_LONG_IDLE, T_SHORT_IDLE) = (0.35, 0.10, 0.15, 0.40)
        P_TEC = P_OFF * T_OFF + P_SLEEP * T_SLEEP + P_LONG_IDLE * T_LONG_IDLE + P_SHORT_IDLE * T_SHORT_IDLE
        return P_TEC

    def equation_five(self):
        """Equation 5: P_TEC_MAX Calculation for Workstations"""
        (T_SLEEP, T_LONG_IDLE, T_SHORT_IDLE) = (0.10, 0.15, 0.40)
        P_EEE = 0.2 * self.sysinfo.eee
        P_MAX = self.sysinfo.max_power
        N_HDD = self.sysinfo.disk_num
        P_TEC_MAX = 0.28 * (P_MAX + N_HDD * 5) + 8.76 * P_EEE * (T_SLEEP + T_LONG_IDLE + T_SHORT_IDLE)
        return P_TEC_MAX

    def equation_six(self, wol):
        """Calculation of P_OFF_MAX for Small-scale Servers"""
        P_OFF_BASE = 1.0
        if wol:
            P_OFF_WOL = 0.4
        else:
            P_OFF_WOL = 0
        P_OFF_MAX = P_OFF_BASE + P_OFF_WOL
        return P_OFF_MAX

    def equation_seven(self):
        """Equation 7: Calculation of P_IDLE_MAX for Small-scale Servers"""
        N = self.sysinfo.disk_num
        P_IDLE_BASE = 24.0
        P_IDLE_HDD = 8.0
        P_EEE = 0.2 * self.sysinfo.eee
        P_IDLE_MAX = P_IDLE_BASE + (N - 1) * P_IDLE_HDD + P_EEE
        return P_IDLE_MAX

    def equation_eight(self, discrete, wol):
        """Equation 8: Calculation of E_TEC_MAX for Thin Clients"""
        TEC_BASE = 60

        if discrete:
            TEC_GRAPHICS = 36
        else:
            TEC_GRAPHICS = 0

        if wol:
            TEC_WOL = 2
        else:
            TEC_WOL = 0

        if self.sysinfo.integrated_display:
            (EP, r, A) = self.equation_three()
            TEC_INT_DISPLAY = 8.76 * 0.35 * (1 + EP) * (4 * r + 0.05 * A)
        else:
            TEC_INT_DISPLAY = 0
        debug("TEC_INT_DISPLAY = %s" % (TEC_INT_DISPLAY))

        TEC_EEE = 8.76 * 0.2 * (0.15 + 0.35) * self.sysinfo.eee

        E_TEC_MAX = TEC_BASE + TEC_GRAPHICS + TEC_WOL + TEC_INT_DISPLAY + TEC_EEE

        return E_TEC_MAX

def qualifying(sysinfo):
    if sysinfo.product_type == 1:

        # Energy Star 5.2
        print("Energy Star 5.2:")
        estar52 = EnergyStar52(sysinfo)
        E_TEC = estar52.equation_one()

        if sysinfo.computer_type == 3:
            gpu_bit = '64'
        else:
            gpu_bit = '128'

        over_gpu_width = estar52.equation_two(True)
        under_gpu_width = estar52.equation_two(False)
        different=False

        for i,j in zip(over_gpu_width, under_gpu_width):
            (cat1, max1) = i
            (cat2, max2) = j
            if cat1 != cat2 or max1 != max2:
                different=True
                debug("Category %s E_TEC_MAX %s is different from Category %s E_TEC_MAX %s" % (cat1, max1, cat2, max2))
        else:
            if different is True:
                print("\n  If GPU Frame Buffer Width > %s bits," % (gpu_bit))
                for i in over_gpu_width:
                    (category, E_TEC_MAX) = i
                    if E_TEC <= E_TEC_MAX:
                        result = 'PASS'
                        operator = '<='
                    else:
                        result = 'FAIL'
                        operator = '>'
                    print("    Category %s: %s (E_TEC) %s %s (E_TEC_MAX), %s" % (category, E_TEC, operator, E_TEC_MAX, result))
                print("\n  If GPU Frame Buffer Width <= %s bits," % (gpu_bit))
                for i in under_gpu_width:
                    (category, E_TEC_MAX) = i
                    if E_TEC <= E_TEC_MAX:
                        result = 'PASS'
                        operator = '<='
                    else:
                        result = 'FAIL'
                        operator = '>'
                    print("    Category %s: %s (E_TEC) %s %s (E_TEC_MAX), %s" % (category, E_TEC, operator, E_TEC_MAX, result))
            else:
                for i in under_gpu_width:
                    (category, E_TEC_MAX) = i
                    if E_TEC <= E_TEC_MAX:
                        result = 'PASS'
                        operator = '<='
                    else:
                        result = 'FAIL'
                        operator = '>'
                    print("\n  Category %s: %s (E_TEC) %s %s (E_TEC_MAX), %s" % (category, E_TEC, operator, E_TEC_MAX, result))

        # Energy Star 6.0
        print("\nEnergy Star 6.0:\n")
        estar60 = EnergyStar60(sysinfo)
        E_TEC = estar60.equation_one()

        if sysinfo.power_supply == 'i':
            lower = 1.015
            if sysinfo.computer_type == 1:
                higher = 1.03
            else:
                higher = 1.04
        elif sysinfo.power_supply == 'e':
            lower = 1.015
            if sysinfo.computer_type != 2:
                higher = 1.03
            else:
                higher = 1.04

        if sysinfo.discrete:
            for AllowancePSU in (1, lower, higher):
                if AllowancePSU == 1:
                    print("  If power supplies do not meet the requirements of Power Supply Efficiency Allowance,")
                elif AllowancePSU == lower:
                    print("  If power supplies meet lower efficiency requirements,")
                elif AllowancePSU == higher:
                    print("  If power supplies meet higher efficiency requirements,")
                for gpu in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7'):
                    E_TEC_MAX = estar60.equation_two(gpu) * AllowancePSU
                    if E_TEC <= E_TEC_MAX:
                        result = 'PASS'
                        operator = '<='
                    else:
                        result = 'FAIL'
                        operator = '>'
                    if gpu == 'G1':
                        gpu = "G1 (FB_BW <= 16)"
                    elif gpu == 'G2':
                        gpu = "G2 (16 < FB_BW <= 32)"
                    elif gpu == 'G3':
                        gpu = "G3 (32 < FB_BW <= 64)"
                    elif gpu == 'G4':
                        gpu = "G4 (64 < FB_BW <= 96)"
                    elif gpu == 'G5':
                        gpu = "G5 (96 < FB_BW <= 128)"
                    elif gpu == 'G6':
                        gpu = "G6 (FB_BW > 128; Frame Buffer Data Width < 192 bits)"
                    elif gpu == 'G7':
                        gpu = "G7 (FB_BW > 128; Frame Buffer Data Width >= 192 bits)"
                    print("    %s (E_TEC) %s %s (E_TEC_MAX) for %s, %s" % (E_TEC, operator, E_TEC_MAX, gpu, result))
        else:
            for AllowancePSU in (1, lower, higher):
                if AllowancePSU == 1:
                    print("  If power supplies do not meet the requirements of Power Supply Efficiency Allowance,")
                elif AllowancePSU == lower:
                    print("  If power supplies meet lower efficiency requirements,")
                elif AllowancePSU == higher:
                    print("  If power supplies meet higher efficiency requirements,")
                E_TEC_MAX = estar60.equation_two('G1') * AllowancePSU
                if E_TEC <= E_TEC_MAX:
                    result = 'PASS'
                    operator = '<='
                else:
                    result = 'FAIL'
                    operator = '>'
                print("    %s (E_TEC) %s %s (E_TEC_MAX), %s" % (E_TEC, operator, E_TEC_MAX, result))

    elif sysinfo.product_type == 2:
        # Energy Star 5.2
        print("Energy Star 5.2:")
        estar52 = EnergyStar52(sysinfo)
        P_TEC = estar52.equation_three()
        P_TEC_MAX = estar52.equation_four()
        if P_TEC <= P_TEC_MAX:
            result = 'PASS'
            operator = '<='
        else:
            result = 'FAIL'
            operator = '>'
        print("  %s (P_TEC) %s %s (P_TEC_MAX), %s" % (P_TEC, operator, P_TEC_MAX, result))

        # Energy Star 6.0
        print("Energy Star 6.0:")
        estar60 = EnergyStar60(sysinfo)
        P_TEC = estar60.equation_four()
        P_TEC_MAX = estar60.equation_five()
        if P_TEC <= P_TEC_MAX:
            result = 'PASS'
            operator = '<='
        else:
            result = 'FAIL'
            operator = '>'
        print("  %s (P_TEC) %s %s (P_TEC_MAX), %s" % (P_TEC, operator, P_TEC_MAX, result))
    elif sysinfo.product_type == 3:
        # Energy Star 5.2
        print("Energy Star 5.2:")
        estar52 = EnergyStar52(sysinfo)
        for wol in (True, False):
            (category, P_OFF_MAX, P_IDLE_MAX) = estar52.equation_five(wol)
            P_OFF = sysinfo.off
            P_IDLE = sysinfo.short_idle

            if P_OFF <= P_OFF_MAX and P_IDLE <= P_IDLE_MAX:
                result = 'PASS'
            else:
                result = 'FAIL'

            if P_OFF <= P_OFF_MAX:
                op1 = '<='
            else:
                op1 = '>'

            if P_IDLE <= P_IDLE_MAX:
                op2 = '<='
            else:
                op2 = '>'
            if wol:
                print("  If Wake-On-LAN (WOL) is enabled by default upon shipment.")
            else:
                print("  If Wake-On-LAN (WOL) is disabled by default upon shipment.")
            print("    Category %s: %s (P_OFF) %s %s (P_OFF_MAX), %s (P_IDLE) %s %s (P_IDLE_MAX), %s" % (category, P_OFF, op1, P_OFF_MAX, P_IDLE, op2, P_IDLE_MAX, result))

        # Energy Star 6.0
        print("Energy Star 6.0:")
        estar60 = EnergyStar60(sysinfo)
        for wol in (True, False):
            P_OFF = sysinfo.off
            P_OFF_MAX = estar60.equation_six(wol)
            P_IDLE = sysinfo.short_idle
            P_IDLE_MAX = estar60.equation_seven()

            if P_OFF <= P_OFF_MAX and P_IDLE <= P_IDLE_MAX:
                result = 'PASS'
            else:
                result = 'FAIL'

            if P_OFF <= P_OFF_MAX:
                op1 = '<='
            else:
                op1 = '>'

            if P_IDLE <= P_IDLE_MAX:
                op2 = '<='
            else:
                op2 = '>'
            if wol:
                print("  If Wake-On-LAN (WOL) is enabled by default upon shipment.")
            else:
                print("  If Wake-On-LAN (WOL) is disabled by default upon shipment.")
            print("    %s (P_OFF) %s %s (P_OFF_MAX), %s (P_IDLE) %s %s (P_IDLE_MAX), %s" % (P_OFF, op1, P_OFF_MAX, P_IDLE, op2, P_IDLE_MAX, result))

    elif sysinfo.product_type == 4:
        # Energy Star 5.2
        print("Energy Star 5.2:")
        estar52 = EnergyStar52(sysinfo)
        for wol in (True, False):
            if wol:
                print("  If Wake-On-LAN (WOL) is enabled by default upon shipment.")
            else:
                print("  If Wake-On-LAN (WOL) is disabled by default upon shipment.")

            P_OFF = sysinfo.off
            P_OFF_MAX = estar52.equation_six(wol)

            P_SLEEP = sysinfo.sleep
            P_SLEEP_MAX = estar52.equation_seven(wol)

            P_IDLE = sysinfo.short_idle
            if sysinfo.media_codec:
                P_IDLE_MAX = 15.0
                category = 'B'
            else:
                P_IDLE_MAX = 12.0
                category = 'A'

            print("    Category %s:" % (category))

            if P_OFF <= P_OFF_MAX:
                op1 = '<='
            else:
                op1 = '>'
            print("      %s (P_OFF) %s %s (P_OFF_MAX)" % (P_OFF, op1, P_OFF_MAX))

            if P_SLEEP <= P_SLEEP_MAX:
                op2 = '<='
            else:
                op2 = '>'
            print("      %s (P_SLEEP) %s %s (P_SLEEP_MAX)" % (P_SLEEP, op2, P_SLEEP_MAX))

            if P_IDLE <= P_IDLE_MAX:
                op3 = '<='
            else:
                op3 = '>'
            print("      %s (P_IDLE) %s %s (P_IDLE_MAX)" % (P_IDLE, op3, P_IDLE_MAX))


            if P_OFF <= P_OFF_MAX and P_SLEEP <= P_SLEEP_MAX and P_IDLE <= P_IDLE_MAX:
                result = 'PASS'
            else:
                result = 'FAIL'
            print("        %s" % (result))
        # Energy Star 6.0
        print("Energy Star 6.0:")
        estar60 = EnergyStar60(sysinfo)
        E_TEC = estar60.equation_one()
        for discrete in (True, False):
            for wol in (True, False):
                E_TEC_MAX = estar60.equation_eight(discrete, wol)
                if discrete:
                    msg1 = "it has Discrete Graphics enabled"
                else:
                    msg1 = "it doesn't have Discrete Graphics enabled"
                if wol:
                    msg2 = "Wake-On-LAN (WOL) is enabled"
                else:
                    msg2 = "Wake-On-LAN (WOL) is disabled"
                print("  If %s and %s by default upon shipment," % (msg1, msg2))
                if E_TEC <= E_TEC_MAX:
                    operator = '<='
                    result = 'PASS'
                else:
                    operator = '>'
                    result = 'FAIL'
                print("    %s (E_TEC) %s %s (E_TEC_MAX), %s" % (E_TEC, operator, E_TEC_MAX, result))
    else:
        raise Exception('This is a bug when you see this.')

def main():
    version = "v1.1"
    print("Energy Star 5.2/6.0 calculator %s\n" % (version)+ '=' * 80)
    if args.test == 1:
        # Test case from Energy Star 5.2/6.0 for Notebooks
        sysinfo = SysInfo(
                auto=True,
                product_type=1, computer_type=3,
                cpu_core=2, cpu_clock=2.0,
                mem_size=8, disk_num=1,
                width=1366, height=768, eee=1, power_supply='e',
                diagonal=14, ep=False,
                discrete=False, switchable=True,
                off=1.0, sleep=1.7, long_idle=8.0, short_idle=10.0)
    elif args.test == 2:
        # Test case from OEM/ODM only for Energy Star 5.2
        # Category B: 19.16688 (E_TEC) <= 60.8 (E_TEC_MAX), PASS
        sysinfo = SysInfo(
                auto=True,
                product_type=1, computer_type=3,
                cpu_core=2, cpu_clock=1.8,
                mem_size=16, disk_num=1,
                width=1366, height=768, eee=1, power_supply='e',
                diagonal=14, ep=False,
                discrete=True, switchable=False,
                off=0.27, sleep=0.61, long_idle=6.55, short_idle=6.55)
    elif args.test == 3:
        # Test case from Energy Star 5.2/6.0 for Workstations
        sysinfo = SysInfo(
                auto=True,
                product_type=2, disk_num=2, eee=0,
                off=2, sleep=4, long_idle=50, short_idle=80, max_power=180)
    elif args.test == 4:
        # Test case from Energy Star 5.2/6.0 for Small-scale Servers 
        sysinfo = SysInfo(
                auto=True,
                product_type=3,
                cpu_core=1, more_discrete=False,
                eee=1, disk_num=1,
                off=2.7, short_idle=65.0)
    elif args.test == 5:
        # Test case from Energy Star 5.2/6.0 for Thin Clients
        sysinfo = SysInfo(
                auto=True,
                product_type=4, computer_type=2,
                integrated_display=True, width=1366, height=768, diagonal=14, ep=True,
                off=2.7, sleep=2.7, long_idle=15.0, short_idle=15.0, media_codec=True)
    elif args.test == 6:
        # Test Case #1
        sysinfo = SysInfo(
                auto=True,
                product_type=1, computer_type=2,
                cpu_core=2, cpu_clock=2.4,
                mem_size=4, disk_num=1,
                width=1680, height=1050, eee=1, power_supply='e',
                diagonal=27, ep=True,
                discrete=False, switchable=True,
                off=12, sleep=23, long_idle=34, short_idle=45)
    else:
        sysinfo = SysInfo()

    qualifying(sysinfo)

    if args.output:
        xlsx = True
        try:
            from xlsxwriter import Workbook
        except:
            warning("You need to install Python xlsxwriter module or you can not output Excel format file.")
            xlsx = False

        if xlsx:
            book = Workbook(args.output)
            book.set_properties({'comments':"Created by Energy Star 5.2/6.0 calculator %s from Canonical Ltd." % (version)})

            sheet = book.add_worksheet()
            sheet.set_column('A:A', 60)
            sheet.set_column('B:B', 46)
            header = book.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'fg_color': '#CFE2F3'})
            field = book.add_format({
                'border': 1,
                'fg_color': '#F3F3F3'})
            field1 = book.add_format({
                'left': 1,
                'right': 1,
                'fg_color': '#F3F3F3'})
            field2 = book.add_format({
                'left': 1,
                'right': 1,
                'bottom': 1,
                'fg_color': '#F3F3F3'})
            value = book.add_format({'border': 1})
            float2 = book.add_format({'border': 1})
            float2.set_num_format('0.00')
            float3 = book.add_format({'border': 1})
            float3.set_num_format('0.000')
            result = book.add_format({
                'border': 1,
                'fg_color': '#F4CCCC'})
            result_value = book.add_format({
                'border': 1,
                'fg_color': '#FFF2CC'})

            sheet.merge_range("A1:B1", "General", header)

            sheet.write("A2", "Product Type", field)
            if sysinfo.product_type == 1:
                sheet.write("B2", "Desktop, Integrated Desktop, and Notebook Computers", value)

                sheet.write("A3", "Computer Type", field)
                if sysinfo.computer_type == 1:
                    sheet.write("B3", "Desktop", value)
                elif sysinfo.computer_type == 2:
                    sheet.write("B3", "Integrated Desktop", value)
                else:
                    sheet.write("B3", "Notebook", value)

                sheet.write("A4", "CPU cores", field)
                sheet.write("B4", sysinfo.cpu_core, value)

                sheet.write("A5", "CPU clock (GHz)", field)
                sheet.write("B5", sysinfo.cpu_clock, float2)

                sheet.write("A6", "Memory size (GB)", field)
                sheet.write("B6", sysinfo.mem_size, value)

                sheet.write("A7", "Number of Hard Drives", field)
                sheet.write("B7", sysinfo.disk_num, value)

                sheet.write("A8", "IEEE 802.3az compliant (Energy Efficient Ethernet) Gigabit Ethernet ports", field)
                sheet.write("B8", sysinfo.eee, value)

                sheet.merge_range("A10:B10", "Graphics", header)

                sheet.write("A11", "Graphics Type", field)
                if sysinfo.switchable:
                    sheet.write("B11", "Switchable", value)
                elif sysinfo.discrete:
                    sheet.write("B11", "Discrete", value)
                else:
                    sheet.write("B11", "Integrated", value)

                if sysinfo.computer_type == 3:
                    sheet.write("A12", "GPU Frame Buffer Width > 64 bits", field)
                else:
                    sheet.write("A12", "GPU Frame Buffer Width > 128 bits", field)
                sheet.write("B12", "No", value)
                sheet.data_validation('B12', {
                    'validate': 'list',
                    'source': [
                        'Yes',
                        'No']})

                sheet.write("A13", "Graphics Category", field)
                sheet.write("B13", "G1 (FB_BW <= 16)", value)
                sheet.data_validation('B13', {
                    'validate': 'list',
                    'source': [
                        'G1 (FB_BW <= 16)',
                        'G2 (16 < FB_BW <= 32)',
                        'G3 (32 < FB_BW <= 64)',
                        'G4 (64 < FB_BW <= 96)',
                        'G5 (96 < FB_BW <= 128)',
                        'G6 (FB_BW > 128; Frame Buffer Data Width < 192 bits)',
                        'G7 (FB_BW > 128; Frame Buffer Data Width >= 192 bits)']})

                sheet.merge_range("A15:B15", "Display", header)

                sheet.write("A16", "Enhanced-performance Integrated Display", field)
                sheet.write("B16", "No", value)
                sheet.data_validation('B16', {
                    'validate': 'list',
                    'source': [
                        'Yes',
                        'No']})

                sheet.write("A17", "Physical Diagonal (inch)", field)
                sheet.write("B17", sysinfo.diagonal, value)

                sheet.write("A18", "Screen Width (px)", field)
                sheet.write("B18", sysinfo.width, value)

                sheet.write("A19", "Screen Height (px)", field)
                sheet.write("B19", sysinfo.height, value)

                sheet.merge_range("A21:B21", "Power Supply", header)

                sheet.write("A22", "Power Supply Type", field)
                if sysinfo.power_supply == 'e':
                    sheet.write("B22", "External", value)
                else:
                    sheet.write("B22", "Internal", value)

                sheet.write("A23", "Meet the requirements of Power Supply Efficiency Allowance", field)
                sheet.write("B23", "None", value)
                sheet.data_validation('B23', {
                    'validate': 'list',
                    'source': [
                        'None',
                        'Lower',
                        'Higher']})

                sheet.merge_range("A25:B25", "Power Consumption", header)
                sheet.write("A26", "Off mode (W)", field)
                sheet.write("B26", sysinfo.off, float2)
                sheet.write("A27", "Sleep mode (W)", field)
                sheet.write("B27", sysinfo.sleep, float2)
                sheet.write("A28", "Long idle mode (W)", field)
                sheet.write("B28", sysinfo.long_idle, float2)
                sheet.write("A29", "Short idle mode (W)", field)
                sheet.write("B29", sysinfo.short_idle, float2)

                sheet.merge_range("A31:B31", "Energy Star 5.2", header)

                sheet.write("A32", "T_OFF", field1)
                sheet.write("A33", "T_SLEEP", field1)
                sheet.write("A34", "T_IDLE", field2)

                sheet.write("A35", "P_OFF", field1)
                sheet.write("A36", "P_SLEEP", field1)
                sheet.write("A37", "P_IDLE", field2)

                sheet.write("A38", "E_TEC", result)

                sheet.write("A39", "TEC_BASE", field1)
                sheet.write("A40", "TEC_MEMORY", field1)
                sheet.write("A41", "TEC_GRAPHICS", field1)
                sheet.write("A42", "TEC_STORAGE", field1)

                sheet.write("A43", "E_TEC_MAX", result)

                sheet.merge_range("A46:B46", "Energy Star 6.0", header)

                sheet.write("A47", "T_OFF", field1)
                sheet.write("A48", "T_SLEEP", field1)
                sheet.write("A49", "T_LONG_IDLE", field1)
                sheet.write("A50", "T_SHORT_IDLE", field2)

                sheet.write("A51", "P_OFF", field1)
                sheet.write("A52", "P_SLEEP", field1)
                sheet.write("A53", "P_LONG_IDLE", field1)
                sheet.write("A54", "P_SHORT_IDLE", field2)

                sheet.write("A55", "E_TEC", result)

                sheet.write("A56", "ALLOWANCE_PSU", field1)
                sheet.write("B56", '=IF(EXACT(B23, "Higher"), 0.03, IF(EXACT(B23, "Lower"), 0.015, 0))', float3)
                sheet.write("A57", "TEC_BASE", field1)
                sheet.write("A58", "TEC_MEMORY", field1)
                sheet.write("A59", "TEC_GRAPHICS", field1)
                sheet.write("A60", "TEC_STORAGE", field1)
                sheet.write("A61", "TEC_INT_DISPLAY", field1)
                sheet.write("A62", "TEC_SWITCHABLE", field1)
                sheet.write("A63", "TEC_EEE", field1)

                sheet.write("A64", "E_TEC_MAX", result)

            book.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug",  help="print debug messages", action="store_true")
    parser.add_argument("-t", "--test",  help="use test case", type=int)
    parser.add_argument("-o", "--output",  help="output Excel file", type=str)
    args = parser.parse_args()
    main()
