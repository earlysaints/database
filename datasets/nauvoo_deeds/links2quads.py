from xml.dom import minidom

inxml = minidom.parse(r'm_link.xml')
outcsv = open(r'links_quads.csv','w')
outcsv.write('id,assert_type,subject,predicate,object\n')
i=15000 #after persons in number space

for link in inxml.getElementsByTagName('deed'):
    lid = link.getElementsByTagName('LINK_ID')[0].childNodes[0].data
    pid = link.getElementsByTagName('PERSON_ID')[0].childNodes[0].data
    did = link.getElementsByTagName('DEED_ID')[0].childNodes[0].data.rstrip()
    outcsv.write(str(i)+',relationship,D'+did+',mentions,I'+pid+'\n')
    i=i+1

outcsv.flush()
outcsv.close()
