This project simulates the crowd simulation process in supermarket.

# Specification of Implementation
## Modelling
The simulation is agent-based.

The agents located at the "agent map", which is a 2D grid showing where are the agents.
The supermarket geometry, "shop map, or just shop" is another 2D grid, containing the descriptive information regarding the supermarket.
When scale factor is 1, the "agent map" uses the same grid structure as the "shop map".
A StateMap class is consist by the agent map and the shop map.

## files
- main.py: the controller of different modules, consuming all input parameters via a yaml.
- some special parameters in yaml can be also overridden by the option of main.py, such as agent_number, map_scale_factor. could be more but at this moment let use just keeps these 2 but reserve the extensibility for more parameters in yaml in the future.
- state.py: containing data objects of map, such as StateMap, agent map, and shop map.

## algorithm
- an agent shows up at the entrance.
- the agent moves toward to the product01 position at the shop.
- another agents shows up at the entrance.
- the first agent (agent01) moves toward to product01, if agent01 has been accessed product01, then moves toward to product02. the 2nd follows the same logic.
- keep spawning more agents
- the agent exhausts the product list will go to the exit and removed.

### how agent moves
the agent movement is completed by the update method of AgentMap.
when "update" is invoked, all agents are walked through.
each agents will think (via agent_thinking method) and then return the value of "where to move on the agent map" and "how many cells of grid to move", and then update its own location information.

let us implement _potential_deadlock_detection later on after a working minimal viable product. it means that what a deadlock patter is found before updating its own location information.

noticeably there are obstacles that an agent can not move to. if the calculation shows such update, then choose the next possible move. if there is no way to go, stop for this iteration.

### shop description
- a shop should have obstacles (shelf) that an agent can not move on to.
- a shop also have products that an agent will stay beside it (beside means 1 cell. make this parameter in yaml as well so I can change the parameter easily later on) for 5 iteration step.
- a shelf element occupies one cell of shop map. many shelf elements consists of a shelf.
- a product element occupies one cell of the shop map as well. product elements are usually a part of the shelf.
- design a way via yaml input to indicate where to put the shelf elements and product elements.
- product element has different types. the product list of an agent consisted of several products in different types.


## minimal viable product
- the shop should have one entrance, where agents spawn, and one exit, where agents are removed.
- each agent has its own product list. they are going to the shop to find the products.



# objective
a working minimal viable product. I expect to see clogging if there are too many agents spawned in a short period. I want to know what is the number of the agents.