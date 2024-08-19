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
import numpy as np
import matplotlib.pyplot as plt

if "science" in plt.style.available: plt.style.use("science")

from lectron.blocks import GeneBlock
from lectron.board import Board


def main():
    # create the blocks with their respective parameters
    blocks = [
        GeneBlock(threshhold=2, label="YOX1"),
        GeneBlock(threshhold=1, label="YHP1"),
        GeneBlock(threshhold=2, label="HCM1"),
        GeneBlock(threshhold=1, label="CLN3"),
        GeneBlock(threshhold=1, label="SBF"),
        GeneBlock(threshhold=1, label="SFF"),
        GeneBlock(threshhold=1, label="MBF"),
        GeneBlock(threshhold=1, label="ACE2"),
        GeneBlock(threshhold=1, label="SWI5"),
        GeneBlock(hysteresis=0.1, threshhold=2, time_constant=0.1,
                  label="YOX1 & YHP1"),
        GeneBlock(hysteresis=0.1, threshhold=2, time_constant=0.1,
                  label="SWI5 & ACE2"),
        GeneBlock(hysteresis=0.1, threshhold=1, time_constant=0.1,
                  label="CLN3 | MBF")
    ]
    # initialise the board
    board = Board()
    board.add_blocks(blocks)
    # direct connections
    board.add_connection("CLN3", "MBF")
    board.add_connection("SFF", "ACE2")
    board.add_connection("SFF", "SWI5")
    # connections for YOX1
    board.add_connection("MBF", "YOX1")
    board.add_connection("SBF", "YOX1")
    # connections for YHP1
    board.add_connection("MBF", "YHP1")
    board.add_connection("SBF", "YHP1")
    # connections for HCM1
    board.add_connection("MBF", "HCM1")
    board.add_connection("SBF", "HCM1")
    # connections for CLN3
    board.add_connection("SWI5", "SWI5 & ACE2")
    board.add_connection("ACE2", "SWI5 & ACE2")

    board.add_connection("SWI5 & ACE2", "CLN3")

    board.add_connection("YOX1", "YOX1 & YHP1")
    board.add_connection("YHP1", "YOX1 & YHP1")

    board.add_connection("SWI5 & ACE2", "CLN3")
    board.add_connection("YOX1 & YHP1", "CLN3", -1)
    # connections for SBF
    board.add_connection("CLN3", "CLN3 | MBF")
    board.add_connection("MBF", "CLN3 | MBF")

    board.add_connection("CLN3 | MBF", "SBF")
    board.add_connection("YOX1 & YHP1", "SBF", -1)
    # connections for SFF
    board.add_connection("SBF", "SFF")
    board.add_connection("HCM1", "SFF")

    # one time step is 1e-3 seconds
    # start the network with a constant supply of CLN3
    # for three seconds
    for iteration in range(3000):
        board["CLN3"].turn_on()
        board.advance()

    # now start measuring the activities
    ntimesteps = 100_000
    activities = np.empty((ntimesteps, 9), dtype=int)
    for timestep in range(ntimesteps):
        board.advance()
        # the last three activities are of the "and" and "or" blocks
        # and are not interesting for the network
        activities[timestep] = board.get_block_states()[:-3]

    # plot the block activities replace 0s with nan so they
    # don't show up in the visualisation
    where_zero = np.where(activities, 1, np.nan)
    block_order = reversed([3, 6, 4, 2, 0, 1, 5, 7, 8])
    for offset, block_idx in enumerate(block_order):
        plt.plot(where_zero[:, block_idx] + offset / 3,
                 label=blocks[block_idx].get_label(),
                 linewidth=6, color="grey")
    # nicht schön aber selten
    plt.yticks([(offset + 3) / 3 for offset in range(9)],
               plt.gca().get_legend_handles_labels()[1])
    plt.xlabel("time in seconds")
    plt.savefig("yeast_cell_simulation.pdf", dpi=300)


if __name__ == "__main__":
    main()
