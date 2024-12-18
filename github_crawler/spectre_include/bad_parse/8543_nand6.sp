* FERNANDO MORAES   -  PUCRS
* revisao em 07/abril/2024
*************************************************************
*              ==> entrada 1 e' a mais proxima do gnd 
*              ==> entrada 2 a mais proxima da saida
*              ==> demais entradas fixas em '1' para o transistor N conduzir
*
* COMPLETAR a avaliação dos tempos de subida e descida - **LER** os comentarios
*************************************************************
simulator lang=spectre insensitive=no
include "st65.scs"
simulator lang=spice

.param Cload=3fF mob=2.4  wp=0.5  wn='2*wp/mob'

.SUBCKT nand2 o1 s1 s2 vcc
M1   o1 s1 vcc vcc psvtgp w=wp l=0.06
M2   o1 s2 vcc vcc psvtgp w=wp l=0.06
M3   0  s1 2   0   nsvtgp w=wn l=0.06
M4   2  s2 o1  0   nsvtgp w=wn l=0.06
.ENDS nand2

.SUBCKT nand3 o1 s1 s2 s3 vcc
M1   o1 s1 vcc vcc psvtgp  w=wp l=0.06
M2   o1 s2 vcc vcc psvtgp  w=wp l=0.06
M3   o1 s3 vcc vcc psvtgp  w=wp l=0.06
M10  0  s1 4   0   nsvtgp  w=wn l=0.06
M11  4  s3 2   0   nsvtgp  w=wn l=0.06
M12  2  s2 o1  0   nsvtgp  w=wn l=0.06 
.ENDS nand3

.SUBCKT nand4 o1 s1 s2 s3 s4 vcc
M1   o1 s1 vcc vcc psvtgp  w=wp l=0.06
M2   o1 s2 vcc vcc psvtgp  w=wp l=0.06
M3   o1 s3 vcc vcc psvtgp  w=wp l=0.06
M4   o1 s4 vcc vcc psvtgp  w=wp l=0.06
M9   0  s1 6   0   nsvtgp  w=wn l=0.06 
M10  6  s4 4   0   nsvtgp  w=wn l=0.06 
M11  4  s3 2   0   nsvtgp  w=wn l=0.06  
M12  2  s2 o1  0   nsvtgp  w=wn l=0.06 
.ENDS nand4

.SUBCKT nand5 o1 s1 s2 s3 s4 s5 vcc
M1   o1 s1 vcc vcc psvtgp  w=wp l=0.06
M2   o1 s2 vcc vcc psvtgp  w=wp l=0.06
M3   o1 s3 vcc vcc psvtgp  w=wp l=0.06
M4   o1 s4 vcc vcc psvtgp  w=wp l=0.06
M5   o1 s5 vcc vcc psvtgp  w=wp l=0.06
M8   0  s1 8   0   nsvtgp  w=wn l=0.06 
M9   8  s5 6   0   nsvtgp  w=wn l=0.06 
M10  6  s4 4   0   nsvtgp  w=wn l=0.06 
M11  4  s3 2   0   nsvtgp  w=wn l=0.06  
M12  2  s2 o1  0   nsvtgp  w=wn l=0.06   
.ENDS nand5

.SUBCKT nand6 o1 s1 s2 s3 s4 s5 s6 vcc
M1   o1 s1 vcc vcc psvtgp  w=wp l=0.06
M2   o1 s2 vcc vcc psvtgp  w=wp l=0.06
M3   o1 s3 vcc vcc psvtgp  w=wp l=0.06
M4   o1 s4 vcc vcc psvtgp  w=wp l=0.06
M5   o1 s5 vcc vcc psvtgp  w=wp l=0.06
M6   o1 s6 vcc vcc psvtgp  w=wp l=0.06
M7   0  s1 10  0   nsvtgp  w=wn l=0.06 
M8   10 s6 8   0   nsvtgp  w=wn l=0.06 
M9   8  s5 6   0   nsvtgp  w=wn l=0.06 
M10  6  s4 4   0   nsvtgp  w=wn l=0.06 
M11  4  s3 2   0   nsvtgp  w=wn l=0.06 
M12  2  s2 o1  0   nsvtgp  w=wn l=0.06 
.ENDS nand6

** circuito propriamente dito
X1 o2 i1 i2 vcc nand2
X2 o3 i1 i2 i3 vcc nand3
X3 o4 i1 i2 i3 i4 vcc nand4
X4 o5 i1 i2 i3 i4 i5 vcc nand5
X5 o6 i1 i2 i3 i4 i5 i6 vcc nand6

** caps de saida
Cl1 o2 0 Cload
Cl2 o3 0 Cload
Cl3 o4 0 Cload
Cl4 o5 0 Cload
Cl5 o6 0 Cload

** alimentações
vcc  vcc 0  dc 1.0
v1 i1 0 pwl(0 1.0   3n   1.0   3.001n 0 3.25n 0   3.251n 1.0)
v2 i2 0 pwl(0 1.0   4.5n 1.0   4.501n 0 4.75n 0   4.751n 1.0)
v3 i3  0  dc 1.0
v4 i4  0  dc 1.0
v5 i5  0  dc 1.0
v6 i6  0  dc 1.0

.tran 0.001N 10N

**
* mede o tempo para a nand de 2 entradas - os tempos em picosegundos são os que interessam
**
.measure tran n2_descida_gnd trig v(i1)  val=0.5  td=2n rise = 1      targ v(o2)  val=0.5        fall = 1
.measure tran n2_descida_out trig v(i2)  val=0.5  td=2n rise = 1      targ v(o2)  val=0.5        fall = 2
.measure tran n2_subida_gnd  trig v(i1)  val=0.5  td=2n fall = 1      targ v(o2)  val=0.5        rise = 1
.measure tran n2_subida_out  trig v(i2)  val=0.5  td=2n fall = 1      targ v(o2)  val=0.5        rise = 2

.measure tran 2_Fs   param = '1e12*n2_descida_gnd'
.measure tran 2_Fo   param = '1e12*n2_descida_out' 
.measure tran 2_Rs   param = '1e12*n2_subida_gnd'
.measure tran 2_Ro   param = '1e12*n2_subida_out'

**
*  COMPLETAR AQUI COM AS MEDIDAS PARA A NAND DE 3 ENTRADAS  (trocar o nome das medidas e o2 por o3)
**

**
*  COMPLETAR AQUI COM AS MEDIDAS PARA A NAND DE 4 ENTRADAS (trocar o nome das medidas e o2 por o4)
**


**
*  COMPLETAR AQUI COM AS MEDIDAS PARA A NAND DE 4 ENTRADAS (trocar o nome das medidas e o2 por o5)
**

**
* mede o tempo para a nand de 6 entradas
**

 
.END

