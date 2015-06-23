from xml.dom import minidom
import codecs
inxml = minidom.parse(r'm_persons.xml')
outcsv = codecs.open(r'person_quads.csv', 'w', 'utf-8')
outcsv.write('id,assert_type,subject,predicate,object\r\n')
i=1

for person in inxml.getElementsByTagName('personk'):
    pid = 'I'+person.getElementsByTagName('PERSON_ID')[0].childNodes[0].data
    pname = person.getElementsByTagName('NAME')[0].childNodes[0].data
    outcsv.write(str(i)+',entity,'+pid+',common name,|'+pname+'|\r\n')
    outcsv.write(str(i+1)+',property,'+pid+',entity type,person\r\n')
    pcontentel = person.getElementsByTagName('CONTENT')
    if pcontentel:
        pcontent = pcontentel[0].childNodes[0].data
        pcontent.replace('&lt;','<')
        pcontent = "<br />".join(pcontent.split("\n"))
        outcsv.write(str(i+2)+',property,'+pid+',description,|'+pcontent+'|\r\n')
    i=i+3

outcsv.flush()
outcsv.close()

    
