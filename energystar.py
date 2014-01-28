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

import subprocess

def debug(message):
    DEBUG=False
    if DEBUG:
        print(message)

def question_str(prompt, length, validator):
    while True:
        s = raw_input(prompt + "\n>> ")
        if len(s) == length and set(s).issubset(validator):
            print('')
            return s
        print("The valid input '" + validator + "'.")

def question_bool(prompt):
    while True:
        s = raw_input(prompt + " [y/n]\n>> ")
        if len(s) == 1 and set(s).issubset("YyNn01"):
            print('')
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
                    print('')
                    return num
            except ValueError:
                print("Please input a positive integer less than or equal to %s." % (maximum))
        print("Please input a positive integer less than or equal to %s." % (maximum))

def question_num(prompt):
    while True:
        s = raw_input(prompt + "\n>> ")
        try:
            num = float(s)
            print('')
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
            width=0,
            height=0,
            diagonal=0,
            ep=False,
            w=0,
            h=0,
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
            max_power=0):
        self.auto = auto
        self.cpu_core = cpu_core
        self.cpu_clock = cpu_clock
        self.mem_size = mem_size
        self.disk_num = disk_num
        self.w = w
        self.h = h
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

        if not auto:
            # Product type
            self.product_type = question_int("""Which product type would you like to verify?
 [1] Desktop, Integrated Desktop, and Notebook Computers
 [2] Workstations
 [3] Small-scale Servers (Not implemented yet)
 [4] Thin Clients (Not implemented yet)""", 4)

            if self.product_type == 1:
                # Computer type
                self.computer_type = question_int("""Which type of computer do you use?
 [1] Desktop
 [2] Integrated Desktop
 [3] Notebook""", 3)

                # GPU Information
                if question_bool("Is there a discrete GPU?"):
                    self.discrete = True
                else:
                    self.discrete = False
                if question_bool("Is it a switchable GPU?"):
                    self.switchable = True
                else:
                    self.switchable = False

                # Power Consumption
                self.off = question_num("What is the power consumption in Off Mode?")
                self.sleep = question_num("What is the power consumption in Sleep Mode?")
                self.long_idle = question_num("What is the power consumption in Long Idle Mode?")
                self.short_idle = question_num("What is the power consumption in Short Idle Mode?")

                # Power Supply
                if self.computer_type != 3:
                    self.power_supply = question_str("\nDoes it use external power supply or internal power supply? [e/i]", 1, "ei")
                else:
                    self.power_supply = 'e'

                # Screen size
                if self.computer_type != '1':
                    self.width = question_num("What is the physical width of the display in inches?")
                    self.height = question_num("What is the physical height of the display in inches?")
                    self.diagonal = question_bool("Is the physical diagonal of the display bigger than or equal to 27 inches?")
                    self.ep = question_bool("Is there an Enhanced-perforcemance Integrated Display?")

                # Gigabit Ethernet
                self.eee = question_num("How many IEEE 802.3az­compliant (Energy Efficient Ethernet) Gigabit Ethernet ports?")
            elif self.product_type == 2:
                self.off = question_num("What is the power consumption in Off Mode?")
                self.sleep = question_num("What is the power consumption in Sleep Mode?")
                self.long_idle = question_num("What is the power consumption in Long Idle Mode?")
                self.short_idle = question_num("What is the power consumption in Short Idle Mode?")
                self.max_power = question_num("What is the maximum power consumption?")
                self.eee = question_num("How many IEEE 802.3az­compliant (Energy Efficient Ethernet) Gigabit Ethernet ports?")

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

        debug("CPU clock: %s" % (self.cpu_clock))
        return self.cpu_clock

    def get_mem_size(self):
        if self.mem_size:
            return self.mem_size

        for size in subprocess.check_output("sudo dmidecode -t 17 | grep Size | awk '{print $2}'", shell=True).split('\n'):
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

    def set_display(self, width, height, diagonal, ep):
        self.width = width
        self.height = height
        self.diagonal = diagonal
        self.ep = ep

    def get_display(self):
        return (self.width, self.height, self.diagonal, self.ep)

    def get_resolution(self):
        if self.w == 0 or self.h == 0:
            (width, height) = subprocess.check_output("xrandr --current | grep current | sed 's/.*current \\([0-9]*\\) x \\([0-9]*\\).*/\\1 \\2/'", shell=True).strip().split(' ')
            self.w = int(width)
            self.h = int(height)
        debug("Resolution: %s x %s" % (self.w, self.h))
        return (self.w, self.h)

    def get_power_consumptions(self):
        return (self.off, self.sleep, self.long_idle, self.short_idle)

class EnergyStar52:
    """Energy Star 5.2 calculator"""
    def __init__(self, sysinfo):
        self.core = sysinfo.get_cpu_core()
        self.disk = sysinfo.get_disk_num()
        self.memory = sysinfo.get_mem_size()
        self.sysinfo = sysinfo

    def qualify_desktop_category(self, category, gpu_discrete, gpu_width):
        if category == 'D':
            if self.core >= 4:
                if self.memory >= 4:
                    return True
                elif gpu_width:
                    return True
        elif category == 'C':
            if self.core >= 2:
                if self.memory >= 2:
                    return True
                elif gpu_discrete:
                    return True
        elif category == 'B':
            if self.core == 2 and self.memory >= 2:
                return True
        elif category == 'A':
            return True
        return False

    def qualify_netbook_category(self, category, gpu_discrete, over_gpu_width):
        if category == 'C':
            if self.core >= 2 and self.memory >= 2:
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

        return E_TEC

    def equation_two(self, over_gpu_width):
        """Equation 2: E_TEC_MAX Calculation for Desktop, Integrated Desktop, and Notebook Computers"""

        result = []

        ## Maximum TEC Allowances for Desktop and Integrated Desktop Computers
        if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
            if self.disk > 1:
                TEC_STORAGE = 25.0 * (self.disk - 1)
            else:
                TEC_STORAGE = 0.0

            if self.qualify_desktop_category('A', self.sysinfo.discrete, over_gpu_width):
                TEC_BASE = 148.0

                if self.memory > 2:
                    TEC_MEMORY = 1.0 * (self.memory - 2)
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

                if self.memory > 2:
                    TEC_MEMORY = 1.0 * (self.memory - 2)
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

                if self.memory > 2:
                    TEC_MEMORY = 1.0 * (self.memory - 2)
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

                if self.memory > 4:
                    TEC_MEMORY = 1.0 * (self.memory - 4)
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
            if self.memory > 4:
                TEC_MEMORY = 0.4 * (self.memory - 4)
            else:
                TEC_MEMORY = 0.0

            if self.disk > 1:
                TEC_STORAGE = 3.0 * (self.disk - 1)
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

    def equation_five(self):
        """Equation 5: Calculation of P_OFF_MAX for Small-scale Servers"""
        P_OFF_MAX = P_OFF_BASE + P_OFF_WOL

    def equation_six(self):
        """Equation 6: Calculation of P_OFF_MAX for Thin Clients"""
        P_OFF_MAX = P_OFF_BASE + P_OFF_WOL

    def equation_seven(self):
        """Equation 7: Calculation of P_SLEEP_MAX for Thin Clients"""
        P_SLEEP_MAX = P_SLEEP_BASE + P_SLEEP_WOL

class EnergyStar60:
    """Energy Star 6.0 calculator"""
    def __init__(self, sysinfo):
        self.clock = sysinfo.get_cpu_clock()
        self.core = sysinfo.get_cpu_core()
        self.disk = sysinfo.get_disk_num()
        self.memory = sysinfo.get_mem_size()
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

        return E_TEC

    def equation_two(self, gpu_category):
        """Equation 2: E_TEC_MAX Calculation for Desktop, Integrated Desktop, and Notebook Computers"""

        P = self.core * self.clock
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
        debug("TEC_BASE = %s" % (TEC_BASE))

        TEC_MEMORY = 0.8 * self.memory
        debug("TEC_MEMORY = %s" % (TEC_MEMORY))

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
        debug("TEC_GRAPHICS = %s" % (TEC_GRAPHICS))

        if self.sysinfo.switchable:
            if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
                TEC_SWITCHABLE = 0.5 * TEC_GRAPHICS
            else:
                TEC_SWITCHABLE = 0
        else:
            TEC_SWITCHABLE = 0
        debug("TEC_SWITCHABLE = %s" % (TEC_SWITCHABLE))

        if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
            TEC_EEE = 8.76 * 0.2 * (0.15 + 0.35) * self.sysinfo.eee
        else:
            TEC_EEE = 8.76 * 0.2 * (0.10 + 0.30) * self.sysinfo.eee
        debug("TEC_EEE = %s" % (TEC_EEE))

        if self.sysinfo.computer_type == 1 or self.sysinfo.computer_type == 2:
            TEC_STORAGE = 26 * (self.disk - 1)
        else:
            TEC_STORAGE = 2.6 * (self.disk - 1)
        debug("TEC_STORAGE = %s" % (TEC_STORAGE))

        if self.sysinfo.computer_type != 1:
            (EP, r, A) = self.equation_three()

        if self.sysinfo.computer_type == 2:
            TEC_INT_DISPLAY = 8.76 * 0.35 * (1 + EP) * (4 * r + 0.05 * A)
        elif self.sysinfo.computer_type == 3:
            TEC_INT_DISPLAY = 8.76 * 0.30 * (1 + EP) * (2 * r + 0.02 * A)
        else:
            TEC_INT_DISPLAY = 0
        debug("TEC_INT_DISPLAY = %s" % (TEC_INT_DISPLAY))

        return TEC_BASE + TEC_MEMORY + TEC_GRAPHICS + TEC_STORAGE + TEC_INT_DISPLAY + TEC_SWITCHABLE + TEC_EEE

    def equation_three(self):
        """Equation 3: Calculation of Allowance for Enhanced-performance Integrated Displays"""
        (width, height, diagonal, enhanced_performance_display) = self.sysinfo.get_display()
        if enhanced_performance_display:
            if diagonal:
                EP = 0.75
            else:
                EP = 0.3
        else:
            EP = 0
        (w, h) = self.sysinfo.get_resolution()
        r = 1.0 * w * h / 1000000
        A = width * height
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


def qualifying(sysinfo):
    if sysinfo.product_type == 1:

        # Energy Star 5.2
        print("Energy Star 5.2:");
        estar52 = EnergyStar52(sysinfo)
        E_TEC = estar52.equation_one()

        if sysinfo.computer_type == 3:
            gpu_bit = '64'
        else:
            gpu_bit = '128'

        over_gpu_width = estar52.equation_two(True)
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

        under_gpu_width = estar52.equation_two(False)
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

        # Energy Star 6.0
        print("\nEnergy Star 6.0:\n");
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
            print("  If power supplies do not meet the requirements of Power Supply Efficiency Allowance,")
            for gpu in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7'):
                E_TEC_MAX = estar60.equation_two(gpu)
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
            print("  If power supplies meet less efficiency requirements,")
            for gpu in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7'):
                E_TEC_MAX = estar60.equation_two(gpu) * lower
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
            print("  If power supplies meet more efficiency requirements,")
            for gpu in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7'):
                E_TEC_MAX = estar60.equation_two(gpu) * higher
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
            print("  If power supplies do not meet the requirements of Power Supply Efficiency Allowance,")
            E_TEC_MAX = estar60.equation_two('G1')
            if E_TEC <= E_TEC_MAX:
                result = 'PASS'
                operator = '<='
            else:
                result = 'FAIL'
                operator = '>'
            print("    %s (E_TEC) %s %s (E_TEC_MAX), %s" % (E_TEC, operator, E_TEC_MAX, result))

            print("  If power supplies meet less efficiency requirements,")
            E_TEC_MAX = estar60.equation_two('G1') * lower
            if E_TEC <= E_TEC_MAX:
                result = 'PASS'
                operator = '<='
            else:
                result = 'FAIL'
                operator = '>'
            print("    %s (E_TEC) %s %s (E_TEC_MAX), %s" % (E_TEC, operator, E_TEC_MAX, result))

            print("  If power supplies meet more efficiency requirements,")
            E_TEC_MAX = estar60.equation_two('G1') * higher
            if E_TEC <= E_TEC_MAX:
                result = 'PASS'
                operator = '<='
            else:
                result = 'FAIL'
                operator = '>'
            print("    %s (E_TEC) %s %s (E_TEC_MAX), %s" % (E_TEC, operator, E_TEC_MAX, result))

    elif sysinfo.product_type == 2:
        # Energy Star 5.2
        print("Energy Star 5.2:");
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
        print("Energy Star 6.0:");
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
        raise Exception('Not implemented yet.')
    elif sysinfo.product_type == 4:
        raise Exception('Not implemented yet.')
    else:
        raise Exception('This is a bug when you see this.')

def main():
    # Test case from Energy Star 5.2/6.0 for Notebooks
#    sysinfo = SysInfo(
#            auto=True,
#            product_type=1, computer_type=3,
#            cpu_core=2, cpu_clock=2.0,
#            mem_size=8, disk_num=1,
#            w=1366, h=768, eee=1, power_supply='e',
#            width=12, height=6.95, diagonal=False,
#            discrete=False, switchable=True,
#            off=1.0, sleep=1.7, long_idle=8.0, short_idle=10.0)
    # Test case from OEM/ODM only for Energy Star 5.2
    # Category B: 19.16688 (E_TEC) <= 60.8 (E_TEC_MAX), PASS
#    sysinfo = SysInfo(
#            auto=True,
#            product_type=1, computer_type=3,
#            cpu_core=2, cpu_clock=1.8,
#            mem_size=16, disk_num=1,
#            w=1366, h=768, eee=1, power_supply='e',
#            width=12, height=6.95, diagonal=False,
#            discrete=True, switchable=False,
#            off=0.27, sleep=0.61, long_idle=6.55, short_idle=6.55)
    # Test case from Energy Star 5.2/6.0 for Workstations
#    sysinfo = SysInfo(
#            auto=True,
#            product_type=2, disk_num=2, eee=0,
#            off=2, sleep=4, long_idle=50, short_idle=80, max_power=180)
    sysinfo = SysInfo()
    qualifying(sysinfo)

if __name__ == '__main__':
    main()
