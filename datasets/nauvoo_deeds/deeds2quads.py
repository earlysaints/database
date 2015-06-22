from xml.dom import minidom, Node
import codecs

def att(obj,key):
    a=""
    b=obj.getElementsByTagName(key)
    if (b):
        a=b[0].childNodes[0].toxml()
    return a


inxml = minidom.parse(r'deeds.xml')
outcsv = codecs.open(r'deeds_quads.csv','w','utf-8')
outcsv.write('id,assert_type,subject,predicate,object\r\n')

preds = {'GRANTOR':'grantor name', 'GRANTOR_RES':'grantor residence',
         'GRANTEE':'grantee name', 'GRANTEE_RES':'grantee residence',
         'TRANSDATE':'date', 'TRANSDATE_NUM':'date*', 'PRICE':'price',
         'VERIFIED':'verified', 'COMMENTS':'note', 'AREA':'area',
         'ACK':'acknowledgement', 'WITNESS':'witness'}
p=1

for deed in inxml.getElementsByTagName('deed'):
    did = deed.getElementsByTagName('DEED_ID')[0].childNodes[0].data
    outcsv.write('D'+did+',entity,D'+did+',common name,Deed '+did+'\n')
    outcsv.write('D'+did+'T,property,D'+did+',entity type,deed\n')
    i=1
    pn=1
    for node in deed.childNodes:
        if (node.nodeType == Node.ELEMENT_NODE and node.nodeName in preds.keys() and node.hasChildNodes()):
            pred = preds[node.nodeName]
            valc = node.childNodes[0]
            val = valc.nodeValue.rstrip()
            val = "".join(val.split("\n"))
            outcsv.write('D'+did+'_'+str(i)+',property,D'+did+','+pred+',|'+val+'|\n')
            i=i+1

    ## Process Parcels
    val=''
    for ln in deed.getElementsByTagName('ln'):
        desc=""
        pid = 'P'+str(pn)
        outcsv.write(pid+'E,property,'+pid+',entity type,land parcel\n')
        outcsv.write(pid+'D,relationship,D'+did+',is about,'+pid+'\n')
        if (ln.getElementsByTagName('twn')):
            twn = ln.getElementsByTagName('twn')[0].childNodes[0].data.rstrip()
            desc = desc+"town:"+twn+" "
            outcsv.write(pid+'_1,property,'+pid+',location town,'+twn+'\n')
        if (ln.getElementsByTagName('rng')):
            rng = ln.getElementsByTagName('rng')[0].childNodes[0].data.rstrip()
            desc = desc+"range:"+rng+" "
            outcsv.write(pid+'_2,property,'+pid+',location range,'+rng+'\n')
        if (ln.getElementsByTagName('twp')):
            twp = ln.getElementsByTagName('twp')[0].childNodes[0].data.rstrip()
            desc = desc+"township:"+twp+" "
            outcsv.write(pid+'_3,property,'+pid+',location township,'+twp+'\n')
        if (ln.getElementsByTagName('plt')):
            plt = ln.getElementsByTagName('plt')[0].childNodes[0].data.rstrip()
            desc = desc+"plat:"+plt+" "
            outcsv.write(pid+'_4,property,'+pid+',location plat,'+plt+'\n')
        if (ln.getElementsByTagName('sec')):
            sec = ln.getElementsByTagName('sec')[0].childNodes[0].data.rstrip()
            desc = desc+"section:"+sec+" "
            outcsv.write(pid+'_5,property,'+pid+',location section,'+sec+'\n')
        if (ln.getElementsByTagName('blk')):
            blk = ln.getElementsByTagName('blk')[0].childNodes[0].data.rstrip()
            desc = desc+"block:"+blk+" "
            outcsv.write(pid+'_6,property,'+pid+',location block,'+blk+'\n')
        if (ln.getElementsByTagName('lot')):
            lot = ln.getElementsByTagName('lot')[0].childNodes[0].data.rstrip()
            desc = desc+"lot:"+lot+" "
            outcsv.write(pid+'_7,property,'+pid+',location lot,'+lot+'\n')
        if (ln.getElementsByTagName('pt')):
            pt = ln.getElementsByTagName('pt')[0].childNodes[0].data.rstrip()
            desc = desc+"part:"+pt+" "
            outcsv.write(pid+'_8,property,'+pid+',location part,'+pt+'\n')
        if (ln.getElementsByTagName('desc')):
            dsc = ln.getElementsByTagName('desc')[0].childNodes[0].data.rstrip()
            desc = desc+"desc:"+dsc+" "
            outcsv.write(pid+'_9,property,'+pid+',location description,|'+dsc+'|\n')
        if (ln.getElementsByTagName('area')):
            area = ln.getElementsByTagName('area')[0].childNodes[0].data.rstrip()
            desc = desc+"("+area+" acres)"
            outcsv.write(pid+'_10,property,'+pid+',area,'+area+'\n')
        outcsv.write(pid+',entity,'+pid+',common name,|'+desc+'|\n')
        val=val+desc+'<br/>'
        pn=pn+1
    outcsv.write('D'+did+'_'+str(i)+',property,D'+did+',parcels,|'+val+'|\n')
    
    #Parse Sources
    s=deed.getElementsByTagName('SOURCE')
    if (s):
        outcsv.write('D'+did+'_'+str(i)+',property,D'+did+',source,|'+s[0].childNodes[0].data+'|\n')
        i=i+1  
    b=att(deed,'HCBOOK')
    p=att(deed,'HCPAGE')
    e=att(deed,'HCENTRY')
    d=att(deed,'HCDATE')
    n=att(deed,'HCDATE_NUM')
    if (len(b+p+e+d+n)>0):
        srcxml='<HC book="'+b+'" page="'+p+'" entry="'+e+'" date="'+d+'" daten="'+n+'">Hancock County Deeds book '+b+' page '+p+' #'+e+' ('+d+')</HC>'
        outcsv.write('D'+did+'_'+str(i)+',property,D'+did+',source,|'+srcxml+'|\n')
        i=i+1
    b=att(deed,'TBOOK')
    p=att(deed,'TPAGE')
    if (len(b+p)>0):
        srcxml='<TLB book="'+b+'" page="'+p+'">Trustees Land Book '+b+' page '+p+'</TLB>'
        outcsv.write('D'+did+'_'+str(i)+',property,D'+did+',source,|'+srcxml+'|\n')
        i=i+1
    b=att(deed,'NBOOK')
    p=att(deed,'NPAGE')
    e=att(deed,'NENTRY')
    d=att(deed,'NDATE')
    n=att(deed,'NDATE_NUM')
    if (len(b+p+e+d+n)>0):
        srcxml='<NC book="'+b+'" page="'+p+'" entry="'+e+'" date="'+d+'" daten="'+n+'">Nauvoo Municipal Court book '+b+' page '+p+' #'+e+' ('+d+')</NC>'
        outcsv.write('D'+did+'_'+str(i)+',property,D'+did+',source,|'+srcxml+'|\n')
        i=i+1
    b=att(deed,'BMBOOK')
    p=att(deed,'BMPAGE')
    e=att(deed,'BMENTRY')
    d=att(deed,'BMDATE')
    n=att(deed,'BMDATE_NUM')
    if (len(b+p+e+d+n)>0):
        srcxml=srcxml+'<BM book="'+b+'" page="'+p+'" entry="'+e+'" date="'+d+'" daten="'+n+'">Hancock County Bonds and Mortgages book '+b+' page '+p+' #'+e+' ('+d+')</BM>'
        outcsv.write('D'+did+'_'+str(i)+',property,D'+did+',source,|'+srcxml+'|\n')
        i=i+1

# TRANSACTION DATE NUMBER
outcsv.flush()
outcsv.close()


