from xml.dom import minidom
import codecs
inxml = minidom.parse(r'm_persons.xml')
outcsv = codecs.open(r'persons.csv', 'w', 'utf-8')
outcsv.write('id,assert_type,subject,predicate,object\r\n')

for person in inxml.getElementsByTagName('personk'):
    pid = 'I'+person.getElementsByTagName('PERSON_ID')[0].childNodes[0].data
    pname = person.getElementsByTagName('NAME')[0].childNodes[0].data
    outcsv.write(pid+',entity,'+pid+',common name,|'+pname+'|\r\n')
    outcsv.write(pid+'T,property,'+pid+',entity type,person\r\n')
    pcontentel = person.getElementsByTagName('CONTENT')
    if pcontentel:
        pcontent = pcontentel[0].childNodes[0].data
        pcontent.replace('&lt;','<')
        pcontent = "<br />".join(pcontent.split("\n"))
        outcsv.write(pid+'C,property,'+pid+',description,|'+pcontent+'|\r\n')

outcsv.flush()
outcsv.close

    
