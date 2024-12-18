Two types of post-silicon devices are modeled: CNT-FET and CNT-interconnect.


The first type is the CNT-FET.       

This predictive model is a surface potential based compact model that captures the ballistic transport in the channel and the Schottky-barrier effect due to the contacts. With all model equations in the closed form, this model is efficient for large-scale circuit simulation and scalable with process and design conditions.
 
The Verilog-A file and the lookup table need to be uploaded to use the model in the SPICE environment. For more details on model setup in Verliog-A, please check the manual-FET to run this model with SPECTRE .

Level 1: Verilog-A file for CNT-FET: V1.0
Lookup table: V1.0
 

The second type is CNT-interconnect that models the RLC properties of a single-wall metallic carbon nanotube. 

This model considers the impact of finite wire length on carrier mobility and the Schottky-barrier effect due to the contacts. A CNT-interconnect is modeled as a two-terminal RLC netlist for circuit simulations. The Verilog-A model is available for download here. Please check the manual-interconnect for further model information and simulation with SPECTRE.

Level 1: Verilog-A file for CNT-interconnect: V1.0

A typical SPECTRE netlist for an inverter using CNT-FETs  is shown in the example:

   

    simulator lang=spectre

    global 0 vdd!

   

    V0 (net037 0) vsource dc=0 type=pwl wave=[ 0 0.0 50p 2 ]

    C1 (net078 0) capacitor c=100a

   

    I30 (vdd! net037 net078 _net0) CNT diameter=1e-9 angle=0 tins=10e-9 \

    eins=16 tback=130e-9 eback=3.9 types=-1 L=115e-9 phisb=0.1 rs=0 \

    rd=0 beta=16 Cc=7e-12 mob=1 Csubfit=0.4 Cp=40e-12

   

    I31 (net078 net037 0 _net0) CNT diameter=1e-9 angle=0 tins=10e-9 eins=16 \

    tback=130e-9 eback=3.9 types=1 L=115e-9 phisb=0.1 rs=0 rd=0 \

    beta=16 Cc=7e-12 mob=1 Csubfit=0.4 Cp=40e-12

   

    V1 (vdd! 0) vsource dc=2 type=dc

    V2 (_net0 0) vsource dc=5 type=dc

 

Acknowledgement

We thank Prof. H.-S. P. Wong's group at Stanford University, Dr. A. Islamshah at Motorola Lab, and Dr. A. Keshavarzi at Intel for their support and valuable suggestions to the development of predictive CNT-FET models. 