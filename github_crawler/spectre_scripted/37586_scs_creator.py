import sys
sys.stdout = open('stimulus.scs', 'w')

print('simulator lang=spectre') 
print('parameters VDD = 1.8')
print('//tr is (transition time)/2')
print('parameters tr = 50p') 
print('//f is the fall time') 
print('//parameters f = 100p')
print('//K is the signal period') 
print('parameters K = 40n') 
print('\n')
print('vVdd (vdd 0) vsource dc=VDD')
print('vGnd (gnd 0) vsource dc=0')
print('\n')

lines = [line.rstrip('\n') for line in open('scs_creator_input.txt','r')]
for line in lines:
	words=line.split()
	print('v'+words[0]+' ('+words[1]+ ' '+words[2]+') vsource type=pwl wave=\[')
	bits=list(words[3])
	for i in range(len(bits)):
		ostr=""
		ostr+="+ ("
		if i==0:
			ostr+=" 0*K   ) "
		else:
			ostr+=str(i).rjust(2)+'*K+tr) '
		if bits[i]=='0':
			ostr+='0    ('+str(i+1).rjust(2)+'*K-tr) 0'
		if bits[i]=='1':
			ostr+='VDD  ('+str(i+1).rjust(2)+'*K-tr) VDD'
		print(ostr)
	print('+ ]')
		
			
			
	
