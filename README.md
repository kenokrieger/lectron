# <img src="https://raw.githubusercontent.com/kenokrieger/lectron/master/LOGO.png" alt="lectron" height=60>

The lectron package is a programatical replication of a
[lectron kit](https://en.wikipedia.org/wiki/Raytheon_Lectron). 
It can be used to model various molecular networks by connecting
the blocks through excitatory or inhibitory links.

## Install

You can install the package directly from [GitHub](https://github.com/kenokrieger/zephyros) by running
```bash
pip install git+https://github.com/kenokrieger/lectron
```
or download the source code of the latest 
[release](https://github.com/kenokrieger/lectron/releases/latest)
and then run
```bash
python3 -m pip install .
``` 
in the top-level directory to install the package.

## Usage

### Customisation

By default, the maximum voltage of a block is set to 9 V and 
the time increment for each step of the charging is set to 
one millisecond.
To change the values use 
```python
import lectron.blocks

lectron.blocks.MAX_VOLTAGE = 9.0
lectron.blocks.DELTA_T = 1e-3
```

### Creating a new block

````python
from lectron.blocks import GeneBlock

test_block = GeneBlock(hysteresis=0.8, threshhold=2,  time_constant=4.0,
                       label="test")
# to fully discharge the block use
test_block.turn_off()
# to fully charge the block use
test_block.turn_on()
# to get the current voltage use
test_block.get_voltage()
# to check whether the block is active use
test_block.is_active()
# to update the block use
ingoing_connections = 1 # on board corresponds to the sum 
                        # of the connections w_ij and the activations S_j,
                        # i.e. \sum_i w_ij S_j
                        # if the sum over the connections is larger than
                        # the threshold the block charges, else it 
                        # discharges
test_block.update(ingoing_connections)
````

### Connecting two blocks on a board
````python
from lectron.blocks import GeneBlock
from lectron.board import Board

board = Board()
test_block_1 = GeneBlock()
test_block_2 = GeneBlock()
# add the blocks to the board
board.add_block(test_block_1, label="test_1")
board.add_block(test_block_2, label="test_2")
# create an outgoing connection from test_block_1 to test_block_2
# use 1 for an excitatory and -1 for an inhibitory connection
board.add_connection(test_block_1, test_block_2, 1)
# blocks can also be connected by label
board.add_connection("test_1", "test_2", 1)
````

### Updating the board
````python
from lectron.board import Board

board = Board()
# to advance the simulation on timestep
board.advance()
# to get the block activations
board.get_block_states()
````

## Examples 

For an example of the yeast cell cycle, see `yeast_cell_cycle.py`.
### Example 1: Retrieve the charging curve of a block
```python
import numpy as np
import matplotlib.pyplot as plt
from lectron.board import GeneBlock

nmeasurements= 40_000 # number of measurments for the curve
time_constant = 4.0 # time in seconds
time_array = np.linspace(0, nmeasurements / 1e3, nmeasurements)
voltage = np.empty((nmeasurements, ))

test_block = GeneBlock(threshhold=0, time_constant=time_constant)
# set the blocks voltage to zero
test_block.turn_off()
# charge the block
for iteration in range(nmeasurements):
    test_block.update(0)
    voltage[iteration] = test_block.get_voltage()

plt.plot(time_array, voltage, linestyle="dotted", linewidth=3,
         label="modelled")
# plot the true charging curve of the block
# known from electrical physics
plt.plot(time_array, 9.0 * (1 - np.exp(-time_array / time_constant)),
         linestyle="dashed", linewidth=1, label="true")
plt.xlabel("Time in s")
plt.ylabel("Voltage in V")
plt.legend()
plt.savefig("Charging_Curve.pdf", dpi=300)
plt.close()

test_block.turn_on()
# discharge the block
for iteration in range(nmeasurements):
    test_block.update(-1)
    voltage[iteration] = test_block.get_voltage()

plt.plot(time_array, voltage, linestyle="dotted", linewidth=3,
         label="modelled")
plt.plot(time_array, 9.0 * np.exp(-time_array / time_constant),
         linestyle="dashed", linewidth=1, label="true")
plt.xlabel("Time in s")
plt.ylabel("Voltage in V")
plt.legend()
plt.savefig("Discharging_Curve.pdf", dpi=300)
plt.close()
```

### Example 2: Model coupled inhibitory genes
```python
import matplotlib.pyplot as plt
import numpy as np

from lectron.board import Board
from lectron.blocks import GeneBlock


def create_circular_inhibition(board, ninhibitors=3):
    """
    Create a board of circular inhibiting blocks.

    Args:
        board(lectron.board): The board to place the blocks on.
        ninhibitors(int): The number of inhibiting blocks.

    Returns:
        lectron.board: The board with the new blocks.

    """
    for iteration in range(ninhibitors):
        board.add_block(GeneBlock(threshhold=0))
    blocks = board.get_blocks()
    # add circular inhibiting connections between each block
    for block_idx in range(ninhibitors):
        board.add_connection(blocks[block_idx], blocks[block_idx - 1], -1)
    #turn on one block to avoid race condition
    blocks[0].turn_on()


def measure_circular_inhibition(ninhibitors=3, nmeasurements=100_000):
    """
    Measure voltage and block activity in a circular inhibitor.

    Args:
        ninhibitors(int): The number of inhibiting blocks.
    """
    block_states = []
    block_voltages = []

    # time in seconds
    time_array = np.linspace(0, nmeasurements / 1e3, nmeasurements)
    voltages = np.empty((nmeasurements, ninhibitors), dtype=float)
    activities = np.empty((nmeasurements, ninhibitors), dtype=int)

    board = Board()
    create_circular_inhibition(board, ninhibitors)
    for iteration in range(100_000):
        board.advance()
        activities[iteration] = board.get_block_states()
        voltages[iteration] = board.get_block_voltages()

    for block_idx in range(ninhibitors):
        plt.plot(time_array, activities[:, block_idx],
                 label=f"Block {block_idx}")
    plt.xlabel("Time in s")
    plt.ylabel("Activity")
    plt.savefig("Block_States_{}.pdf".format(ninhibitors), dpi=300)
    plt.close()


    for block_idx in range(ninhibitors):
        plt.plot(time_array, voltages[:, block_idx],
                 label=f"Block {block_idx}")
    plt.xlabel("Time in s")
    plt.ylabel("Voltage in V")
    plt.savefig("Block_Voltages_{}.pdf".format(ninhibitors), dpi=300)
    plt.close()

    
# Measure the block activity and voltage of a circular inhibitor.
board = Board()
measure_circular_inhibition(board, ninhibitors=3)
```
