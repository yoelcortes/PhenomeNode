# PhenomeNode: Graphical Representations of Process Phenomena

**This library is still under development and is not yet ready for users.**

PhenomeNode automates the systematic creation of graph representations at the phenomenological level, not just at level of unit operations or superstructures of units. 
The following preview shows a phenomenological diagram where both variables (rings) and equations (solid circles) are represented as nodes. 
The material balance, energy balance, equilibrium, and pressure equation nodes are colored black, red, purple, and green. Variables that are present as inlet and outlet streams of unit operations are colored yellow
while implicit variables are grey.

```python
import phenomenode as phn
stage = phn.StageVLE()
stage.diagram(format='png', label_format='h', label_nodes=True, cluster=False, dpi='900')
```

![VLEstage](VLE.png)
