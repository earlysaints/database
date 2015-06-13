from xml.dom import minidom

inxml = minidom.parse(r'm_link.xml')
outcsv = open(r'links.csv','w')
outcsv.write('id,assert_type,subject,predicate,object\n')

for link in inxml.getElementsByTagName('deed'):
    lid = link.getElementsByTagName('LINK_ID')[0].childNodes[0].data
    pid = link.getElementsByTagName('PERSON_ID')[0].childNodes[0].data
    did = link.getElementsByTagName('DEED_ID')[0].childNodes[0].data.rstrip()
    outcsv.write('L'+lid+',relationship,I'+pid+',mentioned in,D'+did+'\n')

outcsv.flush()
outcsv.close
