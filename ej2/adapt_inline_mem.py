import re
import sys

if(len(sys.argv)>1):
	file_name=sys.argv[1]
else:
	file_name=input("Ingrese el nombre del archivo con su extension. Ej: testcase.v\nArchivo: ")


file=open(file_name)

code=file.read()
file.close()

pattern1= r'  reg \[(.*)\] (\S*) \[(.*)\];\n  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n'

pattern2= r'h(.*?);'

pattern3= r'  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end'

block=re.findall(pattern1,code)

for n in range(len(block)):

	dump_lines=re.findall(pattern2,str(block[n]))
	dump_file= open("memdump"+str(n)+".mem","w")

	for x in dump_lines:
		dump_file.write(str(x) +'\n')
	dump_file.close()


	code=re.sub(pattern3,"  $readmemh(\"memdump"+str(n)+".mem\", mem);\n",code,count=1)


adapted_file = open("adapted_"+file_name,"w")
adapted_file.write(code)
adapted_file.close()