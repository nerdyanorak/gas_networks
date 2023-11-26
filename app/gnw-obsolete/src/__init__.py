"""The GasNetwork package

GasNetwork provides a set of interfaces and classes that describe (gas) network
facilities and are used to generate a MIP/LP formulation for the given
optimisation problem.

The network is made up from storages, hubs, markets, 
and flows from/to the storage to/from the trading hubs

The struture of a gas network is as follows:

Network holds one or more Systems
System may contain on or more
    - Hubs
    - Storages
    - Suppliers @todo: to be supported
    - Consumers @todo: to be supproted
    - bi/uni-directional Flows connecting Hubs, Storages,
      Supplieres, Consumers, etc.
Systems my be connected having Flows between a Hub of one System and a Hub
of the other System.
Hubs may contain a Market,
Markets have standard products entity StdProds and discount factor curve DF
StdProds have a non-empty list of standard product definitions StdProdDef.
Each StdProdDef has a non-empty list of bid/ask prices and max trading capacity
limit as well as a current hedge-position.

System, Hub, Storage, Supplier, Consumer, Flow and Market
are gas network entities (GNEntity). Network is the top-level object
that manages all the GNEntities and is repsonsible for inputs, model build
(using PuLP), execution and outputs.

In general for all entities e and all dispatch periods t
volume(t) == volume(t+1) + sum(inflow(t,i)) - sum(outflow(t,j))
must hold,
subject to
e.min_volume(t) <= e.volume(t) <= e.max_volume(t)
e.min_inflow(t) <= sum(e.inflow(t,i)) <= e.max_inflow(t)
e.min_outflow(t) <= sum(e.outflow(t,j)) <= e.max_outflow(t)
for all i in INFLOWS(e), j in OUTFLOWS(e), e in ENTITIES

Dispatch periods t are provided as a vector of time steps in hours [h],
delta_time_dispatch, such that the duration of a
dispatch period t is delta_time_dispatch(t).
Start time of dispatch period t is
sum(delta_time_dispatch(j), j=0..t-1)
and the end time of dispatch period t is
sum(delta_time_dispatch(j), j=0..t-1) + delta_time_dispatch(t) =
sum(delta_time_dispatch(j), j=0..t), t = 0..N-1.

All additional constraints applicable, especially if they span over
multiple disptach periods are expressed as right sided open intervals
[t_s,t_e), with t_s <= t_e, t_s in 0..N-1, t_e in 0..N-1.

Depending on the type of entity additional constraints and
contributions to the objective function may exist. In the following the
various types of entities are characterised textually in more detail.

Flow
====
UniDirectionalFlow
------------------
This is the simplest of the entities. It is used to connect the gas flows
between 2 other (non Flow) entities, subject to potential capacity
constraints. The two by the Flow entity (flw) connected entities are called
source (src) and sink (snk), such that
    - the flow balance euqation
      src.outflow(t) [MWh] ==
      flw.inflow(t) [MWh] ==
      flw.outflow(t) [MWh] ==
      snk.inflow(t) [MWh]
    - the capacity constraints
      min_inflow(t)*delta_time_dispatch(t) [MW]*[h] <= flw.inflow(t) [MWh]
      flw.inflow(t) [MWh] <= max_inflow(t)*delta_time_dispatch(t) [MW]*[h] and
      min_outflow(t)*delta_time_dispatch(t) [MW]*[h] <= flw.outflow(t) [MWh]
      flw.outflow(t) [MWh] <= max_outflow(t)*delta_time_dispatch(t) [MW]*[h].
      In general flw.min_inflow(t) == flw.min_outflow(t) and
      flw.max_inflow(t) == flw.max_outflow(t)
must hold.
@todo: Additionally, a fix capacity cost [EUR/MW] and/or a variable flow
volume cost [EUR/MWh] may be charged, affecting the objective function.
  
BiDirectionalFlow
-----------------
Holds two UniDirectionalFlow entities, each connecting the same two other
(non Flow) entities but with swapped source/sink roles, i.e.,
bdflw(udflw1(src,snk),udflw2(snk,src)) having the additional constraints
that either
    - udflw1.inflow(t) == udflw1.outflow(t) > 0 or
      udflw2.inflow(t) == udflw2.outflow(t) > 0 or 
      udflw1.inflow(t) == udflw1.outflow(t) ==
      udflw2.inflow(t) == udflw2.outflow(t) == 0 --> MIP

@todo: Additionally, a fix cost for flow direction reversal [EUR] --> MIP

Hub
===
A Hub h holds a list of UniDirectionalFlow inflow entities (h := snk),
a list of UniDirectionalFlow outflow entities (h := src). The
UniDirectionalFlow entities held within BiDirectionalFlow entities are
contained in the two Flow lists, i.e., the fact that a UniDirectionalFlow
entity may be part of a BiDirectionalFlow entity is transparent to Hub h.
As UniDirectionalFlow entities have to be initialised with the src and snk
entities on the one hand and the Hub entity is initialised with list
inflow and outflow lists of UniDirectionalFlow entities where the Hub takes
the role of src and snk entity, respectively, it is required that
initialisation of those entity object instances can be carried out after
creation. The Hub h is subject to the following constraints:
    - sum(flw.outflow(t), flw in inflowList) [MWh] == h.inflow(t) [MWh]
    - h.inflow(t) [MWh] == h.outflow(t) [MWh]
    - h.outflow(t) [MWh] == sum(flw.inflow(t), flw in outflowList) [MWh]

Market
======
A Market entity m allows to sell gas volumes at the bid price and to buy
gas volumes at the asking price (--> affecting objective function)
and acts as a snk of a UniDirectionalFlow (for selling volumes) and as
a src (for buying volumes). To combine the two UniDirectionalFlow entities
involved into a BiDirectionalFlow entity in order to prevent buying and
sellings during the same dispatch period should not be necessary as
this should be achieved because of optimaility considerations.

The Market entity holds standard product definitions that are (hypotetically)
tradable. The follwong requirements must be satisfied:
    - The delivery periods of those standard products must match
      some dispatch interval [t_s,t_e) exactly,
    - must not overlap with delviery periods of any other defined standard
      products (@todo: relax this requirement), and
    - the union of all standard products' delivery periods must be equal to
      the union of all dispatch periods (@todo: relax this requirement), i.e.,
      every dispatch period t is part of a standard product delivery period.
    - For each standard product a minimum trading size [MW] is
      defined. If this minimum trading size > 0 then at least the volume [MWh]
      equivalent to the minimum trading size over the delivery period of the
      standard product is bought or sold, nothing otherwise
      (--> semi-contiuous variable, MIP).
    - A standard product clip size [MW] may be imposed, such that volumes bought
      or sold (above the minimal trading size) have to be exact integral multiple
      volumes [MWh] implied by that clip size and the standard products clip size.
      (--> MIP)

The market entity holds a discount factor curve object holding the discount
factors for the settlement times corresponding to the dispatch periods t.
In practice the settlement times to which those discount factors relate
correspond to the settlement times of the standard product's delviery
period into which a given dispatch period falls. But is up to the user to
provide appropriate discount factors.

The market entity holds a non-empty list of bid/ask curve objects. Each
bid/ask curve contains bid/ask prices corresponding to the standard products
definition with ever wider bid/ask spreads. Each bid ask curve object
has as well a maximal tradable capacity [MW] for every standard product. If a
standard product clip size [MW] is imposed then this maximal tradable
capacity [MW] must be a multiple of that clip size. (The idea here is that
through the optimisation first volumes are bought and sold at the prices
provided by the bid/ask curve with the narrowest spread, then at the prices
of the bid/ask curve with second narrowest spread, etc., allowing for volume
dependent bid/ask prices, assuming a illiquid market scenario where larger
volumes can only be bought (sold) at a premium (rebate), i.e., negative
economy of scale).


Storage
=======
During each dispatch period t a gas volume volume(t) [MWh] may be
injected (volume(t) > 0) or released/withdrawn (volume(t) < 0) subject to
    - storage fill level dependent injection/release capacity constraints,
      {min,max}_{injection,release}_capacity(t,level(t)) [MW]
    - storage fill volume limits {min,max}_volume_pct(t) [%], w.r.t. the
      working gas volume wgv(t) [MWh]
    - storage starting and ending fill volume {start,end}_volume_pct [%],
      w.r.t. wgv(t) [MWh]
    - storage capacity reserves (for SoS purposes) [MW]
    - storage volume reserves (for SoS purposes) volume_reserve_pct(t) [%],
      w.r.t. wgv(t) [MWh]
    - storage injection/release costs
        - fix per each injection/release dispatch period [EUR] --> MIP
        - fix per each injection/release dispatch interval [EUR] --> MIP
        - variable per injection/release volume [EUR/MWh]
        - same as previous three but as well storage fill level dependent --> MIP
      injection/release costs are part of the objective function
    - injected volume volume_inj(t) >= 0, volume_inj(t) >=  volume(t),
      volume_inj(t) == sum(inflow(t,i))
    - released volume volume_rel(t) >= 0, volume_rel(t) >= -volume(t),
      volume_rel(t) == sum(outflow(t,j))


Consumer
========
A Consumer c has a fixed consumption profile [MWh] equivalent to the
dispatch periods t, subject to constraints
    - c.inflow(t) == consumption(t), and
    - c.outflow(t) == 0

A Consumer is always part of a UniDirectionalFlow entity in the role
of the sink (snk).

Producer
========
Can be as simple as the oposite of the Consumer (e.g., fixed supply profile)
or as complicated as long term gas supply contract with daily, monthly, quarterly,
seasonal, yearly min/max constraints, make-up/carry forward features triggering
price discounts/penalities, etc.

What is common to all Producer entities is that they are always part of a
UniDirectionalFlow entity in the role of the source (src).
"""

__authors__ = ["Marc Roth (re04179)"]
__copyright__ = "RWE Supply & Trading GmbH"
__version__ = "0.1"

__all__ = ["entities", "utils" ]
