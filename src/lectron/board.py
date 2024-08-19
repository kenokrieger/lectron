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


class Board:
    """
    Theoretical equivalent of the physical lectron board on which the gene
    blocks are placed. Blocks can be added to the board by calling the
    add_block method, connections can be added via the add_connection method, or
    by supplying a connections matrix directly.

    The board stores a list of blocks that it contains
    aswell as their connections with respect to each other. By calling
    the advance method, all blocks are updated synchronously.
    """

    def __init__(self):
        """Constructor for the Board class."""
        self._blocks = list()
        self._labelled_blocks = dict()
        self.connections = np.zeros((0, 0), dtype=int)

    def __getitem__(self, item):
        if type(item) is str:
            return self._get_block_by_label(item)
        if type(item) is int:
            return self._blocks[item]
        block_idx = self._blocks.index(item)
        return self._blocks[block_idx]

    def get_blocks(self):
        """
        Returns a list of all blocks currently on the board.

        Returns:
            list: The blocks on the board.

        """
        return self._blocks.copy()

    def get_block_states(self):
        """
        Get a list of all block states which can be ON (1) or OFF (0).

        Returns:
            list: The activity of each block

        """
        return [b.is_active() for b in self._blocks]

    def get_block_voltages(self):
        """
        Get a list of all block's voltages.

        Returns:
            list: The voltage of each block

        """
        return [b.get_voltage() for b in self._blocks]

    def add_block(self, block):
        """
        Add a block to the board.

        Args:
            block(lectron.blocks.GeneBlock): The block to add to the board.

        Returns:
            None.

        """
        new_connections = np.zeros(
            tuple(s + 1 for s in self.connections.shape), dtype=int
        )
        new_connections[:-1, :-1] = self.connections
        self._blocks.append(block)
        self.connections = new_connections
        block_label = block.get_label()
        if block_label:
            self._labelled_blocks[block_label] = block

    def add_blocks(self, blocks):
        for block in blocks:
            self.add_block(block)

    def remove_block(self, block_or_label):
        """
        Remove a block and all its connections from the board.

        Args:
            block_or_label(lectron.blocks.GeneBlock or str): The block to
                remove.

        Returns:
            None.

        """
        if type(block_or_label) is str:
            block = self._get_block_by_label(block_or_label)
            del self._labelled_blocks[block_or_label]
        else:
            block = block_or_label
        block_idx = self._blocks.index(block)
        del self._blocks[block_idx]
        for axis in range(2):
            self.connections = np.delete(self.connections, block_idx, axis)

    def add_connection(self, source, target, value=1):
        """
        Add a connection between two existing blocks on the board.

        Args:
            source(lectron.blocks.GeneBlock or str): The block with the outgoing
                connection.
            target(lectron.blocks.GeneBlock or str): The block with the ingoing
                connection.
            value(int): The value determining the type of the connection where
                1 is a exciting, -1 a inhibiting and 0 a not existing
                connection. Defaults to 1.

        Returns:
            None.

        """
        if type(source) is str:
            source_block = self._get_block_by_label(source)
        else:
            source_block = source
        if type(target) is str:
            target_block = self._get_block_by_label(target)
        else:
            target_block = target
        source_idx = self._blocks.index(source_block)
        target_idx = self._blocks.index(target_block)

        self.connections[target_idx, source_idx] = value

    def remove_connection(self, source_block, target_block):
        """
        Remove a connection between two blocks.

        Alias for add_connection(source_block, target_block, 0)
        """
        # remove active connection by overriding the existing
        # connection with a zero valued connection
        self.add_connection(source_block, target_block, 0)

    def set_connections(self, connections):
        """
        Set all connections by passing a numpy.ndarray with shape (N, N), where
        N is the number of blocks, that contains all connections between the
        blocks.

        Args:
            connections(numpy.ndarray): A matrix storing the connections between
                the blocks.

        Returns:
            None.

        """
        self.connections = connections

    def advance(self):
        """
        Update all blocks on the board synchronously according to their
        connections.
        """
        block_states = np.array([b.is_active() for b in self._blocks])
        ingoing_connections = np.matmul(self.connections, block_states)

        for block, ingoing_connection in zip(self._blocks, ingoing_connections):
            block.update(ingoing_connection)

    def _get_block_by_label(self, block_or_label):
        try:
            block = self._labelled_blocks[block_or_label]
        except KeyError:
            raise KeyError("Could not locate block with label"
                           f" {block_or_label}.")
        return block
