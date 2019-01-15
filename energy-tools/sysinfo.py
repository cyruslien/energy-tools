#! /usr/bin/env python3
# -*- coding: utf-8; indent-tabs-mode: nil; tab-width: 4; c-basic-offset: 4; -*-
#
# Copyright (C) 2014-2018 Canonical Ltd.
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

from logging import debug, warning

import json
import math
import os
import re
import subprocess

class SysInfo:
    def question_str(self, prompt, length, validator, name):
        if name in self.profile:
            return self.profile[name]
        while True:
            s = input(prompt + "\n>> ")
            if len(s) == length and set(s).issubset(validator):
                print('-'*80)
                self.profile[name] = s
                return s
            print("The valid input '" + validator + "'.")

    def question_bool(self, prompt, name):
        if name in self.profile:
            return self.profile[name]
        while True:
            s = input(prompt + " [y/n]\n>> ")
            if len(s) == 1 and set(s).issubset("YyNn01"):
                print('-'*80)
                if s == 'Y' or s == 'y' or s == '1':
                    self.profile[name] = True
                    return True
                else:
                    self.profile[name] = False
                    return False

    def question_int(self, prompt, maximum, name):
        if name in self.profile:
            return self.profile[name]
        while True:
            s = input(prompt + "\n>> ")
            if set(s).issubset("0123456789"):
                try:
                    num = int(s)
                    if num <= maximum:
                        print('-'*80)
                        self.profile[name] = num
                        return num
                except ValueError:
                    print("Please input a positive integer less than or equal to %s." % (maximum))
            print("Please input a positive integer less than or equal to %s." % (maximum))

    def question_num(self, prompt, name):
        if name in self.profile:
            return self.profile[name]
        while True:
            s = input(prompt + "\n>> ")
            try:
                num = float(s)
                print('-'*80)
                self.profile[name] = num
                return num
            except ValueError:
                print("Oops!  That was no valid number.  Try again...")

    def get_diagonal(self):
        key = 'Display Diagonal'
        if key in self.profile:
            return self.profile[key]
        else:
            import gi
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk
            screen = Gdk.Screen.get_default()
            major = screen.get_primary_monitor()
            diagonal_mm = math.sqrt(screen.get_monitor_width_mm(major) ** 2 + screen.get_monitor_height_mm(major) ** 2)
            self.profile[key] = diagonal_mm / 25.4
            return self.profile[key]

    def get_screen_area(self):
        key = 'Screen Area'
        if key in self.profile:
            return self.profile[key]
        else:
            import gi
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk
            screen = Gdk.Screen.get_default()
            major = screen.get_primary_monitor()
            self.profile[key] = screen.get_monitor_width_mm(major) * screen.get_monitor_height_mm(major) / 25.4 / 25.4
            return self.profile[key]

    def __init__(self, profile=None):
        self.ep = False
        self.diagonal = 0.0
        self.width = 0
        self.height = 0

        if profile:
            self.profile = profile
        else:
            self.profile = {}

        # Product type
        self.product_type = self.question_int("""Which product type would you like to verify?
[1] Desktop, Integrated Desktop, and Notebook Computers
[2] Workstations
[3] Small-scale Servers
[4] Thin Clients""", 4, "Product Type")

        if self.product_type == 1:
            # Computer type
            self.computer_type = self.question_int("""Which type of computer do you use?
[1] Desktop
[2] Integrated Desktop
[3] Notebook""", 3, "Computer Type")
            self.tvtuner = self.question_bool("Is there a television tuner?", "TV Tuner")

            if self.computer_type != 3:
                self.audio = self.question_bool("Is there a discrete audio?", "Discrete Audio")
            else:
                self.audio = False

            # GPU Information
            if self.question_bool("""Does it have switchable graphics and automated switching enabled by default?
Switchable Graphics: Functionality that allows Discrete Graphics to be disabled
when not required in favor of Integrated Graphics.""", "Switchable Graphics"):
                self.switchable = True
                # Those with switchable graphics can not apply the Discrete Graphics allowance.
                self.discrete = False
                self.discrete_gpu_num = 0
            else:
                self.discrete_gpu_num = self.question_int("How many discrete graphics cards?", 10, "Discrete Graphics Cards")
                if self.discrete_gpu_num > 0:
                    self.switchable = False
                    self.discrete = True
                    if self.computer_type == 3:
                        self.fb_bw = self.question_num("How many is the display frame buffer bandwidth in gigabytes per second (GB/s) (abbr FB_BW)?\nThis is a manufacturer declared parameter and should be calculated as follows: (Data Rate [Mhz] × Frame Buffer Data Width [bits]) / ( 8 × 1000 ) ", "Frame Buffer Bandwidth")
                else:
                    self.switchable = False
                    self.discrete = False

            # Screen size
            if self.computer_type != 1:
                self.diagonal = self.get_diagonal()
                self.screen_area = self.get_screen_area()
                (width, height) = self.get_resolution()
                if width * height >= 2300000:
                    self.ep = self.question_bool("""Is it an Enhanced-perforcemance Integrated Display?
  i. Contrast ratio of at least 60:1 measured at a horizontal viewing angle of at least 85° from the 
     perpendicular on a flat screen and at least 83° from the perpendicular on a curved screen, 
     with or without a screen cover glass; 
 ii. A native resolution greater than or equal to 2.3 megapixels (MP); and
iii. Color Gamut greater than or equal to 32.9% of CIE LUV.""", "Enhanced Display")
                else:
                    self.ep = False

            # Power Consumption
            self.off = self.question_num("What is the power consumption in Off Mode?", "Off Mode")
            if self._check_wol():
                self.profile["Wake-on-LAN"] = True
                self.off_wol = self.question_num("What is the power consumption in Off Mode with Wake-on-LAN enabled?", "Off Mode with WOL")
            else:
                self.profile["Wake-on-LAN"] = False
                self.off_wol = self.off
            self.sleep = self.question_num("What is the power consumption in Sleep Mode?", "Sleep Mode")
            if self._check_wol():
                self.profile["Wake-on-LAN"] = True
                self.sleep_wol = self.question_num("What is the power consumption in Sleep Mode with Wake-on-LAN enabled?", "Sleep Mode with WOL")
            else:
                self.profile["Wake-on-LAN"] = False
                self.sleep_wol = self.sleep
            self.long_idle = self.question_num("What is the power consumption in Long Idle Mode?", "Long Idle Mode")
            self.short_idle = self.question_num("What is the power consumption in Short Idle Mode?", "Short Idle Mode")
        elif self.product_type == 2:
            self.off = self.question_num("What is the power consumption in Off Mode?", "Off Mode")
            self.sleep = self.question_num("What is the power consumption in Sleep Mode?", "Sleep Mode")
            self.long_idle = self.question_num("What is the power consumption in Long Idle Mode?", "Long Idle Mode")
            self.short_idle = self.question_num("What is the power consumption in Short Idle Mode?", "Short Idle Mode")
            self.max_power = self.question_num("What is the maximum power consumption?", "Maximum Power")
            self.get_disk_num()
        elif self.product_type == 3:
            self.off = self.question_num("What is the power consumption in Off Mode?", "Off Mode")
            self.short_idle = self.question_num("What is the power consumption in Short Idle Mode?", "Short Idle Mode")
            if self.get_cpu_core() < 2:
                self.more_discrete = self.question_bool("Does it have more than one discrete graphics device?", "More Discrete Graphics")
            else:
                self.more_discrete = False
        elif self.product_type == 4:
            self.off = self.question_num("What is the power consumption in Off Mode?", "Off Mode")
            self.sleep = self.question_num("What is the power consumption in Sleep Mode?\n(You can input the power consumption in Long Idle Mode, if it lacks a discrete System Sleep Mode)", "Sleep Mode")
            self.long_idle = self.question_num("What is the power consumption in Long Idle Mode?", "Long Idle Mode")
            self.short_idle = self.question_num("What is the power consumption in Short Idle Mode?", "Short Idle Mode")
            self.media_codec = self.question_bool("Does it support local multimedia encode/decode?", "Media Codec")
            self.discrete = self.question_bool("Does it have discrete graphics?", "Discrete Graphics")
            self.integrated_display = self.question_bool("Does it have integrated display?", "Integrated Display")
            if self.integrated_display:
                self.diagonal = self.get_diagonal()
                self.screen_area = self.get_screen_area()
                (width, height) = self.get_resolution()
                if width * height >= 2300000:
                    self.ep = self.question_bool("""Is it an Enhanced-perforcemance Integrated Display?
  i. Contrast ratio of at least 60:1 measured at a horizontal viewing angle of at least 85° from the 
     perpendicular on a flat screen and at least 83° from the perpendicular on a curved screen, 
     with or without a screen cover glass; 
 ii. A native resolution greater than or equal to 2.3 megapixels (MP); and
iii. Color Gamut greater than or equal to 32.9% of CIE LUV.""", "Enhanced Display")
                else:
                    self.ep = False

        # Ethernet
        if "Gigabit Ethernet" in self.profile:
            self.eee = self.profile["Gigabit Ethernet"]
        else:
            self._check_eee_num()

        if "Disk Number" in self.profile:
            self.disk_num = self.profile["Disk Number"]
        if "CPU Cores" in self.profile:
            self.cpu_core = self.profile["CPU Cores"]
        if "CPU Clock" in self.profile:
            self.cpu_clock = self.profile["CPU Clock"]
        if "Memory Size" in self.profile:
            self.mem_size = self.profile["Memory Size"]

    def _check_wol(self):
        if "Wake-on-LAN" in self.profile:
            return self.profile["Wake-on-LAN"]
        with open("/proc/acpi/wakeup") as f:
            line = f.readline()
            while line:
                if line.startswith('GLAN'):
                    if 'enabled' in line:
                        return True
                    elif 'disabled' in line:
                        return False
                line = f.readline()
        return False

    def _check_eee_num(self):
        self.eee = 0
        for dev in os.listdir("/sys/class/net/"):
            if dev.startswith('eth') or dev.startswith('enp'):
                if os.path.exists("/sys/class/net/" + dev + "/speed"):
                    speed = 0
                    with open("/sys/class/net/" + dev + "/speed") as f:
                        speed = int(f.read())
                    if speed >= 1000:
                        self.eee = self.eee + 1

    def _get_cpu_vendor(self):
        vendor=subprocess.check_output("cat /proc/cpuinfo | grep 'vendor_id' | grep -ioE '(intel|amd)'", shell=True, encoding='utf8').strip()
        if re.match("intel", vendor, re.IGNORECASE):
            return 'intel'
        if re.match("amd", vendor, re.IGNORECASE):
            return 'amd'
        return 'unknown'

    def get_cpu_core(self):
        if "CPU Cores" in self.profile:
            self.cpu_core = self.profile["CPU Cores"]
            return self.cpu_core

        try:
            subprocess.check_output('cat /proc/cpuinfo | grep cores', shell=True, encoding='utf8')
        except subprocess.CalledProcessError:
            self.cpu_core = 1
        else:
            self.cpu_core = int(subprocess.check_output('cat /proc/cpuinfo | grep "cpu cores" | sort -ru | head -n 1 | cut -d: -f2 | xargs', shell=True, encoding='utf8').strip())

        debug("CPU core: %s" % (self.cpu_core))
        self.profile["CPU Cores"] = self.cpu_core
        return self.cpu_core

    def get_cpu_clock(self):
        if "CPU Clock" in self.profile:
            self.cpu_clock = self.profile["CPU Clock"]
            return self.cpu_clock

        cpu = self._get_cpu_vendor()
        if cpu == 'intel':
            self.cpu_clock = float(subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | sort -u | cut -d: -f2 | cut -d@ -f2 | xargs | sed 's/GHz//'", shell=True, encoding='utf8').strip())
        elif cpu == 'amd':
            self.cpu_clock = float(subprocess.check_output("sudo dmidecode -t processor | grep 'Current Speed' | cut -d: -f2 | xargs | sed 's/MHz//'", shell=True, encoding='utf8').strip()) / 1000
        else:
            raise Exception('Unknown CPU Vendor')

        debug("CPU clock: %s GHz" % (self.cpu_clock))
        self.profile["CPU Clock"] = self.cpu_clock
        return self.cpu_clock

    def get_mem_size(self):
        if "Memory Size" in self.profile:
            self.mem_size = self.profile["Memory Size"]
            self.mem_total_slots = self.profile["Memory Total Slots"]
            self.mem_used_slots = self.profile["Memory Used Slots"]
            return self.mem_size

        self.mem_size = 0
        self.mem_used_slots = 0
        self.mem_total_slots = int(subprocess.check_output("sudo dmidecode -t 16 | grep ' Devices:' | awk -F':' '{print $2}'", shell=True, encoding='utf8'))
        for size in subprocess.check_output("sudo dmidecode -t 17 | grep 'Size:.*MB' | awk '{print $2}'", shell=True, encoding='utf8').split('\n'):
            if size:
                self.mem_size = self.mem_size + int(size)
                self.mem_used_slots = self.mem_used_slots + 1
        self.mem_size = self.mem_size / 1024

        debug("Memory size: %s GB" % (self.mem_size))
        debug("Memory total slots: %s" % (self.mem_total_slots))
        debug("Memory used slots: %s" % (self.mem_used_slots))
        self.profile["Memory Size"] = self.mem_size
        self.profile["Memory Total Slots"] = self.mem_total_slots
        self.profile["Memory Used Slots"] = self.mem_used_slots
        return self.mem_size

    def get_disk_num(self):
        if "Disk Number" in self.profile:
            self.disk_num = self.profile["Disk Number"]
            return self.disk_num

        self.disk_num = len(subprocess.check_output('ls /sys/block | grep -e sd -e nvme', shell=True, encoding='utf8').strip().split('\n'))

        debug("Disk number: %s" % (self.disk_num))
        self.profile["Disk Number"] = self.disk_num
        return self.disk_num

    def get_eee_num(self):
        if "Gigabit Ethernet" in self.profile:
            self.eee = self.profile["Gigabit Ethernet"]
            return self.eee

        self._check_eee_num()

        debug("Gigabit Ethernet: %s" % (self.eee))
        self.profile["Gigabit Ethernet"] = self.eee
        return self.eee

    def set_display(self, diagonal, ep):
        self.diagonal = diagonal
        self.ep = ep

    def get_display(self):
        return (self.diagonal, self.ep)

    def get_dmi_info(self, info):
        base = '/sys/devices/virtual/dmi/id/'
        if os.path.exists(base + info):
            with open(base + info, "r") as data:
                return data.read().strip().replace(' ','_')

    def get_bios_version(self):
        if "BIOS version" not in self.profile:
            self.profile["BIOS version"] = self.get_dmi_info('bios_version')
        return self.profile["BIOS version"]

    def get_product_name(self):
        if "Product name" not in self.profile:
            self.profile["Product name"] = self.get_dmi_info('product_name')
        return self.profile["Product name"]

    def get_resolution(self):
        if "Display Width" in self.profile and "Display Height" in self.profile:
            self.width = self.profile["Display Width"]
            self.height = self.profile["Display Height"]
            return (self.width, self.height)

        (width, height) = subprocess.check_output("xrandr --current | grep current | sed 's/.*current \\([0-9]*\\) x \\([0-9]*\\).*/\\1 \\2/'", shell=True, encoding='utf8').strip().split(' ')
        self.width = int(width)
        self.height = int(height)
        debug("Resolution: %s x %s" % (self.width, self.height))
        self.profile["Display Width"] = self.width
        self.profile["Display Height"] = self.height
        return (self.width, self.height)

    def get_power_consumptions(self):
        return (self.off, self.sleep, self.long_idle, self.short_idle)

    def get_basic_info(self):
        return (self.get_cpu_core(), self.get_cpu_clock(), self.get_mem_size(), self.get_disk_num())

    def report(self, filename):
        product_types = ('Desktop, Integrated Desktop, and Notebook Computers', 'Workstations', 'Small-scale Servers', 'Thin Clients')
        computer_types = ('Desktop', 'Integrated Desktop', 'Notebook')
        units = { "CPU Clock": "GHz", "Display Diagonal": "inches", "Display Height": "pixels", "Display Width": "pixels", "Memory Size": "GB", "Screen Area": "inches^2" }
        with open(filename, "w") as data:
            data.write('Devicie configuration details:')
            data.write('\n\tProduct Type: ' + product_types[self.profile['Product Type'] - 1])
            data.write('\n\tComputer Type: ' + computer_types[self.profile['Computer Type'] - 1])

            for key in sorted(self.profile.keys()):
                if key not in ('Off Mode', 'Sleep Mode', 'Short Idle Mode', 'Long Idle Mode', 'Product Type', 'Computer Type', 'BIOS version'):
                    if key in units:
                        if isinstance(self.profile[key], float):
                            data.write('\n\t' + key + ': ' + str(round(self.profile[key], 2)) + ' ' + units[key])
                        else:
                            data.write('\n\t' + key + ': ' + str(self.profile[key]) + ' ' + units[key])
                    else:
                        data.write('\n\t' + key + ': ' + str(self.profile[key]))
            try:
                result = subprocess.run(['ubuntu-report', 'show'], stdout=subprocess.PIPE)
                ubuntu_report = json.loads(result.stdout)
                data.write('\nManifest version: ' + ubuntu_report['OEM']['DCD'])
            except FileNotFoundError:
                pass
            except KeyError:
                pass

            data.write('\nBIOS version: ' + self.get_bios_version())

            for k in ('Short Idle Mode', 'Long Idle Mode', 'Sleep Mode', 'Off Mode'):
                data.write('\n' + k + ': ' + str(self.profile[k]) + ' W')
            data.write('\n')

    def save(self, filename):
        with open(filename, "w") as data:
            data.write(json.dumps(self.profile, sort_keys=True, indent=4, separators=(',', ': ')) + '\n')
