# Copyright (C) 2024  Keno Krieger <kriegerk@uni-bremen.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
MAX_VOLTAGE = 9.0 # maximum voltage at the condensator in volts
DELTA_T = 1e-3 # time step in seconds


class GeneBlock:
    """
    The theoretical counterpart to the physical gene block of the lectron kit.
    When the amount of ingoing connections is higher than the threshhold, the
    condensator of the block starts charging up. Once the voltage of the
    condensator exceeds a certain threshhold, the block itself turns active and
    starts an outgoing connection.
    """

    def __init__(self, hysteresis=0.8, threshhold=2, time_constant=4.0,
                 label=""):
        """
        Constructor of the GeneBlock class.
        
        Args:
            hysteresis(float): Set a percentile value for the hysteresis of the
                condensator. The hysteresis controls at what voltage at the
                condensator the block turns active and inactive again.

                U_{activate} = 4.5 V +/- hysteresis \cdot 4.5 V
            
            threshhold(int): The threshhold of active ingoing connections 
                which is needed to activate the block.
            
            time_constant(float): The time constant of the condensator that
                controls how fast it is charging and discharging.

        """
        self.hysteresis = hysteresis
        self.threshhold = threshhold
        self.time_constant = time_constant
        self.label = label
        self._voltage = 0.0
        self._is_active = False

    def set_hysteresis(self, hysteresis):
        """
        Set the hysteresis of the gene block. The hysteresis determines when
        the block turns active, or, respectively, inactive.

        Args:
            hysteresis(float): The value for the hysteresis.

        Returns:
            None

        """
        self.hysteresis = hysteresis

    def get_hysteresis(self):
        """
        Get the current value of the hysteresis.

        Returns:
            float: The value of the hysteresis.
        """
        return self.hysteresis

    def set_threshhold(self, threshhold):
        """
        Set the threshhold for the block activation.

        Args:
            threshhold(int): The value for the threshhold.

        Returns:
            None.

        """
        self.threshhold = threshhold

    def get_threshhold(self):
        """
        Get the current threshhold.

        Returns:
            int: The value of the threshhold.

        """
        return self.threshhold

    def set_time_constant(self, time_constant):
        """
        Set the time constant determining the charge and discharge of the
        condensator.

        Args:
            time_constant(float): The value for the time constant.

        Returns:
            None.

        """
        self.time_constant = time_constant

    def get_time_constant(self):
        """
        Get the current value of the time constant.

        Returns:
            float: The time constant.

        """
        return self.time_constant

    def set_label(self, label):
        """
        Set a new value for the block label.

        Args:
            label(str): The label for the block.
        
        """
        self.label = label
    
    def get_label(self):
        """
        Get the current label of the block.

        Returns:
            The label of the block.
        
        """
        return self.label

    def get_voltage(self):
        """
        Get the current voltage of the condensator inside the block.

        Returns:
            float: The voltage.

        """
        return self._voltage

    def is_active(self):
        """
        Check whether the block is active.

        Returns:
            int: 1 if the block is active else 0.

        """
        if self._is_active and self._voltage > MAX_VOLTAGE / 2 - self.hysteresis * MAX_VOLTAGE / 2:
            return 1
        if not self._is_active and self._voltage > MAX_VOLTAGE / 2 + self.hysteresis * MAX_VOLTAGE / 2:
            self._is_active = True
            return 1
        self._is_active = False
        return 0

    def turn_on(self):
        """
        Turn the block on by setting its voltage to the maximum voltage.
        """
        self._voltage = MAX_VOLTAGE
    
    def turn_off(self):
        """
        Turn the block of by setting its voltage to 0
        """
        self._voltage = 0.0

    def update(self, ingoing_connections):
        """
        Update the block according to its ingoing connections.

        Args:
            ingoing_connections(int): The amount of ingoing connections.

        Returns:
            None.

        """
        if ingoing_connections >= self.threshhold:
            self._charge()
        else:
            self._discharge()

    def _charge(self):
        """
        Increase the voltage of the condensator.
        """
        self._voltage += (
            (MAX_VOLTAGE - self._voltage) / self.time_constant * DELTA_T
        )

    def _discharge(self):
        """
        Decrease the voltage of the condensator.
        """
        self._voltage -= self._voltage / self.time_constant * DELTA_T
