from xml.dom import minidom, Node
import codecs

inxml = minidom.parse(r'deeds.xml')
outcsv = codecs.open(r'deeds.csv','w','utf-8')
outcsv.write('id,assert_type,subject,predicate,object\r\n')

parcsv = codecs.open(r'parcels.csv','w','utf-8')
parcsv.write('id,assert_type,subject,predicate,object\r\n')

preds = {'GRANTOR':'grantor name', 'GRANTOR_RES':'grantor residence',
         'GRANTEE':'grantee name', 'GRANTEE_RES':'grantee residence',
         'TRANSDATE':'date', 'TRANSDATE_NUM':'date*', 'PRICE':'price',
         'LOTS':'parcels*', 'LAND':'parcels*', 'ACK':'acknowledgement',
         'VERIFIED':'verified', 'COMMENTS':'note', 'AREA':'area',
         'WITNESS':'witness'}
p=1

for deed in inxml.getElementsByTagName('deed'):
    did = deed.getElementsByTagName('DEED_ID')[0].childNodes[0].data
    outcsv.write('D'+did+',entity,D'+did+',common name,Deed '+did+'\n')
    outcsv.write('D'+did+'T,property,D'+did+',entity type,deed\n')
    i=1             
    for node in deed.childNodes:
        if (node.nodeType == Node.ELEMENT_NODE and node.nodeName <> 'DEED_ID' and node.hasChildNodes()):
            tag = node.nodeName
            if (tag in preds.keys()):
                pred = preds[tag]
                valc = node.childNodes[0]
                if (valc.nodeType == Node.ELEMENT_NODE): #LOTS or LAND
                    val = ""
                    for ln in valc.getElementsByTagName('ln'):
                        desc=""
                        pid = 'P'+str(p)
                        parcsv.write(pid+'E,property,'+pid+',entity type,land parcel\n')
                        parcsv.write(pid+'D,relationship,D'+did+',is about,'+pid+'\n')
                        if (ln.getElementsByTagName('twn')):
                            twn = ln.getElementsByTagName('twn')[0].childNodes[0].data.rstrip()
                            desc = desc+"town:"+twn+" "
                            parcsv.write(pid+'Tn,property,'+pid+',location town,'+twn+'\n')
                        if (ln.getElementsByTagName('rng')):
                            rng = ln.getElementsByTagName('rng')[0].childNodes[0].data.rstrip()
                            desc = desc+"range:"+rng+" "
                            parcsv.write(pid+'Rg,property,'+pid+',location range,'+rng+'\n')
                        if (ln.getElementsByTagName('twp')):
                            twp = ln.getElementsByTagName('twp')[0].childNodes[0].data.rstrip()
                            desc = desc+"township:"+twp+" "
                            parcsv.write(pid+'Tp,property,'+pid+',location township,'+twp+'\n')
                        if (ln.getElementsByTagName('plt')):
                            plt = ln.getElementsByTagName('plt')[0].childNodes[0].data.rstrip()
                            desc = desc+"plat:"+plt+" "
                            parcsv.write(pid+'Pl,property,'+pid+',location plat,'+plt+'\n')
                        if (ln.getElementsByTagName('sec')):
                            sec = ln.getElementsByTagName('sec')[0].childNodes[0].data.rstrip()
                            desc = desc+"section:"+sec+" "
                            parcsv.write(pid+'Sc,property,'+pid+',location section,'+sec+'\n')
                        if (ln.getElementsByTagName('blk')):
                            blk = ln.getElementsByTagName('blk')[0].childNodes[0].data.rstrip()
                            desc = desc+"block:"+blk+" "
                            parcsv.write(pid+'Bk,property,'+pid+',location block,'+blk+'\n')
                        if (ln.getElementsByTagName('lot')):
                            lot = ln.getElementsByTagName('lot')[0].childNodes[0].data.rstrip()
                            desc = desc+"lot:"+lot+" "
                            parcsv.write(pid+'Lt,property,'+pid+',location lot,'+lot+'\n')
                        if (ln.getElementsByTagName('pt')):
                            pt = ln.getElementsByTagName('pt')[0].childNodes[0].data.rstrip()
                            desc = desc+"part:"+pt+" "
                            parcsv.write(pid+'Pt,property,'+pid+',location part,'+pt+'\n')
                        if (ln.getElementsByTagName('desc')):
                            dsc = ln.getElementsByTagName('desc')[0].childNodes[0].data.rstrip()
                            desc = desc+"desc:"+dsc+" "
                            parcsv.write(pid+'D,property,'+pid+',location description,'+dsc+'\n')
                        parcsv.write(pid+',entity,'+pid+',common name,|'+desc+'|\n')
                        val=val+desc+'<br/>'
                        p=p+1
                else:
                    val = valc.nodeValue.rstrip()
                val = "".join(val.split("\n"))
                outcsv.write('D'+did+'_'+str(i)+',property,D'+did+','+pred+',|'+val+'|\n')
                i=i+1

# SOURCES
# PARCELS
# TRANSACTION DATE NUMBER
outcsv.flush()
outcsv.close()
parcsv.flush()
parcsv.close()
        
